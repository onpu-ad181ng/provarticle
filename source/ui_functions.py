import numpy as np

from PyQt5.QtWidgets import (QLabel, QHBoxLayout, QPushButton, QWidget, QVBoxLayout,
                             QSpacerItem, QSizePolicy, QFrame, QLayoutItem, QBoxLayout)
from PyQt5.Qt import QSizePolicy


def clear_layout(layout: QLayoutItem):
  if layout is None:
    return
  if layout.isEmpty():
    return

  while layout.count():
    item = layout.takeAt(0)
    widget = item.widget()
    if widget is not None:
      widget.setParent(None)
    else:
      clear_layout(item.layout())


def cutoff_string(string, max_length):
  if len(string) <= max_length:
    return string

  string = string[:max_length] + '...'
  return string



def clear_widget(widget: QWidget):
  widget.setParent(None)


def add_spacer(layout: QBoxLayout):
  layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding))


def test_fill_scroll(window, entries_count):
  layout = window.today_recommended_layout

  #clear_layout(layout)

  for i in range(entries_count):
    draw_article(layout, i)

