import json
import os
import typing
import httpx
import requests
from dotenv import load_dotenv  # If not installed, run: pip install python-dotenv

import utils


class ModNotFoundException(Exception):
    """
    Exception raised when a mod is not found.

    Attributes:
        mod -- mod which caused the error
        message -- explanation of the error
    """

    def __init__(self, mod, message="Mod was not found"):
        self.mod = mod
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"'{self.mod}' -> {self.message}"


class ModVersionNotFoundException(Exception):
    """
    Exception raised when a game version of a mod is not found.

    Attributes:
        version -- version of mod which caused the error
        message -- explanation of the error
    """

    def __init__(self, version, message=f"Version of mod was not found"):
        self.version = version
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"'{self.version}' -> {self.message}"


def get_api_key():
    if not os.path.exists('.env'):
        utils.clear()
        print("It appears that this is the first time you have executed this program.")
        print("In order to download mods from CurseForge, you'll need an API key.")
        print("To get an api key, go to this link 'https://console.curseforge.com/' and create/login into your account.")
        print("After getting into your account, go to the tab 'API keys' on the left and copy the key.")
        key = input("\nInsert API key here: ")

        with open('.env', 'w') as f:
            f.write(f"CURSEFORGE_API_KEY={key}")

        return key

    return os.getenv("CURSEFORGE_API_KEY")


API_BASE = 'https://api.curseforge.com'
API_VERSION = 'v1'
API_URL = f'{API_BASE}/{API_VERSION}'
GAME_ID = 432  # Minecraft
CATEGORY_ID = 6  # Mods


load_dotenv()
headers = {
    'Accept': 'application/json',
    'x-api-key': get_api_key()
}


def get_mod_from_slug(slug: str):
    """
    Returns the mod given by the slug.
    Raises ModNotFoundException if no mod was found.
    """

    url = f"{API_URL}/mods/search"
    params = {
        'gameId': GAME_ID,
        'classId': CATEGORY_ID,
        'slug': slug
    }

    err = 0

    while True:
        try:
            return requests.get(
                url,
                params=params,
                headers=headers
            ).json()['data'][0]
        except IndexError:
            raise ModNotFoundException(slug)
        except json.decoder.JSONDecodeError:
            # Retry 3 times before raising exception
            if err == 3:
                raise ModNotFoundException(slug)

            err += 1
            print(f"Something went wrong, trying again ({err})...")
            continue


async def get_mod_from_slug_async(
        slug: str,
        before_response_funcs: typing.List[typing.Callable] = None,
        after_response_funcs: typing.List[typing.Callable] = None):
    """
    Returns the mod given by the slug. \n
    Returns None if no mod was found. \n
    Functions are called before and after making a http request. \n
    """

    timeout = httpx.Timeout(30)
    attempt = 0
    url = f"{API_URL}/mods/search"
    params = {
        'gameId': GAME_ID,
        'classId': CATEGORY_ID,
        'slug': slug
    }
    async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
        while True:
            if attempt >= 3:
                print(f"Error: Max attempts made for '{slug}'")
                return

            try:
                if before_response_funcs is not None:
                    request_object = client.build_request(method="GET", url=url, headers=headers, params=params)
                    for before_response_func in before_response_funcs:
                        await before_response_func(request_object)

                response = await client.get(url, params=params)

                mod = None
                if response.json()['data']:
                    mod = response.json()['data'][0]

                if after_response_funcs is not None:
                    for response_func in after_response_funcs:
                        await response_func(response, mod)

                return mod
            except httpx.ReadTimeout:
                attempt += 1
                print(f"Error: httpx.ReadTimeout for '{slug}', trying again ({attempt})")
            except httpx.ConnectTimeout:
                attempt += 1
                print(f"Error: httpx.ConnectTimeout for '{slug}', trying again ({attempt})")


def get_latest_mod_file(mod_id, game_version: str, mod_loader_type: int = 0, page_size: int = 200):
    """
    Returns the latest file that matches the params. \n
    Raises ModNotFoundException if no mod was found. \n
    Raises ModVersionNotFoundException if no file was found. \n

    Mod loader type can be: \n
    0=Any \n
    1=Forge \n
    2=Cauldron \n
    3=LiteLoader \n
    4=Fabric \n
    5=Quilt \n
    Modloader defaults to 0.
    """

    url = f"{API_URL}/mods/{mod_id}/files"
    params = {
        'gameVersion': game_version,
        'modLoaderType': mod_loader_type,
        'pageSize': page_size
    }

    err = 0

    while True:
        try:
            files = requests.get(
                url,
                params=params,
                headers=headers
            ).json()['data']

            for file in files:
                major_game_version = f"{game_version.split('.')[0]}.{game_version.split('.')[1]}"
                has_snapshot = f"{major_game_version}-Snapshot" in file['gameVersions']
                has_correct_version = game_version in file['gameVersions']
                has_download_file = file['downloadUrl'] is not None
                if ((not has_snapshot) or (has_snapshot and has_correct_version)) and has_download_file:
                    return file

            # If no correct version is found, raise ModVersionNotFoundException
            raise ModVersionNotFoundException(game_version)
        except IndexError:
            raise ModNotFoundException(mod_id)
        except json.decoder.JSONDecodeError:
            # Retry 3 times before raising exception
            if err == 3:
                raise ModVersionNotFoundException(game_version)

            err += 1
            print(f"Something went wrong, trying again ({err})...")
            continue


async def get_latest_mod_file_async(
        mod_id: int, game_version: str,
        mod_loader_type: int = 0, page_size: int = 200,
        before_response_funcs: typing.List[typing.Callable] = None,
        after_response_funcs: typing.List[typing.Callable] = None):
    """
    Returns the latest file that matches the params. \n
    Returns None if no mod or file was found. \n
    Functions are called before and after making a http request. \n

    Mod loader type can be: \n
    0=Any \n
    1=Forge \n
    2=Cauldron \n
    3=LiteLoader \n
    4=Fabric \n
    5=Quilt \n
    Modloader defaults to 0.
    """

    timeout = httpx.Timeout(30)
    attempt = 0
    url = f"{API_URL}/mods/{mod_id}/files"
    params = {
        'gameVersion': game_version,
        'modLoaderType': mod_loader_type,
        'pageSize': page_size
    }
    async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
        while True:
            if attempt >= 3:
                print(f"Error: Max attempts made for '{mod_id}'")
                return

            try:
                if before_response_funcs is not None:
                    request_object = client.build_request(method="GET", url=url, headers=headers, params=params)
                    for before_response_func in before_response_funcs:
                        await before_response_func(request_object)

                response = await client.get(url, params=params)

                correct_file = None
                for file in response.json()['data']:
                    major_game_version = f"{game_version.split('.')[0]}.{game_version.split('.')[1]}"
                    has_snapshot = f"{major_game_version}-Snapshot" in file['gameVersions']
                    has_correct_version = game_version in file['gameVersions']
                    has_download_file = file['downloadUrl'] is not None
                    if ((not has_snapshot) or (has_snapshot and has_correct_version)) and has_download_file:
                        correct_file = file
                        break

                if after_response_funcs is not None:
                    for response_func in after_response_funcs:
                        await response_func(response, correct_file)

                return correct_file
            except IndexError:
                return
            except httpx.ReadTimeout:
                attempt += 1
                print(f"Error: httpx.ReadTimeout for '{mod_id}', trying again ({attempt})")
            except httpx.ConnectTimeout:
                attempt += 1
                print(f"Error: httpx.ConnectTimeout for '{mod_id}', trying again ({attempt})")
