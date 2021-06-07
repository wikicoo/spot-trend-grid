import asyncio
import websockets as ws
from websockets import ConnectionClosed

count = 0

proxies = {
    'https': 'https://127.0.0.1:1087',
    'http': 'http://127.0.0.1:1087'
}

async def hello():
    uri = "wss://stream.binance.com:9443"
    streamName = '/ws/BTCUSDT@kline_1m'

    while True:
        try:
            async with ws.connect(uri+streamName, ssl=True, http_proxy_host="127.0.0.1", http_proxy_port=7890, proxy_type="socks5") as websocket:
                await websocket.send('start')

                asyncio.create_task(ping(websocket))

                while True:
                    try:
                        kline = await websocket.recv()
                        print(kline)
                    except ConnectionClosed as e:
                        print(e.code)
                        if e.code == 1006:
                            print('restart')
                            await asyncio.sleep(2)
                            break
        except ConnectionRefusedError as e:
            print(e)
            global count
            if count == 10:
                return
            count += 1
            await asyncio.sleep(2)


async def ping(ws):
    while True:
        try:
            await ws.send('pong')
            await asyncio.sleep(300)
        except:
            break


asyncio.get_event_loop().run_until_complete(hello())
