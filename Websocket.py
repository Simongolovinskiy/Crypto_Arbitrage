import websocket
import json
import requests
import zlib
import time
import datetime
import pandas as pd

def inflate(data):

    decompress = zlib.decompressobj(-zlib.MAX_WBITS)
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated

class Socket():

    url = 'https://www.okcoin.com/api/spot/v3/instruments'
    pair = [x['instrument_id'] for x in requests.get(url).json()]
    b = {"op": "subscribe", "args": [f'spot/depth5:{x}' for x in pair]}

    def __init__(self):
        pass

    def On_message(self, _wsa, data):

            data = inflate(data)
            print(data)
            # dbase = pd.DataFrame(data)
            # print(dbase)


    def On_Open(self, WebSocket):

       WebSocket.send(json.dumps(self.b))


    def On_Close(self, *args):

       print(*args)


    def On_Error(self, WebSocket, err):

        print(WebSocket, err)



    def content(self):

        url = 'wss://real.okcoin.com:8443/ws/v3'
        wsa = websocket.WebSocketApp(url, on_message=self.On_message, on_error=self.On_Error, on_close=self.On_Close, on_open=self.On_Open)
        wsa.run_forever()


if __name__ == '__main__':
    a = Socket()
    a.content()

