#pragma once
#include <memory>
#include "sdk.h"

using namespace std;

#ifdef USE_SHARED_PTR
typedef shared_ptr<VBase> VBasePtr;
#else
typedef VBase* VBasePtr;
#endif

enum Type
{
	QUEUE,
	STACK,
	TypeMax,
};

extern "C"
{
	int __stdcall CreateVBase(const Type t, VBasePtr& ptr);
}
