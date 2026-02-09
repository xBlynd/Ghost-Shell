import sys
import os
from src.core.host_bridge import HostBridge

def run(args):
    if not args:
        print("Usage: xsv host [ls|nuke|ps|info]")
        return

    cmd = args[0].lower()

    if cmd == "ls":
        target = args[1] if len(args) > 1 else "."
        items = HostBridge.list_path(target)
        if items is None: return
        print(f"📂 Listing: {os.path.abspath(target)}")
        print(f"{'TYPE':<6} {'SIZE':<10} {'NAME'}")
        print("-" * 40)
        for i in items:
            size = f"{i['size']/1024:.1f} KB" if i['type'] == "FILE" else "-"
            print(f"{i['type']:<6} {size:<10} {i['name']}")

    elif cmd == "nuke":
        if len(args) < 2: return
        target = args[1]
        if input(f"⚠️ NUKE {target}? (y/n): ") == "y":
            HostBridge.nuke_path(target)
            print("💥 Nuked.")

    elif cmd == "ps":
        procs = HostBridge.get_processes()
        print(f"⚙️ Running Processes ({len(procs)}):")
        for p in procs[:15]: print(p)

    # --- UPDATED INFO COMMAND ---
    elif cmd == "info":
        data = HostBridge.get_deep_info()
        
        print("\n🖥️  SYSTEM DIAGNOSTICS")
        print("=" * 40)
        print(f"👑 User:        {data['user']}")
        print(f"🏠 Hostname:    {data['hostname']}")
        print(f"📡 Local IP:    {data['ip_local']}")
        print("-" * 40)
        print(f"💿 OS:          {data['os']} ({data['machine']})")
        print(f"🧠 CPU:         {data['cpu']}")
        print(f"💾 RAM:         {data['ram_total']}")
        print(f"💽 Disk Free:   {data['disk_free']} / {data['disk_total']}")
        print("=" * 40 + "\n")

    elif cmd == "open" or cmd == "launch":
        if len(args) > 1: HostBridge.launch(args[1])
        
    else:
        print("Unknown host command.")