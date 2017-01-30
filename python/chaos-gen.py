#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# (c) 2016 FABtotum, http://www.fabtotum.com
#
# This file is part of FABUI.
#
# FABUI is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# FABUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FABUI.  If not, see <http://www.gnu.org/licenses/>.


# Import standard python module
import argparse
import time
import os
import json
import gettext

# Import external modules

# Import internal modules

# Set up message catalog access
tr = gettext.translation('chaos-generator', 'locale', fallback=True)
_ = tr.ugettext

#~ qt5_types = load_types("/home/daniel/Applications/qt/5.7/gcc_64/include")

#~ with open("code_storm.models") as f:
#~ with open("cycle_test.models") as f:
	#~ content = json.loads( f.read() )
	#~ models = content["models"]
	#~ packages = content["packages"]

#~ cpp_typemap.update(qt5_typemap)

#~ project = {
	#~ "project": "ChaosGenerator",
	#~ "organization" : "Colibri-Embedded",
	#~ "year": "2017",
	#~ "authors" : [
		#~ {"name":"Daniel Kesler", "email":"kesler.daniel@gmail.com"}
	#~ ],
	#~ "language" : "cpp",
	#~ "framework" : "qt5"
#~ }

#~ gus, errors = cpp_generator_planning(models, packages, cpp_typemap, cpp_builtin_types, qt5_types)
#~ tmp = cpp_generator_planning(models, packages, cpp_typemap)

#~ for gu in gus:
	#~ env = gu['env'].copy()
	#~ env.update(project)
	#~ create_from_template(gu['template'], gu['filename'], env, overwrite=True)

#~ content = {
	#~ "project" : project,
	#~ "models" : models,
	#~ "views" : []
#~ }

def cg_run(files, includes, templates, language, framework, output_path):
	#~ from templating import create_from_template, create_dir, create_link, build_path
	#~ from extensions.language.cpp import cpp_typemap, cpp_builtin_types, cpp_class_filename
	#~ from extensions.framework.qt5 import load_types, qt5_typemap

	#~ from analyzers.cpp import cpp_generator_planning
	import language.cpp  as cpp
	import framework.qt5 as qt5_fw
	
	result = {
		"errors" : []
	}
	
	if language == 'c++':
		language = 'cpp'
	
	# Language support check
	language_ctx = {
		"cpp" : cpp
	}
	
	if language not in language_ctx:
		return {
			"errors": [
				"Error: Language '{0}' is not supported".format(language)
				]
			}
	
	lang = language_ctx[language]
	
	# Framework support check
	framework_ctx = {
		"generic"	: None,
		"qt"		: qt5_fw,
		"qt5"		: qt5_fw
	}
		
	if framework not in framework_ctx:
		return {
			"errors": [
				"Error: Framework '{0}' is not supported".format(framework)
				]
			}
	fwk = framework_ctx[framework]
	
	# Prepend default template search path
	exe_file_path = os.path.dirname(os.path.realpath(__file__))
	templates.insert(0, os.path.join(exe_file_path, "templates" ) )
	templates.append( os.path.join(exe_file_path, "templates", language, "framework", framework ) )
	
	typemap = lang.typemap
	typemap.update( fwk.typemap )
	
	fwk_types = fwk.load_from_includes(includes)
	#~ print typemap
	templating_env = lang.create_templating_environment(templates)
	
	models = []
	views = []
	packages = {}
	project = {}
	
	for fn in files:
		with open(fn) as f:
			content = json.loads( f.read() )
			if 'models' in content:
				models.extend( content['models'] )
			if 'project' in content:
				project.update( content['project'] )
	
	#~ gus, errors = cpp_generator_planning(models, packages, cpp_typemap, cpp_builtin_types, qt5_types)
	units, planner_error = lang.planner(models, packages, typemap, lang.builtin_types, fwk_types)
	
	
	lang.create_dir(output_path)
	for unit in units:
		unit_env = unit['env'].copy()
		unit_env.update(project)
		unit_template = templating_env.get_template(unit['template'])
		unit_filename = lang.build_path(output_path, unit['filename'])
		
		# Generate file from template
		lang.create_file_from_template(unit_template, unit_filename, unit_env, overwrite=True);
	
	return result

def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("file", nargs='+', help=_("Input file(s)") )
	parser.add_argument("--framework", default='generic', help=_("Framework (generic, qt, ...)") )
	parser.add_argument("-l", "--language", default='c++', help=_("Language (c++, c, ...)") )
	parser.add_argument("-I", dest='include', action='append', help=_("Include path") )
	parser.add_argument("-T", dest='templates', action='append', help=_("Template search path") )
	parser.add_argument("-o", dest='output', help=_("Output path.") )
	
	# GET ARGUMENTS
	args = parser.parse_args()
	
	# Arguments
	files 		= args.file
	includes	= []
	for inc in args.include or []:
		if inc not in includes:
			includes.append(inc)
			
	language	= args.language
	framework	= args.framework
	output_path	= args.output or ""
	templates	= args.templates or []
	
	# Run chaos generator
	result = cg_run(files, includes, templates, language, framework, output_path)
	
	for e in result['errors']:
		print e

if __name__ == "__main__":
    main()
