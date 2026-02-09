# ( The Manual )

**Changes:** Updated the Routing Logic to show the priority list (System -> Custom -> Library), and added the new "Threading" rule for GUI apps (like the Scare prank).

```markdown
# 🛠️ xsvCommandCenter Developer Guide

**Target Audience:** Hackers, Developers, and Future Ian.
**Goal:** Expand the system without breaking the Core.

---

## 👻 1. The Ghost Shell Architecture
The Ghost Shell (`src/commands/cmd_shell.py`) is an **Infinite Loop** that acts as a traffic controller. It does not "know" commands; it routes them.

### The Routing Logic (Order of Operations)
When you type a command (e.g., `ping`), the Shell follows this strict priority:

1.  **Hardcoded Aliases:** Checks `cmd_shell.py` (exit, clear, exec, reload).
2.  **System Modules:** Checks `src/commands/cmd_ping.py`.
3.  **Custom Modules:** Checks `src/commands/custom/cmd_ping.py` (Your Playground).
4.  **Magic Commands (JSON):** Checks `data/config/commands.json` (Links to `library/`).
5.  **System Fallback:** If nothing matches, it sends the text to the Host OS.

### The Three Modes of Execution
| Mode | Syntax | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **Smart** | `ping google.com` | Tries Internal -> Magic -> System. | 99% of daily use. |
| **Forced** | `exec ping ...` | Bypasses xsv entirely. Forces Host OS to run it. | Testing or conflicts. |
| **Raw** | `cmd` / `sh` | Drops you into the actual OS terminal. | Complex pipes (`|`), heavy admin work. |

---

## 🧩 2. How to Add Features (The New Way)

### Method A: The Wizard (Recommended)
Don't write files manually. Use the engine.
1.  **Type:** `create command mytool`
2.  **Enter Description:** "My cool tool"
3.  **Paste Code:** Paste your Python logic.
4.  **Result:** Auto-generates `src/commands/custom/cmd_mytool.py` with proper boilerplate.

### Method B: The Library Link (Scripts)
**Best for:** Running a PowerShell/Bash script you found online.
1.  Drop the script into `library/` (e.g., `library/matrix.py`).
2.  Open `data/config/commands.json`.
3.  Add it:
    ```json
    "matrix": {
        "type": "script",
        "path": "library/matrix.py",
        "description": "The Matrix Effect"
    }
    ```

---

## ⚠️ Coding Guidelines (Critical)

### 1. GUI Tools Must Be Threaded
If your command opens a window (like `tkinter` or `pygame`), you **MUST** run it in a separate thread, or it will freeze the Shell.

**Bad Code:**
```python
root = tk.Tk()
root.mainloop() # <--- FREEZES SHELL HERE

```

**Good Code:**

```python
import threading
def popup():
    root = tk.Tk()
    root.mainloop()

t = threading.Thread(target=popup, daemon=True)
t.start() # <--- Shell stays alive

```

### 2. File Paths

Never hardcode `C:\Users`. Always use the `Path` library relative to `__file__`.

```python
PROJECT_ROOT = Path(__file__).parent.parent.parent

```

```

---

### 3. `TODO.md` ( The Worklist )
**Changes:** Massive update. Checked off the entire Phase 1. Added the Pivot explanation.

```markdown
# 📋 Project Worklist

## 🔥 Phase 1: The Foundation (COMPLETED)
- [x] **Modular Architecture:** Core (`src/commands`) vs. Custom (`src/commands/custom`).
- [x] **Dynamic Router:** Auto-loads modules from both locations.
- [x] **Hardware Detective:** `InfoEngine` scans CPU/RAM.
- [x] **Ghost Shell:** Interactive terminal (`xsv@HOST >`) with sticky headers.
- [x] **Launchers:** `LAUNCH.bat` (Windows).
- [x] **The Creator:** `create` command with Dispatcher Pattern (routes to Todo/Journal).
- [x] **The Editor:** `edit` command (detects VS Code/Notepad).
- [x] **Hot Reload:** `reload` command updates code instantly.
- [x] **Safety:** `exec` and `sh` escape hatches.

## 🚧 Phase 2: The Toolbelt (Essential Modules)
* **Current Focus: The Hacker Kit**
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

## 🔭 Phase 3: Expansion (Advanced)
- [ ] **`cmd_gameserver.py`**: Minecraft/Ark installers (Servers go to `data/servers`).
- [ ] **`cmd_ai.py`**: Gemini API hook.
- [ ] **ParrotOS Support**: Verify all scripts on Linux.
- [ ] **Dashboard**: Future GUI skin.

## 📜 Pivot Log (History)
* *Pivoted `DependencyEngine` into `cmd_dev.py` for granular control.*
* *Moved `INSTALL_THIS_PC.bat` logic into internal `setup` command.*
* *Split `src/commands` to protect Core files from User scripts.*

```

