#pragma once
#include <mongoose.h>
#include <string>
#include <functional>
#include <thread>
#include <mutex>
#include <memory>

class MongooseThread
{
public:
    using EVHandler = std::function<void(struct mg_connection *nc, int ev, void *ev_data)>;
    MongooseThread(const char* bind_addr);
    ~MongooseThread();
    void SetEVHandler(EVHandler&& handler) {
        m_ev_handler = handler;
    }
    void Start();
private:
    // 初始化mongoose相关
    void init();
    // loop run
    static void therad_run_func(MongooseThread* self);
    // handler
    static void ev_handler(struct mg_connection *nc, int ev, void *ev_data);
private:
    EVHandler m_ev_handler;
    std::mutex m_handler_mutex;
    std::string m_bind_address;
    // mongoogse
    struct mg_mgr m_mgr;
    struct mg_connection *m_nc;
    // thread
    std::unique_ptr<std::thread> m_thread;
};