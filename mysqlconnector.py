#!/usr/bin/python
# -*- coding: utf-8 -*-
#

import mysql.connector
import config # project config file

cnx = mysql.connector.connect(user=config.config['db_user'],
                              password=config.config['db_pass'],
                              host=config.config['db_host'],
                              database=config.config['db_name'])




cnx.close()