#!/usr/bin/python
# -*- coding: utf-8 -*-
#

import mysql.connector
import config # project config file
import markets
import logging

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

        if not database_ready:
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
        for each in markets.list_all_markets():
            _sql_tables_create_stmt.append("CREATE TABLE %s_sell_orders LIKE _sell_order_template" % each)
            # _sql_tables_create_stmt += "CREATE TABLE %s_buy_orders LIKE __buy_order_template;\n" % each
            # _sql_tables_create_stmt += "CREATE TABLE %s_trades LIKE _trade_template;\n" % each
        _cursor = self._connection.cursor()
        print('Creating new tables for all markets from templates...')
        try:
            for each in _sql_tables_create_stmt:
                _cursor.execute(each)
            _cursor.close()
        except mysql.connector.Error as e:
            print(e)

        # Database initialized
        return True

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

    def remove_tables_from_db(self, database_name=None, list_of_tables = None):
        if not database_name:
            database_name = self._database

        _tables = show_tables(database_name)

        if _tables and list_of_tables:
            # self._cursor.execute("USE %s" & database_name)
            _q = "DROP TABLE IF EXISTS "
            print(_q)



if __name__ == "__main__":
    mysql = MySqlExchangeProcessor(
                                    user=config.config['db_user'],
                                    password=config.config['db_pass'],
                                    host=config.config['db_host'],
                                    database=config.config['db_name']
    )




    mysql.close()





