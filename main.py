import websocket
import json
import requests
import threading
from triples import trade

class Orderbook:

    def __init__(self, data) -> None:

        self.bid = {}
        self.ask = {}
        self.Snapshot(data)

    def Snapshot(self, data):

        for ask in data['asks']:
            self.ask[float(ask['price'])] = float(ask['amount'])

        for bid in data['bids']:
            self.bid[float(bid['price'])] = float(bid['amount'])

    def Update(self, data):

        for ask in data['asks']:
            if float(ask['price']) not in self.ask.keys():
                self.ask[float(ask['price'])] = float(ask['amount'])
            else:
                if not ask['amount']:
                    del self.ask[float(ask['price'])]
                else:
                    self.ask[float(ask['price'])] = float(ask['amount'])

        for bid in data['bids']:
            if float(bid['price']) not in self.bid.keys():
                self.bid[float(bid['price'])] = float(bid['amount'])
            else:
                if not bid['amount']:
                    del self.bid[float(bid['price'])]
                else:
                    self.bid[float(bid['price'])] = float(bid['amount'])


class Socket:

    url = 'https://gate.kickex.com/api/v1/market/pairs?type=market'
    coins = [pair["pairName"] for pair in requests.get(url).json()]
    Orderbooks = {}

    def __init__(self) -> None:

        pass

    def Main(self):

        for name in self.coins:
            threading.Thread(name=name, target=self.RunSocket, args=(name, )).start()

    def RunSocket(self, coin):

        url = 'wss:https://gate.kickex.com/ws'
        wsrun = websocket.WebSocketApp(
            url, on_message=self.On_Message,
            on_error=self.On_Error, on_close=self.On_Close,
            on_open=lambda websocket: self.On_Open(websocket, coin)
        )

        wsrun.run_forever()

    def On_Open(self, WebSocket, coin):

        send = {"id": "dsncjksdnc", 'type': 'getOrderBookAndSubscribe', 'pair': coin}
        params = json.dumps(send)
        WebSocket.send(params)

    def On_Message(self, _wsa, answer):

        coin = threading.current_thread().name
        data = json.loads(answer)

        if len(data['asks']) > 1 and len(data['bids']) > 1:
            if coin not in self.Orderbooks.keys():
                self.Orderbooks[coin] = Orderbook(data)
        else:
            self.Orderbooks[coin].Update(data)

        #bid, ask = self.Orderbooks[coin].bid, self.Orderbooks[coin].ask

        for pair in self.Orderbooks:
            for order in trade:
                if pair in order and pair == coin:
                    bid, ask = self.Orderbooks[coin].bid, self.Orderbooks[coin].ask
                    print(coin)
                    print(f'{bid}/{ask}')
                    print('__________________________________________________________________________________________________________________________________________________________')

                    #print(f'{pair}/{coin}', f'{bid}/{ask}')





    def On_Close(self, *args):

        print(args)

    def On_Error(self, WebSocket, err):

        print(WebSocket, err)


if __name__ == '__main__':
    crypt = Socket()
    crypt.Main()



