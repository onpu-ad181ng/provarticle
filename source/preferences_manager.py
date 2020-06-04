from PyQt5.QtWidgets import QTextEdit, QPushButton

from .profile import Profile
from .dao import DAO

class PreferencesManager:
  def __init__(self, dao: DAO, display_box, edit_box, apply_button):
    self._dao = dao
    self.profile = None # type: Profile
    self.display_box = display_box # type: QTextEdit
    self.edit_box = edit_box # type: QTextEdit
    self.apply_button = apply_button

    self.apply_button.pressed.connect(self._apply_topic_changes)


  def visualize_topics(self):
    topics = self._dao.get_topics_text(self.profile.profile_id)
    topics_text = ', '.join(topics)
    self.display_box.setText(topics_text)
    self.edit_box.setText(topics_text)


  def _apply_topic_changes(self):
    old_topics = self._dao.get_topics_text(self.profile.profile_id)

    new_topics = self.edit_box.toPlainText()
    new_topics = new_topics.split(',')
    new_topics = [topic.strip() for topic in new_topics]

    deleted_topics = [topic for topic in old_topics if topic not in new_topics]
    added_topics = [topic for topic in new_topics if topic not in old_topics]

    for topic in deleted_topics:
      self._dao.delete_topic_by_text(topic)
    for topic in added_topics:
      self._dao.add_topic(self.profile.profile_id, topic)

    self.visualize_topics()
