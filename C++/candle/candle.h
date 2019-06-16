#pragma once
#include <vector>

using std::vector;
using std::pair;

class OneCandle
{
public:
	OneCandle() = default;
	OneCandle(int x, int y);
	~OneCandle() {  }
	int GetOutsideLight();
	vector<pair<int, int> > GetLights();
public:
	int m_x;
	int m_y;
};