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