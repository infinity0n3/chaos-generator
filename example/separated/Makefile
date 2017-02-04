CGG ?= ../python/chaos-gen.py

INPUT = json_serializer.cg_interface  link.cg_data  link.cg_interface  serializer.cg_data

all: $(INPUT)
	$(CGG) $^ -l c++ --framework qt5 -s
