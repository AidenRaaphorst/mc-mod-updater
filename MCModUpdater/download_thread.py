import logging
import requests

from PyQt5 import QtCore
from PyQt5.QtWidgets import *

from MCModUpdater import utils


class DownloadThread(QtCore.QThread):
    update_progress = QtCore.pyqtSignal()
    hide_progress = QtCore.pyqtSignal()
    done = QtCore.pyqtSignal()

    def __init__(self, mod_widgets, mod_folder):
        super().__init__()

        self.mod_widgets = mod_widgets
        self.mod_folder = mod_folder

    def run(self):
        logging.info("Downloading mods...")
        for i, widget in enumerate(self.mod_widgets):
            mod_url = widget.findChild(QLabel, 'modURL').text()
            file_name = utils.get_file_name_from_url(mod_url)

            logging.info(f"Downloading '{file_name}'")

            try:
                utils.download_file_from_url(url=mod_url, directory=self.mod_folder)
            except requests.exceptions.ConnectionError:
                logging.error(f"Could not download '{file_name}', no internet connection or server is not responding")
            self.update_progress.emit()

        self.hide_progress.emit()
        logging.info("Done\n")

        self.done.emit()
