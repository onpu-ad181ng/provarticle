class Article:
  def __init__(self, url, name, topics, reading_time, history_manager, logo=None):
    self.url = url
    self.name = name
    self.topics = topics
    self.reading_time = reading_time
    self.history_manager = history_manager
    self.logo = logo

    # turns topics into a single line
    self.topics_text = ', '.join(self.topics)

  def read(self):
    self.history_manager.report_opened_article(self)

    # TODO: open browser upon article being read
