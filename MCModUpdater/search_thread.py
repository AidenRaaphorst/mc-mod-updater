import httpx
import asyncio
import logging

import requests
from PyQt5 import QtCore

from MCModUpdater import utils
from MCModUpdater import modrinth
from MCModUpdater import curseforge
from MCModUpdater.resources import constants


class SearchThread(QtCore.QThread):
    update_progress = QtCore.pyqtSignal()
    done = QtCore.pyqtSignal()
    cancelled = QtCore.pyqtSignal()
    append_failed_mod = QtCore.pyqtSignal(str)
    show_failed_mods = QtCore.pyqtSignal()
    make_and_append_mod_widget = QtCore.pyqtSignal(str, str, str, bytes, bool)

    _gather = asyncio.gather()

    def __init__(self, mod_urls, mc_version, curseforge_mod_loader_type, modrinth_mod_loader):
        super().__init__()
        self.mod_urls = mod_urls
        self.mc_version = mc_version
        self.curseforge_mod_loader_type = curseforge_mod_loader_type
        self.modrinth_mod_loader = modrinth_mod_loader

    def run(self):
        async def get_mods(urls: list[str]):
            async def handle_response_curseforge(response: httpx.Response, mod):
                url = response.request.url.__str__()
                slug = url.split("&slug=")[1]

                if mod is None:
                    logging.error(f"Couldn't find mod '{slug}' using CurseForge")
                    self.append_failed_mod.emit(f"{constants.CF_BASE_MOD_URL}/{slug}")
                    self.update_progress.emit()
                    return

                file = await curseforge.get_latest_mod_file_async(
                    mod_id=mod['id'],
                    game_version=self.mc_version,
                    mod_loader_type=self.curseforge_mod_loader_type
                )

                if file is None:
                    logging.error(f"Couldn't find correct file for '{slug}' using CurseForge")
                    self.append_failed_mod.emit(f"{constants.CF_BASE_MOD_URL}/{slug}")
                    self.update_progress.emit()
                    return

                if file['downloadUrl'] is None:
                    logging.error(f"Couldn't find file URL for '{slug}' using CurseForge")
                    self.append_failed_mod.emit(f"{constants.CF_BASE_MOD_URL}/{slug}")
                    self.update_progress.emit()
                    return

                logging.info(f"Found file for '{slug}' using CurseForge")
                mod_name = mod['name']
                mod_logo_url = mod['logo']['thumbnailUrl']
                file_url = file['downloadUrl']

                self.make_and_append_mod_widget.emit(
                    mod_name,
                    file_url,
                    f"File: {utils.get_file_name_from_url(file_url)}\n"
                    f"Source: CurseForge",
                    requests.get(mod_logo_url).content,
                    True
                )
                self.update_progress.emit()

            async def handle_response_modrinth(response: httpx.Response, mod):
                url = response.request.url.__str__()
                slug = url.split('/')[-1]

                if mod is None:
                    logging.error(f"Couldn't find mod '{slug}' using Modrinth")
                    self.append_failed_mod.emit(f"{constants.MR_BASE_MOD_URL}/{slug}")
                    self.update_progress.emit()
                    return

                file = await modrinth.get_latest_mod_file_async(
                    mod_slug=mod['slug'],
                    game_version=self.mc_version,
                    mod_loader=self.modrinth_mod_loader
                )

                if file is None:
                    logging.error(f"Couldn't find correct file for '{slug}' using Modrinth")
                    self.append_failed_mod.emit(f"{constants.MR_BASE_MOD_URL}/{slug}")
                    self.update_progress.emit()
                    return

                logging.info(f"Found file for '{slug}' using Modrinth")
                mod_name = mod['title']
                mod_logo_url = mod['icon_url']
                file_url = file['files'][0]['url']

                self.make_and_append_mod_widget.emit(
                    mod_name,
                    file_url,
                    f"File: {utils.get_file_name_from_url(file_url)}\n"
                    f"Source: Modrinth",
                    requests.get(mod_logo_url).content,
                    True
                )
                self.update_progress.emit()

            tasks = []
            for url in urls:
                slug = utils.get_slug_from_url(url)
                if constants.CF_BASE_MOD_URL in url:
                    if not curseforge.get_api_key():
                        logging.error(f"Cannot search for '{url}' because API key is not set")
                        self.append_failed_mod.emit(f"{constants.CF_BASE_MOD_URL}/{slug}")
                        self.update_progress.emit()
                        continue

                    logging.info(f"Looking for '{slug}' using Curseforge")
                    tasks.append(curseforge.get_mod_from_slug_async(
                        slug=slug,
                        after_response_funcs=[handle_response_curseforge]
                    ))
                elif constants.MR_BASE_MOD_URL in url:
                    logging.info(f"Looking for '{slug}' using Modrinth")
                    tasks.append(modrinth.get_mod_from_slug_async(
                        mod_slug=slug,
                        after_response_funcs=[handle_response_modrinth]
                    ))
                else:
                    logging.error(f"URL '{url}' is not supported")
                    self.append_failed_mod.emit(url)
                    self.update_progress.emit()

            self._gather = asyncio.gather(*tasks)
            return await self._gather

        try:
            asyncio.run(get_mods(self.mod_urls))
        except asyncio.exceptions.CancelledError:
            self.cancelled.emit()
            return

        self.done.emit()
        self.show_failed_mods.emit()

    def stop(self):
        self._gather.get_loop().cancel()
