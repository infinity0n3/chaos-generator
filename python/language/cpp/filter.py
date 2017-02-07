from language.cpp import typemap as cpp_typemap
from language.cpp.test import cpp_is_ptr_test, cpp_is_ref_test

import re
from jinja2 import contextfilter

container_parser = re.compile("((?P<container>\\w+)<)?(?P<type>(\\w|[,*&])+)>?(?P<ptr>\*)?(?P<ref>\&)?(\[(?P<width>\d+)\])?")
type_parser = re.compile("(?P<type>\\w+)(?P<ptr>\*)?(?P<ref>\&)?(\[(?P<width>\d+)\])?")

def cpp_by_value_filter(var, var_type='', prefix='', suffix=''):
	if isinstance(var, dict):
		var_name = var['name']
		var_type = var['type']
	elif isinstance(var, basestring):
		var_name = var
	
	if cpp_is_ptr_test(var_type):
		return '*(' + prefix + var_name + suffix + ')'
	else:
		return prefix + var_name + suffix
		
def cpp_by_ptr_filter(var, var_type, prefix='', suffix=''):
	if isinstance(var, dict):
		var_name = var['name']
		var_type = var['type']
	elif isinstance(var, basestring):
		var_name = var
		
	if cpp_is_ptr_test(var_type):
		return prefix + var_name + suffix
	else:
		return '&(' + prefix + var_name + suffix + ')'
		
def cpp_to_ref_filter(var_type, const=False):
	result = var_type
	
	is_ptr = '*' in var_type
	is_ref = '&' in var_type
	
	if not is_ptr and not is_ref:
		result += '&'
		
	if const:
		result = 'const ' + result
	
	return result

def cpp_camel_name_filter(name, capitalize_first=False):
	tags = re.split("[ _-]", name)
	
	result = ''
	first=True
	for t in tags:
		tt = t.capitalize()
		if first and not capitalize_first:
			tt = t
			
		first=False
			
		result += tt
	
	return result

def cpp_attr_filter(var_name, var_type, attr, prefix='', suffix=''):
	attr_access = '->' if var_type[-1] == '*' else '.'
	return prefix+var_name+suffix + attr_access + attr

def cpp_defprotect(value):
	result = value
	result = result.replace('.', '_')
	result = result.replace(' ', '_')
	result = result.replace('/', '_')
	result = result.replace('\\', '_')
	result = result.replace('"', '')
	result = result.replace("'", '')
	return result.upper() + '_H'

def cpp_blockcomment_filter(block):
	start_comment = '/** '
	line_comment = ' * '
	end_comment = ' **/'
	
	result = []
	lines = block.split('\n');
	
	result.append(start_comment)
	
	for line in lines:
		result.append(line_comment + line)
	
	result.append(end_comment)

	return "\n".join(result)

def cpp_linecomment_filter(line):
	start_comment = '// '
	end_comment = ''
	
	if line:
		lines = line.split('\n');
	else:
		lines = []
	line = " ".join(lines)
	
	return start_comment + line + end_comment

def cpp_block_filter(block, terminate=False):
	start_block = '{'
	end_block 	= '};' if terminate else '}';
	
	lines = block.split('\n')
	if lines[0] == "":
		lines[0] = start_block
	else:
		lines.insert(0, start_block)

	if lines[-1] == "":
		lines[-1] = end_block
	else:
		lines.append(end_block)
	
	return "\n".join(lines)

def cpp_disect_type(decl):
	result = {}
	
	m = container_parser.search(decl)

	container = m.group("container")
	contained_types = m.group("type") or ""
	container_ptr = m.group("ptr") or ""
	container_ref = m.group("ref") or ""
	container_width = ""
	if m.group("width"):
		container_width = "[{0}]".format(m.group("width"))

	result["container"] = m.group("container") or ""
	result["width"] = m.group("width") or ""
	result["extra"] = container_ptr + container_ref

	types = []

	tl = contained_types.split(',')
	for t in tl:
		m = type_parser.search(t)
		if m:
			ptr = m.group("ptr") or ""
			ref = m.group("ref") or ""
			var_type = m.group("type")
			types.append({
				"name": var_type,
				"extra": ptr + ref
			})

	result["types"] = types

	return result

def cpp_type_filter(typename, typemap=None):
	
	
	if not typename:
		return 'void'
	
	if not typemap:
		typemap = cpp_typemap

	m = cpp_disect_type(typename)

	result = ''

	types = []

	for t in m['types']:
		var_type = t['name']
		if var_type in typemap:
			var_type = typemap[var_type]
		types.append( var_type + t['extra'] )

	if m['container']:
		container = m['container']
		if container in typemap:
			container = typemap[container]
		container_width = ""
		if m['width']:
			container_width = "[" + m['width'] + "]"
			
		result = "{0}<{1}>{2}{3}".format(container, ",".join(types), m['extra'], container_width)
	else:
		result = types[0]
	
	return result

def cpp_arguments_filter(arg_list, use_default=False):
	if not arg_list:
		return ''
		
	result = ''
	prefix = ''
	for arg in arg_list:
		const = ''
		if 'tags' in arg:
			if 'const' in arg['tags']:
				const = 'const '
		result += prefix + const + arg['type'] + ' ' + arg['name']
		if "default" in arg and use_default:
			result += ' = ' + arg["default"]
		if not prefix:
			prefix = ', '
			
	return result

def cpp_list_filter(arg_list):
	if not arg_list:
		return ''
	result = ''
	prefix = ''
	
	for arg in arg_list:
		result += prefix + arg
		if not prefix:
			prefix = ', '
			
	return result

def cpp_declare_var_filter(var_type, var_name, init='', new=False):
	
	result = ""
	
	var_type_pure = var_type.replace('*', '').replace('&', '')
	
	if new:
		if  cpp_is_ptr_test(var_type):
			result = "{0} {1} = new {2}({3})".format(var_type, var_name, var_type_pure, init)
		else:
			result = "{0} {1} = {0}({2})".format(var_type, var_name, init)
	else:
		result = var_type + " " + var_name
		if init:
			result += " = " + init

	return result
	
def cpp_new_value_filter(var_type, init=''):
	is_ptr = cpp_is_ptr_test(var_type)
	result = ""
	
	var_type = var_type.replace('*', '').replace('&', '')
	
	if is_ptr:
		result = "new {0}({1})".format(var_type, init)
	else:
		result = "{0}({1})".format(var_type, init)
		
	return result
	
cpp_indent = re.compile("(?P<indent>\\s*)(?P<code>.*)")

@contextfilter
def cpp_section_filter(context, value, section_name, method_name='', class_name='', condition=True, indent=''):
	
	lines = value.split('\n')
	
	if not lines[0]:
		lines.pop(0)
	
	if not condition:
		return "\n".join(lines)
	
	for line in lines:
		m = cpp_indent.search(line)
		if m.group('indent'):
			indent = m.group('indent')
			break;
	
	section = section_name
	if class_name and method_name:
		section = "{0}_{1}_{2}".format(class_name,method_name,section_name)
	
	if section in context['sections']:
		lines = context['sections'][section].split('\n')
	
	lines.insert(0, "{0}// section:{1}".format(indent, section_name))
	lines.append("{0}// endsection:{1}".format(indent, section_name))
	
	return "\n".join(lines)

def cpp_extract_sections(filename, class_name=''):
	with open(filename) as f:
		content = f.read()
	
	section_seeker = re.compile("//\s*(?P<end>end)?section:(?P<section>\\w+)")
	lines = content.split('\n')
	
	fun_name = ''
	section_name = ''
	section = []
	sections = {}
	
	for line in lines:
		if class_name:
			tmp = line.split(class_name + '::')
			if len(tmp) > 1:
				tmp = tmp[1].strip().split('(')
				if len(tmp) > 1:
					fun_name = tmp[0]
		
		m = section_seeker.search(line)
		if m:
			name,end = m.group('section', 'end')
			if end:
				if class_name and fun_name:
					sections["{0}_{1}_{2}".format(class_name,fun_name,section_name)] = "\n".join(section)
				else:
					sections[section_name] = "\n".join(section)
				section_name = ''
				section = []
			else:
				section_name = name
		else:
			if section_name:
				section.append(line)
			
	return sections

def cpp_class_filename(class_name, prefix='', suffix=''):
	result = prefix + class_name.lower() + suffix	
	return result
