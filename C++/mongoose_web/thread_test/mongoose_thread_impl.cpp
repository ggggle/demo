#include "mongoose_thread_impl.h"
#include <iostream>
using namespace std;

MongooseThread::MongooseThread(const char* bind_addr):
    m_thread(nullptr)
{
    if (nullptr != bind_addr) {
        m_bind_address = bind_addr;
    }
}

MongooseThread::~MongooseThread()
{
    mg_mgr_free(&m_mgr);
}

void MongooseThread::Start()
{
    m_thread = std::make_unique<std::thread>(therad_run_func, this);
}

void MongooseThread::init()
{
    mg_mgr_init(&m_mgr, this);
    struct mg_bind_opts bind_opts;
    memset(&bind_opts, 0, sizeof mg_bind_opts);
    const char* error_str;
    bind_opts.error_string = &error_str;
    m_nc = mg_bind_opt(&m_mgr, m_bind_address.c_str(), ev_handler, bind_opts);
    if (nullptr == m_nc)
    {
        cout << "bind error: " << error_str << endl;
        exit(1);
    }
    mg_set_protocol_http_websocket(m_nc);
}

void MongooseThread::therad_run_func(MongooseThread* self)
{
    self->init();
    while (true)
    {
        mg_mgr_poll(&self->m_mgr, 1000);
    }
}

void MongooseThread::ev_handler(struct mg_connection *nc, int ev, void *ev_data)
{
    static_cast<MongooseThread*>(nc->mgr->user_data)->m_ev_handler(nc, ev, ev_data);
}
