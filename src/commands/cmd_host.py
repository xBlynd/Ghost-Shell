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
        if items is None: 
            print("❌ Path not found.")
            return
        print(f"📂 Listing: {os.path.abspath(target)}")
        print(f"{'TYPE':<6} {'SIZE':<10} {'NAME'}")
        print("-" * 50)
        for i in items:
            size = f"{i['size']/1024:.1f} KB" if i['type'] == "FILE" else "-"
            print(f"{i['type']:<6} {size:<10} {i['name']}")

    elif cmd == "nuke":
        if len(args) < 2: return
        target = args[1]
        if input(f"⚠️ NUKE {target}? (y/n): ") == "y":
            if HostBridge.nuke_path(target): print("💥 Nuked.")
            else: print("❌ Nuke failed.")

    elif cmd == "ps":
        procs = HostBridge.get_processes()
        print(f"⚙️ Running Processes ({len(procs)}):")
        for p in procs[:15]: print(p)

    # --- ENTHUSIAST INFO DISPLAY ---
    elif cmd == "info":
        print("\n⏳ Scanning enthusiast hardware & peripherals...")
        data = HostBridge.get_deep_info()
        
        print("\n" + "="*60)
        print(f"   SYSTEM AUDIT REPORT | {data.get('OS', 'Unknown')}")
        print("="*60)

        print(f"\n🧠 CORE")
        print(f"   CPU:   {data.get('CPU', 'Unknown')}")
        print(f"   Mobo:  {data.get('Mobo', 'Unknown')}")
        print(f"   RAM:   {data.get('RAM_Total', '?')} GB")

        print(f"\n🎮 GRAPHICS")
        gpus = data.get('GPUs', [])
        # Handle single dict or list of dicts
        if isinstance(gpus, dict): gpus = [gpus]
        for g in gpus:
            vram = "Unknown VRAM"
            if g.get('AdapterRAM'):
                try: vram = f"{int(g['AdapterRAM']) // (1024**3)} GB"
                except: pass
            print(f"   • {g.get('Name', 'Unknown GPU')} [{vram}]")

        print(f"\n❄️ COOLING & PERIPHERALS")
        usb = data.get('USB_Devices', [])
        if isinstance(usb, dict): usb = [usb]
        if not usb:
            print("   (No dedicated cooler/hub detected via USB)")
        else:
            for u in usb:
                print(f"   • {u.get('FriendlyName', 'Unknown Device')}")

        print(f"\n☁️ CLOUD DRIVES")
        clouds = data.get('Cloud', [])
        if not clouds:
            print("   (No Cloud Mounts Detected)")
        else:
            for c in clouds:
                print(f"   • {c['name']}: {c['path']}")

        print(f"\n💽 STORAGE")
        disks = data.get('Disks', [])
        if isinstance(disks, dict): disks = [disks]
        for d in disks:
            print(f"   • {d.get('FriendlyName', 'Disk')} ({d.get('MediaType', '')})")

        print("\n" + "="*60 + "\n")

    elif cmd == "open" or cmd == "launch":
        if len(args) > 1: HostBridge.launch(args[1])
        
    else:
        print("Unknown host command.")