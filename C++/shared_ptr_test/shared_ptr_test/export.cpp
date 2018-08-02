#include <iostream>
#include "export.h"
#include "sdk_impl.h"

extern "C" int __stdcall CreateVBase(const Type t, VBasePtr& ptr)
{
#ifdef USE_SHARED_PTR
	switch (t)
	{
	case QUEUE:
		ptr = dynamic_pointer_cast<VBase>(make_shared<Queue>());
		break;
	case STACK:
		ptr = dynamic_pointer_cast<VBase>(make_shared<Stack>());
		break;
	default:
		cout << "error Type" << endl;
		return -1;
	}
	return 0;
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