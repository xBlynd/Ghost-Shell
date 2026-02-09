# 🌌 xsvCommandCenter: The Digital Life Container

**Version:** 5.4-Granular
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
* **`DependencyEngine` (Planned)**: Checks for installed tools (Node, Python, Git) before running scripts.

### 2. The Dynamic Router (`src/main.py`)
* **Auto-Discovery**: Automatically finds and loads any tool dropped into `src/commands/`.
* **Zero-Bottleneck**: No hardcoded menus. You add a file, it works.

### 3. The Interface
* **Ghost Shell (`cmd_shell.py`)**: A persistent, interactive terminal (`xsv@HOST >`).
* **GUI Dashboard (Planned)**: A future "Rich/Electron" skin for a visual Matrix-style control panel.

---

## 🔮 The Module Roadmap (Granular & Smart)

### 🛠️ Development (`cmd_dev.py`)
* **Granular Installation**:
    * `xsv dev install vscode`: Installs VS Code + My Extensions (checks OS first).
    * `xsv dev install node`: Installs Node.js (via NVM or Choco).
    * `xsv dev install all`: Installs the full suite (Git, VS Code, Python, Node).
* **Environment Sync**:
    * `xsv dev sync`: Pulls my latest VS Code settings/keybindings from Vault.

### 🌐 Web Server (`cmd_web.py`)
* **Smart Launch**:
    * `xsv web start`: Detects project type (HTML/React/PHP).
    * *Logic:* "Oh, this is React? Do you have Node? No? I'll use a portable version."
* **Quick Serve**:
    * `xsv web serve .`: Instantly hosts current folder on LAN (using Python or Node).

### 🎮 Gaming (`cmd_gameserver.py`)
* **Game Server Deployer**:
    * One-click install/start for: Minecraft, Battlefield, Ark.
    * *Feature:* Downloads server binaries to `library/games/` only when requested.
* **Pixel Game Engine**:
    * Built-in Python games (Snake/Tetris) inside the shell.

### 🕵️ Cybersecurity & Diagnostics
* **The "Analyst" (`cmd_scan.py`)**:
    * Deep diagnostics: Event Logs, Network Traffic, Hidden Users.
* **"Hack the Box" Mode**:
    * ParrotOS/Kali integration. Automated pentesting setup.
* **"The Cleaner" (`cmd_nuke.py`)**:
    * Wipes temp files, clears logs, removes traces.

### 🤖 AI Integration (`cmd_ai.py`)
* **The Oracle**:
    * Direct hook into Gemini/Perplexity APIs.
    * `xsv ask "How do I fix this registry error?"`

### 🎭 Mischief (`cmd_prank.py`)
* **Prank Module**: Harmless scripts (Mouse jitter, fake updates) for family/friends.

---

## 📂 Data Strategy

| Zone | Content | Storage Location |
| :--- | :--- | :--- |
| **🟢 GREEN (Public)** | Source Code, Game Installers, Public Scripts | **GitHub** |
| **🔴 RED (Private)** | Journals, Client Passwords, API Keys, `user_settings.json` | **OneDrive / USB** |

---

## 🚀 Usage Guide
1.  **Plug in USB.**
2.  **Double-click `LAUNCH.bat`.**
3.  **Login** (Secure Shell opens).
4.  **Command:** `dev install vscode` (Surgical install).
5.  **Command:** `web serve` (Instant preview).