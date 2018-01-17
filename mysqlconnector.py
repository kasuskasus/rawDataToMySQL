#!/usr/bin/python
# -*- coding: utf-8 -*-
#

import mysql.connector
import config # project config file
import markets
import logging
from sys import stdout
from time import time

def std_write(n, m):
    """Writes in one line"""
    stdout.write("\r Element %d" % n + " out of %d" % m)
    stdout.flush()

class MySqlExchangeProcessor():
    """ Used to establish connection to MySql database, prepare clean table structure based on markets data
    and perform insertion and updates of information based on messages from exchanges"""

    def __init__(self, user=None, password=None, host='127.0.0.1', database=None):
        self.database_ready = False

        if database:
            self._database = database
        # Try to connect to DB
        try:
            self._connection = mysql.connector.connect(user=user, password=password, host=host, database=database)
        except mysql.connector.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            sys.exit(1)

        try:
            database_ready = self.prepare_database()
        except mysql.connector.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            sys.exit(1)

        if database_ready:
            print("Database successfully initialized!")
        else:
            raise RuntimeError

    def prepare_database(self):
        # Get list of available tables and exclude items with "_template" ending
        _list_of_tables=[]
        for x in self.get_tables():
            if x[0] and "_template" not in x[0]:
                _list_of_tables.append(x[0])

        # Prepare and execute drop statements (if tables exist)
        if len(_list_of_tables) > 0:
            _sql_tables_drop_stmt = "DROP TABLE IF EXISTS %s" % ', '.join(_list_of_tables)

            _cursor = self._connection.cursor()
            print('Dropping all existing tables (excluding templates)...')
            try:
                _cursor.execute(_sql_tables_drop_stmt)
                _cursor.close()
            except ValueError as e:
                print(e)

        # Prepare and execute create table statements for all markets
        _sql_tables_create_stmt = []
        ttt = time()
        for each in markets.list_all_markets():
            # _sql_tables_create_stmt.append("CREATE TABLE %s_buy_orders (timestamp varchar(255), seq varchar(255), price varchar(255), amount varchar(255), constraint pk primary key (price))" % each)
            # _sql_tables_create_stmt.append("CREATE TABLE %s_sell_orders (timestamp varchar(255), seq varchar(255), price varchar(255), amount varchar(255), constraint pk primary key (price))" % each)
            # _sql_tables_create_stmt.append("CREATE TABLE %s_trades (timestamp varchar(255), seq varchar(255), price varchar(255), amount varchar(255), buysell varchar(255), constraint pk primary key (price))" % each)

            _sql_tables_create_stmt.append("CREATE TABLE %s_sell_orders LIKE _sell_order_template" % each)
            _sql_tables_create_stmt.append("CREATE TABLE %s_buy_orders LIKE _buy_order_template" % each)
            _sql_tables_create_stmt.append("CREATE TABLE %s_trades LIKE _trade_template" % each)
        _cursor = self._connection.cursor()
        print('Creating new tables for all markets from templates...')
        try:
            n = 0
            m = len(_sql_tables_create_stmt)
            for each in _sql_tables_create_stmt:
                _cursor.execute(each)
                n += 1
                std_write(n, m)
            print("")
            _cursor.close()
        except mysql.connector.Error as e:
            print(e)
        print("Took", time()-ttt, ' secs to initialize')
        # Database exists?
        databases_existing = []
        for x in self.get_databases():
            databases_existing.append(x[0])

        database_exists = self._database in databases_existing

        # Tables exist?
        tables_existing = []
        a = ""
        for x in self.get_tables(self._database):
            a = x[0]
            a = a.replace("_sell_orders","")
            a = a.replace("_buy_orders","")
            a = a.replace("_trades","")
            if a != "_sell_order_template" and a != "_buy_order_template" and a != "_trade_template":
                tables_existing.append(a)

        # Getting rid of duplicates
        tables_existing=list(dict.fromkeys(tables_existing))

        # Comparing 2 lists - if zero len -> list are identical
        if len(set(tables_existing) ^ set(markets.list_all_markets())) == 0:
            tables_exist = True

        if database_exists and tables_existing:
            return True
        else:
            return False

    def close(self):
        self._connection.close()

    def get_databases(self):
        _sql = "SHOW DATABASES;"
        _cursor = self._connection.cursor()
        _cursor.execute(_sql)
        _results = _cursor.fetchall()
        _cursor.close()
        return _results

    def get_tables(self, database_name=None):
        if not database_name:
            database_name = self._database

        _cursor = self._connection.cursor()
        _cursor.execute("USE %s" % database_name + ";")
        _cursor.execute("SHOW TABLES;")

        _results = _cursor.fetchall()
        _cursor.close()
        return _results

    def insert_data(self, timestamp=None, seq=None, data_array=None, currency_pair=None, type=None):
        if not seq and data_array and currency_pair and type:
            raise RuntimeError
        else:
            _table = currency_pair + "_" + type + '_orders'
            _values_substring = ""
            ttt = time()
            for each in data_array:
                _values_substring = _values_substring + "('" + str(each[0]) + "', '" + str(each[1]) + "', '" + str(each[2]) + "', '" + str(each[3]) + "'),"
            _sql_insert = "INSERT INTO " + self._database + "."+ _table + " (timestamp, seq, price, amount) VALUES " + _values_substring[:-1]

            print(_sql_insert)

            _cursor_new = self._connection.cursor()
            _cursor_new.execute(_sql_insert)
            self._connection.commit()
            _cursor_new.close()
            print("Time ", time()-ttt)

    def update_record(self, currency_pair=None, update_values=None, type=None):
        if not currency_pair and update_values and type:
            raise RuntimeError
        else:

            _table = self._database + "." + currency_pair + "_" + type + '_orders'
            ttt = time()
            print("Updating: ", update_values, end="")
            _sql_update = "REPLACE INTO {} (timestamp, seq, price, amount) VALUES ('{}','{}','{}','{}')".format(_table, str(update_values[0]),str(update_values[1]),str(update_values[2]),str(update_values[3]))
            # print (_sql_update)

            _cursor_update = self._connection.cursor()
            _cursor_update.execute(_sql_update)
            self._connection.commit()
            _cursor_update.close()

            print(" - took " + str(time()-ttt) + " sec")

    # def insert_trade(self, ):
if __name__=='__main__':
    mysql = MySqlExchangeProcessor(
                                    user=config.config['db_user'],
                                    password=config.config['db_pass'],
                                    host=config.config['db_host'],
                                    database=config.config['db_name']
    )



    mysql.close()





