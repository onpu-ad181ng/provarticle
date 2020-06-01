#from source.recomender import test

#results = test()

#for result in results:
#  print(result)

import sqlite3 as sq
import os

from sqlite3 import Error as SqError

from source.dao import DAO

dao = DAO()

dao.describe_db()
#connection = sql_connection('prdb.db')
#cursor = connection.cursor()

print(1)
