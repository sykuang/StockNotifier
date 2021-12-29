#!/usr/bin/env python3

from FinMind.data import DataLoader
import logging
from datetime import datetime, timedelta
import pandas as pd
try:
    from .Singleton import Singleton
except:
    from Singleton import Singleton
import requests
import talib


class FinMindAPI(metaclass=Singleton):
    def __init__(self, token=None):
        self.api = DataLoader()
        if token:
            self.api.login_by_token(api_token=token)
            self.token = token
        else:
            self.token = ""
        logging.basicConfig()
        self._log = logging.getLogger(self.__class__.__name__)

    def setDebug(self):
        self._log.setLevel(logging.DEBUG)

    def getData(self, symbol: str, delta: int = 60, country="tw") -> pd.DataFrame:
        today = datetime.today()
        start = (today - timedelta(days=delta)).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")
        self._log.info("from %s to %s" % (start, end))
        if country == "us":
            url = "https://api.finmindtrade.com/api/v3/data"
            parameter = {
                "dataset": "USStockPrice",
                "stock_id": symbol,
                "date": start,
                "token": self.token,
            }
            data = requests.get(url, params=parameter)
            data = data.json()
            data = pd.DataFrame(data["data"])
            return data
        else:
            return self.api.taiwan_stock_daily(
                stock_id=symbol, start_date=start, end_date=end
            )


class HistoryData:
    def __init__(self, token=None):
        self.api = FinMindAPI(token)
        logging.basicConfig()
        self._log = logging.getLogger(self.__class__.__name__)
        self._log.debug(self.__class__.__name__)

    def getData(self, symbol: str, delta: int = 60) -> pd.DataFrame:
        pass

    def getMA(self, symbol: str, days=20):
        data = self.getData(symbol, days + 10)
        return talib.MA(data, days)

    def setDebug(self):
        self._log.setLevel(logging.DEBUG)
        self.api.setDebug()

    def getBBANDS(self, symbol: str, days=20):
        data = self.getData(symbol, days + 10)
        return talib.BBANDS(data, timeperiod=days, nbdevup=2, nbdevdn=2, matype=0)

    def getPrice(self,strategy,symbol):
        match strategy:
            case "UBBANDS":
                return self.getBBANDS(symbol)[0].iloc[-1]
            case "MBBANDS":
                return self.getBBANDS(symbol)[1].iloc[-1]
            case "LBBANDS":
                return self.getBBANDS(symbol)[2].iloc[-1]
            case "MA20":
                return self.getMA(symbol).iloc[-1]
            case _:
                self._log.error("Wrong strategy")
                raise KeyError
class TWHistoryData(HistoryData):
    def getData(self, symbol: str, delta: int = 60) -> pd.DataFrame:
        # In TW stock it uses close as column name, in US it uses Close.self..
        return self.api.getData(symbol=symbol, delta=delta, country="tw")["close"]


class USHistoryData(HistoryData):
    def getData(self, symbol: str, delta: int = 60) -> pd.DataFrame:
        return self.api.getData(symbol=symbol, delta=delta, country="us")["Close"]


if __name__ == "__main__":
    from os import environ

    log = logging.getLogger("main")
    log.setLevel(logging.DEBUG)
    try:
        env_token = environ["FINMIND_TOKEN"]
        history = TWHistoryData(env_token)
    except:
        log.warning("FINMIND_TOKEN token is not defined in envroiments")
        history = TWHistoryData()
    #
    history.setDebug()
    MA = history.getPrice("MA20","2454")
    log.info(MA)
    ubb = history.getPrice("UBBANDS","2454")
    log.info(ubb)
    mbb = history.getPrice("MBBANDS","2454")
    log.info(mbb)
    lbb = history.getPrice("LBBANDS","2454")
    log.info(lbb)
