import sys
from PyQt5.QtWidgets import QApplication

from MCModUpdater.ui_thread import UI

# Initialize the app
app = QApplication(sys.argv)
UIWindow = UI()
app.exec_()
