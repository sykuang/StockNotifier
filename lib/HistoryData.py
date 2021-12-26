#!/usr/bin/env python3

from FinMind.data import DataLoader
from os import environ
import logging
from datetime import datetime, timedelta

import pandas


class HistoryData:
    __instance = None
    _token = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        logging.basicConfig()
        self._log = logging.getLogger("HistoryData")
        try:
            env_token = environ["FINMIND_TOKEN"]
        except:
            self._log.warning("FINMIND_TOKEN token is not defined in envroiments")
            pass
        else:
            self.api = DataLoader()
            self.api.login_by_token(api_token=env_token)

    def setDebug(self):
        self._log.setLevel(logging.DEBUG)

    def getData(self, symbol: str, delta: int = 60) -> pandas.DataFrame:
        today = datetime.today()
        start = (today - timedelta(days=delta)).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")
        self._log.info("from %s to %s" % (start, end))
        return self.api.taiwan_stock_daily(
            stock_id=symbol, start_date=start, end_date=end
        )

    def _getMA(self, data: pandas.DataFrame, delta: int = 20):
        return data.rolling(delta).mean()

    def getMA(self, symbol: str):
        data = self.getData(symbol)
        return self._getMA(data["close"])


if __name__ == "__main__":
    log = logging.getLogger("main")
    log.setLevel(logging.DEBUG)
    history = HistoryData()
    history.setDebug()
    MA = history.getMA("2454")
    log.info(MA)
