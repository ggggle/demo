#include <iostream>
#include <vector>

#include "../shared_ptr_test/sdk.h"
#include "../shared_ptr_test/export.h"

vector<VBasePtr> ptr_v;
int Test1()
{
	auto itr = CreateVBase(STACK);
	itr->InPut('a');
	itr->InPut('b');
	itr->InPut('c');
	itr->OutPut();
	auto source = itr.get();
	cout << itr.use_count() << endl;
	auto pp = itr;
	cout << itr.use_count() << endl;
	ptr_v.push_back(pp);
	ptr_v.push_back(itr);
	cout << itr.use_count() << endl;
	cout << pp.use_count() << endl;
	ptr_v.pop_back();
	cout << itr.use_count() << endl;
	cout << pp.use_count() << endl;
#ifndef USE_SHARED_PTR
	// 需要显示调用delete
	delete itr;
#endif // !USE_SHARED_PTR
	return 0;
}

int main()
{
	Test1();
	ptr_v.clear();
	cout << "clear" << endl;
	cout << "end" << endl;
	return 0;
}