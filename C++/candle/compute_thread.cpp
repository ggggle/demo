#include "compute_thread.h"
#include "layout.h"
#include <iostream>
#include <chrono>

using namespace std;

ComputeThread::ComputeThread():
	m_thread(run, this)
{

}

void ComputeThread::PushTask(std::vector<size_t> enum_v)
{
	m_task_v_lock.lock();
	m_task_v.emplace_back(enum_v);
	m_task_v_lock.unlock();
}

void ComputeThread::PutVec(const vector<size_t>& vec)
{
	for (const auto& itr : vec)
	{
		cout << itr << ";";
	}
	cout << endl;
}

void ComputeThread::run(ComputeThread* self)
{
	static mutex cout_mutex;
	static vector<pair<int, int> > all_pot;
	static std::once_flag _once_flag;
	call_once(_once_flag, [&]() {
		for (int x = 0; x < 7; ++x)
		{
			for (int y = 0; y < 6; ++y)
			{
				all_pot.emplace_back(std::make_pair(x, y));
			}
		}
	});
	Layout _layout;
	vector<vector<size_t> > task_v;
	while (true)
	{
		self->m_task_v_lock.lock();
		task_v.swap(self->m_task_v);
		self->m_task_v_lock.unlock();
		if (task_v.empty()) {
			this_thread::sleep_for(chrono::seconds(1));
			continue;
		}
		for (const auto& enum_v : task_v)
		{
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
				cout_mutex.lock();
				cout << no_use_lights << ":" << endl;
				PutVec(enum_v);
				cout_mutex.unlock();
			}
			_layout.Rest();
		}
		task_v.clear();
	}
}
