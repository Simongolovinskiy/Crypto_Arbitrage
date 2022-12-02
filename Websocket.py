import websocket
import time
class Socket():
    def __init__(self):

        pass

    def On_message(self,_wsa, data):

        print(data)

    def OnOpen(self):

        pass

    def OnClose(self):

        pass

    def OnError(self):

        pass

    def content(self):

        url = 'wss://real.okcoin.com:8443/ws/v3'
        wsa = websocket.WebSocketApp(url, on_message = self.On_message)
        wsa.run_forever()
a = Socket()
a.content()
