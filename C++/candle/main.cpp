#include "layout.h"
#include "candle.h"
#include "compute_thread.h"
#include <iostream>
#include <thread>
#include <future>
#include <mutex>
#include <chrono>

using namespace std;

static bool GetNextEnum(vector<size_t>& last_enum, size_t index)
{
	static const size_t MAX_NUM = 42 - 1;
	static const size_t VEC_SIZE = last_enum.size();
	size_t& last_num = last_enum[index];
	if (MAX_NUM == last_num + (VEC_SIZE - index - 1))
	{
		bool over = true;
		for (int i = index - 1; i >= 0; --i)
		{
			if (last_enum[i] < MAX_NUM - (VEC_SIZE - i - 1))
			{
				over = false;
				last_enum[i] += 1;
				for (size_t m = i + 1; m < VEC_SIZE; ++m)
				{
					last_enum[m] = last_enum[m - 1] + 1;
				}
				break;
			}
		}
		return over;
	}
	last_num += 1;
	return false;
}

static void ThreadRun()
{
	auto start_t = chrono::system_clock::now();
	vector<size_t> enum_v{ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 };
	const size_t CANDLE_NUM = enum_v.size();
	const size_t THREAD_NUM = thread::hardware_concurrency();
	vector<ComputeThread*> compute_v;
	for (size_t i = 0; i < THREAD_NUM; ++i)
	{
		compute_v.emplace_back(new ComputeThread());
	}
	int i = 0;
	do
	{
		compute_v[i]->PushTask(enum_v);
		if (THREAD_NUM == ++i) {
			i = 0;
		}
	} while (false == GetNextEnum(enum_v, CANDLE_NUM - 1));
	auto duration = chrono::duration_cast<chrono::microseconds>(chrono::system_clock::now() - start_t);
	cout << "all done " << static_cast<double>(duration.count()) * chrono::microseconds::period::num / chrono::microseconds::period::den << endl;
	getchar();
}

int main()
{
	ThreadRun();
	return 0;
}


/*
static void PutVec(vector<size_t>& vec)
{
	for (const auto& itr : vec)
	{
		std::cout << itr << ";";
	}
	std::cout << std::endl;
}
static void Compute(const size_t first_start)
{
	static vector<pair<int, int> > all_pot;
	static mutex cout_mutex;
	for (int x = 0; x < 7; ++x)
	{
		for (int y = 0; y < 6; ++y)
		{
			all_pot.emplace_back(std::make_pair(x, y));
		}
	}
	Layout _layout;
	vector<size_t> enum_v{ first_start, first_start + 1, first_start + 2, first_start + 3, first_start + 4, first_start + 5, first_start + 6,
	first_start + 7, first_start + 8, first_start + 9 };
	do 
	{
		if (*enum_v.cbegin() >= first_start + 1)
		{
			break;
		}
		int no_use_lights = 0;
		OneCandle candle = OneCandle();
		for (const auto& candle_pot : enum_v)
		{
			candle.m_x = all_pot[candle_pot].first;
			candle.m_y = all_pot[candle_pot].second;
			no_use_lights += candle.GetOutsideLight();
			if (no_use_lights > 10) {
				break;
			}
			no_use_lights += _layout.PlaceCandle(candle);
			if (no_use_lights > 10) {
				break;
			}
		}
		if (no_use_lights <= 10)
		{
			lock_guard<mutex> _(cout_mutex);
			cout << no_use_lights << ":" << endl;
			PutVec(enum_v);
		}
		_layout.Rest();
	} while (false == GetNextEnum(enum_v, enum_v.size() - 1));
	lock_guard<mutex> _(cout_mutex);
	cout << first_start << " end" << endl;
	PutVec(enum_v);
}


static void Compute2(const size_t first, const size_t second)
{
	static vector<pair<int, int> > all_pot;
	static mutex cout_mutex;
	static std::once_flag _once_flag;
	std::call_once(_once_flag, [&]() {
		for (int x = 0; x < 7; ++x)
		{
			for (int y = 0; y < 6; ++y)
			{
				all_pot.emplace_back(std::make_pair(x, y));
			}
		}
	});
	Layout _layout;
	vector<size_t> enum_v{ first, second, second + 1, second + 2, second + 3, second + 4, second + 5,
		second + 6, second + 7, second + 8 };
	do
	{
		if (enum_v[1] >= second + 1)
		{
			break;
		}
		int no_use_lights = 0;
		OneCandle candle = OneCandle();
		for (const auto& candle_pot : enum_v)
		{
			candle.m_x = all_pot[candle_pot].first;
			candle.m_y = all_pot[candle_pot].second;
			no_use_lights += candle.GetOutsideLight();
			if (no_use_lights > 10) {
				break;
			}
			no_use_lights += _layout.PlaceCandle(candle);
			if (no_use_lights > 10) {
				break;
			}
		}
		if (no_use_lights <= 10)
		{
			lock_guard<mutex> _(cout_mutex);
			cout << no_use_lights << ":" << endl;
			PutVec(enum_v);
		}
		_layout.Rest();
	} while (false == GetNextEnum(enum_v, enum_v.size() - 1));
	lock_guard<mutex> _(cout_mutex);
	cout << first << "," << second << " end";
	PutVec(enum_v);
}

static vector<future<void> > ThreadAsync()
{
	vector<future<void> > future_vec;
	for (size_t i = 0; i <= 32; ++i)
	{
		for (size_t m = i + 1; m <= 33; ++m)
		{
			future_vec.emplace_back(async(Compute2, i, m));
		}
	}
	return future_vec;
}*/

