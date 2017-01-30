import os, sys

typemap = {
		"vector" : "QVector",
		"list"   : "QList",
		"stack"  : "QStack",
		"queue"  : "QQueue",
		"string" : "QString",
		# JSON specific
		"jsonobject" : "QJsonObject",
		"jsondocument" : "QJsonDocument",
		"jsonarray" : "QJsonArray",
		"jsonvalue" : "QJsonValue",
		# UndoStack
		"undocommand" : "QUndoCommand",
		"undostack" : "QUndoStack"
	}

def load_from_includes(include_path):
	types = {}
		
	for path in include_path:
		for (dirpath, dirnames, filenames) in os.walk(path):
			for filename in filenames:
				if filename[0] == 'Q':
					types[filename] = ['<'+filename+'>']
			break
			
	return types
