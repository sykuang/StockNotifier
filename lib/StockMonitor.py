#!/usr/bin/env python3
from .Notifier import Notifier
from fugle_realtime import WebSocketClient
import logging
import json


class StockMonitor:
    _ws = None

    def __init__(self, Notifier, symbol: str, price: float, token="demo"):
        logging.basicConfig()
        self._log = logging.getLogger(self.__class__.__name__)

        self._notifier = Notifier
        self._symbol = symbol
        self._price = price
        self._token = token
        self._notified = False

    def setPrice(self, price: float):
        self._price = price

    def Monitor(self):
        ws_client = WebSocketClient(api_token=self._token)
        notifier = self._notifier
        target_price = self._price
        notified = self._notified
        log = self._log

        def handle_message(msg):
            nonlocal notified
            if notified:
                return
            nonlocal notifier
            nonlocal target_price
            nonlocal log
            msg = json.loads(msg)
            info_type = msg["data"]["info"]["type"]
            if info_type == "EQUITY":
                return
            symbol = msg["data"]["info"]["symbolId"]
            try:
                price = msg["data"]["quote"]["trade"]["price"]
                log.debug(
                    "Symbol %s is $%.2f Target %.2f" % (symbol, price, target_price)
                )
                if price <= target_price:
                    MSG = "%s is $%.2f now!" % (symbol, price)
                    log.info("sendMSG:%s" % MSG)
                    notifier.sendMsg(MSG)
                    notified = True
            except:
                log.error("except")
                raise

            # notifer.sendMsg(msg)

        ws = ws_client.intraday.quote(symbolId=self._symbol, on_message=handle_message)
        self._ws = ws
        ws.run_async()

    def setDebug(self):
        self._log.setLevel(logging.DEBUG)

    def quit(self):
        if self._ws != None:
            self._ws.close()
            self._ws = None

    def __del__(self):
        if self._ws != None:
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
