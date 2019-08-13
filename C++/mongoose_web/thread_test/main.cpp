#include "mongoose_thread_impl.h"
#include <iostream>
#include <chrono>
#include <string>

using namespace std;

static void hanler_1(struct mg_connection *nc, int ev, void *ev_data, int num)
{
    switch (ev)
    {
    case MG_EV_WEBSOCKET_HANDSHAKE_DONE:
        break;
    case MG_EV_WEBSOCKET_FRAME:
        break;
    case MG_EV_HTTP_REQUEST:
        // 等待一段时间后再应答
        this_thread::sleep_for(chrono::seconds(5));
        mg_printf(nc, "%s", "HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n");
        mg_printf_http_chunk(nc, "{ \"result\": success " __FUNCTION__ "}");
        mg_send_http_chunk(nc, "", 0);
        break;
    default:
        break;
    }
    // cout << num << endl;
}

static void hanler_2(struct mg_connection *nc, int ev, void *ev_data, string str_data)
{
    switch (ev)
    {
    case MG_EV_WEBSOCKET_HANDSHAKE_DONE:
        break;
    case MG_EV_WEBSOCKET_FRAME:
        break;
    case MG_EV_HTTP_REQUEST:
        mg_printf(nc, "%s", "HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n");
        mg_printf_http_chunk(nc, "{ \"result\": success " __FUNCTION__ "}");
        mg_send_http_chunk(nc, "", 0);
        break;
    default:
        break;
    }
    // cout << str_data << endl;
}

static void hanler_3(struct mg_connection *nc, int ev, void *ev_data, void* any)
{
    switch (ev)
    {
    case MG_EV_WEBSOCKET_HANDSHAKE_REQUEST:
    {
        struct http_message *hm = (struct http_message *) ev_data;
        cout << __FUNCTION__ << " ws req" << endl;
        mg_str* head_auth = mg_get_http_header(hm, "Auth");
        if (nullptr != head_auth) {
            break;
        }
        mg_printf(nc, "HTTP/1.1 403 Unauthorized\r\n\r\n");
        nc->flags |= MG_F_SEND_AND_CLOSE;
        break;
    }
        
    case MG_EV_WEBSOCKET_HANDSHAKE_DONE:
        cout << __FUNCTION__ << " ws done" << endl;
        break;
    case MG_EV_WEBSOCKET_FRAME:
        break;
    case MG_EV_HTTP_REQUEST:
        break;
    default:
        break;
    }
    // cout << any << endl;
}

int main()
{
    MongooseThread num_mong("8001");
    num_mong.SetEVHandler(bind(hanler_1, placeholders::_1, placeholders::_2, placeholders::_3, 8001));
    num_mong.Start();

    MongooseThread str_mong("8002");
    str_mong.SetEVHandler(bind(hanler_2, placeholders::_1, placeholders::_2, placeholders::_3, "8002"));
    str_mong.Start();

    MongooseThread any_mong("8003");
    any_mong.SetEVHandler(bind(hanler_3, placeholders::_1, placeholders::_2, placeholders::_3, &any_mong));
    any_mong.Start();

    getchar();
    return 0;
}