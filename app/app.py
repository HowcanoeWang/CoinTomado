import sys
from sqlalchemy import create_engine

from PyQt5.QtWidgets import QApplication

from models import *
from gui import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.showMaximized()

sys.exit(app.exec_())