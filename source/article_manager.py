import webbrowser
from datetime import datetime

from PyQt5.QtWidgets import (QLabel, QHBoxLayout, QPushButton, QWidget, QVBoxLayout,
                             QSpacerItem, QSizePolicy, QFrame)
from PyQt5 import QtCore

from .dao import DAO
from .article import Article
from .ui_functions import clear_layout, add_spacer, clear_widget, cutoff_string
from .recomender import Recomender

class ArticleManager:
  def __init__(self, dao: DAO, today_reading_layout, today_reading_time,
               later_reading_layout, later_reading_time, recomend_button,
               recommender: Recomender):
    self.profile = None
    self.articles = {} # maps article id's to article objects
    self.widgets = {} # maps article id's to widgets
    self.normal_articles = []
    self.rp_articles = []

    self._dao = dao
    self._recommender = recommender
    self._today_reading_layout = today_reading_layout
    self._today_reading_time = today_reading_time
    self._later_reading_layout = later_reading_layout
    self._later_reading_time = later_reading_time
    self._recomend_button = recomend_button

    self._recomend_button.pressed.connect(self.recommend_new)


  def draw_active_articles(self):
    self._load_active_articles()

    self.draw_normal_recomendations()


  def recommend_new(self, amount=3):
    interests = self._dao.get_interests(self.profile.profile_id)
    new_articles_data = self._recommender.get_recomendation_articles(interests)
    new_articles_data = self._filter_recomended_articles(new_articles_data)
    new_articles_data = new_articles_data[:amount]

    for data in new_articles_data:
      self._create_new_normal_article(data)
    self.draw_active_articles()


  def draw_normal_recomendations(self):
    today_limit = 15
    todays_articles, later_articles = self._split_today_and_later_articles(self.normal_articles,
                                                                           today_limit,
                                                                           sort=True)

    clear_layout(self._today_reading_layout)
    reading_time = 0
    for article in todays_articles:
      article_widget = self._draw_article(self._today_reading_layout, article)
      article_widget.mousePressEvent = lambda x: self._register_article_click(article.article_id)
      self.widgets[article.article_id] = article_widget
      reading_time += article.reading_time
    add_spacer(self._today_reading_layout)
    self._today_reading_time.setText('Approximate reading time: {} minutes'.format(reading_time))

    clear_layout(self._later_reading_layout)
    reading_time = 0
    for article in later_articles:
      article_widget = self._draw_article(self._later_reading_layout, article)
      article_widget.mousePressEvent = lambda x: self._register_article_click(article.article_id)
      self.widgets[article.article_id] = article_widget
      reading_time += article.reading_time
    add_spacer(self._later_reading_layout)
    self._later_reading_time.setText('Approximate reading time: {} minutes'.format(reading_time))


  def _filter_recomended_articles(self, data):
    active_articles = self._dao.get_active_articles(self.profile.profile_id)
    active_urls = [article_data['url'] for article_data in active_articles]
    filtered_non_active_articles = [article for article in data if article['url'] not in active_urls]

    read_articles = self._dao.get_read_articles(self.profile.profile_id)
    read_urls = [article_data['url'] for article_data in read_articles]

    filtered_non_read_articles = [article for article in filtered_non_active_articles
                                  if article['url'] not in read_urls]
    return filtered_non_read_articles



  def _create_new_normal_article(self, article_data):
    article_id = self._dao.create_new_article(0, self.profile.profile_id, False, article_data['url'],
                                              article_data['title'], article_data['reading_time'], '',
                                              datetime.now().strftime("%Y-%m-%d %I:%M"))



  def _split_today_and_later_articles(self, articles, minutes_limit, sort):
    if sort:
      articles.sort(key=lambda a: a.reading_time)

    # calculates where to split the articles
    cumulative_time = 0
    last_cumulative_time = 0
    split_index = 0
    for i, article in enumerate(self.normal_articles):
      last_cumulative_time = cumulative_time

      cumulative_time += article.reading_time
      split_index = i + 1

      if cumulative_time > minutes_limit:
        overshoot = cumulative_time - minutes_limit
        undershoot = minutes_limit - last_cumulative_time
        if overshoot > undershoot and last_cumulative_time != 0:
          split_index = split_index - 1
          break
        elif overshoot < undershoot:
          break
        #break

    todays = articles[:split_index]
    later = articles[split_index:]
    return todays, later


  # removes article, opens browser, considers to recommend more
  def _register_article_click(self, article_id):
    article = self.articles[article_id]
    self._mark_article_as_read(article_id, mark_as_read=True)
    webbrowser.open(article.url)

    self._decide_on_recomending()


  def _decide_on_recomending(self):
    # todo: make it actually decide
    self.recommend_new(2)


  def _load_active_articles(self):
    self.articles = {}
    self.widgets = {}
    self.normal_articles = []
    self.rp_articles = []
    articles_data = self._dao.get_active_articles(self.profile.profile_id)

    for article_data in articles_data:
      new_article = Article(*article_data.values())
      self.articles[new_article.article_id] = new_article

      if new_article.is_rp:
        self.rp_articles.append(new_article)
      else:
        self.normal_articles.append(new_article)


  def _mark_article_as_read(self, article_id, mark_as_read):
    clear_widget(self.widgets[article_id])

    self.articles.pop(article_id, None)
    self.widgets.pop(article_id, None)
    self.normal_articles = [a for a in self.normal_articles if a.article_id != article_id]
    self.rp_articles = [a for a in self.rp_articles if a.article_id != article_id]

    self._dao.delete_from_active_articles(article_id)
    if mark_as_read:
      self._dao.update_history_as_read(article_id, datetime.now().strftime("%Y-%m-%d %I:%M"))


  def _draw_article(self, layout, article: Article) -> QWidget:
    article_widget = QFrame()
    article_widget.setMinimumSize(400, 55)
    article_widget.setMaximumSize(400, 55)
    article_widget.setStyleSheet("QFrame {background-color: rgb(200,200,200);}")

    article_insides = QHBoxLayout()
    article_widget.setLayout(article_insides)

    title_and_url_layout = QVBoxLayout()

    title = QLabel(cutoff_string(article.name, 30))
    title.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
    title.setMaximumSize(200, 20)
    title.setMinimumSize(200, 20)
    title_and_url_layout.addWidget(title)

    url = QLabel(cutoff_string(article.url, 30))
    url.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
    url.setMaximumSize(200, 20)
    url.setMinimumSize(200, 20)
    title_and_url_layout.addWidget(url)

    title_and_url_layout.addSpacerItem(QSpacerItem(40, 40, QSizePolicy.MinimumExpanding))

    reading_time_layout = QVBoxLayout()
    add_spacer(reading_time_layout)
    read_time = QLabel("{} minutes".format(article.reading_time))
    read_time.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
    read_time.setMaximumSize(50, 15)
    read_time.setMinimumSize(50, 15)
    reading_time_layout.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
    reading_time_layout.addWidget(read_time)
    reading_time_layout.addSpacerItem(QSpacerItem(1, 40, QSizePolicy.MinimumExpanding))

    article_insides.addLayout(title_and_url_layout)
    article_insides.addLayout(reading_time_layout)

    layout.addWidget(article_widget)

    return article_widget


