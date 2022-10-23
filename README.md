# MC Mod Updater
Console based (soon GUI) application that can update your minecraft mods. [TODO and idea's](https://trello.com/b/aAbONtbP/mcmodupdater)

## Installation
For Windows, go to the [releases](https://github.com/AidenRaaphorst/mc-mod-updater/releases) and download the exe file.  
When opening the file, you may get a Microsoft Defender SmartScreen pop-up, this is because I don't have money to buy a license, just click 'More info' and 'Run anyway'.

For Linux and macOS, download the source code, run `pip install -r requirements.txt` and open `main.py`.

The first time you use the app, it will ask for a CurseForge API key.  
To get one, visit https://console.curseforge.com/, login or make an account, 
click on the tab called 'API keys' and copy the key.

## Usage
1. Put your mod URLs in the generated `mods.txt` file.
2. Type the version that you want to update to.
3. Change the default settings in the confirmation screen, if needed.
4. Confirm that the mods the program found are correct.
5. Wait for all the mods to be downloaded.
