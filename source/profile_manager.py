from datetime import datetime

from .dao import DAO
from .profile import Profile

class ProfileManager:
  def __init__(self, dao: DAO):
    self.dao = dao
    self.profile = None

  def initialize_profile(self):
    profile_data = self.dao.get_last_profile()
    self.profile = Profile(*profile_data.values())

    # alter the 'last used' date
    date_now = datetime.now().strftime("%Y-%m-%d %I:%M")
    self.profile.date_last_used = date_now
    self.dao.update_profile_last_used_field(self.profile.profile_id,
                                            self.profile.date_last_used)

    return self.profile
