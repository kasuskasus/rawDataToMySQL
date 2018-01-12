#!/usr/bin/python
# -*- coding: utf-8 -*-
#

import websocket
import time
import json

try:
    import thread
except ImportError:
    import _thread as thread
import time

ws2ChannelMap = {
    'trollbox':1001,
    'ticker':1002,
    'footer':1003,
    'hearbeat':1010
}


class WebSocketAppPoloniex(websocket.WebSocketApp):

    def __init__(self,
                 url = "wss://api2.poloniex.com/",
                 on_message = None,
                 on_error = None,
                 on_close = None):
        self.url = url
        self.on_message=on_message
        self.on_error=on_error
        self.on_close=on_close
        self.sock=None

    def on_message(self, message):
        print(message)

    def on_error(self, error):
        print(error)

    def on_close(self):
        print("### closed ###")

    def on_open(self):
        print("### opened ###")

        def run(*args):
            ws.send(json.dumps({'command': 'subscribe', 'channel': 'BTC_ETH'}))

        thread.start_new_thread(run,())

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = WebSocketAppPoloniex()
    ws.on_open()
    ws.run_forever()
