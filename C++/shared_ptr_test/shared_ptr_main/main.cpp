#include <iostream>
#include <vector>

#include "../shared_ptr_test/sdk.h"
#include "../shared_ptr_test/export.h"
#include "../shared_ptr_test/sdk_impl.h"

vector<VBasePtr> ptr_v;
vector<VBasePtr*> pptr_v;
int func1(const VBasePtr ptr)
{
	ptr->InPut('o');
	cout << "fun1:" << ptr.use_count() << endl;
	ptr->OutPut();
	return 0;
}

int fun2(VBasePtr ptr)
{
	cout << "fun2.1:" << ptr.use_count() << endl;
	CreateVBase(STACK, ptr);
	cout << "fun2.3:" << ptr.use_count() << endl;
	ptr_v.push_back(ptr);
	cout << "fun2.2:" << ptr.use_count() << endl;
	return 0;
}

int Test1()
{
	VBasePtr rt;
	bool expired = rt._Expired();
	if (NULL == rt)
	{
		cout << "NULL" << endl;
	}
	if (nullptr == rt)
	{
		cout << "nullptr" << endl;
	}
	cout << "init:" << rt.use_count() << endl;
	int ret = CreateVBase(QUEUE, rt);
	expired = rt._Expired();
	cout << "create" << endl;
	rt->InPut('a');
	rt->InPut('b');
	rt->InPut('c');
	rt->InPut('p');
	rt->InPut('b');
	rt->OutPut();
	cout << "@@:" << rt.use_count() << endl;
	func1(rt);
	cout << "##:" << rt.use_count() << endl;
	fun2(rt);
	cout << "!!:" << rt.use_count() << endl;
	auto source = rt.get();
	cout << rt.use_count() << endl;
	auto pp = rt;
	cout << rt.use_count() << endl;
	ptr_v.push_back(pp);
	ptr_v.push_back(rt);
	cout << rt.use_count() << endl;
	cout << pp.use_count() << endl;
	ptr_v.pop_back();
	
	cout << rt.use_count() << endl;
#ifndef USE_SHARED_PTR
	// 需要显示调用delete
	delete rt;
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