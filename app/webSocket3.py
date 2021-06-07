import websocket
import json

try:
    import thread
except ImportError:
    import _thread as thread
import time

data = {
    "method": "SUBSCRIBE",
    "params":
        [
            "btcusdt@kline_1m"
        ],
    "id": 1
}


def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def on_open(ws):
    def run(*args):
        for i in range(1):
            time.sleep(1)
            print(json.dumps(data))
            ws.send(json.dumps(data))
        time.sleep(30)
        ws.close()
        print("thread terminating...")

    thread.start_new_thread(run, ())


if __name__ == "__main__":
    uri = "wss://stream.binance.com:9443/ws/BTCUSDT@kline_1m"
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(uri,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.run_forever(proxy_type='http', http_proxy_host='127.0.0.1', http_proxy_port=7890)
