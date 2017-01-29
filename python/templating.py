import os
import jinja2

from extensions.language.cpp import cpp_blockcomment_filter, \
	cpp_linecomment_filter, cpp_block_filter, cpp_type_filter, \
	cpp_arguments_filter, cpp_section_filter, cpp_extract_sections, \
	cpp_defprotect, cpp_list_filter

templateSearchPath = os.path.dirname(os.path.realpath(__file__)) + '/' + "templates"
templateLoader = jinja2.FileSystemLoader( searchpath=templateSearchPath )
templateEnv = jinja2.Environment( loader=templateLoader )

templateEnv.filters['cpp_blockcomment'] = cpp_blockcomment_filter
templateEnv.filters['cpp_linecomment'] = cpp_linecomment_filter
templateEnv.filters['cpp_block'] = cpp_block_filter
templateEnv.filters['cpp_defprotect'] = cpp_defprotect
templateEnv.filters['cpp_type'] = cpp_type_filter
templateEnv.filters['cpp_arguments'] = cpp_arguments_filter
templateEnv.filters['cpp_section'] = cpp_section_filter
templateEnv.filters['cpp_list'] = cpp_list_filter

def create_from_template(template, output, env = {}, overwrite = False, preserve = True):
	#~ if not os.path.exists(output) or overwrite:
	env['sections'] = {}
	
	if os.path.exists(output):
		if not overwrite:
			return
			
		if overwrite and preserve:
			class_name = ''
			if 'class' in env:
				if 'name' in env['class']:
					class_name = env['class']['name']
			sections = cpp_extract_sections(output, class_name)
			env['sections'] = sections
			
	t = templateEnv.get_template(template)
	if 'filename' not in env:
		env['filename'] = os.path.basename(output)
	outputText = t.render( env )
	if output:
		f = open(output, 'w')
		f.write(outputText)
		f.close()
		print("create '{:s}' based on '{:s}'".format(output,template))
	else:
		print("create based on '{:s}'".format(template))
		print(outputText)

def create_dir(f):
	if not os.path.exists(f):
		os.makedirs(f)
		print( 'mkdir {:s}'.format(f) )

def create_link(src, dst, overwrite = False):
	if os.path.lexists(dst):
		if overwrite:
			os.remove(dst)
			os.symlink(src, dst)
			print( 'softlink {:s} -> {:s}'.format(dst,src) )
	else:
		os.symlink(src, dst)
		print( 'softlink {:s} -> {:s}'.format(dst,src) )

def build_path(*args):
	return os.path.join(*args)
