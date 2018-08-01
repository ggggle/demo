#include <iostream>
#include "export.h"
#include "sdk_impl.h"

VBasePtr __stdcall CreateVBase(Type t)
{
#ifdef USE_SHARED_PTR
	switch (t)
	{
	case QUEUE:
		return dynamic_pointer_cast<VBase>(make_shared<Queue>());
	case STACK:
		return dynamic_pointer_cast<VBase>(make_shared<Stack>());
	default:
		cout << "error Type" << endl;
		return NULL;
	}
#else
	switch (t)
	{
	case QUEUE:
		return dynamic_cast<VBasePtr>(new Queue);
	case STACK:
		return dynamic_cast<VBasePtr>(new Stack);
	default:
		cout << "error Type" << endl;
		return NULL;
	}
#endif // USE_SHARED_PTR
}