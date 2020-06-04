class Article:
  def __init__(self, article_id, rp_id, profile_id, is_rp,
               url, name, reading_time, logo=None):
    self.article_id = article_id
    self.rp_id = rp_id
    self.profile_id = profile_id
    self.is_rp = is_rp
    self.url = url
    self.name = name
    self.reading_time = reading_time
    self.logo = logo
