#include <iostream>
#include "export.h"
#include "sdk_impl.h"

extern "C" VBasePtr* __stdcall CreateVBase(Type t)
{
#ifdef USE_SHARED_PTR
	VBasePtr ptr;
	switch (t)
	{
	case QUEUE:
		ptr = dynamic_pointer_cast<VBase>(make_shared<Queue>());
		return &ptr;
		break;
	case STACK:
		ptr = dynamic_pointer_cast<VBase>(make_shared<Stack>());
		ptr.operator*().InPut('2');
		return &ptr;
		break;
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