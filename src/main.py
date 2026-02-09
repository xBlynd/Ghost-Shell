import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.host_bridge import HostBridge
from src.commands import cmd_journal, cmd_todo, cmd_host

def main():
    if len(sys.argv) < 2:
        HostBridge.clear_screen()
        print("xsvCommandCenter [v2.1-Navigator]")
        print("---------------------------------")
        print("Commands:")
        print("  host [ls|nuke|ps]    - System Navigator")
        print("  journal [add|view]   - Daily Logs")
        print("  todo [add|list]      - Task Manager")
        return

    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    if cmd == "host":
        cmd_host.run(args)
    
    elif cmd == "journal":
        cmd_journal.run(args)
    
    elif cmd == "todo":
        cmd_todo.run(args)
        
    else:
        print(f"❌ Unknown command: {cmd}")

if __name__ == "__main__":
    main()