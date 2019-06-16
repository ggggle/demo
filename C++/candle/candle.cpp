#include "candle.h"

OneCandle::OneCandle(int x, int y):
	m_x(x)
	,m_y(y)
{
}

int OneCandle::GetOutsideLight()
{
	switch (m_x)
	{
	case 0:
	case 6:
		if (0 == m_y || 5 == m_y) {
			return 2;
		}
		else {
			return 1;
		}
	default:
		if (0 == m_y || 5 == m_y) {
			return 1;
		}
		else {
			return 0;
		}
	}
}

vector<pair<int, int> > OneCandle::GetLights()
{
	vector<pair<int, int> > lights_vec;
	lights_vec.emplace_back(std::make_pair(m_x, m_y));
	switch (m_x)
	{
	case 0:
		switch (m_y)
		{
		case 0:// (0,0)
			lights_vec.emplace_back(std::make_pair(m_x, m_y + 1));
			lights_vec.emplace_back(std::make_pair(m_x + 1, m_y));
			break;
		case 5: // (0,5)
			lights_vec.emplace_back(std::make_pair(m_x, m_y - 1));
			lights_vec.emplace_back(std::make_pair(m_x + 1, m_y));
			break;
		default:
			lights_vec.emplace_back(std::make_pair(m_x, m_y + 1));
			lights_vec.emplace_back(std::make_pair(m_x + 1, m_y));
			lights_vec.emplace_back(std::make_pair(m_x, m_y - 1));
			break;
		}
		break;
	case 6:
		switch (m_y)
		{
		case 0:
			lights_vec.emplace_back(std::make_pair(m_x, m_y + 1));
			lights_vec.emplace_back(std::make_pair(m_x - 1, m_y));
			break;
		case 5:
			lights_vec.emplace_back(std::make_pair(m_x, m_y - 1));
			lights_vec.emplace_back(std::make_pair(m_x - 1, m_y));
			break;
		default:
			lights_vec.emplace_back(std::make_pair(m_x, m_y + 1));
			lights_vec.emplace_back(std::make_pair(m_x, m_y - 1));
			lights_vec.emplace_back(std::make_pair(m_x - 1, m_y));
			break;
		}
		break;
	default:
		switch (m_y)
		{
		case 0:
			lights_vec.emplace_back(std::make_pair(m_x + 1, m_y));
			lights_vec.emplace_back(std::make_pair(m_x - 1, m_y));
			lights_vec.emplace_back(std::make_pair(m_x, m_y + 1));
			break;
		case 5:
			lights_vec.emplace_back(std::make_pair(m_x + 1, m_y));
			lights_vec.emplace_back(std::make_pair(m_x - 1, m_y));
			lights_vec.emplace_back(std::make_pair(m_x, m_y - 1));
			break;
		default:
			lights_vec.emplace_back(std::make_pair(m_x + 1, m_y));
			lights_vec.emplace_back(std::make_pair(m_x - 1, m_y));
			lights_vec.emplace_back(std::make_pair(m_x, m_y + 1));
			lights_vec.emplace_back(std::make_pair(m_x, m_y - 1));
			break;
		}
		break;
	}
	return lights_vec;
}
