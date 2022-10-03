import json
import typing
import httpx
import requests


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


API_BASE = 'https://api.modrinth.com'
API_VERSION = 'v2'
API_URL = f'{API_BASE}/{API_VERSION}'


def get_mod_from_slug(mod_slug: str):
    """
    Returns the mod given by the slug.
    Raises ModNotFoundException if no mod was found.
    """

    try:
        result = requests.get(f"{API_URL}/project/{mod_slug}").json()
        return result
    except json.decoder.JSONDecodeError:
        raise ModNotFoundException(mod_slug)


async def get_mod_from_slug_async(
        mod_slug: str,
        before_response_funcs: typing.List[typing.Callable] = None,
        after_response_funcs: typing.List[typing.Callable] = None):
    """
    Returns the mod given by the slug. \n
    Returns None if no mod or file was found. \n
    Functions are called before and after making a http request. \n
    """

    timeout = httpx.Timeout(30)
    attempt = 0
    url = f"{API_URL}/project/{mod_slug}"
    async with httpx.AsyncClient(timeout=timeout) as client:
        while True:
            if attempt >= 3:
                print(f"Error: Max attempts made for '{mod_slug}'")
                return

            try:
                if before_response_funcs is not None:
                    request_object = client.build_request(method="GET", url=url)
                    for before_response_func in before_response_funcs:
                        await before_response_func(request_object)

                response = await client.get(url)

                mod = None
                if response.status_code == 200:
                    mod = response.json()

                if after_response_funcs is not None:
                    for response_func in after_response_funcs:
                        await response_func(response, mod)

                return mod
            except httpx.ReadTimeout:
                attempt += 1
                print(f"Error: httpx.ReadTimeout for '{mod_slug}', trying again ({attempt})")
            except httpx.ConnectTimeout:
                attempt += 1
                print(f"Error: httpx.ConnectTimeout for '{mod_slug}', trying again ({attempt})")


def get_latest_mod_file(mod_slug: str, game_version: str, mod_loader: str = None):
    """
    Returns the latest file that matches the params. \n
    Raises ModNotFoundException if no mod was found. \n
    Raises ModVersionNotFoundException if no file was found. \n
    """

    try:
        mods = requests.get(f"{API_URL}/project/{mod_slug}/version").json()
    except json.decoder.JSONDecodeError:
        raise ModNotFoundException(mod_slug)

    for mod in mods:
        has_game_version = game_version in mod['game_versions']
        has_mod_loader = True if mod_loader is None else mod_loader in mod['loaders']
        if has_game_version and has_mod_loader:
            return mod

    # If correct game version is not found, raise error
    raise ModVersionNotFoundException(game_version)


async def get_latest_mod_file_async(
        mod_slug: str, game_version: str, mod_loader: str = None,
        before_response_funcs: typing.List[typing.Callable] = None,
        after_response_funcs: typing.List[typing.Callable] = None):
    """
    Returns the latest file that matches the params. \n
    Returns None if no mod or file was found. \n
    Functions are called before and after making a http request. \n
    """

    timeout = httpx.Timeout(30)
    attempt = 0
    url = f"{API_URL}/project/{mod_slug}/version"
    async with httpx.AsyncClient(timeout=timeout) as client:
        while True:
            if attempt >= 3:
                print(f"Error: Max attempts made for '{mod_slug}'")
                return

            try:
                if before_response_funcs is not None:
                    request_object = client.build_request(method="GET", url=url)
                    for before_response_func in before_response_funcs:
                        await before_response_func(request_object)

                response = await client.get(url)

                correct_file = None
                if response.status_code == 200:
                    for file in response.json():
                        has_game_version = game_version in file['game_versions']
                        has_mod_loader = True if mod_loader is None else mod_loader in file['loaders']
                        if has_game_version and has_mod_loader:
                            correct_file = file

                if after_response_funcs is not None:
                    for response_func in after_response_funcs:
                        await response_func(response, correct_file)

                return correct_file
            except httpx.ReadTimeout:
                attempt += 1
                print(f"Error: httpx.ReadTimeout for '{mod_slug}', trying again ({attempt})")
            except httpx.ConnectTimeout:
                attempt += 1
                print(f"Error: httpx.ConnectTimeout for '{mod_slug}', trying again ({attempt})")
