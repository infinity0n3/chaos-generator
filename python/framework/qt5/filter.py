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
	"QString" : "toString()",
	"QLatin1String" : "{0}toString()",
	"bool" : "{0}toBool()",
	"int" : "{0}toInt()",
	"unsigned" : "(unsigned){0}toInt()",
	"double" : "{0}toDouble()",
	"qint64" : "{0}toInt()",
}

def qt_to_jsonvalue(var, var_type='', prefix='', suffix=''):
	
	if isinstance(var, dict):
		if "name" in var and "type" in var:
			var_name = prefix+var['name']+suffix
			var_type = var['type']
		else:
			# error
			pass
	
	elif isinstance(var, basestring):
		var_name = prefix+var+suffix
		
	if var_type in tojson_map:
		return tojson_map[var_type].format(var_name)
	else:
		#~ return "/* !!! Direct conversion of type '{0}' to QJsonValue is not supported !!! */".format(var_type)
		return cpp_attr_filter(var_name, var_type, "toJSONObject()")
	
def qt_from_jsonvalue(var, json_obj_name):
	#print ">> qt_from_jsonvalue", var, json_obj_name
	
	return ""


