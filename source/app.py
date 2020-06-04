from PyQt5 import QtWidgets, QtGui

from PyQt5.QtCore import QSize, Qt, pyqtSlot
from PyQt5.QtWidgets import (QFileDialog, QGraphicsPixmapItem, QTableWidgetItem, QGraphicsScene, QDialogButtonBox,
               QLabel, QMainWindow, QPushButton, QDialog, QListWidget, QMessageBox, QVBoxLayout, QFrame)
from PyQt5.uic import loadUi

from .dao import DAO
from .profile_manager import ProfileManager
from .article_manager import ArticleManager
from .recomender import Recomender

from .ui_functions import *

class App(QMainWindow):

  def __init__(self):
    QMainWindow.__init__(self)
    self._init_ui()

    #try:
    self._create_managers()
    #except Exception as e:
    #  self._give_up_and_die(e)
    #  self.close()

    self._init_profile()

    self._update_active_articles()




  def _create_managers(self):
    self._dao = DAO()
    self._dao.connect_to_db(always_init_db=True, init_with_test=True)

    self._recommender = Recomender(None)
    self._article_manager = ArticleManager(self._dao,
                                           self.today_recommended_layout,
                                           self.today_reading_time,
                                           self.next_recommended_layout,
                                           self.next_reading_time,
                                           self.recomend_button,
                                           self._recommender)
    self._profile_manager = ProfileManager(self._dao, self.profiles_layout, self._article_manager,
                                           self.profile_name, self.profile_desc, self.profile_box,
                                           self.update_button)


  def _update_active_articles(self):
    self._article_manager.draw_articles()
    self._profile_manager.draw_profiles()


  def _init_profile(self):
    self._profile = self._profile_manager.initialize_profile()

    self._article_manager.profile = self._profile


  def _give_up_and_die(self, why):
    print('i died because', why)
    exit(-1)
    pass


  def _init_ui(self):
    loadUi('ui.ui', self)

    self.today_recommended_layout = QVBoxLayout()
    self.today_widget = QFrame()
    #self.today_widget.setStyleSheet("border:1px solid rgb(0, 0, 0);")
    self.today_widget.setLayout(self.today_recommended_layout)
    self.today_recommended_scroller.setWidget(self.today_widget)

    self.next_recommended_layout = QVBoxLayout()
    self.next_widget = QWidget()
    self.next_widget.setLayout(self.next_recommended_layout)
    self.next_recommended_scroller.setWidget(self.next_widget)

    self.profiles_layout = QVBoxLayout()
    self.profiles_widget = QFrame()
    self.profiles_widget.setLayout(self.profiles_layout)
    self.profiles_scroller.setWidget(self.profiles_widget)

