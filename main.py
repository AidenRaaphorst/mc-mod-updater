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
    print(" 1. Any")
    print(" 2. Fabric")
    print(" 3. Forge")
    print(" 4. Quilt")
    print(" 5. LiteLoader")
    print(" 6. Cauldron")
    mod_loader = input("\nMinecraft mod loader (leave empty for Fabric): ").lower()

    if mod_loader == "any" or mod_loader == "1":
        return 0
    elif mod_loader == "" or mod_loader == "fabric" or mod_loader == "2":
        return 4
    elif mod_loader == "forge" or mod_loader == "3":
        return 1
    elif mod_loader == "quilt" or mod_loader == "4":
        return 5
    elif mod_loader == "liteLoader" or mod_loader == "5":
        return 3
    elif mod_loader == "cauldron" or mod_loader == "6":
        return 2
    else:
        print("\nThat was not an option.")
        input("Press Enter to try again")
        clear_screen()
        get_mc_mod_loader_type()


def show_mod_results():
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
        print("Downloadable mods:")
        for i, mod in enumerate(mod_urls):
            # Make numbers align to the right
            digits = len(str(len(mod_urls))) - len(str(i + 1))
            number = f"{' ' * digits}{i + 1}"

            print(f" {number}. {utils.get_slug_from_url(mod)}")
        print()


def remove_mod_urls():
    if not mod_urls:
        print("There are no downloadable mods.")
        input("Press Enter to exit")
        exit()

    print("Are the mods correct?")
    print("If not, enter the number next to the mod to remove it.")
    print("To select multiple mods, separate them with a comma.")
    print("Example: 1, 2, 5")
    print()
    mod_numbers = input("Select number(s) (leave empty if everything is correct): ").split(", ")

    if mod_numbers == ['']:
        return

    try:
        mod_numbers = [int(x) for x in mod_numbers]
    except ValueError:
        print("\nThat is not an option.")
        input("Press Enter to try again")
        clear_screen()
        show_mod_results()
        remove_mod_urls()
        return

    for number in sorted(mod_numbers, reverse=True):
        if number == 0 or number > len(mod_urls):
            print("\nThat is not an option.")
            input("Press Enter to try again")
            break

        mod_urls.pop(number-1)

    clear_screen()
    show_mod_results()
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
        f.write("# Put the mod URLs here.\n")
        f.write("# Only works with CurseForge URLs for now.\n")
        f.write("# Example (without the '#'):\n")
        f.write("# https://www.curseforge.com/minecraft/mc-mods/fabric-api")
        f.write("\n")
        f.write("\n")

    print("File 'mods.txt' was created, put mod URLs in the file and save before continuing.")
    input("Press Enter when done")
    clear_screen()

current_mod_urls = utils.get_urls_from_file('mods.txt')
current_mod_slugs = utils.get_slugs_from_file('mods.txt')
print("URLs found:")
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

show_mod_results()
remove_mod_urls()
clear_screen()

move_old_mods()
print()
print()
print()

download_mods()

print()
input("Press Enter to exit")
