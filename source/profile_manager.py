from datetime import datetime

from PyQt5.QtWidgets import (QLabel, QHBoxLayout, QPushButton, QWidget, QVBoxLayout,
                             QSpacerItem, QSizePolicy, QFrame)
from PyQt5 import QtCore

from .article_manager import ArticleManager
from .dao import DAO
from .profile import Profile
from .ui_functions import clear_layout, clear_widget, add_spacer, cutoff_string

class ProfileManager:
  def __init__(self, dao: DAO, profiles_layout, article_manager: ArticleManager,
               profile_name_text, profile_desc_text, profile_select_box,
               update_button):
    self._dao = dao
    self.profile = Profile(None, None, None, None, None)
    self._article_manager = article_manager
    self._profiles_layout = profiles_layout
    self._profile_name_text = profile_name_text
    self._profile_desc_text = profile_desc_text
    self._profile_select_box = profile_select_box

    self._update_button = update_button
    self._update_button.pressed.connect(self._update_or_create_profile)


  def draw_profiles(self):
    profiles_data = self._dao.get_profiles()
    profiles = [Profile(**data) for data in profiles_data]

    clear_layout(self._profiles_layout)
    for drawn_profile in profiles:
      profile_widget = self._draw_profile(drawn_profile,
                                          drawn_profile.profile_id == self.profile.profile_id,
                                          self._profiles_layout)
      print(drawn_profile.profile_id)
      profile_widget.mousePressEvent = lambda x: self._switch_profiles(int(drawn_profile.profile_id))
    add_spacer(self._profiles_layout)

    self._write_profile_info()

    pass


  def _update_or_create_profile(self):
    entered_name = self._profile_name_text.text()
    desc = self._profile_desc_text.toPlainText()

    # update if exists, create new if does not
    if self._dao.does_profile_name_exist(entered_name):
      self._dao.update_profile(self.profile.name, entered_name, desc)
    else:
      self._dao.create_profile(entered_name, desc, datetime.now().strftime("%Y-%m-%d %I:%M"))

    self.initialize_profile()
    self.draw_profiles()


  def _write_profile_info(self):
    self._profile_name_text.setText(self.profile.name)
    self._profile_desc_text.setPlainText(self.profile.description)
    self._write_selection_box(self.profile.name)


  def _write_selection_box(self, selected_profile_name):
    items_list = ['None']
    profile_names = [data['name'] for data in self._dao.get_profiles()]

    selected_index = 0
    for i, name in enumerate(profile_names):
      if name == selected_profile_name:
        selected_index = i
        break

    items_list = profile_names + items_list
    self._profile_select_box.clear()
    self._profile_select_box.addItems(items_list)
    self._profile_select_box.setCurrentIndex(selected_index)


  def _switch_profiles(self, profile_id):
    print(profile_id)
    new_profile_data = self._dao.get_profile(profile_id)
    self._load_profile_from_data(new_profile_data)
    self.draw_profiles()
    self._article_manager.draw_articles()


  def _draw_profile(self, profile, is_selected, layout):
    profile_widget = QFrame()
    profile_widget.setMinimumSize(400, 55)
    profile_widget.setMaximumSize(400, 55)
    if is_selected:
      profile_widget.setStyleSheet("QFrame {background-color: rgb(200,200,255);}")
    else:
      profile_widget.setStyleSheet("QFrame {background-color: rgb(200,200,200);}")

    profile_insides = QHBoxLayout()
    profile_widget.setLayout(profile_insides)

    title_and_description_layout = QVBoxLayout()

    title = QLabel(cutoff_string(profile.name, 30))
    title.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
    title.setMaximumSize(200, 20)
    title.setMinimumSize(200, 20)
    title_and_description_layout.addWidget(title)

    desc = QLabel(cutoff_string(profile.description, 50))
    desc.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
    desc.setMaximumSize(350, 20)
    desc.setMinimumSize(350, 20)
    title_and_description_layout.addWidget(desc)

    title_and_description_layout.addSpacerItem(QSpacerItem(40, 40, QSizePolicy.MinimumExpanding))

    profile_insides.addLayout(title_and_description_layout)

    layout.addWidget(profile_widget)

    return profile_widget


  def _load_profile_from_data(self, profile_data):
    self.profile.profile_id = profile_data['profile_id']
    self.profile.name = profile_data['name']
    self.profile.description = profile_data['description']
    self.profile.date_created = profile_data['date_created']
    self.profile.date_last_used = profile_data['date_last_used']

    # alter the 'last used' date
    date_now = datetime.now().strftime("%Y-%m-%d %I:%M")
    self.profile.date_last_used = date_now
    self._dao.update_profile_last_used_field(self.profile.profile_id,
                                             self.profile.date_last_used)


  def initialize_profile(self):
    profile_data = self._dao.get_last_profile()
    self._load_profile_from_data(profile_data)
    return self.profile
