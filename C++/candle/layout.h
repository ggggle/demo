#pragma once
#include "candle.h"

class Layout
{
public:
	Layout();
	~Layout() = default;
	// ���ط������������������ص���
	int PlaceCandle(OneCandle& candle);
	void Rest();
private:
	bool room_array[7][6];
};