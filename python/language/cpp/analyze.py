import re
from copy import deepcopy
from language.cpp.filter import cpp_disect_type, cpp_type_filter, \
	cpp_class_filename, cpp_camel_name_filter, cpp_to_ref_filter

from tarjan import tarjan

def cpp_extract_types(value, container_extras=False, contained_extras=False):
	"""
	Extract type and container from CONTAINER<TYPE> notation
	"""
	result = []
	
	m = cpp_disect_type(value)
	
	for t in m['types']:
		result.append( t['name'] + (t['extra'] if contained_extras else "") )
		
	if m['container']:
		result.append( m['container'] + (t['extra'] if container_extras else "") )
		
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

def cpp_convert_types(model, typemap):
	
	iterrable = ["vector", "list", "queue", "set", "hash"]
	collection = ["stack"]
	
	for extra_deps in model['extra_deps'] if 'extra_deps' in model else []:
		tmp = []
		for t in model['extra_deps']:
			tmp.append( cpp_type_filter(t, typemap) )
		model['extra_deps'] = tmp
	
	for propertie in model['properties'] if 'properties' in model else []:
		raw_type = propertie['type']
		type_class = 'value'
		
		tags = []
		if 'tags' in propertie:
			tags = propertie['tags']
		
		t = cpp_extract_types(raw_type, contained_extras=True)
		if len(t) > 1:
			container = t[-1]
			if container in iterrable:
				type_class = 'iterrable'
			propertie['container'] = container
			propertie['contained'] = {
				"container" : container,
				"name" : propertie['name'],
				"type" : cpp_type_filter(t[0])
			}
		
		propertie['type'] = cpp_type_filter(raw_type, typemap)
		propertie['type_class'] = type_class
		
		if 'foreign' in tags:
			if 'const' not in tags and 'contained' not in propertie:
				tags.append('const')
				
			if 'ref_store' not in tags:
				tags.append('ref_store')
	
	for method in model['methods'] if 'methods' in model else []:
		
		if 'return' in method:
			raw_type = method['return']
			method['return'] = cpp_type_filter(raw_type, typemap)
		else:
			method['return'] = 'void'
		
		for argument in method['arguments'] if 'arguments' in method else []:
			raw_type = argument['type']
			type_class = 'value'
			
			t = cpp_extract_types(raw_type, contained_extras=True)
			if len(t) > 1:
				container = t[-1]
				if container in iterrable:
					type_class = 'iterrable'
				argument['container'] = container
				argument['contained'] = {
					"container" : container,
					"name" : argument['name'],
					"type" : cpp_type_filter(t[0])
				}
				
			argument['type'] = cpp_type_filter(raw_type, typemap)
			argument['type_class'] = type_class
	
	return model

def preprocess_types(models, model_env, typemap):
	
	def add_if_not_exists(container, item):
		for obj in container:
			if obj['name'] == item['name']:
				return
		
		container.append(item)
	
	print "== processing types =="
	for model in models:
		name = model['name']
		print "++", name
		model_env[name] = cpp_convert_types( model.copy(), typemap )
		
	for name in model_env:
		model = model_env[name]
		
		extends = model.pop("extends", [])
		if extends:
			tags 		= model['tags'] if 'tags' in model else []
			methods 	= model['methods'] if 'methods' in model else []
			properties 	= model['properties'] if 'properties' in model else []
			interfaces 	= model['interfaces'] if 'interfaces' in model else []
			parents 	= model['parents'] if 'parents' in model else []
			
			for ex_name in extends:
				print "   EXTENDS", ex_name, " -> ", name
				
				ex = model_env[ex_name]
				
				for method in ex['methods'] if 'methods' in ex else []:
					add_if_not_exists(methods, method)
						
				for propertie in ex['properties'] if 'properties' in ex else []:
					add_if_not_exists(properties, propertie)
						
				for interface in ex['interfaces'] if 'interfaces' in ex else []:
					if interface not in interfaces:
						interfaces.append(interface)
						
				for parent in ex['parents'] if 'parents' in ex else []:
					if parent not in parents:
						parents.append(parent)
						
			model['methods'] = methods
			model['properties'] = properties
			model['interfaces'] = interfaces
			model['parents'] = parents
			model['tags'] = tags


def add_model_method(model, method, prepend=False):
	if 'methods' not in model:
		model['methods'] = [method]
	else:
		if prepend:
			model['methods'].insert(0, method)
		else:
			model['methods'].append(method)
			
def add_method_tag(method, tag, prepend=False):
	if 'tags' not in method:
		method['tags'] = [tag]
	else:
		if prepend:
			method['tags'].insert(0, tag)
		else:
			method['tags'].append(tag)

def preporcess_constructors(model_env):
	print "== processing constructors =="
	# Gather model type usage
	for name in model_env:
		model = model_env[name]
		
		is_abstract = False
		default_contructor = True
		default_destructor = True
			
		if 'methods' in model:
			for method in model['methods']:
				if method['name'] == name:
					default_contructor = False
					
				if 'tags' in method:
					if 'abstract' in method['tags']:
						is_abstract = True
		
		# Add default desctructor
		if default_destructor:
			destructor = {
				'name' : '~' + name,
				'tags' : ['destructor'],
				'brief': "Default desctructor"
			}
			if is_abstract:
				destructor['tags'].append('virtual')
			
			add_model_method(model, destructor, prepend=True)
		
		# Add default constructor
		if default_contructor:
			constructor = {
				'name' : name,
				'tags' : ['constructor'],
				'brief': "Default constructor"
			}
			add_model_method(model, constructor, prepend=True)

def preprocess_encapsulation(model_env):
	print "== processing encapsulation =="
	for name in model_env:
		model = model_env[name]
		for propertie in model['properties'] if 'properties' in model else []:
			p_name = propertie['name']
			p_type = propertie['type']
			
			tags = []
			if 'tags' in propertie:
				tags = propertie['tags']
				
			if 'protected' in tags:
				add_method_tag(model, 'has_protected')
			
			if "private" not in tags:
				if "no_read" not in tags:
					getter_name = cpp_camel_name_filter(p_name)
					getter = {
						'brief': "m_{0} set function".format(p_name),
						'name' : getter_name,
						'return': cpp_to_ref_filter(p_type),
						'template': 'cpp/property_getter.impl.template',
						'meta': {
							'property': {'name': p_name}
						},
						'tags' : ['getter', 'return_const', 'const'],
					}
					add_model_method(model, getter)
					propertie['getter'] = getter_name
				
				if "no_write" not in tags:
					setter_name = "set"+cpp_camel_name_filter(p_name, True)
					setter = {
						'brief': "m_{0} get function".format(p_name),
						'name' : setter_name,
						'return': 'void',
						'template': 'cpp/property_setter.impl.template',
						'meta': {
							'property': {'name': p_name}
						},
						'arguments': [{
							'brief': "New m_{0} value".format(p_name),
							'name': p_name,
							'type': cpp_to_ref_filter(p_type),
							'tags': ['const']
						}],
						'tags' : ['setter'],
					}
					add_model_method(model, setter)
					propertie['setter'] = setter_name
					
			if "protected" not in tags and "public" not in tags:
				if "private" not in tags:
					tags.append("private")
				
			propertie['tags'] = tags

def tags_contains_prefix(tags, tag_prefix):
	for tag in tags:
		if tag.startswith(tag_prefix):
			return tag
	return None
	
def preprocess_containers(model_env):
	print "== processing containers =="
	for name in model_env:
		model = model_env[name]
		for propertie in model['properties'] if 'properties' in model else []:
			if 'contained' in propertie:
				
				print propertie
				
				p_name = propertie['name']
				p_type = propertie['type']
				p_container = propertie['contained']['container']
				p_contained_type = propertie['contained']['type']
				
				tags = []
				if 'tags' in propertie:
					tags = propertie['tags']
				
				if 'container_add' in tags:
					method_name = cpp_camel_name_filter('add_' + p_name + '_item')
					print "Container[container_add]", method_name
					method = {
						'brief': "Add item to m_{0} conteinr".format(p_name),
						'name' : method_name,
						'return': 'void',
						'template': 'cpp/container_add.impl.template',
						'arguments': [{
							'brief': "New m_{0} value".format(p_name),
							'name': 'item',
							'type': cpp_to_ref_filter(p_contained_type),
							'tags': ['const']
						}],
						'tags' : ['container_add'],
					}
					add_model_method(model, method)
					
				if tags_contains_prefix(tags, 'container_new:'):
					contained_property = tags_contains_prefix(tags, 'container_new:').split(':')[1].split(',')
					method_name = cpp_camel_name_filter('add_' + p_name + '_item')
					print "Container[container_add_by]", method_name
					
				if 'container_remove' in tags:
					method_name = cpp_camel_name_filter('remove_' + p_name)
					print "Container[container_remove]", method_name
					
				if tags_contains_prefix(tags, 'container_remove_by:'):
					contained_property = tags_contains_prefix(tags, 'container_contains_by:').split(':')[1].split(',')
					method_name = cpp_camel_name_filter('remove_' + p_name)
					print "Container[container_remove_by]", method_name
					
				if 'container_contains' in tags:
					method_name = cpp_camel_name_filter(p_name + '_contains')
					print "Container[container_contains]", method_name
					
				if tags_contains_prefix(tags, 'container_search_by:'):
					contained_property = tags_contains_prefix(tags, 'container_contains_by:').split(':')[1].split(',')
					method_name = cpp_camel_name_filter(p_name + '_search_by' )
					print "Container[container_search_by {0}]".format(contained_property), method_name
					
				if tags_contains_prefix(tags, 'container_contains_by:'):
					
					contained_property = tags_contains_prefix(tags, 'container_contains_by:').split(':')[1]
					method_name = cpp_camel_name_filter(p_name + '_contains_' + contained_property)
				
					print "Container[container_contains_by {0}]".format(contained_property), method_name

def planner(models, packages, typemap, builtin_types = {}, library_types = {}, custom_types = {}, cpp_ext='.cpp', hpp_ext='.h' ):
	
	model_uses = {}
	model_inherits = {}
	model_package = {}
	model_env = {}
	
	errors = []
	
	preprocess_types(models, model_env, typemap)
	
	preporcess_constructors(model_env)
	
	preprocess_encapsulation(model_env)
	
	preprocess_containers(model_env)
	
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
			types = cpp_extract_types(propertie['type'])
			for t in types:
				if t not in model_types:
					model_types.append(t)
		
		if 'methods' in model:
			for method in model['methods']:
				for argument in method['arguments'] if 'arguments' in method else []:
					types = cpp_extract_types(argument['type'])
					for t in types:
						if t not in model_types:
							model_types.append(t)
							
				if 'return' in method:
					types = cpp_extract_types(method['return'])
					for t in types:
						if t not in model_types and t != 'void':
							model_types.append(t)
							
		extra_deps = []
		if 'extra_deps' in model:
			extra_deps = model['extra_deps']
		
		model_uses[name] = model_types + extra_deps
		model_inherits[name] = model_inherit
	
		has_package = False
		for pkg in packages:
			if name in packages[pkg]:
				model_package[name] = pkg
				has_package = True
				break
		if not has_package:
			model_package[name] = model['package'] if 'package' in model else cpp_class_filename(name)
	
	
	## Check reference validity
	has_errors = False
	for m in model_uses:
		for dep in model_uses[m]:
			if ( dep not in builtin_types and
			   dep not in library_types and 
			   dep not in model_uses ):
				errors.append({
					"type": "critical",
					"msg": "Model '{0}' references an undefined model '{1}'".format(m, dep)
				})
				has_errors = True
				
	for m in model_inherits:
		for dep in model_inherits[m]:
			if ( dep not in builtin_types and
			   dep not in library_types and 
			   dep not in model_uses ):
				errors.append({
					"type": "critical",
					"msg": "Model '{0}' inherits an undefined model '{1}'".format(m, dep)
				})
				has_errors = True
	
	if has_errors:
		return [], errors
	
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
						
						include = '"'+model_package[dep]+hpp_ext+'"'
						
						if r == None:
							if not same_package:
								inc_hpp.append(include)
						elif r == "before":
							if not same_package:
								inc_hpp.append(include) 
						elif r == "after":
							fwd_hpp.append(dep)
							
						if not same_package:
							if include not in inc:
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
