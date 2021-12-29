from lib.LineNotifier import LineNotifier
import logging

class PriceHandeler:
    def __init__(self, notifier: LineNotifier, symbol, price: float, compare:str)->None:
        self.compare = compare
        self.target_price = price
        self.symbol = symbol
        self.notifier = notifier
        self.notified=False
        logging.basicConfig()
        self._log = logging.getLogger(self.__class__.__name__)
        self._log.setLevel(logging.INFO)
    def __shouldNotify(self, price) -> bool:
        if self.notified:
            return False
        notify = False
        target_price = self.target_price
        match self.compare:
            case "<":
                if price < target_price:
                    notify=True
            case ">":
                if price > target_price:
                    notify=True
            case ">=":
                if price >= target_price:
                    notify=True
            case "<=":
                if price <= target_price:
                    notify=True
            case "=":
                if price == target_price:
                    notify=True
        return notify 

    def notify(self, price):
        if self.__shouldNotify(price):
            MSG = "%s is $%.2f now!" % (self.symbol, price)
            self._log.info("sendMSG:%s" % MSG)
            self.notifier.sendMsg(MSG)
            self.notified=True
