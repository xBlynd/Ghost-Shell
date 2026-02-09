import os
import sys
import shutil
from pathlib import Path

# --- CONFIGURATION ---
PROJECT_ROOT = Path(".")
SRC = PROJECT_ROOT / "src"
CORE = SRC / "core"
CMDS = SRC / "commands"

def write_file(path, content):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Created/Updated: {path}")

# ==========================================
# 1. THE DETECTIVE: src/core/info_engine.py
# ==========================================
INFO_ENGINE_CODE = r"""
import platform
import subprocess
import json
import os
from pathlib import Path

class InfoEngine:
    @staticmethod
    def get_cloud_paths():
        """Detects Cloud Storage Mounts"""
        home = Path.home()
        clouds = []
        
        # 1. OneDrive
        onedrive = os.environ.get("OneDrive")
        if onedrive and Path(onedrive).exists():
            clouds.append({"name": "OneDrive", "path": onedrive})
            
        # 2. Google Drive (Virtual G: or Folder)
        gdrive = home / "Google Drive"
        if gdrive.exists(): 
            clouds.append({"name": "Google Drive", "path": str(gdrive)})
        
        # Check for Virtual Drives (G:)
        if os.name == "nt":
            if Path("G:/").exists():
                clouds.append({"name": "Google Drive (Virtual)", "path": "G:/"})

        return clouds

    @staticmethod
    def scan_windows_deep():
        """
        The 'CPU-Z' Style Scanner. 
        Uses raw WMI/CIM queries to get enthusiast details.
        """
        ps_script = r"""
        $ErrorActionPreference = "SilentlyContinue"

        # --- MOTHERBOARD & BIOS ---
        $bios = Get-CimInstance Win32_BIOS
        $base = Get-CimInstance Win32_BaseBoard
        $cs = Get-CimInstance Win32_ComputerSystem

        # --- CPU DETAIL ---
        $cpu = Get-CimInstance Win32_Processor
        
        # --- RAM DETAILED (Stick by Stick) ---
        $mem = Get-CimInstance Win32_PhysicalMemory | Select-Object Manufacturer, PartNumber, Speed, Capacity, DeviceLocator

        # --- GPU DETAILED ---
        $gpu = Get-CimInstance Win32_VideoController | Select-Object Name, VideoProcessor, DriverVersion, AdapterRAM, CurrentRefreshRate

        # --- STORAGE (NVMe/SSD distinction) ---
        $disk = Get-PhysicalDisk | Select-Object FriendlyName, MediaType, BusType, Size, Model, FirmwareVersion

        # --- NETWORK (MAC & Connection) ---
        $net = Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object Name, InterfaceDescription, MacAddress, LinkSpeed

        # --- USB DEVICES (Coolers/Hubs) ---
        # Looking for specific enthusiast gear
        $usb = Get-PnpDevice -Class 'USB', 'HIDClass' -Status 'OK' | Where-Object { $_.FriendlyName -match 'Corsair|NZXT|Liquid|Pump|AIO|Cooler|Hub|Commander|Link|Kraken' } | Select-Object FriendlyName

        $info = @{
            System = @{
                Hostname = $cs.Name
                Model = $cs.Model
                Manufacturer = $cs.Manufacturer
            }
            BIOS = @{
                Version = $bios.SMBIOSBIOSVersion
                Date = $bios.ReleaseDate
                Serial = $bios.SerialNumber
            }
            Mobo = @{
                Make = $base.Manufacturer
                Model = $base.Product
                Serial = $base.SerialNumber
            }
            CPU = @{
                Name = $cpu.Name
                Cores = $cpu.NumberOfCores
                Threads = $cpu.NumberOfLogicalProcessors
                Socket = $cpu.SocketDesignation
            }
            RAM_Sticks = @($mem)
            GPUs = @($gpu)
            Disks = @($disk)
            Network = @($net)
            Cooling = @($usb)
        }
        $info | ConvertTo-Json -Depth 4 -Compress
        """
        try:
            res = subprocess.check_output(["powershell", "-NoProfile", "-Command", ps_script], encoding="utf-8", errors="ignore")
            return json.loads(res)
        except Exception as e:
            return {"Error": str(e)}

    @staticmethod
    def get_report():
        """Orchestrates the scan based on OS"""
        info = {
            "OS_Type": platform.system(),
            "Cloud": InfoEngine.get_cloud_paths(),
            "Data": {}
        }
        
        if info["OS_Type"] == "Windows":
            info["Data"] = InfoEngine.scan_windows_deep()
        elif info["OS_Type"] == "Linux":
            info["Data"] = {"Status": "Basic Linux Scan (TODO: Implement lscpu)"}
            
        return info
"""

# ==========================================
# 2. THE WORKER: src/core/host_engine.py
# ==========================================
HOST_ENGINE_CODE = r"""
import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
from src.core.info_engine import InfoEngine

class HostEngine:
    @staticmethod
    def clear_screen():
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def launch(path):
        """Universal Open/Launch"""
        p = Path(path)
        if not p.exists(): return False
        
        s = platform.system().lower()
        try:
            if s == "windows": os.startfile(p)
            elif s == "darwin": subprocess.run(["open", str(p)])
            else: subprocess.run(["xdg-open", str(p)]) # Linux/ChromeOS
            return True
        except: return False

    @staticmethod
    def list_dir(target="."):
        p = Path(target)
        if not p.exists(): return None
        items = []
        try:
            for i in p.iterdir():
                items.append({
                    "name": i.name, 
                    "type": "DIR" if i.is_dir() else "FILE",
                    "size": i.stat().st_size if i.is_file() else 0
                })
            return sorted(items, key=lambda x: (x["type"]=="FILE", x["name"]))
        except: return []

    @staticmethod
    def nuke(target):
        p = Path(target)
        if not p.exists(): return False
        try:
            if p.is_dir(): shutil.rmtree(p)
            else: os.remove(p)
            return True
        except: return False

    @staticmethod
    def get_procs():
        cmd = ["tasklist"] if os.name == "nt" else ["ps", "-e"]
        try: 
            return subprocess.check_output(cmd, encoding="utf-8", errors="ignore").splitlines()
        except: return []

    @staticmethod
    def run_sys_command(command):
        """Runs a raw system command (ping, ipconfig, etc.) safely"""
        try:
            subprocess.run(command, shell=True)
            return True
        except Exception as e:
            print(f"❌ Execution Error: {e}")
            return False

    @staticmethod
    def get_info():
        return InfoEngine.get_report()
"""

# ==========================================
# 3. THE ROUTER: src/commands/cmd_host.py
# ==========================================
CMD_HOST_CODE = r"""
import sys
import os
from src.core.host_engine import HostEngine

def run(args):
    if not args:
        print("Usage: xsv host <sub-command>")
        print("  ls <path>    - List Files")
        print("  nuke <path>  - Force Delete")
        print("  ps           - Process List")
        print("  info         - Deep Scan")
        print("  cmd <cmd>    - Run System Command (e.g., 'ipconfig')")
        return

    sub_cmd = args[0].lower()
    
    # 1. INFO COMMAND (The Deep Scan)
    if sub_cmd == "info":
        print("\n🔎 Running Deep Hardware Scan (CPU-Z Style)...")
        report = HostEngine.get_info()
        data = report.get("Data", {})
        
        print("\n" + "="*60)
        print(f"   SYSTEM REPORT: {data.get('System', {}).get('Model', 'Unknown PC')}")
        print("="*60)

        # BIOS & MOBO
        print(f"\n📟 MOTHERBOARD")
        mobo = data.get("Mobo", {})
        bios = data.get("BIOS", {})
        print(f"   Board: {mobo.get('Make')} {mobo.get('Model')}")
        print(f"   BIOS:  {bios.get('Version')} (Date: {bios.get('Date')})")
        print(f"   S/N:   {bios.get('Serial')}")

        # CPU
        cpu = data.get("CPU", {})
        print(f"\n🧠 PROCESSOR")
        print(f"   Name:   {cpu.get('Name')}")
        print(f"   Socket: {cpu.get('Socket')}")
        print(f"   Specs:  {cpu.get('Cores')} Cores / {cpu.get('Threads')} Threads")

        # RAM
        print(f"\n💾 MEMORY")
        sticks = data.get("RAM_Sticks", [])
        if isinstance(sticks, dict): sticks = [sticks]
        for s in sticks:
            cap = int(s.get('Capacity', 0)) // (1024**3)
            print(f"   • {s.get('Manufacturer')} {cap}GB @ {s.get('Speed')}MHz ({s.get('PartNumber')})")

        # GPU
        print(f"\n🎮 GRAPHICS")
        gpus = data.get("GPUs", [])
        if isinstance(gpus, dict): gpus = [gpus]
        for g in gpus:
            vram = "Unknown"
            if g.get('AdapterRAM'):
                vram = f"{int(g['AdapterRAM']) // (1024**3)} GB"
            print(f"   • {g.get('Name')} [{vram}]")
            print(f"     Driver: {g.get('DriverVersion')}")

        # STORAGE
        print(f"\n💽 DRIVES")
        disks = data.get("Disks", [])
        if isinstance(disks, dict): disks = [disks]
        for d in disks:
            size_gb = int(d.get('Size', 0)) // (1024**3)
            print(f"   • {d.get('Model')} ({d.get('MediaType')}) - {size_gb} GB")

        # CLOUD
        print(f"\n☁️ CLOUD")
        for c in report.get("Cloud", []):
            print(f"   • {c['name']}: {c['path']}")

        # COOLING
        print(f"\n❄️ ENTHUSIAST USB")
        usb = data.get("Cooling", [])
        if usb:
            if isinstance(usb, dict): usb = [usb]
            for u in usb: print(f"   • {u.get('FriendlyName')}")
        else:
            print("   (No smart devices found)")

        print("\n" + "="*60 + "\n")

    # 2. FILE COMMANDS
    elif sub_cmd == "ls":
        target = args[1] if len(args) > 1 else "."
        items = HostEngine.list_dir(target)
        if items:
            print(f"📂 Listing: {os.path.abspath(target)}")
            print("-" * 40)
            for i in items: 
                icon = "📁" if i['type'] == "DIR" else "📄"
                print(f"{icon} {i['name']}")
            
    elif sub_cmd == "nuke":
        if len(args) > 1: HostEngine.nuke(args[1])

    # 3. SYSTEM COMMANDS
    elif sub_cmd == "ps":
        print("Running Processes:")
        for p in HostEngine.get_procs()[:10]: print(p)

    elif sub_cmd == "cmd" or sub_cmd == "exec":
        full_cmd = " ".join(args[1:])
        HostEngine.run_sys_command(full_cmd)
        
    elif sub_cmd == "open" or sub_cmd == "launch":
        if len(args) > 1: HostEngine.launch(args[1])

    else:
        print(f"❌ Unknown host command: {sub_cmd}")
"""

# ==========================================
# 4. THE UPDATED MAIN: src/main.py
# ==========================================
MAIN_CODE = r"""
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

# IMPORT NEW ENGINE (REPLACED HOST BRIDGE)
from src.core.host_engine import HostEngine
from src.commands import cmd_journal, cmd_todo, cmd_host, cmd_launcher, cmd_alias

def main():
    if len(sys.argv) < 2:
        HostEngine.clear_screen()
        print("xsvCommandCenter [v4.0-Modular]")
        print("-------------------------------")
        print("  host [info|ls|cmd]   - System Tools")
        print("  journal [add|view]   - Daily Logs")
        print("  todo [add|list]      - Task Manager")
        print("  alias [add|list]     - Manage Shortcuts")
        
        # Custom Commands
        cmd_launcher.Launcher().list_commands()
        return

    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    if cmd == "host":
        cmd_host.run(args)
    elif cmd == "journal":
        cmd_journal.run(args)
    elif cmd == "todo":
        cmd_todo.run(args)
    elif cmd == "alias":
        cmd_alias.run(args)
    
    # MAGIC LAUNCHER
    else:
        launcher = cmd_launcher.Launcher()
        found = launcher.run(cmd)
        if not found:
            print(f"❌ Unknown command: {cmd}")

if __name__ == "__main__":
    main()
"""

# ==========================================
# 5. THE UPDATED LAUNCHER: src/commands/cmd_launcher.py
# ==========================================
LAUNCHER_CODE = r"""
import sys
import json
import subprocess
from pathlib import Path
from src.core.host_engine import HostEngine

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
                script_path = self.library_path / Path(cfg['path']).name
                if not script_path.exists():
                    script_path = self.root / cfg['path']
                
                HostEngine.launch(str(script_path))
                
            elif cfg['type'] == 'shell':
                subprocess.run(cfg['cmd'], shell=True)
                
            print("✅ Done.")
        except Exception as e:
            print(f"❌ Error: {e}")
        return True
"""

if __name__ == "__main__":
    print("🏗️  Starting Architecture Upgrade (v4)...")
    
    # 1. Create New Core Files
    write_file(CORE / "info_engine.py", INFO_ENGINE_CODE)
    write_file(CORE / "host_engine.py", HOST_ENGINE_CODE)
    
    # 2. Update Commands & Main
    write_file(CMDS / "cmd_host.py", CMD_HOST_CODE)
    write_file(CMDS / "cmd_launcher.py", LAUNCHER_CODE)
    write_file(SRC / "main.py", MAIN_CODE)
    
    # 3. Clean Up Old Files
    old_bridge = CORE / "host_bridge.py"
    if old_bridge.exists():
        os.remove(old_bridge)
        print("🗑️  Deleted Obsolete: src/core/host_bridge.py")
        
    print("\n✅ UPGRADE COMPLETE.")
    print("   The system is now Modular. You have 'InfoEngine' and 'HostEngine'.")
    print("   Try: .\\magic.bat host info")