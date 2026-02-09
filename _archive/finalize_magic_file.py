import sys
import json
import shutil
from pathlib import Path

# --- CONFIGURATION ---
PROJECT_ROOT = Path(".")
SRC = PROJECT_ROOT / "src"
CMDS = SRC / "commands"
CONFIG = PROJECT_ROOT / "data" / "config"

def write_file(path, content):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Verified: {path}")

# 1. THE CONFIG FILE (commands.json)
# This is where you edit your custom commands!
JSON_CONTENT = r"""
{
  "commands": {
    "ping": {
      "type": "shell",
      "cmd": "ping google.com",
      "description": "Test Internet Connection"
    },
    "restore": {
      "type": "script",
      "path": "library/restore_xsv.ps1",
      "description": "Run the Restore Script"
    },
    "matrix": {
      "type": "script",
      "path": "library/matrix.py",
      "description": "Run the Matrix Prank"
    }
  }
}
"""

# 2. THE LAUNCHER LOGIC (cmd_launcher.py)
LAUNCHER_CODE = r"""
import sys
import json
import subprocess
from pathlib import Path
from src.core.host_bridge import HostBridge

class Launcher:
    def __init__(self):
        self.root = Path(__file__).parent.parent.parent
        self.config_path = self.root / "data" / "config" / "commands.json"
        self.library_path = self.root / "library"

    def load_commands(self):
        if not self.config_path.exists(): return {}
        try:
            with open(self.config_path, "r") as f:
                return json.load(f).get("commands", {})
        except: return {}

    def list_commands(self):
        cmds = self.load_commands()
        if not cmds: return
        print("\n⚡ MAGIC COMMANDS (commands.json):")
        print(f"{'COMMAND':<15} {'DESCRIPTION'}")
        print("-" * 40)
        for name, data in cmds.items():
            print(f"{name:<15} {data.get('description', '')}")
        print("")

    def run(self, command_name):
        commands = self.load_commands()
        if command_name not in commands: return False

        cfg = commands[command_name]
        print(f"🚀 Launching: {cfg.get('description', command_name)}...")

        if cfg.get("confirm", False):
            if input("⚠️  Are you sure? (y/n): ").lower() != "y":
                print("🛑 Cancelled.")
                return True

        try:
            if cfg['type'] == 'script':
                # Check library first, then relative path
                script_path = self.library_path / Path(cfg['path']).name
                if not script_path.exists():
                    script_path = self.root / cfg['path']
                
                HostBridge.launch(str(script_path))
                
            elif cfg['type'] == 'shell':
                subprocess.run(cfg['cmd'], shell=True)
                
            print("✅ Done.")
        except Exception as e:
            print(f"❌ Error: {e}")
        return True
"""

# 3. THE MAIN ROUTER (main.py)
# Wires everything together (Host, Journal, Todo, Alias, Magic)
MAIN_CODE = r"""
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.host_bridge import HostBridge
from src.commands import cmd_journal, cmd_todo, cmd_host, cmd_launcher, cmd_alias

def main():
    if len(sys.argv) < 2:
        HostBridge.clear_screen()
        print("xsvCommandCenter [v2.5-Magic]")
        print("-----------------------------")
        print("  host [info|ls]       - System Tools")
        print("  journal [add|view]   - Daily Logs")
        print("  todo [add|list]      - Task Manager")
        print("  alias [add|list]     - Manage Shortcuts")
        
        # List Custom Commands from JSON
        cmd_launcher.Launcher().list_commands()
        return

    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    # 1. BUILT-IN COMMANDS
    if cmd == "host":
        cmd_host.run(args)
    elif cmd == "journal":
        cmd_journal.run(args)
    elif cmd == "todo":
        cmd_todo.run(args)
    elif cmd == "alias":
        cmd_alias.run(args)
        
    # 2. MAGIC LAUNCHER (The Fallback)
    else:
        launcher = cmd_launcher.Launcher()
        found = launcher.run(cmd)
        
        if not found:
            print(f"❌ Unknown command: '{cmd}'")
            print("   (Edit data/config/commands.json to add it!)")

if __name__ == "__main__":
    main()
"""

if __name__ == "__main__":
    print("🪄 Finalizing Magic File System...")
    write_file(CONFIG / "commands.json", JSON_CONTENT)
    write_file(CMDS / "cmd_launcher.py", LAUNCHER_CODE)
    write_file(SRC / "main.py", MAIN_CODE)
    print("\n✅ Magic File System is LIVE.")
    print("TRY THIS: .\\magic.bat ping")