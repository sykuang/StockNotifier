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
from os.path import exists
from lib.YStockMonitor import YStockMonitor

logging.basicConfig()
log = logging.getLogger("main")

monitiors = {}


def getTargetPrice(price: str):
    regx = re.compile(
        "(<=|>=|<|>|=){1}(MA20|MA5|MA10|UBBANDS|LBBANDS|){1}([+-]){0,1}([1-9]{0,1}[0-9]{0,1})(%){0,1}"
    )
    r = regx.match(price)
    g = r.groups()
    log.debug(g)
    return g


def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("country", help="Stock contory", choices=["tw", "us"])
    parser.add_argument("--line_token", type=str, default="")
    parser.add_argument("--tg_token", type=str, default="")
    parser.add_argument("--tg_user", type=str, default="")
    parser.add_argument("config", help="path to config file", type=str)
    parser.add_argument("--finmind_token", type=str, default=None)
    args = parser.parse_args()
    if not exists(args.config):
        print("%s not exist!")
        exit(1)
    return args


def startNotifier(
    tokens: dict, symbol: str, target_price: str, compare: str, target: str
):
    # Add symbol to monitors
    if symbol not in monitiors:
        monitiors[symbol] = YStockMonitor(symbol)
    if tokens["LINE_TOKEN"] != "" and symbol not in monitiors:
        notifier = LineNotifier(tokens["LINE_TOKEN"])
        handler = PriceHandeler(
            notifier, symbol, compare=compare, price=target_price, condition=target
        )

        mon = monitiors[symbol]
        mon.setHandler(handler)
    if tokens["TG_TOKEN"] != "":
        notifier = TGNotifier(tokens["TG_TOKEN"], tokens["TG_USER"])
        handler = PriceHandeler(
            notifier,
            symbol,
            compare=compare,
            price=target_price,
            condition=target,
        )
        mon = monitiors[symbol]
        mon.setHandler(handler)


def main():
    log.setLevel(logging.DEBUG)
    args = getArgs()
    finmind_token = args.finmind_token
    tokens = {
        "LINE_TOKEN": args.line_token,
        "TG_TOKEN": args.tg_token,
        "TG_USER": args.tg_user,
    }
    config = args.config
    with open(config, "r") as f:
        cfg = json.load(f)
    if args.country == "tw":
        history = TWHistoryData(finmind_token)
    else:
        history = USHistoryData(finmind_token)
    history.setDebug()
    for stock in cfg[args.country]:
        try:
            target = getTargetPrice(stock["target"])
            percent = bool(target[-1])
            addition_num = target[-2] or 0
            addition_compare = target[2] or "="
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
            add_p = (int(addition_num) * p) / 100 if percent else float(addition_num)
            if addition_compare == "+":
                target_p += add_p
            else:
                target_p -= add_p
        log.info("Target price of %s is %s %.2f" % (symbol, compare, target_p))
        # Transfer symbol for Yahoo finance
        if args.country == "tw":
            symbol = f"{symbol}.tw"
        startNotifier(tokens, symbol, target_p, compare, target)
    for m in monitiors.values():
        m.monitor()
    try:
        # Run only 8 hours
        sleep(60 * 60 * 8)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log.error(e)
    finally:
        log.debug("exit")
        for m in monitiors.values():
            m.quit()


if __name__ == "__main__":
    main()
