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