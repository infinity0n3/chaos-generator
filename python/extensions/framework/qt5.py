import os, sys

qt5_typemap = {
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
	}

def load_types(include_path):
	files = []
	dirs = []
	types = {}
	
	for (dirpath, dirnames, filenames) in os.walk(include_path):
		files.extend(filenames)
		dirs.extend(dirnames)
		break
		
	for dirname in dirs:
		sub_path = os.path.join(include_path, dirname)
		files = []
		for (dirpath, dirnames, filenames) in os.walk(sub_path):
			for filename in filenames:
				if filename[0] == 'Q':
					types[filename] = ['<'+filename+'>']
			break
			
	return types
