import logging


class StockMonitor:
    handlers = []
    debug = False

    def __init__(self, symbol) -> None:

        logging.basicConfig()
        self._log = logging.getLogger(self.__class__.__name__)
        self._log.setLevel(logging.INFO)
        self.symbol = symbol
        pass

    def setHandler(self, handler) -> None:
        self.handlers.append(handler)

    def monitor(self):
        pass

    def setDebug(self):
        self.debug = True

    def quit(self):
        pass
