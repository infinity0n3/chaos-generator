import os
import jinja2

from language.cpp.filter import cpp_blockcomment_filter, \
	cpp_linecomment_filter, cpp_block_filter, cpp_type_filter, \
	cpp_arguments_filter, cpp_section_filter, cpp_extract_sections, \
	cpp_defprotect, cpp_list_filter, cpp_declare_var_filter, cpp_attr_filter

from language.cpp.test import cpp_is_ptr_test, cpp_is_ref_test

def create_templating_environment(template_paths):
	loaders = []
	
	for search_path in template_paths:
		loaders.append( jinja2.FileSystemLoader( searchpath=search_path ) )
	
	templateLoader = jinja2.ChoiceLoader( loaders )
	
	templateEnv = jinja2.Environment( loader=templateLoader )

	templateEnv.filters['cpp_blockcomment'] = cpp_blockcomment_filter
	templateEnv.filters['cpp_linecomment'] = cpp_linecomment_filter
	templateEnv.filters['cpp_block'] = cpp_block_filter
	templateEnv.filters['cpp_defprotect'] = cpp_defprotect
	templateEnv.filters['cpp_type'] = cpp_type_filter
	templateEnv.filters['cpp_arguments'] = cpp_arguments_filter
	templateEnv.filters['cpp_section'] = cpp_section_filter
	templateEnv.filters['cpp_list'] = cpp_list_filter
	templateEnv.filters['cpp_declare_var'] = cpp_declare_var_filter
	templateEnv.filters['cpp_attr'] = cpp_attr_filter
	
	templateEnv.tests['cpp_is_ptr'] = cpp_is_ptr_test
	templateEnv.tests['cpp_is_ref'] = cpp_is_ref_test
	
	return templateEnv
		
def create_file_from_template(template, output, env = {}, overwrite = False, preserve = True):
	#~ if not os.path.exists(output) or overwrite:
	env['sections'] = {}
	
	if os.path.exists(output):
		if not overwrite:
			return
			
		if overwrite and preserve:
			sections = {}
			for iclass in env['classes'] if 'classes' in env else []:
				class_name = iclass['name'] or ""
				sec = cpp_extract_sections(output, class_name)
				sections.update(sec)
			env['sections'] = sections
			
	if 'filename' not in env:
		env['filename'] = os.path.basename(output)
	outputText = template.render( env )
	if output:
		f = open(output, 'w')
		f.write(outputText)
		f.close()
		print("create '{:s}' based on '{:s}'".format(output,template))
	else:
		print("create based on '{:s}'".format(template))
		print(outputText)
