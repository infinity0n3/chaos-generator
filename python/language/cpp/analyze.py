import re
from copy import deepcopy
from language.cpp.filter import cpp_type_parser, cpp_type_filter, cpp_class_filename

from tarjan import tarjan

def cpp_extract_types(value, typemap):
	"""
	Extract type and container from CONTAINER<TYPE> notation
	"""
	result = []
	m = cpp_type_parser.search(value)
	
	if m.group('type'):
		result.append( cpp_type_filter(m.group('type')) )
		
	if m.group('container'):
		result.append( cpp_type_filter(m.group('container')) )
		
	return result

def cpp_position(a, b, group):
	"""
	Return relative position to each other of element `a` and `b` in `group`
	"""
	if a not in group:
		return None
		
	if b not in group:
		return None
	
	a_idx = 0
	b_idx = 0
	i = 0
	for g in group:
		if g == a:
			a_idx = i
		if g == b:
			b_idx = i
		i += 1
		
	if a_idx < b_idx:
		return "after"
	elif a_idx > b_idx:
		return "before"
	else:
		return "same"

def planner(models, packages, typemap, builtin_types = {}, library_types = {}, custom_types = {}, cpp_ext='.cpp', hpp_ext='.h' ):
	
	model_uses = {}
	model_inherits = {}
	model_package = {}
	model_env = {}
	
	errors = {}
	
	for model in models:
		name = model['name']
		model_env[name] = model.copy()
		
	# Gather model type usage
	for name in model_env:
		model = model_env[name]
		model_types = []
		model_inherit = []
		
		is_abstract = False
		default_contructor = True
		default_destructor = True
			
		if 'methods' in model:
			for method in model['methods']:
				if method['name'] == name:
					default_contructor = False
				if 'return' not in method:
					method['return'] = 'void'
				if 'tags' in method:
					if 'abstract' in method['tags']:
						is_abstract = True
		
		for parent in model['parents'] if 'parents' in model else []:
			if parent not in model_types:
				model_types.append( parent )
			if parent not in model_inherit:
				model_inherit.append(parent)
					
		for interface in model['interfaces'] if 'interfaces' in model else []:
			if interface not in model_types:
				model_types.append( interface )
			if interface not in model_inherit:
				model_inherit.append(interface)
				
			# Add interfaces to parents list as in c++ they are the same
			if 'parents' not in model:
				model['parents'] = []
				
			if interface not in model['parents']:
				model_env[name]['parents'].append(interface)
				
				# Add interface functions to child model
				interface = model_env[interface]
				for method in interface['methods'] if 'methods' in interface else []:
					if 'tags' in method:
						if 'abstract' in method['tags']:
							method_impl = deepcopy(method)
							idx = method_impl['tags'].index('abstract')
							method_impl['tags'].append("virtual")
							method_impl['tags'].pop(idx)
							if 'methods' in model_env[name]:
								model['methods'].append(method_impl)
							else:
								model['methods'] = [method_impl]
					
		for propertie in model['properties'] if 'properties' in model else []:
			types = cpp_extract_types(propertie['type'], typemap)
			for t in types:
				if t not in model_types:
					model_types.append(t)
		
		if default_destructor:
			destructor = {
				'name' : '~' + name,
				'tags' : ['destructor']
			}
			if is_abstract:
				destructor['tags'].append('virtual')
				
			if 'methods' not in model:
				model['methods'] = [destructor]
			else:
				model['methods'].insert(0, destructor)
		
		if default_contructor:
			constructor = {
				'name' : name,
				'tags' : ['constructor']
			}
			if 'methods' not in model:
				model['methods'] = [constructor]
			else:
				model['methods'].insert(0, constructor)
		
		if 'methods' in model:
			for method in model['methods']:
				for argument in method['arguments'] if 'arguments' in method else []:
					types = cpp_extract_types(argument['type'], typemap)
					for t in types:
						if t not in model_types:
							model_types.append(t)
							
		model_uses[name] = model_types
		model_inherits[name] = model_inherit
	
		has_package = False
		for pkg in packages:
			if name in packages[pkg]:
				model_package[name] = pkg
				has_package = True
				break
		if not has_package:
			model_package[name] = model['package'] if 'package' in model else cpp_class_filename(name)
	
	scc = tarjan(model_uses)
	
	## Sort by inheritance
	scc_sorted = []
	for group in scc:
		fixed = group[:]
		for m in group:
			for i in model_inherits[m] if m in model_inherits else []:
				if i in group:
					r = cpp_position(m ,i, fixed)
					if r == "after":
						idx1 = fixed.index(i)
						tmp = fixed.pop(idx1)
						idx0 = fixed.index(m)
						fixed.insert(idx0, tmp)
						
		scc_sorted.append(fixed)
		
	scc = scc_sorted

	package_includes = {}

	## Populate packages with includes and forward declarations
	for group in scc:
		for m in group:
			if m in model_uses:
				pkg1 = model_package[m]
				inc = ['"'+pkg1+hpp_ext+'"']
				inc_hpp = []
				fwd_hpp = []
				for dep in model_uses[m]:
					if dep in builtin_types:
						t = 'builtin'
					elif dep in library_types:
						t = 'framework'
						inc.extend( library_types[dep] )
						inc_hpp.extend( library_types[dep] )
					else:
						r = cpp_position(m, dep, group)
						
						pkg2 = model_package[dep]
						
						same_package = (pkg1 == pkg2)
						same_group = (dep in group)
						
						include = '"'+cpp_class_filename(dep)+hpp_ext+'"'
						
						if r == None:
							if not same_package:
								inc_hpp.append(include)
						elif r == "before":
							if not same_package:
								inc_hpp.append(include) 
						elif r == "after":
							fwd_hpp.append(dep)
							
						if not same_group:
							if include not in inc_hpp:
								inc.append( include )
				
				model_env[m]['forwards'] = fwd_hpp
				
				if pkg1 not in package_includes:
					package_includes[pkg1] = {
						"def": {
							"includes":inc_hpp,
						},
						"impl":{
							"includes":inc
						},
						"classes" : [ model_env[m] ],
					}
				else:
					package_includes[pkg1]['def']['includes'].extend(inc_hpp)
					package_includes[pkg1]['impl']['includes'].extend(inc)
					package_includes[pkg1]['classes'].append(model_env[m])
				
	
	## Create generator units
	
	gen_units = []
	
	for pkg_name in package_includes:
		pkg = package_includes[pkg_name]
		inc = set(pkg['def']['includes'])
		inc = list(inc)
		inc.sort()
		
		gu = {
			"template" : "cpp/source.h.template",
			"filename" : pkg_name + hpp_ext,
			"env" : {
				"classes": pkg['classes'],
				"includes" : inc,
				"package" : pkg_name
			}
		}
		gen_units.append(gu)
		
		inc = set(pkg['impl']['includes'])
		inc = list(inc)
		inc.sort()
		
		gu = {
			"template" : "cpp/source.cpp.template",
			"filename" : pkg_name + cpp_ext,
			"env" : {
				"classes": pkg['classes'],
				"includes" : inc,
				"package" : pkg_name
			}
		}
		gen_units.append(gu)
	
	return gen_units, errors
