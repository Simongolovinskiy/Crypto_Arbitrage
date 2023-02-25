import websocket
import json
import requests
import threading
from triples import trade
from decimal import Decimal
import queue
from datetime import datetime


class Orderbook:

    def __init__(self, data) -> None:
        self.bid_amount = {}
        self.ask_amount = {}
        self.asks = {}
        self.bids = {}
        self.bid = {}
        self.ask = {}
        self.snapshot(data)

    def snapshot(self, data):

        for ask in data['asks']:
            self.ask[Decimal(ask['price'])] = Decimal(ask['amount'])
        self.asks = min(self.ask.keys())
        self.ask_amount = self.ask[self.asks]
        for bid in data['bids']:
            self.bid[Decimal(bid['price'])] = Decimal(bid['amount'])
        self.bids = max(self.bid.keys())
        self.bid_amount = self.bid[self.bids]

    def update(self, data):

        for ask in data['asks']:
            if Decimal(ask['price']) not in self.ask.keys():
                self.ask[Decimal(ask['price'])] = Decimal(ask['amount'])
            else:
                if not ask['amount']:
                    del self.ask[Decimal(ask['price'])]
                else:
                    self.ask[Decimal(ask['price'])] = Decimal(ask['amount'])
        self.asks = min(self.ask.keys())

        for bid in data['bids']:
            if Decimal(bid['price']) not in self.bid.keys():
                self.bid[Decimal(bid['price'])] = Decimal(bid['amount'])
            else:
                if not bid['amount']:
                    del self.bid[Decimal(bid['price'])]
                else:
                    self.bid[Decimal(bid['price'])] = Decimal(bid['amount'])
        self.bids = max(self.bid.keys())


class Socket:

    url = 'https://gate.kickex.com/api/v1/market/pairs?type=market'
    coins = [pair["pairName"] for pair in requests.get(url).json()]

    def __init__(self,) -> None:

        self.message = {}
        self.price_amount = {}
        self.orderbooks = {}
        self.orderbook_action = {'Buy': 'asks', 'Sell': 'bids'}
        self.queue = queue.Queue()
        self.final_message = queue.Queue()
        self.temp_dict = {}
        for trading in trade:
            self.temp_dict[json.dumps(trading)] = {
                'Trio_of_price': None,
                'Time': None,
                'Message': None
            }

    def main(self):

        for name in self.coins:
            self.orderbooks[name] = None
            threading.Thread(name=name, target=self.run_socket, args=(name, )).start()

        while True:
            if not self.queue.empty():
                name = self.queue.get()
                print(f'Перезапуется поток {name}')
                threading.Thread(name=name, target=self.run_socket, args=(name, )).start()

    def run_socket(self, coin):

        url = 'wss:https://gate.kickex.com/ws'
        wsrun = websocket.WebSocketApp(
            url, on_message=self.on_message,
            on_error=self.on_error, on_close=self.on_close,
            on_open=lambda websocket: self.on_open(websocket, coin)
        )

        wsrun.run_forever()

    def on_open(self, websocket, coin):

        args = {"id": "dsncjksdnc", 'type': 'getOrderBookAndSubscribe', 'pair': coin}
        params = json.dumps(args)
        websocket.send(params)

    def on_message(self, _wsa, answer):

        coin = threading.current_thread().name
        data = json.loads(answer)
        commission = Decimal('0.998')

        if len(data['asks']) == 0 and len(data['bids']) == 0:
            return
        if len(data['asks']) > 1 and len(data['bids']) > 1:
            self.orderbooks[coin] = Orderbook(data)
        else:
            self.orderbooks[coin].update(data)

        for trading in trade:
            if coin in trading.keys():
                triple = json.dumps(trading)
                pair_check = [self.orderbooks[pair].__dict__[self.orderbook_action[action]] for pair,
                              action in trading.items() if self.orderbooks[pair]]
                if len(pair_check) == 3 and self.temp_dict[triple]['Trio_of_price'] != pair_check:

                    for pair, action in trading.items():
                        pairs_for_loop = list(trading.keys())
                        if pair == pairs_for_loop[0]:
                            if action == 'Buy':
                                self.price_amount[self.orderbooks[pair].asks] = self.orderbooks[pair].ask_amount
                                coin_amount = (1 / self.orderbooks[pair].asks) * commission
                        else:
                            if action == 'Buy':
                                self.price_amount[self.orderbooks[pair].asks] = self.orderbooks[pair].ask_amount
                                coin_amount = (coin_amount / self.orderbooks[pair].asks) * commission
                            elif action == 'Sell':
                                self.price_amount[self.orderbooks[pair].bids] = self.orderbooks[pair].bid_amount
                                coin_amount = (coin_amount * self.orderbooks[pair].bids) * commission
                    self.temp_dict[triple]['Trio_of_price'] = pair_check

                    print(coin_amount)
                    if coin_amount > 1:
                        if not self.temp_dict[triple]['Time']:
                            self.temp_dict[triple]['Time'] = datetime.now()
                            # temp_text = [Decimal(str(x)) for x, pair in zip(pair_check, pairs_for_loop)]
                            self.temp_dict[triple]['Message'] = f'Профит: {coin_amount}\nТройка: {trading}\n Цена объем: {self.price_amount}\n'
                            self.price_amount = {}
                    else:
                        if self.temp_dict[triple]['Time']:
                            self.temp_dict[triple]['Message'] += f'Время: {(datetime.now() - self.temp_dict[triple]["Time"]).total_seconds()}'
                            self.final_message.put(self.temp_dict[triple]['Message'])
                            self.temp_dict[triple]['Time'] = None
                            self.temp_dict[triple]['Message'] = None
                            self.price_amount = {}

    def on_close(self, *args):

        self.orderbooks[threading.current_thread().name] = None
        self.queue.put(threading.current_thread().name)
        print(f' Отсоединился поток {threading.current_thread().name}')
        print(f'Аргументы функции on_close {args}')

    def on_error(self, websocket, err):

        print(f'Ошибка {err}')


if __name__ == '__main__':
    crypto = Socket()
    crypto.main()


