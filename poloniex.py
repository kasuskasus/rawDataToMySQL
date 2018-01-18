#!/usr/bin/python
# -*- coding: utf-8 -*-
#

from time import time
import json
import logging
from multiprocessing.dummy import Process as Thread

import websocket  # pip install websocket-client

import markets
import mysqlconnector
import config

# from poloniex import Poloniex

logger = logging.getLogger(__name__)


class WSSClass(object):

    def __init__(self, api=None):
        # self.api = api
        # if not self.api:
        #     self.api = Poloniex(jsonNums=float)
        self.tick = {}
        self._values_buy, self._values_sell = [], []
        self._total_buy, self._total_sell = 0, 0
        self.orderbook_seq, self.trade_seq = {}, {}
        #
        # iniTick = self.api.returnTicker()
        # self._ids = {market: iniTick[market]['id'] for market in iniTick}
        # for market in iniTick:
        #     self.tick[self._ids[market]] = iniTick[market]

        self._ws = websocket.WebSocketApp("wss://api2.poloniex.com/",
                                          on_open=self.on_open,
                                          on_message=self.on_message,
                                          on_error=self.on_error,
                                          on_close=self.on_close)



    def on_message(self, ws, message):
        print(json.loads(message))

        # Parsing string into json array
        _message_json = json.loads(message)

        # Parsing JSON array into variables

        if _message_json[0] == markets.wss_channels['trollbox']:
            # trollbox
            pass

        elif _message_json[0] == markets.wss_channels['ticker']:
            # handling ticker
            pass

        elif _message_json[0] == markets.wss_channels['base_coin']:
            # handling base_coin
            pass

        elif _message_json[0] == markets.wss_channels['heartbeat']:
            # handling heartbeat
            pass

        else:
            def find(l, elem):
                """Returns element elem location in twodimensional list"""
                for row, i in enumerate(l):
                    try:
                        column = i.index(elem)
                    except ValueError:
                        continue
                    return row, column
                return -1

            _currency_id = _message_json[0]
            _sequence_number = _message_json[1]
            print('Messages in received message: ', len(_message_json[2]))

            print(_currency_id, self.orderbook_seq.get(_currency_id), _sequence_number)

            if self.orderbook_seq.get(_currency_id) == None:
                # This is a new init, everything is ok
                self.orderbook_seq[_currency_id] = _sequence_number
            else:
                # Something went wrong! Throwing error (TODO - add exception to restart connection!)
                if int(self.orderbook_seq.get(_currency_id)) + 1 != int(_sequence_number):
                    raise ValueError
                # Everything is fine, update _sequence_number
                else:
                    self.orderbook_seq[_currency_id] = _sequence_number

            for m in _message_json[2]:
                print(m)
                _msg_type = m[0] #_message_json[2][0][0]  # i - initial orderbook, o - orderbook (0 - sell, 1 - buy), t - trade (0 - sell, 1 - buy)

                if _msg_type == 'i':
                    _SQL_add_order_book_record = "INSERT INTO %s (seq, price, amount) VALUES (%s, %s, %s)"

                    # Initial sell order book

                    _temp_values_sell, _temp_values_buy = [], []

                    for x in _message_json[2][0][1]['orderBook'][0]:
                        _temp_values_sell.append(
                                                [str(int(time())),
                                                 _sequence_number,
                                                 x,
                                                 _message_json[2][0][1]['orderBook'][0][x]])

                    # Inserting into MySQL sell book
                    mysql.insert_data(seq = _message_json[1],
                                      currency_pair=_message_json[2][0][1]['currencyPair'],
                                      data_array=_temp_values_sell, #self._values_sell,
                                      type='sell')

                    # Initial buy order book
                    for y in _message_json[2][0][1]['orderBook'][1]:
                        _temp_values_buy.append(
                                                [str(int(time())),
                                                 _sequence_number,
                                                 y,
                                                 _message_json[2][0][1]['orderBook'][1][y]])

                    # Inserting into MySQL buy book
                    mysql.insert_data(seq=_message_json[1],
                                      currency_pair=_message_json[2][0][1]['currencyPair'],
                                      data_array=_temp_values_buy, #self._values_buy,
                                      type='buy')

                elif _msg_type == 'o':
                    if m[1] == 0: # treat sell order book change
                        print ("sell orderbook change")

                        item_get = mysql.get_orderbook_item(currency_pair = markets.get_currency_ticker_by_id(_currency_id),
                                                            type = 'sell',
                                                            price = m[2])

                        if len(item_get) == 0:
                            print("new sell order book item", [m[2], m[3]])
                        else:
                            print ("was: ", item_get, ", will be: ", [m[2],m[3]])


                        _update_values = [str(int(time())),
                                          _sequence_number,
                                          m[2],
                                          m[3]]
                        # Update value
                        mysql.update_record(currency_pair=markets.get_currency_ticker_by_id(_currency_id),
                                            update_values=_update_values,
                                            type='sell')


                    else: # treat buy order book change
                        print("buy orderbook change")

                        item_get = mysql.get_orderbook_item(
                                                        currency_pair=markets.get_currency_ticker_by_id(_currency_id),
                                                        type='buy',
                                                        price=m[2])

                        if len(item_get) == 0:
                            print("new buy order book item: ", [m[2], m[3]])
                        else:
                            print("was: ", item_get, ", will be: ", [m[2], m[3]])

                        print ("buy ob change")
                        if find(self._values_buy, m[2]) != -1:
                            print("was:", self._values_buy[find(self._values_buy, m[2])[0]][2], " - ", self._values_buy[find(self._values_buy, m[2])[0]][3])
                        else:
                            print("new sell orderbook value")
                        print ("will be: ", m[2], " - ",m[3])

                        _update_values = [str(int(time())),
                                          _sequence_number,
                                          m[2],
                                          m[3]]
                        # Update value
                        mysql.update_record(currency_pair=markets.get_currency_ticker_by_id(_currency_id),
                                            update_values=_update_values,
                                            type='buy')

                elif _msg_type == 't':
                    # Process trades
                    _trade_seq = m[1]
                    _trade_type = m[2]
                    _trade_price = m[3]
                    _trade_amount = m[4]
                    _trade_timestamp = m[5]



                else:
                    pass

                #

        if 'error' in message:
            return logger.error(message['error'])

        if message[0] == 1002:
            if message[1] == 1:
                return logger.info('Subscribed to ticker')

            if message[1] == 0:
                return logger.info('Unsubscribed to ticker')

            data = message[2]
            data = [float(dat) for dat in data]
            self.tick[data[0]] = {'id': data[0],
                                  'last': data[1],
                                  'lowestAsk': data[2],
                                  'highestBid': data[3],
                                  'percentChange': data[4],
                                  'baseVolume': data[5],
                                  'quoteVolume': data[6],
                                  'isFrozen': data[7],
                                  'high24hr': data[8],
                                  'low24hr': data[9]
                                  }

    def on_error(self, ws, error):
        logger.error(error)

    def on_close(self, ws):
        if self._t._running:
            try:
                self.stop()
            except Exception as e:
                logger.exception(e)
            try:
                self.start()
            except Exception as e:
                logger.exception(e)
                self.stop()
        else:
            logger.info("Websocket closed!")

    def on_open(self, ws):
        # self._ws.send(json.dumps({'command': 'subscribe', 'channel': 1002}))
        print('subscribed to 1002')
        self._ws.send(json.dumps({'command': 'subscribe', 'channel': 'BTC_ETH'}))
        self._ws.send(json.dumps({'command': 'subscribe', 'channel': 'BTC_DOGE'}))

    @property
    def status(self):
        """
        Returns True if the websocket is running, False if not
        """
        try:
            return self._t._running
        except:
            return False

    def start(self):
        """ Run the websocket in a thread """
        self._t = Thread(target=self._ws.run_forever)
        self._t.daemon = True
        self._t._running = True
        self._t.start()
        logger.info('Websocket thread started')

    def stop(self):
        """ Stop/join the websocket thread """

        self._t._running = False
        self._ws.close()
        self._t.join()
        logger.info('Websocket thread stopped/joined')

    def __call__(self, market=None):
        """ returns ticker from mongodb """
        if market:
            pass

        # return 'USD_BTC_ticker'

        return self.tick


if __name__ == "__main__":
    import pprint

    logging.basicConfig(level=logging.DEBUG)
    # websocket.enableTrace(True)
    mysql = mysqlconnector.MySqlExchangeProcessor(
                                    user=config.config['db_user'],
                                    password=config.config['db_pass'],
                                    host=config.config['db_host'],
                                    database=config.config['db_name']
    )
    ticker = WSSClass()
    try:
        ticker.start()
        pprint.pprint(ticker('USDT_BTC'))
    except Exception as e:
        logger.exception(e)
    input("Enter to stop")
    ticker.stop()
