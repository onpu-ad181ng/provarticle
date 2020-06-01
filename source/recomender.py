import urllib as ulb
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests

from .text_extractor import TextExtractor
from .similar_topics_finder import SimilarTopicsFinder
from .article import Article

class Recomender:
  def __init__(self, history_manager, preferences_manager):
    self.history_manager = history_manager
    self.preferences_manager = preferences_manager

    self._text_extractor = TextExtractor()
    self._similar_topics_finder = SimilarTopicsFinder()

  def get_recomendation_articles(self, topics):
    all_topics = self._similar_topics_finder.add_similar_topics(topics, None)
    query = self._formulate_query(all_topics)
    search_items = self._request_search(query)
    filtered_items = self._filter_blacklisted(search_items)
    items_with_word_count = self._get_word_count(filtered_items)
    reordered_items = self._reorder_by_less_popular_topics(items_with_word_count)
    article_objects = self._create_article_objects(reordered_items)

  def _get_word_count(self, items):
    items_with_time = items
    for i in range(len(items_with_time)):
      url = items_with_time[i]['url']
      items_with_time[i]['reading_time'] = self._text_extractor.get_reading_time(url)
    return items_with_time

  def _reorder_by_less_popular_topics(self, items):
    return items

  def _create_article_objects(self, search_items):
    articles = []
    for item in search_items:
      article = Article(item['url'], item['title'], item['words'], item['reading_time'], self.history_manager)
      articles.append(article)
    return articles

  def _formulate_query(self, topics):
    quoted_topics = ['"' + topic + '"' for topic in topics]
    query_with_ors = ' OR '.join(quoted_topics)
    query = query_with_ors + ' guide'
    return query

  def _request_search(self, query, pages=1):
    """Returns list of search result items based on query

    :param query: search query, example: ""unity" OR "Unreal engine" guide"
    :param pages: amount of pages to search for
    :return: list of search result items (in dicts)
    """

    query = query.replace(' ', '+')
    url = 'https://google.com/search?q={}'.format(query)

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"

    headers = {'user-agent': user_agent}
    resp = requests.get(url, headers=headers)

    if resp.status_code == 200:
      soup = BeautifulSoup(resp.content, "html.parser")
    else:
      raise Exception("Something's fucky")

    items = []

    for result in soup.find_all('div', class_='rc'):
      anchors = result.find_all('a')
      if anchors:
        link = anchors[0]['href']
        title = result.find('h3').text

        topic_words = list({topic.text.lower() for topic in result.find_all('em')})

        item = {
          'title': title,
          'url': link,
          'topics': topic_words
        }
        items.append(item)
      else:
        raise Exception('No anchor to extract text from')

    return items

  def _filter_blacklisted(self, search_results):
    # TODO: remove empty list as the default blacklisted list
    blacklisted = self.preferences_manager.get_blacklisted()
    blacklisted = []

    filtered_results = [item for item in search_results if item['url'] not in blacklisted]

    return filtered_results
