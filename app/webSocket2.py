import websocket
import json
import time
import threading


class WebsocketClient(object):
    """docstring for WebsocketClient"""

    def __init__(self, address, message_callback=None):
        super(WebsocketClient, self).__init__()
        self.address = address
        self.message_callback = message_callback

    def on_message(self, ws, message):
        # message = json.loads(message)
        print("on_client_message:", message)
        if self.message_callback:
            self.message_callback(message)

    def on_error(self, ws, error):
        print("client error:", error)

    def on_close(self, ws):
        print("### client closed ###")
        self.ws.close()
        self.is_running = False

    def on_open(self, ws):
        self.is_running = True
        print("on open")

    def close_connect(self):
        self.ws.close()

    def send_message(self, message):
        try:
            self.ws.send(message)
        except BaseException as err:
            pass

    def run(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(self.address,
                                         on_message=lambda ws, message: self.on_message(ws, message),
                                         on_error=lambda ws, error: self.on_error(ws, error),
                                         on_close=lambda ws: self.on_close(ws))
        self.ws.on_open = lambda ws: self.on_open(ws)
        self.is_running = False
        while True:
            print(self.is_running)
            if not self.is_running:
                self.ws.run_forever()
            time.sleep(3)


class WSClient(object):
    def __init__(self, address, call_back):
        super(WSClient, self).__init__()
        self.client = WebsocketClient(address, call_back)
        self.client_thread = None

    def run(self):
        self.client_thread = threading.Thread(target=self.run_client)
        self.client_thread.start()

    def run_client(self):
        self.client.run()

    def send_message(self, message):
        self.client.send_message(message)

uri = "wss://stream.binance.com:9443/ws/BTCUSDT@kline_1m"

ws_client = WSClient(uri, lambda message: print("call_back message:", message))
ws_client.run()

time.sleep(3)

data = {
    "method": "SUBSCRIBE",
    "params":
        [
            "btcusdt@kline_1m"
        ],
    "id": 1
}
ws_client.send_message(json.dumps(data, indent=4))
