# MC Mod Updater
Console based application that can update your minecraft mods.

## Installation
For Windows, go to the [releases](https://github.com/AidenRaaphorst/mc-mod-updater/releases) and download the exe file.  
When opening the file, you may get a Microsoft Defender SmartScreen pop-up, this is because I don't have money to buy a license, just click 'More info' and 'Run anyway'.

For Linux and macOS, download the source code and run `main.py`.

The first time you use the app, it will ask for a CurseForge API key.  
To get one, visit https://console.curseforge.com/, login or make an account, 
click on the tab called 'API keys' and copy the key.

## Usage
1. Put your mod URLs in the generated `mods.txt` file.
2. Type the version that you want to update to.
3. Change the default settings in the confirmation screen, if needed.
4. Confirm that the mods the program found are correct.
5. Wait for all the mods to be downloaded.

## Todo's and idea's
| Colour      | Meaning                                       |
| ----------- | --------------------------------------        |
| 🟢 Green    | Fully implemented                             |
| 🟡 Yellow   | (Somewhat) Implemented, needs further testing |
| 🟠 Orange   | Working on it                                 |
| 🔴 Red       | Not implemented                               |
| 🟣 Purple      | Not planned for the near future               |

[comment]: <> (🔴🟠🟡🟢🔵🟣⚫⚪)

TODO:
- 🟡 Make it easier to use for people that struggle with console based apps
- 🔴 Add `mods.txt` presets
- 🟠 Add GUI
  - 🔴 Add functionality
  - 🟠 Add settings pane
  - 🟣 Add search pane
  - 🔴 Add icons to mods found online
- 🟣 Be able to either use CLI or GUI
- 🟣 Add mods folder scanning instead of putting URLs in a txt file
- 🔴 Use CurseForge/Modrinth custom exceptions for async functions
