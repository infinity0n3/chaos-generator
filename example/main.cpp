#include <QApplication>

#include "functions_document.h"
#include <bitset>
#include <iostream>
#include <QDebug>

//~ #include "bitmask_operators.hpp"

//~ template<>
//~ struct enable_bitmask_operators<IOType>{
    //~ static const bool enable=true;
//~ };
//~ #define USE_ENUM_FLAGS_FUNCTION 0
//~ #include "enum_flags.h"
//~ ENUM_FLAGS(IOType)

//~ inline T&	operator	^=	(T& x, T y)		{	x = x ^ y;	return x;	};
//inline bool			flags(T x)			{	return static_cast<INT_T>(x) != 0;};
/*num class T;	\
inline T	operator	&	(T x, T y)		{	return static_cast<T>	(static_cast<INT_T>(x) & static_cast<INT_T>(y));	}; \
inline T	operator	|	(T x, T y)		{	return static_cast<T>	(static_cast<INT_T>(x) | static_cast<INT_T>(y));	}; \
inline T	operator	^	(T x, T y)		{	return static_cast<T>	(static_cast<INT_T>(x) ^ static_cast<INT_T>(y));	}; \
inline T	operator	~	(T x)			{	return static_cast<T>	(~static_cast<INT_T>(x));							}; \
inline T	operator	bool	(T x)			{	return static_cast<unsigned>	(x) != 0);							}; \
inline T&	operator	&=	(T& x, T y)		{	x = x & y;	return x;	}; \
inline T&	operator	|=	(T& x, T y)		{	x = x | y;	return x;	}; \
inline T&	operator	^=	(T& x, T y)		{	x = x ^ y;	return x;	};*/

/*
struct IOType
{
	enum {
		NONE = 0,
		IN = 1,
		OUT = 2,
		INOUT = 4
	} Value;
	
	IOType(decltype(Value) value) : Value(value) {} // implicit
	
	IOType(){}
	
    explicit operator bool() {
        return Value != 0;
    }
    
    operator =(unsigned &v)
    {
		
	}
};

inline bool operator==(IOType a, IOType b) {
    return a.Value == b.Value;
}

inline bool operator!=(IOType a, IOType b) {
    return !(a == b);
}*/





int main(int argc, char *argv[])
{
	QApplication a(argc, argv);

	auto x = int();

	auto doc = new FunctionsDocument();
	auto block1 = doc->addPyBlock("TestBlock1", "@project_path@/custom.test");
	
	//auto block2 = doc->addPyBlock("TestBlock2", "@project_path@/custom.test");

	//doc->saveToFile("test.json");

	//doc->loadFromFile("test.json");
	//doc->saveToFile("test2.json");
	
	//~ std::bitset<8> flags;
	
	//~ flags.reset();
	//~ flags |= 1 | 2;
	//~ unsigned flags = IOType::IN | IOType::OUT;
	
	//~ std::cout << flags.to_string() << std::endl;
	//unsigned f = IOType::NONE;
	//IOType f;
	
	IOType b;
	b = IOType::OUT + IOType::IN;
	b -= IOType::IN;
	
	//~ unsigned f;
	//~ f |= IOType::IN;
	if( b | IOType::IN )
		std::cout << "flag IN set" << std::endl;
		
	//~ if(flags | 2)
		//~ std::cout << "flag 2 set" << std::endl;

	delete doc;

	//return a.exec();
}
