#include <iostream>
#include <string>
#include "sdk_impl.h"

using namespace std;

Queue::Queue() 
{
	cout << "queue::init" << endl;
	m_v.reserve(1024);
}

Queue::~Queue()
{
	cout << "~Queue::delete~" << endl;
}

int Queue::InPut(char in_char)
{
	m_v.push_back(in_char);
	return 0;
}

int Queue::OutPut()
{
	cout << string(&m_v[0], m_v.size()) << endl;
	return 0;
}


Stack::~Stack()
{
	cout << "~Stack::delete~" << endl;
}

int Stack::OutPut()
{
	cout << "m_v capacity:" << m_v.capacity() << endl;
	if (m_v.empty())
	{
		return 0;
	}
	auto itr = m_v.end();
	--itr;
	for (; m_v.begin() != itr; --itr)
	{
		cout << *itr;
	}
	cout << *itr << endl;
	return 0;
}

VBase::~VBase() {}