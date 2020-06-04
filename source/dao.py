import pandas as pd
import sqlite3 as sq
import os

from sqlite3 import Error as SqError

class DAO:
  def __init__(self):
    self._default_db_path = 'prdb.db'
    self._connection = None # type: sq.Connection
    self._cursor = None # type: sq.Cursor

    self.ready = False


  def connect_to_db(self, always_init_db, init_with_test):
    create_dbase_later = False
    if not os.path.exists(self._default_db_path):
      print('Database does not exist, creating a new one')
      create_dbase_later = True

    self._connection = sq.connect(self._default_db_path)
    print("Connection is established")
    self._cursor = self._connection.cursor()

    if create_dbase_later:
      print('Initializing database')
      self._init_db(init_test=init_with_test)
    if not self._verify_table_schema() or always_init_db:
      print('Reinitializing database')
      self._clear_db()
      self._init_db(init_test=init_with_test)

    self.ready = True


  def get_last_profile(self):
    profiles = pd.read_sql_query('Select * FROM profiles '
                                 'ORDER BY date_last_used DESC',
                                 self._connection)
    latest_profile = profiles.iloc[0]
    profile_data = latest_profile.to_dict()
    return profile_data


  def get_active_articles(self, profile_id):
    articles = pd.read_sql_query('SELECT articles.article_id, rp_id, profile_id, is_rp_article, url, title, reading_time, logo '
                                 'FROM articles '
                                 'INNER JOIN active_articles '
                                 'ON articles.article_id = active_articles.article_id '
                                 'WHERE profile_id = {}'.format(profile_id),
                                 self._connection) # type: pd.DataFrame

    articles = articles.to_dict('records')
    return articles


  def get_interests(self, profile_id):
    topics = pd.read_sql_query(
      'SELECT topic_text '
      'FROM topics '
      'WHERE profile_id = {}'.format(profile_id),
      self._connection)  # type: pd.DataFrame
    topics = topics['topic_text']

    return topics.tolist()


  # creates new article and adds it to history and active articles
  def create_new_article(self, rp_id, profile_id, is_rp, url, title, reading_time, logo, date):
    query = ('INSERT INTO articles(rp_id, profile_id, '
             'is_rp_article, url,title, reading_time, logo) '
             'VALUES({}, {}, {}, "{}", "{}", {}, "{}")'.format(
      rp_id, profile_id, is_rp, url, title, reading_time, logo))
    self._execute_write_query(query)

    article_id = int(pd.read_sql_query('SELECT last_insert_rowid()', self._connection).values[0])
    query = ('INSERT INTO history(article_id, date_added, was_read, date_read) '
             'VALUES({}, "{}", 0, "1970-1-1")'.format(article_id, date))
    self._execute_write_query(query)

    query = ('INSERT INTO active_articles(article_id) '
             'VALUES({})'.format(article_id))
    self._execute_write_query(query)
    return article_id


  def add_to_history(self, article_id):
    query = ('INSERT IN')
    pass


  def update_profile_last_used_field(self, profile_id, date):
    self._execute_write_query('UPDATE profiles SET date_last_used = "{}" '
                        'WHERE profile_id = {}'.format(date, profile_id))


  def update_history_as_read(self, article_id, date_read):
    self._execute_write_query('UPDATE history SET was_read = 1, date_read = "{}" '
                              'WHERE article_id = {}'.format(date_read, article_id))


  def delete_from_active_articles(self, article_id):
    self._execute_write_query('DELETE FROM active_articles '
                              'WHERE article_id = {}'.format(article_id))


  def _execute_write_query(self, query):
    result = None
    try:
      result = self._cursor.execute(query)
      self._connection.commit()
    except SqError as e:
      print(e)

    return result


  def get_read_articles(self, profile_id):
    articles = pd.read_sql_query(
      'SELECT articles.article_id, rp_id, profile_id, is_rp_article, url, title, reading_time, logo '
      'FROM articles '
      'INNER JOIN history '
      'ON articles.article_id = history.article_id '
      'WHERE profile_id = {} AND was_read = 1'.format(profile_id),
      self._connection)  # type: pd.DataFrame

    articles = articles.to_dict('records')
    return articles


  def _clear_db(self):
    tables = pd.read_sql_query('SELECT * FROM sqlite_master', self._connection)['name']
    tables = [table for table in tables if table != 'sqlite_sequence']
    for table in tables:
      self._cursor.execute('DROP TABLE {}'.format(table))

    self._connection.commit()


  def _init_db(self, init_test):
    for table_command in self._default_table_commands():
      try:
        self._cursor.execute(table_command)
      except Exception as e:
        print(table_command)
        print(e)
    self._connection.commit()

    if init_test:
      self._init_test_data()


  def _init_test_data(self):
    self._cursor.execute('INSERT INTO profiles (profile_id, name, description, date_created, date_last_used)'
                         'VALUES('
                         '0, "test profile", "test description", "2020-01-01", "2020-01-01")')

    topics = ['unity', 'unreal engine', 'pathfinding']
    for i, topic in enumerate(topics):
      self._cursor.execute('INSERT INTO topics (topic_id, profile_id, topic_text)'
                           'VALUES('
                           '?, 0, ?)', (i, topic))

    # creating articles
    self._cursor.execute('INSERT INTO articles (article_id, rp_id, profile_id, is_rp_article, url, title, reading_time, logo)'
                         'VALUES('
                         '0, 0, 0, 0, "https://medium.com/@badgerdox/addressableassetsoverview-1da9b80a47dc",'
                         '"unity test article", 31, "")')

    self._cursor.execute('INSERT INTO articles_topics (article_topic_id, article_id, topic_id)'
                         'VALUES (0, 0, 0), (1, 0, 1)')

    self._cursor.execute('INSERT INTO active_articles (last_displayed_id, article_id)'
                         'VALUES('
                         '0, 0)')

    self._cursor.execute('INSERT INTO history (history_id, article_id, date_added, was_read, date_read)'
                         'VALUES('
                         '0, 0, "2020-05-01", 0, "")')

    self._connection.commit()


  def _default_table_commands(self):
    commands = ['CREATE TABLE profiles('
               'profile_id integer PRIMARY KEY AUTOINCREMENT,'
               'name text,'
               'description text,'
               'date_created text,'
               'date_last_used text)',

                'CREATE TABLE topics('
                'topic_id integer PRIMARY KEY AUTOINCREMENT,'
                'profile_id integer,'
                'topic_text text)',

                'CREATE TABLE history('
                'history_id integer PRIMARY KEY AUTOINCREMENT,'
                'article_id integer,'
                'date_added text,'
                'was_read integer,'
                'date_read text)',

                'CREATE TABLE articles_topics('
                'article_topic_id integer PRIMARY KEY AUTOINCREMENT,'
                'article_id integer,'
                'topic_id integer)',

                'CREATE TABLE articles('
                'article_id integer PRIMARY KEY AUTOINCREMENT,'
                'rp_id integer,'
                'profile_id integer,'
                'is_rp_article integer,'
                'url text,'
                'title text,'
                'reading_time integer,'
                'logo text)',

                'CREATE TABLE active_articles('
                'last_displayed_id integer PRIMARY KEY AUTOINCREMENT,'
                'article_id integer)',

                'CREATE TABLE reading_plans('
                'rp_id integer PRIMARY KEY AUTOINCREMENT,'
                'profile_id integer,'
                'rp_name text,'
                'rp_description text)',

                'CREATE TABLE reading_plan_topics('
                'rp_topic_id integer PRIMARY KEY AUTOINCREMENT,'
                'rp_id integer,'
                'rp_topic_text text)',

                'CREATE TABLE reading_plan_articles_topics('
                'rp_article_topic_id integer PRIMARY KEY AUTOINCREMENT,'
                'article_id integer,'
                'rp_topic_id integer)',
                ]
    return commands

  # returns True if table schema matches the default
  def _verify_table_schema(self):
    default_schema = self._default_table_commands()
    current_schema = pd.read_sql_query('SELECT * FROM sqlite_master', self._connection)['sql'].values
    current_schema = [table for table in current_schema if table != 'CREATE TABLE sqlite_sequence(name,seq)']

    if len(default_schema) != len(current_schema):
      return False

    for default_table, current_table in zip(default_schema, current_schema):
      if default_table != current_table:
        return False

    return True


  def describe_db(self):
    #self._cursor.execute('SELECT name FROM sqlite_master')

    print(pd.read_sql_query('SELECT * FROM sqlite_master', self._connection)['sql'].values)

  def __del__(self):
    self._connection.close()
