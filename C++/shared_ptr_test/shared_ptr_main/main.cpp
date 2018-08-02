#include <iostream>
#include <vector>

#include "../shared_ptr_test/sdk.h"
#include "../shared_ptr_test/export.h"

vector<VBasePtr> ptr_v;
vector<VBasePtr*> pptr_v;
int Test1()
{
	VBasePtr* rt;
	rt = CreateVBase(STACK);
	cout << "create" << endl;
	(*rt)->InPut('a');
	(*rt)->InPut('b');
	(*rt)->InPut('c');
	rt->get()->InPut('p');
	(*rt)->InPut('b');
	(*rt)->OutPut();
	auto source = (*rt).get();
	cout << (*rt).use_count() << endl;
	auto pp = (*rt);
	cout << (*rt).use_count() << endl;
	ptr_v.push_back(pp);
	ptr_v.push_back((*rt));
	cout << (*rt).use_count() << endl;
	cout << pp.use_count() << endl;
	ptr_v.pop_back();
	
	cout << (*rt).use_count() << endl;
	pptr_v.push_back(rt);
	cout << pp.use_count() << endl;
	ptr_v.push_back(*rt);
	cout << rt->use_count() << endl;
	ptr_v.push_back(*rt);
	cout << (*rt).use_count() << endl;
	ptr_v.push_back((*rt));
	cout << rt->use_count() << endl;
#ifndef USE_SHARED_PTR
	// 需要显示调用delete
	delete (*rt);
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