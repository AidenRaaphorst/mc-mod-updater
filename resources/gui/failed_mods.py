from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

import sys

QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)  # Enable highdpi scaling
QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)  # Use highdpi icons
QApplication.setAttribute(QtCore.Qt.AA_DisableWindowContextHelpButton, True)  # Disable Help button


class FailedModsPopup(QDialog):
    def __init__(self):
        super(FailedModsPopup, self).__init__()

        # Load ui file
        try:
            loadUi("failed-mods.ui", self)
        except Exception as e:
            # print(e)
            loadUi("resources/gui/failed-mods.ui", self)

        # Define widgets
        self._mods_label = self.findChild(QLabel, "modsLabel")

        self._mods_label.setTextFormat(QtCore.Qt.RichText)
        self._mods_label.setOpenExternalLinks(True)

    def set_mod_urls(self, mod_urls: list):
        mod_urls = map(lambda url: f'<a href="{url}">{url}</a>', mod_urls)
        # for url in mod_urls:
        #     url = f'<a href="{url}">{url}</a>'

        self._mods_label.setText("<br>".join(mod_urls))


if __name__ == '__main__':
    # Initialize the app
    app = QApplication(sys.argv)
    UIWindow = FailedModsPopup()
    UIWindow.show()
    app.exec_()
