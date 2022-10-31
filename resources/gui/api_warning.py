from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

import sys

import utils

QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)  # Enable highdpi scaling
QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)  # Use highdpi icons
QApplication.setAttribute(QtCore.Qt.AA_DisableWindowContextHelpButton, True)  # Disable Help button


class ApiWarningPopup(QDialog):
    def __init__(self):
        super(ApiWarningPopup, self).__init__()

        # Load ui file
        try:
            # loadUi("api-warning.ui", self)
            loadUi(utils.resource_path("api-warning.ui"), self)
        except Exception as e:
            # print(e)
            # loadUi("resources/gui/api-warning.ui", self)
            loadUi(utils.resource_path("resources/gui/api-warning.ui"), self)

        # Define widgets
        self._explanation_label = self.findChild(QLabel, "explanationLabel")
        self._api_input = self.findChild(QLineEdit, "apiInput")
        self._api_input.setFocus()
        self._button_box = self.findChild(QDialogButtonBox, "buttonBox")
        self._button_box.button(QDialogButtonBox.Save).clicked.connect(self._save)
        self._button_box.button(QDialogButtonBox.Ignore).clicked.connect(self._ignore)
        self._button_box.button(QDialogButtonBox.Close).clicked.connect(self._close)
        self._pressed_button_text = ''

        self._explanation_label.setOpenExternalLinks(True)

    def _save(self):
        # print("save")
        self._pressed_button_text = "Save"

    def _ignore(self):
        # print("ignore")
        self._pressed_button_text = "Ignore"

    def _close(self):
        # print("close")
        self._pressed_button_text = "Close"

    def get_response(self):
        return self._api_input.text(), self._pressed_button_text


if __name__ == '__main__':
    # Initialize the app
    app = QApplication(sys.argv)
    UIWindow = ApiWarningPopup()
    UIWindow.show()
    app.exec_()
