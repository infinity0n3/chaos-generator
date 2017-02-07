from language.cpp import typemap as cpp_typemap
import re
from jinja2 import contextfilter

def cpp_is_ptr_test(value):
	return value[-1] == '*'
	
def cpp_is_ref_test(value):
	return value[-1] == '&'
