#pragma once
#include <vector>
#include "sdk.h"

class Queue:public VBase
{
public:
	Queue();
	virtual ~Queue();
	virtual int OutPut();
	virtual int InPut(char in_char);
public:
	std::vector<char> m_v;
};

class Stack:public Queue
{
public:
	Stack() { }
	virtual ~Stack();
	virtual int OutPut();
};