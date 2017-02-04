CGG ?= ../python/chaos-gen.py

INPUT = cg.project \
		cg_serializer.models  \
		cg_json_serializer.models  \
		cg_linkable.models \
		cg_document.models \
		cg_document_functions.models \
		cg_document_models.models
            
INC = -I /opt/qt5/include/QtCore \
	  -I /opt/qt5/include/QtWidgets

all: $(INPUT)
	$(CGG) $^ -l c++ --framework qt5 -o out $(INC)
