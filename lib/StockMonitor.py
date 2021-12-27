#!/usr/bin/env python3
from .Notifier import Notifier
from fugle_realtime import WebSocketClient
import logging
import json


class StockMonitor:
    def __init__(self, Notifier, symbol: str, price, token="demo"):
        self._notifier = Notifier
        self._symbol = symbol
        self._price = price
        self._token = token
        self._notified = False

    def setPrice(self, price: int):
        self._price = price

    def Monitor(self):
        ws_client = WebSocketClient(api_token=self._token)
        notifer = self._notifier
        target_price = self._price
        notified = self._notified

        def handle_message(msg):
            nonlocal notified
            if notified:
                return
            nonlocal notifer
            nonlocal target_price
            msg = json.loads(msg)
            info_type = msg["data"]["info"]["type"]
            if info_type == "EQUITY":
                return
            symbol = msg["data"]["info"]["symbolId"]
            try:
                price = msg["data"]["quote"]["trade"]["price"]
                if price <= target_price:
                    notifier.sendMsg("%s is $%.2f now!" % (symbol, price))
            except:
                pass

            # notifer.sendMsg(msg)

        ws = ws_client.intraday.quote(symbolId=self._symbol, on_message=handle_message)
        self._ws = ws
        ws.run_async()

    def __del__(self):
        if self._ws:
            self._ws.close()


if __name__ == "__main__":
    log = logging.getLogger("main")
    log.setLevel(logging.DEBUG)
    from LineNotifier import LineNotifier
    from os import environ

    notifier = LineNotifier(environ["LINE_TOKEN"])
    monitor = StockMonitor(
        symbol="2454", price=2000, token=environ["FUGLE_TOKEN"], Notifier=notifier
    )
    monitor.Monitor()
    pass
