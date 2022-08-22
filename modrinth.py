import json
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
