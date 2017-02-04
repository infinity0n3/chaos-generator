from jinja2 import contextfilter

from language.cpp.filter import cpp_by_value_filter, cpp_attr_filter

tojson_map = {
	"QString" : "QJsonValue({0})",
	"QLatin1String" : "QJsonValue({0})",
	"bool" : "QJsonValue({0})",
	"int" : "QJsonValue({0})",
	"unsigned" : "QJsonValue(int({0}))",
	"double" : "QJsonValue({0})",
	"qint64" : "QJsonValue({0})",
}

fromjson_map = {
	"QString" : '{0}["{1}"].toString()',
	"QLatin1String" : '{0}["{1}"].toString()',
	"bool" : '{0}["{1}"].toBool()',
	"int" : '{0}["{1}"].toInt()',
	"unsigned" : '(unsigned){0}["{1}"].toInt()',
	"double" : '{0}["{1}"].toDouble()',
	"qint64" : '{0}["{1}"].toInt()',
}

def qt_to_jsonvalue(var, var_type='', prefix='', suffix='', serializer=''):
	
	if isinstance(var, dict):
		if "name" in var and "type" in var:
			var_name = prefix+var['name']+suffix
			var_type = var['type']
		else:
			print "Error (qt_to_jsonvalue): missing name or type"
			pass
	
	elif isinstance(var, basestring):
		var_name = prefix+var+suffix
		
	if var_type in tojson_map:
		return tojson_map[var_type].format(var_name)
	else:
		#~ return "/* !!! Direct conversion of type '{0}' to QJsonValue is not supported !!! */".format(var_type)
		return cpp_attr_filter(var_name, var_type, "toJSONObject({0})".format(serializer))
	
def qt_from_jsonvalue(var, json_obj_name, prefix='', suffix='',  deserializer=''):
	
	if isinstance(var, dict):
		if "name" in var and "type" in var:
			var_name = prefix+var['name']+suffix
			var_type = var['type']
		else:
			print "Error (qt_from_jsonvalue): missing name or type"
			pass
			
	if var_type in tojson_map:
		return fromjson_map[var_type].format(json_obj_name, var_name)
	else:
		#~ return "/* !!! Direct conversion of type '{0}' to QJsonValue is not supported !!! */".format(var_type)
		return cpp_attr_filter(var_name, var_type, "fromJSONObject({0}, {1})".format(json_obj_name, deserializer))
	
	
	return ""


