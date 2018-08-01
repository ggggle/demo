#pragma once

class VBase
{
public:
	VBase(){}
	virtual ~VBase() = 0;
	virtual int OutPut() = 0;
	virtual int InPut(char) = 0;
};

