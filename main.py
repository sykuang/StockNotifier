#!/usr/bin/env python3
from os import environ
from lib.LineNotifier import LineNotifier
from lib.StockMonitor import StockMonitor
from lib.HistoryData import HistoryData
import logging

if __name__ == "__main__":
    logging.basicConfig()
    log = logging.getLogger("main")
    log.setLevel(logging.DEBUG)

    symbols = ["2454", "0050", "2633"]
    finmind_token = environ["FINMIND_TOKEN"]
    line_token = environ["LINE_TOKEN"]
    fugle_token = environ["FUGLE_TOKEN"]
    notifier = LineNotifier(line_token)
    for symbol in symbols:
        log.info(symbol)
        history = HistoryData(finmind_token)
        MA = history.getMA(symbol)
        log.info("MA20 of %s is %.2f" % (symbol, MA))
        monitior = StockMonitor(notifier, symbol, MA +20, fugle_token)
        monitior.setDebug()
        monitior.Monitor()
    pass
