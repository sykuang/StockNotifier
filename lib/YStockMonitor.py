import yfinance as yf

try:
    from StockMonitor import StockMonitor
except Exception:
    from .StockMonitor import StockMonitor
import asyncio
from datetime import datetime, timedelta, timezone
import logging
import threading
from pandas import to_datetime
import pandas_market_calendars as mcal

lock = threading.Lock()
glog = logging.getLogger("getPrice")


class YStockMonitor(StockMonitor):
    @staticmethod
    def getPrice(symbol: str, handlers, debug=False):
        if not symbol.endswith(".tw"):
            nyse = mcal.get_calendar("NYSE")
            try:
                nowtime = datetime.now(timezone.utc)
                sch = nyse.schedule(start_date=nowtime, end_date=nowtime)
                opentime = sch.iloc[0][0].to_pydatetime()
                closetime = sch.iloc[0][1].to_pydatetime()
                if nowtime < opentime or nowtime > closetime:
                    glog.debug("Market is closed")
                    return
            except IndexError:
                glog.debug("Market is closed")
                return

        if debug:
            # yfinance cannot request 1 min interval if periods is larger than 7 days
            start_date = datetime.now() - timedelta(days=4)
        else:
            start_date = datetime.now() - timedelta(days=1)
        start_date = start_date.strftime("%Y-%m-%d")
        try:
            lock.acquire()
            data = yf.download(
                tickers=symbol,
                start=start_date,
                group_by="ticker",
                progress=False,
                interval="1m",
            )
            lock.release()
            if len(data):
                trade_date = to_datetime(data.index.values[-1])
                today = datetime.now(timezone.utc)
                if trade_date.date() >= today.date():
                    price = data["Close"].iloc[-1]
                    if debug:
                        glog.debug(price)
                    for h in handlers:
                        h.notify(price)
                else:
                    glog.warning(f"Data({trade_date}) is old;Today is {today}")
        except KeyError:
            glog.error("Error keyerror skip!")
        except Exception as e:
            glog.error(f"Error:{str(e)}")
        finally:
            # Update data every 30 seconds
            loop = asyncio.get_event_loop()
            loop.call_later(30, YStockMonitor.getPrice, symbol, handlers, debug)

    def _monitor(self) -> None:
        self._log.info("start monitor")
        self.loop = asyncio.new_event_loop()
        self.loop.call_soon(
            YStockMonitor.getPrice, self.symbol, self.handlers, self.debug
        )
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()

    def monitor(self):
        self._run_thread = threading.Thread(target=self._monitor)
        self._run_thread.start()

    def quit(self) -> None:
        self.loop.stop()
        if self._run_thread:
            self._run_thread.join()


if __name__ == "__main__":
    from time import sleep
    from sys import argv

    country = argv[1]
    log = logging.getLogger("main")
    log.setLevel(logging.DEBUG)
    stock = YStockMonitor("2454.tw") if country == "tw" else YStockMonitor("MSFT")
    stock.setDebug()
    stock.monitor()
    log.info("quit")
    sleep(3 * 30)
    log.info("quit")
    stock.quit()
