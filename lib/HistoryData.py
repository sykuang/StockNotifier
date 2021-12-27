#!/usr/bin/env python3

from FinMind.data import DataLoader
import logging
from datetime import datetime, timedelta
from Singleton import Singleton
import pandas


class HistoryData(metaclass=Singleton):
    def __init__(self, token=None):
        self.api = DataLoader()
        self.api.login_by_token(api_token=token)

        logging.basicConfig()
        self._log = logging.getLogger(self.__class__.__name__)

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
    from os import environ
    log = logging.getLogger("main")
    log.setLevel(logging.DEBUG)
    try:
        env_token = environ["FINMIND_TOKEN"]
        history = HistoryData(env_token)
    except:
        log.warning("FINMIND_TOKEN token is not defined in envroiments")
        history = HistoryData()

    history.setDebug()
    MA = history.getMA("2454")
    log.info(MA)
