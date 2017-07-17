from jinja2 import contextfilter

def singularize_filter(value):
	if len(value) < 2:
		return value
		
	if value[-1] == 's' or value[-1] == 'S':
		return value[:-1]

def pluralize_filter(value):
	if not value:
		return ''
		
	return value + 's'
