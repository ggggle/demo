#pragma once
#include "candle.h"

class Layout
{
public:
	Layout();
	~Layout() = default;
	// 返回放下蜡烛后新增的烛光重叠数
	int PlaceCandle(OneCandle& candle);
	void Rest();
private:
	bool room_array[7][6];
};