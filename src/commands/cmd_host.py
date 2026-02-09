import sys
import os
from src.core.host_bridge import HostBridge

def run(args):
    if not args:
        print("Usage:")
        print("  xsv host ls [path]    - List files")
        print("  xsv host open <path>  - Open file/folder")
        print("  xsv host nuke <path>  - FORCE DELETE file/folder")
        print("  xsv host ps           - List Processes")
        print("  xsv host info         - System Stats")
        return

    cmd = args[0].lower()

    # --- LIST FILES ---
    if cmd == "ls":
        target = args[1] if len(args) > 1 else "."
        items = HostBridge.list_path(target)
        
        if items is None:
            print(f"❌ Path not found: {target}")
            return

        print(f"📂 Listing: {os.path.abspath(target)}\n")
        print(f"{'TYPE':<6} {'SIZE (KB)':<10} {'NAME'}")
        print("-" * 40)
        
        for i in items:
            size_str = f"{i['size']/1024:.1f}" if i['type'] == "FILE" else "-"
            icon = "📁" if i['type'] == "DIR" else "📄"
            print(f"{i['type']:<6} {size_str:<10} {icon} {i['name']}")

    # --- OPEN / LAUNCH ---
    elif cmd == "open" or cmd == "launch":
        if len(args) < 2: return
        HostBridge.launch(args[1])

    # --- NUKE (DELETE) ---
    elif cmd == "nuke":
        if len(args) < 2: 
            print("❌ Error: You must specify a target to nuke.")
            return
        
        target = args[1]
        print(f"⚠️  WARNING: You are about to PERMANENTLY DELETE: {target}")
        confirm = input("Are you sure? (yes/no): ")
        
        if confirm.lower() == "yes":
            if HostBridge.nuke_path(target):
                print(f"💥 Nuked: {target}")
            else:
                print("❌ Delete failed.")
        else:
            print("🛑 Operation cancelled.")

    # --- PROCESS LIST ---
    elif cmd == "ps":
        procs = HostBridge.get_processes()
        print(f"⚙️  Running Processes ({len(procs)}):")
        # Show first 15 for brevity
        for p in procs[:15]:
            print(p)
        print("... (use 'tasklist' for full list)")

    # --- INFO ---
    elif cmd == "info":
        info = HostBridge.get_system_info()
        print(f"🖥️  System: {info['os']} {info['release']}")
        print(f"👤 User:   {info['user']}")

    else:
        print(f"❌ Unknown host command: {cmd}")