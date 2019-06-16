#pragma once
#include <thread>
#include <vector>
#include <mutex>

class ComputeThread
{
public:
	ComputeThread();
	~ComputeThread() = default;
	bool PushTask(const std::vector<size_t>& enum_v);
	static void PutVec(const std::vector<size_t>& vec);
private:
	static void run(ComputeThread* self);
private:
	std::vector<std::vector<size_t> > m_task_v;
	std::mutex m_task_v_lock;
	std::thread m_thread;
};