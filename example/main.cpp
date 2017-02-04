#include <QApplication>

#include "functions_document.h"

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);

	auto doc = new FunctionsDocument();
	
	doc->saveToFile("test.json");

	delete doc;

    //return a.exec();
}
