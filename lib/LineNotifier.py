#!/usr/bin/env python3
from .Notifier import Notifier
import requests
import logging


class LineNotifier(Notifier):
    def __init__(self, token):
        logging.basicConfig()
        self._log = logging.getLogger(self.__class__.__name__)
        self.__token = token

    def sendMsg(self, msg: str):
        headers = {
            "Authorization": "Bearer " + self.__token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        payload = {"message": msg}
        r = requests.post(
            "https://notify-api.line.me/api/notify", headers=headers, params=payload
        )
        return r.status_code


if __name__ == "__main__":
    from os import environ
    log = logging.getLogger("main")
    log.setLevel(logging.DEBUG)
    notify = LineNotifier(environ["LINE_TOKEN"])
    notify.sendMsg("hi")
    pass
