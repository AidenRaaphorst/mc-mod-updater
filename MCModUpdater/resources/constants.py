import os
import sys


def _get_root_dir(dir_name: str, return_normal=False, loops=5):
    """
    Args:
        dir_name: Directory to search for.
        return_normal: Always return normal directory instead of Pyinstaller temp directory.
        loops: Amount of times to search for `dir_name` and go up a directory before raising FileNotFoundError.
    Returns:
        Absolute path to `dir_name`.
    Raises:
        FileNotFoundError: When not being able to find `dir_name` after `loops` loops.
    """
    init_dir = os.path.dirname(__file__)

    # Check for Pyinstaller and return normal, return normal path instead of Pyinstaller temp directory
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS') and return_normal:
        return os.path.join(os.getcwd(), dir_name)

    # Loop through all the files/folders in current directory and return for dir_name.
    # If dir_name hasn't been found in current directory, go up a directory and try again.
    # Raises FileNotFoundError after certain amount of loops.
    curr_dir = init_dir
    for i in range(loops):
        for file in os.listdir(curr_dir):
            if file == dir_name:
                return os.path.realpath(os.path.join(curr_dir, dir_name))
        curr_dir = os.path.realpath(os.path.join(curr_dir, ".."))

    raise FileNotFoundError(f"Directory '{dir_name}' not found after {loops} loops")


def _get_config_dir(root_dir: str, dir_name: str):
    root_dir_name = os.path.basename(root_dir)
    path = os.path.join(_get_root_dir(root_dir_name, return_normal=True), dir_name)
    return os.path.realpath(path)


# General
APP_VERSION = "v1.3.2"

# Paths
ROOT_DIR = _get_root_dir("MCModUpdater")
RESOURCES_PATH = os.path.join(ROOT_DIR, "resources")
CONFIG_DIR_PATH = _get_config_dir(ROOT_DIR, os.path.join("..", "config"))
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR_PATH, "settings.json")
ENV_FILE_PATH = os.path.join(CONFIG_DIR_PATH, ".env")
LOG_FILE_PATH = os.path.join(CONFIG_DIR_PATH, "log.txt")

# CurseForge
CF_BASE_MOD_URL = "https://www.curseforge.com/minecraft/mc-mods"
CF_API_BASE = "https://api.curseforge.com"
CF_API_VERSION = "v1"
CF_API_URL = f"{CF_API_BASE}/{CF_API_VERSION}"
CF_GAME_ID = 432  # Minecraft
CF_CATEGORY_ID = 6  # Mods

# Modrinth
MR_BASE_MOD_URL = "https://modrinth.com/mod"
MR_API_BASE = "https://api.modrinth.com"
MR_API_VERSION = "v2"
MR_API_URL = f"{MR_API_BASE}/{MR_API_VERSION}"
