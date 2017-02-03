#-------------------------------------------------
#
# Project created by QtCreator 2017-01-30T20:31:16
#
#-------------------------------------------------

QT       += core gui

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = ChaosGenerator
TEMPLATE = app

# The following define makes your compiler emit warnings if you use
# any feature of Qt which as been marked as deprecated (the exact warnings
# depend on your compiler). Please consult the documentation of the
# deprecated API in order to know how to port your code away from it.
DEFINES += QT_DEPRECATED_WARNINGS

# You can also make your code fail to compile if you use deprecated APIs.
# In order to do so, uncomment the following line.
# You can also select to disable deprecated APIs only up to a certain version of Qt.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0


SOURCES += main.cpp\
        mainwindow.cpp

HEADERS  += mainwindow.h

FORMS    += mainwindow.ui

#PRE_TARGETDEPS += models/cg_models.pri

CG_FILES = cg.project cg.models

cg.target  = cg_models.pri
cg.commands = python ../python/chaos-gen.py ${QMAKE_FILE_NAME} -l c++ --framework qt5 -o models $(INCPATH)
cg.output = models/cg_models.pri
cg.depends =
cg.input = CG_FILES
cg.CONFIG = no_link combine

QMAKE_EXTRA_COMPILERS += cg

INCLUDEPATH += ./models
include( "models/cg_models.pri" )
