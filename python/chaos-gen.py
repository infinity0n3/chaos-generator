#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# Chaos-Generator
# Copyright (C) 2017  Daniel Kesler <kesler.daniel@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import standard python module
import argparse
import time
import os
import json
import gettext

# Import external modules

# Import internal modules
#https://github.com/Pitmairen/kate-jinja2-highlighting
# Set up message catalog access
tr = gettext.translation('chaos-generator', 'locale', fallback=True)
_ = tr.ugettext

def cg_run(files, includes, templates, language, framework, output_path, suggest):
	"""
	
	"""
	import language.cpp  as cpp
	import language.suggest as lang_suggest
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
	#~ templates.insert(0, os.path.join(exe_file_path, "templates" ) )
	templates.append( os.path.join(exe_file_path, "templates", language, "framework", framework ) )
	templates.append( os.path.join(exe_file_path, "templates" ) )
	
	# Populate types
	typemap = lang.typemap
	typemap.update( fwk.typemap )
	fwk_types = fwk.load_from_includes(includes)
	
	# Generate templating environment
	templating_env = lang.create_templating_environment(templates)
	
	fwk.extend_templating_environment(templating_env)
	
	# Initialize variables
	models = []
	views = []
	data = []
	interfaces = []
	packages = {}
	project = {}
	
	# Load project, models, packages, views
	for fn in files:
		with open(fn) as f:
			print ">>", fn
			content = json.loads( f.read() )
			if 'data' in content:
				data.extend( content['data'] )
			if 'models' in content:
				models.extend( content['models'] )
			if 'interfaces' in content:
				interfaces.extend( content['interfaces'] )
			if 'project' in content:
				project.update( content['project'] )
			if 'packages' in content:
				packages.update( content['packages'] )
	
	if suggest:
		lang_suggest.data2model(data)
		#lang_suggest.interface2model(interfaces)
		
	if not suggest:	
		# Create generation plan
		units, planner_error = lang.planner(models, packages, typemap, lang.builtin_types, fwk_types)
		
		if planner_error:
			result['errors'].extend(planner_error)
			return result
		
		units.extend( fwk.create_extra_units(units, output_path) )
		
		# Generate files
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
	parser.add_argument("-s", dest='suggest', action='store_true', help=_("Only generate suggestions.") )
	
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
	output_path	= args.output or "./"
	templates	= args.templates or []
	suggest		= args.suggest
	
	# Run chaos generator
	result = cg_run(files, includes, templates, language, framework, output_path, suggest)
	
	for e in result['errors']:
		print e
		
	if result['errors']:
		exit(1)

if __name__ == "__main__":
    main()
