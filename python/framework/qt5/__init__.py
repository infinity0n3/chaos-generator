#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# (c) Daniel Kesler <kesler.daniel@gmail.com>
#
# This file is part of Chaos-Generator.
#
# Chaos-Generator is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Chaos-Generator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Chaos-Generator.  If not, see <http://www.gnu.org/licenses/>.

import os, sys
import jinja2

from framework.qt5.filter import qt_to_jsonvalue, qt_from_jsonvalue

typemap = {
		# Builtin
		"pointer": "quintptr",
		"uint32" : "quint32",
		"uint64" : "quint64",
		# Containers
		"vector" : "QVector",
		"list"   : "QList",
		"stack"  : "QStack",
		"queue"  : "QQueue",
		"string" : "QString",
		"hash"   : "QHash",
		# JSON specific
		"jsonobject" : "QJsonObject",
		"jsondocument" : "QJsonDocument",
		"jsonarray" : "QJsonArray",
		"jsonvalue" : "QJsonValue",
		# UndoStack
		"undocommand" : "QUndoCommand",
		"undostack" : "QUndoStack"
	}
	
qt_builtin_types = {
	"quintptr" : []
}

def load_from_includes(include_path):
	types = {}
	
	types.update(qt_builtin_types)
		
	for path in include_path:
		for (dirpath, dirnames, filenames) in os.walk(path):
			for filename in filenames:
				if filename[0] == 'Q':
					types[filename] = ['<'+filename+'>']
			break
			
	return types

def extend_templating_environment(templateEnv):
	
	templateEnv.filters['qt_to_jsonvalue'] = qt_to_jsonvalue
	templateEnv.filters['qt_from_jsonvalue'] = qt_from_jsonvalue
	
	return templateEnv

def create_extra_units(units, output_path):
	sources = ""
	headers = ""
	forms = ""
	
	extra_units = []
	
	for unit in units:
		fn = unit['filename']
		filename = os.path.join(output_path, fn)
		if fn.endswith('.h') or fn.endswith('.hpp') or fn.endswith('.hxx') or fn.endswith('.hh'):
			headers += " " + filename
		elif fn.endswith('.cpp') or fn.endswith('.cxx') or fn.endswith('.cc'):
			sources += " " + filename
	
	env = {
		"sources" : sources,
		"headers" : headers,
		"forms"   : forms
	}
	
	extra_units.append({
		"filename": "cg_models.pri",
		"template": "cpp/framework/qt/qt_project_include.template",
		"env": env
	})
	
	return extra_units
