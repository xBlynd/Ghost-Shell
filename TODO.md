# 📋 Project Worklist

## 🔥 Phase 1: The Foundation (Current)
- [x] **Modular Architecture:** Core vs. Commands.
- [x] **Dynamic Router:** Auto-loads modules.
- [x] **Hardware Detective:** `InfoEngine` scans CPU/RAM.
- [x] **Help System:** Dynamic menu.
- [ ] **Ghost Shell:** Interactive terminal (`xsv@HOST >`).
- [ ] **Launchers:** `LAUNCH.bat` (Windows).

## 🚧 Phase 2: The Toolbelt (Essential Modules)
- [ ] **`cmd_dev.py`**:
    - [ ] Add `install vscode` (Windows/Linux detection).
    - [ ] Add `install node` / `install python`.
    - [ ] Add `sync settings` (VS Code extensions).
- [ ] **`cmd_web.py`**:
    - [ ] Add `serve` (Python `http.server` wrapper).
    - [ ] Add `project init` (Download HTML5 boilerplate).
- [ ] **`cmd_clean.py`**:
    - [ ] Temp file wiper.
    - [ ] Browser cache cleaner.
    - [ ] Silent File Transfer(Moving files from "work" computer to this "usb" untraced.  For my best interest, not to be malicious.)
    - [ ] Script in library for spying or keylogging on kids devices to make sure they aren't doing things we dont want.

## 🔭 Phase 3: Expansion (Advanced)
- [ ] **`cmd_gameserver.py`**: Minecraft/Ark installers.
- [ ] **`cmd_ai.py`**: Gemini API hook.
- [ ] **ParrotOS Support**: Verify all scripts on Linux.
- [ ] **Dashboard**: Future GUI skin.

## 🔭 CORE and ENGINE (Advanced)
- [ ] **Status System**
  - [ ] Testing each command to make sure they work.
- [ ] **DEV MODE**:
- [ ] **Search**
- [ ] Security
- [ ] Relative Time Support: ReminderEngine.parse_time()
  - [ ] adding reminders like "Remind me in 10minutes". Our ReminderEngine needs a Time Parser to convert "10m" or "1h" or "10sec" into a hard timestamp for the JSON vault.
- [ ] USB Autoloader(Plug in usb and terminal popup)


## DIAGNOSTIC / HACK THE BOX / HOST ITs
- [ ] Network issues.  Observing latency issues in Rocket League.  want to know why.  Network monitoring(live), etc in host machine for troubleshooting and fixing.

## 🔭 SCRIPTS or IDEAS or COMMANDS: Expansion (Advanced)
- [ ] **`cmd_gameserver.py`**: Minecraft/Ark installers.
- [ ] **`cmd_ai.py`**: Gemini API hook.
- [ ] **ParrotOS Support**: Verify all scripts on Linux.
- [ ] **Dashboard**: Future GUI skin.
- [ ] Google Search
- [ ] Weather


## 🐧 The Linux Factor (Important)(Discovered or reminded in the Reminder Module.)
Since you want this portable to Linux, notify-send is the standard tool, but it isn't always installed by default on minimal server installs (though it is on most desktops like Ubuntu/Debian).

When you eventually run your Install/Setup script on the host machine, you will need to ensure this package is present.

Debian/Ubuntu: sudo apt install libnotify-bin

Arch: sudo pacman -S libnotify

If it's missing, the new code will just print [Linux Alert] to the terminal so the system doesn't crash.