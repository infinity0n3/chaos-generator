import re
from jinja2 import contextfilter

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

cpp_type_parser = re.compile("((?P<container>\\w+)<)?(?P<type>\\w+)(?P<ptr>\*)?(?P<ref>\&)?(\[(?P<width>\d+)\])?>?(?P<container_ptr>\*)?(?P<container_ref>\&)?(\[(?P<container_width>\d+)\])?")
cpp_typemap = {
	'vector' : 'std::vector',
	'stack' : 'std::stack',
	'queue' : 'std::queue',
	'list'   : 'std::list',
	'string' : 'std::string',
	'wstring' : 'std::wstring'
};

cpp_builtin_types = {
	'unsigned': [],
	'int': [],
	'char': [],
	'short': [],
	'long': [],
	'float': [],
	'uint8_t': 		['<cstdint>'],
	'uint16_t':		['<cstdint>'], 
	'uint32_t':		['<cstdint>'], 
	'uint64_t':		['<cstdint>'], 
	'int8_t':		['<cstdint>'], 
	'int16_t':		['<cstdint>'], 
	'int32_t':		['<cstdint>'], 
	'int64_t':		['<cstdint>'],
	'std::array': 	['<array>'],
	'std::vector': 	['<vector>'],
	'std::list': 	['<list>'],
	'std::set': 	['<set>'],
	'std::queue': 	['<queue>'],
	'std::stack': 	['<stack>'],
	'std::string': 	['<string>'],
	'std::wstring': ['<string>'],
	'std::forward_list': ['<forward_list>'],
	}

def cpp_type_filter(typename, typemap=None):
	
	if not typename:
		return 'void'
	
	if not typemap:
		typemap = cpp_typemap
	
	m = cpp_type_parser.search(typename)
	
	is_array = int(m.group('width')) if m.group('width') else None
	ptr = '*' if m.group('ptr') == '*' else ''
	ref = '&' if m.group('ref') == '&' else ''
	typename = m.group('type')
	has_container = m.group('container')
	
	if typename in typemap:
		typename = typemap[typename]
	
	result = typename + ptr + ref
	
	if has_container:
		
		if has_container in typemap:
			container = typemap[has_container]
		
		container_ptr = '*' if m.group('container_ptr') else ''
		container_ref = '&' if m.group('container_ref') else ''
		result = container + '< ' + result + ' >' + container_ptr + container_ref
	
	return result

def cpp_arguments_filter(arg_list, typemap=None, use_default=False):
	if not arg_list:
		return ''
		
	if not typemap:
		typemap = cpp_typemap
		
	result = ''
	prefix = ''
	for arg in arg_list:
		result += prefix + cpp_type_filter(arg['type'], typemap) + ' ' + arg['name']
		#~ if "default" in p:
			#~ ret = ret + ' = ' + p["default"]
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

cpp_indent = re.compile("(?P<indent>\\s*)(?P<code>.*)")

@contextfilter
def cpp_section_filter(context, value, section_name, method_name='', class_name='', condition=True):
	
	lines = value.split('\n')
	indent = ''
	
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
