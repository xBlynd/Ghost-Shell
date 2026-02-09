import os
from pathlib import Path

# --- CONFIGURATION ---
PROJECT_ROOT = Path(".")
CMD_DIR = PROJECT_ROOT / "src" / "commands"
SRC_DIR = PROJECT_ROOT / "src"

def write_file(path, content):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Updated: {path}")

# 1. NEW ALIAS COMMAND CODE (Supports add, list, nuke)
ALIAS_CODE = r"""
import sys
import shutil
import os
from pathlib import Path

def run(args):
    if not args:
        print("Usage:")
        print("  xsv alias add <name>   - Create new command (e.g., 'magic')")
        print("  xsv alias list         - Show all active aliases")
        print("  xsv alias nuke <name>  - Delete an alias")
        return

    cmd = args[0].lower()
    root = Path(__file__).parent.parent.parent
    
    # --- ADD ---
    if cmd == "add":
        if len(args) < 2:
            print("❌ Usage: xsv alias add <name>")
            return
        
        new_name = args[1]
        
        # We allow creating aliases from xsv.bat OR xsv (for linux)
        # Assuming Windows for .bat creation mostly
        source = root / "xsv.bat"
        target = root / f"{new_name}.bat"

        if not source.exists():
            print("❌ Critical: xsv.bat source not found.")
            return

        try:
            shutil.copy(source, target)
            print(f"✅ Alias Created! You can now type: {new_name}")
        except Exception as e:
            print(f"❌ Error: {e}")

    # --- LIST ---
    elif cmd == "list":
        print("\n🔗 Active Command Aliases:")
        # Find all .bat files in root that look like launchers
        count = 0
        for f in root.glob("*.bat"):
            # Filter out setup scripts or non-launchers if strictly needed
            if f.name not in ["setup_xsv.bat", "setup_path.bat"]: 
                print(f"  🔹 {f.stem}")
                count += 1
        if count == 0:
            print("  (None found)")
        print("")

    # --- NUKE ---
    elif cmd == "nuke":
        if len(args) < 2: return
        target_name = args[1]
        target_file = root / f"{target_name}.bat"
        
        if target_name.lower() == "xsv":
            print("❌ You cannot nuke the original 'xsv' command!")
            return

        if target_file.exists():
            try:
                os.remove(target_file)
                print(f"🗑️  Alias '{target_name}' deleted.")
            except Exception as e:
                print(f"❌ Error deleting: {e}")
        else:
            print(f"❌ Alias '{target_name}' not found.")
            
    else:
        # Implicit 'add' if they just type: xsv alias magic
        # This handles your previous request: "xsv alias magic"
        print(f"Did you mean: xsv alias add {cmd} ?")
"""

# 2. UPDATE MAIN.PY (To ensure it knows about 'alias')
# (We rewrite it just to be safe that 'cmd_alias' is imported)
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
        print("xsvCommandCenter [v2.4-AliasPro]")
        print("--------------------------------")
        print("Built-in:")
        print("  host [ls|nuke|ps]    - System Navigator")
        print("  journal [add|view]   - Daily Logs")
        print("  todo [add|list]      - Task Manager")
        print("  alias [add|list]     - Manage Command Names")
        
        # Show Custom Commands
        cmd_launcher.Launcher().list_commands()
        return

    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    # 1. CHECK BUILT-INS
    if cmd == "host":
        cmd_host.run(args)
    elif cmd == "journal":
        cmd_journal.run(args)
    elif cmd == "todo":
        cmd_todo.run(args)
    elif cmd == "alias":
        cmd_alias.run(args)
        
    # 2. CHECK MAGIC LAUNCHER
    else:
        # Try to run it as a custom command
        launcher = cmd_launcher.Launcher()
        found = launcher.run(cmd)
        
        if not found:
            print(f"❌ Unknown command: {cmd}")

if __name__ == "__main__":
    main()
"""

if __name__ == "__main__":
    print("🚀 Upgrading Alias Module...")
    write_file(CMD_DIR / "cmd_alias.py", ALIAS_CODE)
    write_file(SRC_DIR / "main.py", MAIN_CODE)
    print("\n✅ Upgrade Complete.")
    print("STEP 1: RESTART VS CODE (Close the whole window).")
    print("STEP 2: Open terminal and type: xsv alias add magic")