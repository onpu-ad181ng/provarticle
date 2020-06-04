import sys

from PyQt5 import QtWidgets

from source.app import App

app = QtWidgets.QApplication(sys.argv)

mainWin = App()
mainWin.show()

app.exec_()
del app
