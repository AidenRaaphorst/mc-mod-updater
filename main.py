import os
import shutil
import time

import curseforge
import modrinth
import utils
from utils import clear


curseforge_mod_loader_type = None
modrinth_mod_loader = None


def clear_screen():
    clear()
    print("----------------------")
    print("    MC Mod Updater    ")
    print("----------------------")
    print()


def get_mod_dir():
    while True:
        default = f"C:/Users/{os.getlogin()}/AppData/Roaming/.minecraft/mods"
        print(f"Default is '{default}'")
        location = input("Minecraft mods folder location (leave empty for default): ")

        if location == "":
            return default
        else:
            if not os.path.exists(location):
                print("\nError: Folder does not exist.")
                input("Press Enter to try again")
                clear_screen()
                continue
            return location


def get_mc_version():
    return input("Minecraft version you want to update to: ")


def get_mc_mod_loader():
    while True:
        global curseforge_mod_loader_type, modrinth_mod_loader

        print("Modloaders:")
        print(" 1. Any")
        print(" 2. Fabric")
        print(" 3. Forge")
        print(" 4. Quilt")
        print(" 5. LiteLoader")
        print(" 6. Cauldron")
        mod_loader = input("\nMinecraft mod loader (leave empty for Fabric): ").lower()

        if mod_loader == "any" or mod_loader == "1":
            curseforge_mod_loader_type = 0
            modrinth_mod_loader = None
            return "Any"
        elif mod_loader == "" or mod_loader == "fabric" or mod_loader == "2":
            curseforge_mod_loader_type = 4
            modrinth_mod_loader = "fabric"
            return "Fabric"
        elif mod_loader == "forge" or mod_loader == "3":
            curseforge_mod_loader_type = 1
            modrinth_mod_loader = "forge"
            return "Forge"
        elif mod_loader == "quilt" or mod_loader == "4":
            curseforge_mod_loader_type = 5
            modrinth_mod_loader = "quilt"
            return "Quilt"
        elif mod_loader == "liteloader" or mod_loader == "5":
            curseforge_mod_loader_type = 3
            modrinth_mod_loader = "liteloader"
            return "LiteLoader"
        elif mod_loader == "cauldron" or mod_loader == "6":
            curseforge_mod_loader_type = 2
            modrinth_mod_loader = "cauldron"
            return "Cauldron"
        else:
            print("\nThat was not an option.")
            input("Press Enter to try again")
            clear_screen()
            continue


def look_for_mods():
    global curseforge_mod_loader_type, modrinth_mod_loader

    print("Looking for mods online, this can take some time depending on the API...\n")
    for url in text_file_urls:
        slug = utils.get_slug_from_url(url)

        if "modrinth" in url:
            # Modrinth
            print(f"Looking for mod '{slug}' using Modrinth")
            try:
                mod_file = modrinth.get_latest_mod_file(
                    mod_slug=slug,
                    game_version=mc_version,
                    mod_loader=modrinth_mod_loader
                )
                downloadable_mods_urls.append(mod_file['files'][0]['url'])
                print(f"Found latest file for '{slug}' for version '{mc_version}'.")
            except modrinth.ModNotFoundException:
                mods_not_found.append(slug)
                print(f"Error: Could not find file for mod '{slug}'.")
            except modrinth.ModVersionNotFoundException:
                mods_incorrect_version.append(slug)
                print(f"Error: Could not find file '{slug}' for version '{mc_version}'.")
        elif "curseforge" in url:
            # CurseForge
            print(f"Looking for mod '{slug}' using CurseForge")
            try:
                mod_id = curseforge.get_mod_from_slug(slug)['id']
                mod_file = curseforge.get_latest_mod_file(
                    mod_id=mod_id,
                    game_version=mc_version,
                    mod_loader_type=curseforge_mod_loader_type
                )
                downloadable_mods_urls.append(mod_file['downloadUrl'])
                print(f"Found latest file for '{slug}' for version '{mc_version}'.")
            except curseforge.ModNotFoundException:
                mods_not_found.append(slug)
                print(f"Error: Could not find file for mod '{slug}'.")
            except curseforge.ModVersionNotFoundException:
                mods_incorrect_version.append(slug)
                print(f"Error: Could not find file '{slug}' for version '{mc_version}'.")
        else:
            mods_not_found.append(slug)
            print(f"Error: Could not find file for mod '{slug}', because the website that was linked is not supported.")


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

    if downloadable_mods_urls:
        print("Downloadable mods:")
        for i, mod in enumerate(downloadable_mods_urls):
            # Make numbers align to the right
            digit_spacing = len(str(len(downloadable_mods_urls))) - len(str(i + 1))
            number = f"{' ' * digit_spacing}{i + 1}"

            # print(f" {number}. {utils.get_slug_from_url(mod)}")
            print(f" {number}. {utils.get_file_name_from_url(mod)}")
        print()


def remove_mod_urls():
    if not downloadable_mods_urls:
        print("There are no downloadable mods.")
        input("Press Enter to exit")
        exit()

    print("Are the mods correct?")
    print("If not, enter the number next to the mod to remove it.")
    print("To select multiple mods, separate them with a comma.")
    print("Example: 1, 2, 5")
    mod_numbers = input("\nSelect number(s) (leave empty if everything is correct): ").split(", ")

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
        if number == 0 or number > len(downloadable_mods_urls):
            print("\nThat is not an option.")
            input("Press Enter to try again")
            break

        downloadable_mods_urls.pop(number - 1)

    clear_screen()
    show_mod_results()
    remove_mod_urls()


def get_choice_move_old_mods():
    print("Do you want to move the old mods into a backup folder?")
    choice_move_old_mods = input("y/n (leave empty for yes): ").lower()

    if choice_move_old_mods == "" or choice_move_old_mods == "y" or choice_move_old_mods == "yes":
        return "yes"
    else:
        return "no"


def move_old_mods():
    new_folder = "Backup " + time.strftime("%Y-%m-%d %H.%M.%S", time.localtime())
    os.mkdir(os.path.join(mod_folder, new_folder))

    print(f"Moving old mods to backup folder named '{new_folder}'...\n")

    for file in os.listdir(mod_folder):
        if os.path.isdir(file):
            continue

        if not file.endswith(".jar"):
            continue

        print(f"Moving '{file}' to '{new_folder}'")

        src_path = fr"{mod_folder}\{file}"
        dst_path = fr"{mod_folder}\{new_folder}\{file}"
        shutil.move(src_path, dst_path)
    print("\nDone moving old mods")


def download_mods():
    print("Downloading mods, this can take some time depending on internet speed...\n")
    for url in downloadable_mods_urls:
        name = utils.get_file_name_from_url(url)
        print(f"Downloading '{name}'")
        utils.download_file_from_url(url, mod_folder, name)

    print("\nDone downloading mods")


def confirm_settings():
    global mod_folder, mc_version, mod_loader, choice_move_old_mods

    while True:
        print("Your selected options:")
        print(f" 1. Minecraft Mod Folder:          '{mod_folder}'")
        print(f" 2. Minecraft Game Version:        '{mc_version}'")
        print(f" 3. Minecraft Mod Loader:          '{mod_loader}'")
        print(f" 4. Backup old mods to new folder: '{choice_move_old_mods}'")

        print("\nIf everything is correct, confirm options.")
        print("To change something, type the number next to it.")
        choice_confirm = input("\nTo confirm, type 'y' or 'yes': ").lower()

        if choice_confirm == "":
            print("\nThat is not an option.")
            input("Press Enter to try again")
            clear_screen()
            # confirm_settings()
            continue

        if choice_confirm == "y" or choice_confirm == "yes":
            break

        if choice_confirm == "1":
            clear_screen()
            mod_folder = get_mod_dir()
        elif choice_confirm == "2":
            clear_screen()
            mc_version = get_mc_version()
        elif choice_confirm == "3":
            clear_screen()
            mod_loader = get_mc_mod_loader()
        elif choice_confirm == "4":
            clear_screen()
            get_choice_move_old_mods()
        else:
            print("\nThat is not an option.")
            input("Press Enter to try again")

        clear_screen()
        # confirm_settings()
        continue


clear_screen()

# Check if 'mods.txt' exists, if not, create it and put some comments in
if not os.path.exists("mods.txt"):
    with open("mods.txt", "w") as f:
        f.write("# Put the mod URLs here, without the '#'.\n")
        f.write("# Works with CurseForge and Modrinth links.\n")
        f.write("# Examples:\n")
        f.write("# https://www.curseforge.com/minecraft/mc-mods/fabric-api")
        f.write("# https://modrinth.com/mod/sodium")
        f.write("\n")
        f.write("\n")

    print("File 'mods.txt' was created, put the mod URLs of the mods you wish")
    print("to update in that file and save before continuing.")
    input("\nPress Enter when done")
    clear_screen()

text_file_urls = utils.get_urls_from_file("mods.txt")
print("URLs found:")
for url in text_file_urls:
    print(url)
input("\nPress Enter to continue")
clear_screen()

mod_folder = get_mod_dir()
clear_screen()

mc_version = get_mc_version()
clear_screen()

mod_loader = get_mc_mod_loader()
clear_screen()

choice_move_old_mods = get_choice_move_old_mods()
clear_screen()

confirm_settings()
clear_screen()

downloadable_mods_urls = []
mods_not_found = []
mods_incorrect_version = []

look_for_mods()
clear_screen()

show_mod_results()
remove_mod_urls()
clear_screen()


if choice_move_old_mods == "yes":
    move_old_mods()
print()
print()
print()

download_mods()

input("\nPress Enter to exit")
