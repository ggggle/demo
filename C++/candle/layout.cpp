#include "layout.h"
#include <memory>

Layout::Layout()
{
	Rest();
}

int Layout::PlaceCandle(OneCandle & candle)
{
	int count = 0;
	vector<pair<int, int> > lights_v = candle.GetLights();
	for (const auto& x_y : lights_v)
	{
		bool& is_light = room_array[x_y.first][x_y.second];
		if (is_light) {
			++count;
			continue;
		}
		is_light = true;
	}
	return count;
}

void Layout::Rest()
{
	memset(room_array, 0, sizeof room_array);
}
