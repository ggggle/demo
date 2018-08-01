#include "../shared_ptr_test/sdk.h"
#include "../shared_ptr_test/export.h"

int main()
{
	auto itr = CreateVBase(QUEUE);
	itr->InPut('a');
	itr->InPut('b');
	itr->InPut('c');
	itr->OutPut();
#ifndef USE_SHARED_PTR
	// 需要显示调用delete
	delete itr;
#endif // !USE_SHARED_PTR
	return 0;
}