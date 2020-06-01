import pandas as pd
import sqlite3 as sq
import os

from sqlite3 import Error as SqError

class DAO:
  def __init__(self):
    self._default_db_path = 'prdb.db'
    self._con = None
    self._cursor = None

    #self.initial_schema

    self._connect_to_db()

  def _connect_to_db(self):
    init_dbase_later = False
    if not os.path.exists(self._default_db_path):
      print('Database does not exist, creating a new one')
      init_dbase_later = True

    try:
      self._con = sq.connect(self._default_db_path)
      print("Connection is established: Database is created")
    except SqError:
      print(SqError)
      return None

    self._cursor = self._con.cursor()

    # init db if its not created, reinit if it has a wrong version
    if init_dbase_later:
      self._init_db()
    elif not self._verify_table_schema():
      print('Schemas mismatch, reinitializing database')
      self._clear_db()
      self._init_db()

  def _clear_db(self):
    tables = pd.read_sql_query('SELECT * FROM sqlite_master', self._con)['name']
    for table in tables:
      self._cursor.execute('DROP TABLE {}'.format(table))

    self._con.commit()

  def _init_db(self):
    for table_command in self._default_table_commands():
      self._cursor.execute(table_command)

    self._con.commit()
    #print(.description())

  # returns True if table schema matches the default
  def _verify_table_schema(self):
    default_schema = self._default_table_commands()
    current_schema = pd.read_sql_query('SELECT * FROM sqlite_master', self._con)['sql'].values

    if len(default_schema) != len(current_schema):
      return False

    for default_table, current_table in zip(default_schema, current_schema):
      if default_table != current_table:
        return False

    return True


  def _default_table_commands(self):
    commands = ['CREATE TABLE profiles('
               'profile_id integer PRIMARY KEY,'
               'name text,'
               'description text,'
               'date_created text,'
               'date_last_used text)',

                'CREATE TABLE topics('
                'topic_id integer PRIMARY KEY,'
                'profile_id integer,'
                'topic_text text)',

                'CREATE TABLE history('
                'history_id integer PRIMARY KEY,'
                'profile_id integer,'
                'article_id integer,'
                'date_added text,'
                'was_read integer,'
                'date_read text)',

                'CREATE TABLE articles_topics('
                'article_topic_id integer PRIMARY KEY,'
                'article_id integer,'
                'topic_id integer)',

                'CREATE TABLE articles('
                'article_id integer PRIMARY_KEY,'
                'rp_id integer,'
                'is_rp_article integer,'
                'url text,'
                'title text,'
                'reading_time integer,'
                'logo text)',

                'CREATE TABLE active_articles('
                'last_displayed_id integer PRIMARY KEY,'
                'article_id integer,'
                'profile_id integer)',

                'CREATE TABLE reading_plans('
                'rp_id integer PRIMARY KEY,'
                'profile_id integer,'
                'rp_name text,'
                'rp_description text)',

                'CREATE TABLE reading_plan_topics('
                'rp_topic_id integer PRIMARY KEY,'
                'rp_id integer,'
                'rp_topic_text text)',

                'CREATE TABLE reading_plan_articles_topics('
                'rp_article_topic_id integer PRIMARY KEY,'
                'article_id integer,'
                'rp_topic_id integer)',
                ]
    return commands

  def describe_db(self):
    #self._cursor.execute('SELECT name FROM sqlite_master')

    print(pd.read_sql_query('SELECT * FROM sqlite_master', self._con)['sql'].values)

  def __del__(self):
    self._con.close()
