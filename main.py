import os
import shutil
import time

import curseforge
import utils
from utils import clear


def clear_screen():
    clear()
    print("----------------------")
    print("    MC Mod Updater    ")
    print("----------------------")
    print()


def get_mod_dir():
    default = f"C:/Users/{os.getlogin()}/AppData/Roaming/.minecraft/mods"

    print(f"Default is '{default}'")
    location = input("Minecraft mods folder location (leave empty for default): ")

    if location == '':
        return default
    else:
        if not os.path.exists(location):
            print()
            print("Error: Folder does not exist.")
            input("Press Enter to try again")
            clear_screen()
            get_mod_dir()

        return location


def get_mc_version():
    return input("Minecraft version you want to update to: ")


def get_mc_mod_loader_type():
    print("Modloaders:")
    print(" - Any")
    print(" - Forge")
    print(" - Cauldron")
    print(" - LiteLoader")
    print(" - Fabric")
    print(" - Quilt")
    mod_loader = input("\nMinecraft mod loader (leave empty for Fabric): ").lower()

    if mod_loader == "" or mod_loader == "fabric":
        return 4
    elif mod_loader == "any":
        return 0
    elif mod_loader == "forge":
        return 1
    elif mod_loader == "quilt":
        return 5
    elif mod_loader == "cauldron":
        return 2
    elif mod_loader == "liteLoader":
        return 3
    else:
        print("\nThat was not an option.")
        input("Press Enter to try again")
        clear_screen()
        get_mc_mod_loader_type()


def show_download_urls():
    if mods_not_found:
        print("Mods that could not be found:")
        for mod in mods_not_found:
            print(f" - '{mod}'")
        print()

    if mods_incorrect_version:
        print(f"Mods that did not have version '{mc_version}':")
        for mod in mods_incorrect_version:
            print(f" - '{mod}'")
        print()

    if mod_urls:
        print("Mod download URL's:")
        for i, mod in enumerate(mod_urls):
            print(f" {i + 1}. {mod}")
        print()


def remove_mod_urls():
    print("Are the mods correct?")
    print("If not, enter the number next to the mod to remove it.")
    print("To select multiple mods, separate them with a comma.")
    print("Example: 1, 2, 5")
    print()
    mod_numbers = input("Select number(s) (leave empty if everything is correct): ").split(", ")
    print()

    if mod_numbers == ['']:
        return

    for number in mod_numbers:
        try:
            if int(number) == 0:
                raise IndexError

            mod_urls.pop(int(number) - 1)
        except IndexError:
            print("That is not an option.")
            input("Press Enter to try again")

    clear_screen()
    show_download_urls()
    remove_mod_urls()


def move_old_mods():
    print("Do you want to move the old mods into a backup folder?")
    choice = input("y/n (leave empty for yes): ").lower()

    if choice == "n" or choice == "no":
        return

    new_folder = "Backup " + time.strftime("%Y-%m-%d %H.%M.%S", time.localtime())
    os.mkdir(os.path.join(mc_location, new_folder))

    print(f"Moving old mods to backup folder named '{new_folder}'...\n")

    for file in os.listdir(mc_location):
        if os.path.isdir(file):
            continue

        if not file.endswith(".jar"):
            continue

        print(f"Moving '{file}' to '{new_folder}'")

        src_path = fr"{mc_location}\{file}"
        dst_path = fr"{mc_location}\{new_folder}\{file}"
        shutil.move(src_path, dst_path)
    print("\nDone moving old mods")


def download_mods():
    print("Downloading mods, this can take some time depending on internet speed...\n")
    for url in mod_urls:
        name = url.split("/")[-1]
        print(f"Downloading '{name}'")
        utils.download_file_from_url(url, mc_location, name)
        # name = url.split("/")[-1]
        # response = requests.get(url)
        # open(name, "wb").write(response.content)

    print("\nDone downloading mods")


clear_screen()

# Check if 'mods.txt' exists, if not, create it and put some comments in
if not os.path.exists("mods.txt"):
    with open('mods.txt', 'w') as f:
        f.write("# Put the mod url's here.\n")
        f.write("# Only works with CurseForge url's for now.\n")
        f.write("# Example (without the '#'):\n")
        f.write("# https://www.curseforge.com/minecraft/mc-mods/fabric-api")
        f.write("\n")
        f.write("\n")

    print("File 'mods.txt' was created, put mod url's in the file and save before continuing.")
    input("Press Enter when done")
    clear_screen()

current_mod_urls = utils.get_urls_from_file('mods.txt')
current_mod_slugs = utils.get_slugs_from_file('mods.txt')
print("Url's found:")
for url in current_mod_urls:
    print(url)
print()

input("Press Enter to continue")
clear_screen()

mc_location = get_mod_dir()
clear_screen()

mc_version = get_mc_version()
clear_screen()

mod_loader_type = get_mc_mod_loader_type()
clear_screen()

print("Looking for mods online, this can take some time depending on the API...\n")
mod_urls = []
mods_not_found = []
mods_incorrect_version = []

for slug in current_mod_slugs:
    print(f"Looking for mod '{slug}'")
    try:
        mod_id = curseforge.get_mod(slug)['id']
    except TypeError:
        mods_not_found.append(slug)
        print(f"Error: Could not find file for mod '{slug}'.")
        continue

    mod_file = curseforge.get_latest_mod_file(mod_id, mc_version)
    try:
        mod_urls.append(mod_file['downloadUrl'])
        print(f"Found latest file for '{slug}' for version '{mc_version}'.")
    except TypeError:
        mods_incorrect_version.append(slug)
        print(f"Error: Could not find file '{slug}' for version '{mc_version}'.")
clear_screen()

show_download_urls()
if not mod_urls:
    print("There are no mods that can be downloaded.")
    input("Press Enter to exit")
    exit()
remove_mod_urls()
clear_screen()

move_old_mods()
print()
print()
print()

download_mods()

print()
input("Press Enter to exit")
