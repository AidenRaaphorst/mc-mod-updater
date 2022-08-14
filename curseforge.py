import os
import requests
from dotenv import load_dotenv  # If not installed, run: pip install python-dotenv


# Get API key
def get_api_key():
    if not os.path.exists('.env'):
        print("It appears that this is the first time you have executed this program.")
        print("In order to use this program, you need an API key.")
        print("Go to this link 'https://console.curseforge.com/' and create/login into your account.")
        print("After getting into your account, go to the tab 'API keys' on the left and copy the key.\n")
        key = input("Insert API key here: ")
        print()
        with open('.env', 'w') as f:
            f.write(f"CURSEFORGE_API_KEY={key}")

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


def get_mod(slug: str):
    """
    Returns the mod given by the params.
    Returns None if no mod was found.
    """

    url = f"{API_URL}/mods/search"
    params = {
        'gameId': GAME_ID,
        'classId': CATEGORY_ID,
        'slug': slug
    }

    try:
        return requests.get(
            url,
            params=params,
            headers=headers
        ).json()['data'][0]
    except IndexError:
        return None


def get_latest_mod_file(mod_id, game_version: str, mod_loader_type: int = 4, page_size: int = 200):
    """
    Returns the latest file given by the params.
    Returns None if no file was found.

    Mod loader type can be:

    0=Any

    1=Forge

    2=Cauldron

    3=LiteLoader

    4=Fabric

    5=Quilt
    """

    url = f"{API_URL}/mods/{mod_id}/files"
    params = {
        'gameVersion': game_version,
        'modLoaderType': mod_loader_type,
        'pageSize': page_size
    }

    try:
        files = requests.get(
            url,
            params=params,
            headers=headers
        ).json()['data']

        for file in files:
            major_game_version = f"{game_version.split('.')[0]}.{game_version.split('.')[1]}"
            if not file['gameVersions'].__contains__(f"{major_game_version}-Snapshot"):
                return file
    except IndexError:
        return None
