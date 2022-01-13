#!/usr/bin/env python3
try:
    from .Notifier import Notifier
except:
    from Notifier import Notifier
import requests
import logging


class TGNotifier(Notifier):
    def __init__(self, token,user):
        logging.basicConfig()
        self._log = logging.getLogger(self.__class__.__name__)
        self.__bothtml = "https://api.telegram.org/bot"+token+"/"
        self.user=user

    def sendMsg(self, msg: str):
        action="sendMessage"
        payload={"chat_id":self.user,
                "text":msg
                }
        html=self.__bothtml+action
        r = requests.post(
            html, params=payload
        )
        return r.status_code
if __name__ == "__main__":
    from os import environ
    log = logging.getLogger("main")
    log.setLevel(logging.DEBUG)
    notify = TGNotifier(environ["TG_TOKEN"],environ["TG_ID"])
    notify.sendMsg("hi")
    pass
