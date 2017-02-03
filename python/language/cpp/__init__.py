import re

type_parser = re.compile("((?P<container>\\w+)<)?(?P<type>\\w+)+(?P<ptr>\*)?(?P<ref>\&)?(\[(?P<width>\d+)\])?>?(?P<container_ptr>\*)?(?P<container_ref>\&)?(\[(?P<container_width>\d+)\])?")

typemap = {
	# Builtin
	'pointer'  : 'void',
	# Containers
	'vector'   : 'std::vector',
	'stack'    : 'std::stack',
	'queue'    : 'std::queue',
	'list'     : 'std::list',
	'string'   : 'std::string',
	'wstring'  : 'std::wstring'
};

builtin_types = {
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

from language.cpp.templating import create_templating_environment
from language.cpp.templating import create_file_from_template
from language.cpp.analyze import planner

from language.common import *
