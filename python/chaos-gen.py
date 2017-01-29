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
from templating import create_from_template, create_dir, create_link, build_path
from extensions.language.cpp import cpp_typemap, cpp_builtin_types, cpp_class_filename
from extensions.framework.qt5 import load_types, qt5_typemap

from analyzers.cpp import cpp_generator_planning

qt5_types = load_types("/home/daniel/Applications/qt/5.7/gcc_64/include")

with open("code_storm.models") as f:
#~ with open("cycle_test.models") as f:
	content = json.loads( f.read() )
	models = content["models"]
	packages = content["packages"]

cpp_typemap.update(qt5_typemap)

gus = cpp_generator_planning(models, packages, cpp_typemap, cpp_builtin_types, qt5_types)
#~ tmp = cpp_generator_planning(models, packages, cpp_typemap)

for gu in gus:
	create_from_template(gu['template'], gu['filename'], gu['env'], overwrite=True)

#print tmp['Block']
#~ for m in tmp:
	#~ print m #, '=>', tmp[m]['def']['filename'], tmp[m]['impl']['filename']

#~ env = {
	#~ "project" : "CodeStorm",
	#~ "year" : "2017",
	#~ "organization" : "Colibri-Embedded",
	#~ "authors" : [
		#~ {"name":"Daniel Kesler", "email":"kesler.daniel@gmail.com"}
	#~ ],
	#~ "classes" : [ models[0], models[1] ],
	#~ "includes" : ['"object.h"', '"blockio.h"'],
	#~ "typemap": qt5_typemap,
#~ }

#~ create_from_template('cpp/source.h.template', 'test.h', env, overwrite=True)
#~ create_from_template('c++/source.cpp.template', 'test.cpp', env, overwrite=True)

project = {
	"name": "Code-Storm",
	"year": "2017",
	"authors" : [
		{"name":"Daniel Kesler", "email":"kesler.daniel@gmail.com"}
	],
	"language" : "cpp",
	"dialect"  : "c++11",
	"framework" : "qt5"
}


content = {
	"project" : project,
	"models" : models,
	"views" : []
}

