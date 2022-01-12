#!/usr/bin/env python3
from time import sleep
from lib.LineNotifier import LineNotifier
from lib.PriceHandler import PriceHandeler
from lib.HistoryData import TWHistoryData, USHistoryData
from lib.TGNotifier import TGNotifier
import logging
import json
import argparse
import re

from lib.YStockMonitor import YStockMonitor

logging.basicConfig()
log = logging.getLogger("main")


def getTargetPrice(price: str):
    regx = re.compile(
        "(<=|>=|<|>|=){1}(MA20|MA5|MA10|UBBANDS|LBBANDS|){1}([+-]){0,1}([1-9]{0,1}[0-9]{0,1})(%){0,1}"
    )
    r = regx.match(price)
    g = r.groups()
    log.debug(g)
    return g


def main():
    log.setLevel(logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument("country", help="Stock contory", choices=["tw", "us"])
    parser.add_argument("--finmind_token", type=str, default=None)
    parser.add_argument("--line_token", type=str)
    args = parser.parse_args()
    finmind_token = args.finmind_token

    with open("config.json", "r") as f:
        cfg = json.load(f)
    if args.country == "tw":
        history = TWHistoryData(finmind_token)
    else:
        history = USHistoryData(finmind_token)
    history.setDebug()
    monitiors = dict()
    for stock in cfg[args.country]:
        try:
            target = getTargetPrice(stock["target"])
            percent = True if target[-1] else False
            addition_num = target[-2] if target[-2] else 0
            addition_compare = target[2] if target[2] else "="
            compare = target[0]
            strategy = target[1]
        except:
            log.info("targe format is wrong")
            raise
        try:
            symbol = stock["symbol"]
        except KeyError:
            log.error('"symbol" not found!')
            raise
        except:
            raise
        p = history.getPrice(strategy, symbol)
        log.info("%s of %s is %.2f" % (strategy, symbol, p))
        target_p = p
        if addition_compare != "=":
            if percent:
                add_p = (int(addition_num) * p) / 100
            else:
                add_p = float(addition_num)
            if addition_compare == "+":
                target_p += add_p
            else:
                target_p -= add_p
        log.info("Target price of %s is %s %.2f" % (symbol, compare, target_p))
        if "line" in stock:
            notifier = LineNotifier(stock["line"])
            handler = PriceHandeler(
                notifier,
                symbol,
                compare=compare,
                price=target_p,
                condition=stock["target"],
            )
            if args.country == "tw":
                symbol = symbol + ".tw"
            try:
                mon = monitiors[symbol]
            except KeyError:
                monitiors[symbol] = YStockMonitor(symbol)
                mon = monitiors[symbol]
            finally:
                mon.setHandler(handler)
        if "TG_BOT" in stock:
            notifier=TGNotifier(stock["TG_BOT"],stock["TG_USER"])
            handler = PriceHandeler(
                notifier,
                symbol,
                compare=compare,
                price=target_p,
                condition=stock["target"],
            )
            if args.country == "tw":
                symbol = symbol + ".tw"
            try:
                mon = monitiors[symbol]
            except KeyError:
                monitiors[symbol] = YStockMonitor(symbol)
                mon = monitiors[symbol]
            finally:
                mon.setHandler(handler)
    for m in monitiors.values():
        m.monitor()
    # Run only 8 hours
    log.debug("exit")
    sleep(60 * 60 * 8)
    for m in monitiors.values():
        m.quit()


if __name__ == "__main__":
    main()
