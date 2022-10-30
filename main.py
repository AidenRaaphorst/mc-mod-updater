import os
import sys
import time
import json
import shutil
import asyncio
import pathlib
import platform
from dotenv import load_dotenv

import httpx
import requests
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *

import utils
import modrinth
import curseforge
from resources.gui.failed_mods import FailedModsPopup
from resources.gui.api_warning import ApiWarningPopup


QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)  # Enable highdpi scaling
QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)  # Use highdpi icons


class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()

        self.mod_index = 0
        self.downloadable_mod_widgets: list[QWidget] = []
        self.failed_mods: list[str] = []
        self.api_warning_ignore = False

        # Load ui file
        loadUi("resources/gui/main.ui", self)

        # Define widgets
        self.folder_input: QLineEdit = self.findChild(QLineEdit, "folderInput")
        self.folder_button: QPushButton = self.findChild(QPushButton, "folderButton")
        self.mc_version_input = self.findChild(QLineEdit, "versionInput")
        self.modloader_input = self.findChild(QComboBox, "modloaderOptions")
        self.backup_mods_checkbox: QCheckBox = self.findChild(QCheckBox, "backupCheckBox")
        self.mods_text_edit: QPlainTextEdit = self.findChild(QPlainTextEdit, "modsTextEdit")
        self.search_mods_button: QPushButton = self.findChild(QPushButton, "searchModsButton")
        self.download_mods_button: QPushButton = self.findChild(QPushButton, "downloadModsButton")
        self.scroll_area_widget_contents: QWidget = self.findChild(QWidget, "scrollAreaWidgetContents")
        self.vertical_layout: QVBoxLayout = self.findChild(QVBoxLayout, "verticalLayout")
        self.progress_bar = self.findChild(QProgressBar, "progressBar")

        # Hide/delete example widgets
        self.findChild(QWidget, "modWidgetExample").deleteLater()
        self.progress_bar.hide()

        # Setup for getting mods folder
        self.folder_input.setText(self.get_folder_location(return_default=True))
        self.folder_button.clicked.connect(self.get_folder_location)
        # self.folder_button.clicked.connect(self.debug_create_mod)  # Debug

        # Setup for searching for mods online
        self.search_mods_button.clicked.connect(self.search_online)
        self.mods_text_edit.setPlaceholderText(
            "Mod URL's here, example:\n"
            "https://www.curseforge.com/minecraft/mc-mods/fabric-api\n"
            "https://modrinth.com/mod/sodium\n"
            "https://modrinth.com/mod/sodium-extra\n"
            "https://www.curseforge.com/minecraft/mc-mods/controlling"
        )
        self.mods_text_edit.setPlainText("")

        # Setup for download mods
        self.download_mods_button.clicked.connect(self.download_mods)

        # Misc
        self.mc_version_input.setFocus()
        self.vertical_layout.setAlignment(QtCore.Qt.AlignTop)

        # Settings
        load_dotenv()
        if os.path.exists('settings.json'):
            self.load_settings()

        # Show the app
        self.show()

        # Load CurseForge API key, if it doesn't exist, show popup
        if os.path.exists(".env"):
            curseforge.set_api_key(os.getenv("CURSEFORGE_API_KEY"))
        elif not os.path.exists(".env") and not self.api_warning_ignore:
            self.api_popup = ApiWarningPopup()
            self.api_popup.exec_()

            api_key, button_text = self.api_popup.get_response()

            if button_text == "Save":
                if not api_key == "":
                    with open('.env', 'w') as f:
                        f.write(f"CURSEFORGE_API_KEY={api_key}")
                    curseforge.set_api_key(api_key)
                self.api_warning_ignore = True
            elif button_text == "Ignore":
                self.api_warning_ignore = True

    def get_folder_location(self, return_default=False):
        if return_default:
            system = platform.system()
            if system == "Windows":
                return os.path.expanduser(r"~\AppData\Roaming\.minecraft\mods").replace("\\", "/")
            elif system == "Linux":
                return os.path.expanduser("~/.minecraft/mods")
            elif system == "Darwin":
                return os.path.expanduser("~/Library/Application Support/minecraft/mods")
            else:
                return ""

        previous = self.folder_input.text()
        directory = str(QFileDialog.getExistingDirectory(
            self,
            caption="Select the directory where the mods are stored",
            directory=self.folder_input.text()
        ))

        if directory == "":
            directory = previous

        print(f"\nChanged directory from '{previous}' to '{directory}'")
        self.folder_input.setText(directory)
    
    def make_mod_widget(self, name: str = None, file_url: str = None, details: str = None, logo_url: str=None):
        if not name:
            name = "TESTING"

        if not file_url:
            file_url = "https://some.website.com/this-is-a-mod.jar"

        if not details:
            details = f"File: mod{self.mod_index}\n"\
                      f"Source: this is a test"

        if not logo_url:
            mod_icon = QtGui.QPixmap("resources/img/no-icon.png")
        else:
            data = requests.get(logo_url).content
            mod_icon = QtGui.QPixmap()
            mod_icon.loadFromData(data)

        title_font = QtGui.QFont()
        title_font.setFamily("Segoe UI")
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_font.setWeight(75)

        text_font = QtGui.QFont()
        text_font.setFamily("Segoe UI")
        text_font.setPointSize(9)
        text_font.setBold(False)
        text_font.setWeight(50)

        delete_icon = QtGui.QIcon()
        delete_icon.addPixmap(QtGui.QPixmap("resources/img/trash.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.mod_index += 1

        # Widget
        mod_widget = QWidget(self.scroll_area_widget_contents)
        mod_widget.setMinimumSize(QtCore.QSize(0, 80))
        mod_widget.setMaximumSize(QtCore.QSize(470, 80))
        mod_widget.setObjectName("modWidget")

        # Logo
        mod_logo = QLabel(mod_widget)
        mod_logo.setObjectName("modIcon")
        mod_logo.setGeometry(QtCore.QRect(10, 10, 61, 61))
        mod_logo.setPixmap(mod_icon)
        mod_logo.setScaledContents(True)
        mod_logo.setAlignment(QtCore.Qt.AlignCenter)

        # Mod name
        mod_name_label = QLabel(mod_widget)
        mod_name_label.setObjectName("modName")
        mod_name_label.setGeometry(QtCore.QRect(80, 10, 291, 21))
        mod_name_label.setFont(title_font)
        mod_name_label.setText(name)

        # Filename and source
        mod_details = QLabel(mod_widget)
        mod_details.setObjectName("modDetails")
        mod_details.setGeometry(QtCore.QRect(80, 30, 321, 41))
        mod_details.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        mod_details.setFont(text_font)
        mod_details.setText(details)

        # Mod URL
        file_url_label = QLabel(mod_widget)
        file_url_label.setObjectName("modURL")
        file_url_label.setGeometry(QtCore.QRect(80, 60, 321, 21))
        file_url_label.setText(file_url)
        file_url_label.hide()

        # Delete button
        delete_button = QPushButton(mod_widget)
        delete_button.setObjectName("deleteButton")
        delete_button.setGeometry(QtCore.QRect(410, 20, 41, 41))
        delete_button.clicked.connect(lambda: mod_widget.deleteLater())
        delete_button.setIcon(delete_icon)
        delete_button.setIconSize(QtCore.QSize(32, 32))

        # Add to temp list
        # self.downloadable_mod_widgets.append(mod_widget)
        return mod_widget

    def search_online(self):
        print("\nSearching for mods...")

        # Reset arrays and remove old mod results
        self.downloadable_mod_widgets = []
        self.failed_mods = []
        for widget in self.scroll_area_widget_contents.findChildren(QWidget, "modWidget"):
            widget.deleteLater()

        # Get mod URLs from text box and filter out comments
        mod_urls = self.mods_text_edit.toPlainText().strip().split("\n")
        for mod_url in mod_urls:
            if mod_url.startswith("# "):
                mod_urls.remove(mod_url)

        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(mod_urls))
        self.progress_bar.show()

        mc_version = self.mc_version_input.text()
        modrinth_mod_loader = self.modloader_input.currentText().lower()
        if modrinth_mod_loader == "any":
            curseforge_mod_loader_type = 0
        elif modrinth_mod_loader == "fabric":
            curseforge_mod_loader_type = 4
        elif modrinth_mod_loader == "forge":
            curseforge_mod_loader_type = 1
        elif modrinth_mod_loader == "quilt":
            curseforge_mod_loader_type = 5
        elif modrinth_mod_loader == "liteloader":
            curseforge_mod_loader_type = 3
        elif modrinth_mod_loader == "cauldron":
            curseforge_mod_loader_type = 2

        async def get_mods(urls: list[str]):
            async def handle_response_curseforge(response: httpx.Response, mod):
                url = response.request.url.__str__()
                slug = url.split("&slug=")[1]

                if mod is None:
                    print(f"Couldn't find mod '{slug}'")
                    self.failed_mods.append(f"c {slug}")
                    self.progress_bar.setValue(self.progress_bar.value() + 1)
                    return

                file = await curseforge.get_latest_mod_file_async(
                    mod_id=mod['id'],
                    game_version=mc_version,
                    mod_loader_type=curseforge_mod_loader_type
                )

                if file is None:
                    print(f"Couldn't find correct file for '{slug}'")
                    # print(f"Couldn't find file URL for '{slug}'")
                    self.failed_mods.append(f"c {slug}")
                    self.progress_bar.setValue(self.progress_bar.value() + 1)
                    return

                if file['downloadUrl'] is None:
                    print(f"Couldn't find file URL for '{slug}'")
                    self.failed_mods.append(f"c {slug}")
                    self.progress_bar.setValue(self.progress_bar.value() + 1)
                    return

                print(f"Found file for '{slug}'")
                mod_name = mod['name']
                mod_logo_url = mod['logo']['thumbnailUrl']
                file_url = file['downloadUrl']
                widget = self.make_mod_widget(
                    name=mod_name,
                    file_url=file_url,
                    details=f"File: {utils.get_file_name_from_url(file_url)}\n"
                            f"Source: CurseForge",
                    logo_url=mod_logo_url
                )
                self.downloadable_mod_widgets.append(widget)
                self.progress_bar.setValue(self.progress_bar.value() + 1)

            async def handle_response_modrinth(response: httpx.Response, mod):
                url = response.request.url.__str__()
                slug = url.split('/')[-1]

                if mod is None:
                    print(f"Couldn't find mod '{slug}'")
                    self.failed_mods.append(f"m {slug}")
                    self.progress_bar.setValue(self.progress_bar.value() + 1)
                    return

                file = await modrinth.get_latest_mod_file_async(
                    mod_slug=mod['slug'],
                    game_version=mc_version,
                    mod_loader=modrinth_mod_loader
                )

                if file is None:
                    print(f"Couldn't find correct file for '{slug}'")
                    # print(f"Couldn't find file URL for '{slug}'")
                    self.failed_mods.append(f"m {slug}")
                    self.progress_bar.setValue(self.progress_bar.value() + 1)
                    return

                print(f"Found file '{file['files'][0]['filename']}'")
                mod_name = mod['title']
                mod_logo_url = mod['icon_url']
                file_url = file['files'][0]['url']
                widget = self.make_mod_widget(
                    name=mod_name,
                    file_url=file_url,
                    details=f"File: {utils.get_file_name_from_url(file_url)}\n"
                            f"Source: Modrinth",
                    logo_url=mod_logo_url
                )
                self.downloadable_mod_widgets.append(widget)
                self.progress_bar.setValue(self.progress_bar.value() + 1)

            tasks = []
            for url in urls:
                slug = utils.get_slug_from_url(url)
                if "curseforge.com/minecraft/mc-mods/" in url:
                    if curseforge.get_api_key() == "":
                        print(f"Cannot search for '{url}' because API key is not set")
                        self.failed_mods.append(f"c {slug}")
                        continue

                    print(f"Looking for '{slug}' using Curseforge")
                    tasks.append(curseforge.get_mod_from_slug_async(
                        slug=slug,
                        after_response_funcs=[handle_response_curseforge]
                    ))
                elif "modrinth.com/mod/" in url:
                    print(f"Looking for '{slug}' using Modrinth")
                    tasks.append(modrinth.get_mod_from_slug_async(
                        mod_slug=slug,
                        after_response_funcs=[handle_response_modrinth]
                    ))
                else:
                    print(f"URL '{url}' is not supported")
                    self.failed_mods.append(url)

            return await asyncio.gather(*tasks)
        asyncio.run(get_mods(mod_urls))
        self.progress_bar.hide()

        self.downloadable_mod_widgets.sort(key=lambda widget: widget.findChild(QLabel, "modName").text())
        for widget in self.downloadable_mod_widgets:
            self.vertical_layout.addWidget(widget, alignment=QtCore.Qt.AlignTop)

        if self.failed_mods:
            print("Creating popup showing what mods failed")
            urls: list[str] = []
            for mod in self.failed_mods:
                mod: str = mod
                if mod.startswith("c "):
                    slug = mod.removeprefix("c ")
                    url = f"https://www.curseforge.com/minecraft/mc-mods/{slug}"
                    urls.append(url)
                    continue

                if mod.startswith("m "):
                    slug = mod.removeprefix("m ")
                    url = f"https://modrinth.com/mod/{slug}"
                    urls.append(url)
                    continue

                urls.append(mod)
            urls.sort(key=lambda url: utils.get_slug_from_url(url))

            self.failed_mods_popup = FailedModsPopup()
            self.failed_mods_popup.set_mod_urls(urls)
            self.failed_mods_popup.exec_()

        print("Done")

    def download_mods(self):
        print("\nDownloading mods...")
        make_backup: bool = self.backup_mods_checkbox.isChecked()
        mod_folder = self.folder_input.text()

        if not make_backup:
            print("Not making backup, because checkbox is not checked")
        else:
            print("Making backup")
            new_folder = "Backup " + time.strftime("%Y-%m-%d %H.%M.%S", time.localtime())
            if not os.path.exists(mod_folder):
                print("Mods folder not found, creating it")
                pathlib.Path(mod_folder).mkdir(parents=True, exist_ok=True)

            if any(f.endswith(".jar") for f in os.listdir(mod_folder)):
                os.mkdir(os.path.join(mod_folder, new_folder))

                print(f"Moving old mods to backup folder named '{new_folder}'...")

                for file in os.listdir(mod_folder):
                    if os.path.isdir(file):
                        continue

                    if not file.endswith(".jar"):
                        continue

                    print(f"Moving '{file}' to '{new_folder}'")

                    src_path = fr"{mod_folder}\{file}"
                    dst_path = fr"{mod_folder}\{new_folder}\{file}"
                    shutil.move(src_path, dst_path)
            print("Done moving old mods")

        mod_widgets = self.scroll_area_widget_contents.findChildren(QWidget, "modWidget")
        mod_widgets.sort(key=lambda widget: widget.findChild(QLabel, "modName").text())
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(mod_widgets))
        self.progress_bar.show()
        for i, widget in enumerate(mod_widgets):
            mod_url = widget.findChild(QLabel, 'modURL').text()
            file_name = utils.get_file_name_from_url(mod_url)
            print(f"Downloading '{file_name}'")
            utils.download_file_from_url(url=mod_url, directory=mod_folder)
            self.progress_bar.setValue(self.progress_bar.value() + 1)

        self.progress_bar.hide()
        print("Done")

    def debug_create_mod(self):
        widget = self.make_mod_widget()
        self.vertical_layout.addWidget(widget, alignment=QtCore.Qt.AlignTop)

    def debug_failed_mods_popup(self):
        self.popup = ApiWarningPopup()
        self.popup.exec_()
        # print(self.popup.get_api_input())

    def save_settings(self):
        print("Saving settings")
        with open('settings.json', 'w') as f:
            data = {
                "mods_folder": self.folder_input.text(),
                "mc_version": self.mc_version_input.text(),
                "modloader": self.modloader_input.currentText(),
                "backup_mods": self.backup_mods_checkbox.isChecked(),
                "api_warning_ignore": self.api_warning_ignore,
                "mod_urls": self.mods_text_edit.toPlainText().split("\n")
            }
            json.dump(data, f, indent=4)

        print("Done")

    def load_settings(self):
        print("Loading settings")
        with open('settings.json') as f:
            data = json.load(f)
            self.folder_input.setText(data['mods_folder'])
            self.mc_version_input.setText(data['mc_version'])
            self.modloader_input.setCurrentText(data['modloader'])
            self.backup_mods_checkbox.setChecked(data['backup_mods'])
            self.api_warning_ignore = data['api_warning_ignore']
            self.mods_text_edit.setPlainText("\n".join(data['mod_urls']))

        print("Done")

    def closeEvent(self, *args, **kwargs):
        self.save_settings()
        super(QMainWindow, self).closeEvent(*args, **kwargs)


if __name__ == '__main__':
    # Initialize the app
    app = QApplication(sys.argv)
    UIWindow = UI()
    app.exec_()
