# 🌌 xsvCommandCenter: The Digital Life Container

**Version:** ~~5.4-Granular~~ **6.0-Ghost**
**Status:** Alpha / Active Development
**Philosophy:** "One Stick, Any Computer, Surgical Precision."

---

## 🎯 The Grand Vision
This is not just a script. It is a **Portable Operating Environment**.
It is designed to be the single repository for my entire digital life—my brain, my tools, my games, and my work—capable of running on **any** machine (Windows, Linux, ParrotOS, MacOS) instantly.

### The "Split-Brain" Architecture
1.  **The Brain (GitHub):** The Logic, Engines, and Public Scripts. (Syncs everywhere).
2.  **The Soul (USB/Cloud):** My Journals, Passwords, Device States, and Private Configs. (Never touches public Git).

---

## 🏗️ System Architecture

### 1. The Core (`src/core/`)
* **`InfoEngine`**: The Detective. Identifies Host OS, Hardware, and Cloud Drives.
* **`HostEngine`**: The Worker. Handles file ops, process killing, and launching.
* ~~**`DependencyEngine` (Planned)**~~ *Pivoted to `cmd_dev.py` (The Hacker Kit).*

### 2. The Dynamic Router (`src/main.py`)
* **Auto-Discovery**: Automatically finds and loads any tool dropped into `src/commands/`.
* **NEW: Custom Partition**:
    * `src/commands/` -> **System Tools** (Shell, Setup, Settings).
    * `src/commands/custom/` -> **User Tools** (Scare, Games, AI).

### 3. The Interface
* **Ghost Shell (`cmd_shell.py`)**: A persistent, interactive terminal (`xsv@HOST >`).
    * **Features:** Hot Reload, Three-Mode Execution (Smart/Exec/Raw), and Threading support.
* ~~**GUI Dashboard (Planned)**~~ *Moved to Phase 5 Roadmap.*

---

## 🔮 The Module Roadmap (Granular & Smart)

### 🛠️ The "Ghost" Utilities (LIVE)
* **The Factory (`cmd_create.py`)**:
    * **Dispatcher Logic**: `create todo "Buy milk"` -> Routes to Todo Module.
    * **Wizard**: `create command scare` -> Auto-generates Python boilerplate.
* **The Editor (`cmd_edit.py`)**:
    * Smart-detects VS Code, Notepad, or Nano to edit scripts on the fly.
* **The Hot-Swap (`reload`)**:
    * Updates code in memory without restarting the shell.

### 🛠️ Development (`cmd_dev.py`)
* **Granular Installation**:
    * `dev install vscode`: Installs VS Code + My Extensions (checks OS first).
    * `dev install all`: Installs the full suite (Git, VS Code, Python, Node).
* **Environment Sync**:
    * `dev sync`: Pulls my latest VS Code settings/keybindings from Vault.

### 🌐 Web Server (`cmd_web.py`)
* **Smart Launch**:
    * `web serve`: Instantly hosts current folder on LAN.

### 🎮 Gaming (`cmd_gameserver.py`)
* **Game Server Deployer**:
    * One-click install/start for: Minecraft, Battlefield, Ark.
    * **Storage**: Servers live in `data/servers/`, NOT in the source code.

### 🕵️ Cybersecurity & Diagnostics
* **The "Analyst" (`cmd_scan.py`)**:
    * Deep diagnostics: Event Logs, Network Traffic.
* **"The Cleaner" (`cmd_clean.py`)**:
    * Wipes temp files, clears logs, removes traces.

---

## 📂 Data Strategy

| Zone | Content | Storage Location |
| :--- | :--- | :--- |
| **SYSTEM** | Core Logic, Router, Base Modules | `src/commands/` |
| **USER** | Custom Scripts, Pranks, Tools | `src/commands/custom/` |
| **LIBRARY** | 3rd Party Scripts (Bash/PS1) | `library/` (Linked via JSON) |
| **DATA** | Game Servers, Vault, Databases | `data/` |

---

## 🚀 Usage Guide
1.  **Plug in USB.**
2.  **Double-click `LAUNCH.bat`.**
3.  **Login** (Secure Shell opens).
4.  **Command:** `setup` (Installs shortcuts/path).
5.  **Command:** `create command mytool` (Builds a new tool).