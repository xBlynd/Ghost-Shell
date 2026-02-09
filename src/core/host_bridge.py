import os
import sys
import platform
import subprocess
import shutil
import socket
from pathlib import Path

class HostBridge:
    @staticmethod
    def get_os_type():
        """Returns 'windows', 'linux', or 'macos'."""
        system = platform.system().lower()
        if system == "darwin": return "macos"
        return system

    @staticmethod
    def clear_screen():
        command = "cls" if os.name == "nt" else "clear"
        os.system(command)

    @staticmethod
    def launch(path):
        p = Path(path)
        if not p.exists():
            print(f"❌ Error: Path not found: {path}")
            return False
        
        system = HostBridge.get_os_type()
        try:
            if system == "windows":
                os.startfile(p)
            elif system == "linux":
                subprocess.run(["xdg-open", str(p)])
            elif system == "macos":
                subprocess.run(["open", str(p)])
            return True
        except Exception as e:
            print(f"❌ Launch Failed: {e}")
            return False

    @staticmethod
    def list_path(target="."):
        p = Path(target)
        if not p.exists(): return None
        items = []
        try:
            for item in p.iterdir():
                items.append({
                    "name": item.name,
                    "type": "DIR" if item.is_dir() else "FILE",
                    "size": item.stat().st_size if item.is_file() else 0,
                    "path": str(item)
                })
            return sorted(items, key=lambda x: (x["type"] == "FILE", x["name"]))
        except:
            return []

    @staticmethod
    def nuke_path(target):
        p = Path(target)
        if not p.exists(): return False
        try:
            if p.is_dir(): shutil.rmtree(p)
            else: os.remove(p)
            return True
        except: return False

    @staticmethod
    def get_processes():
        system = HostBridge.get_os_type()
        cmd = ["tasklist"] if system == "windows" else ["ps", "-e"]
        try:
            result = subprocess.check_output(cmd, encoding="utf-8", errors="ignore")
            return result.splitlines()
        except:
            return []

    # --- NEW: DEEP SYSTEM SCAN ---
    @staticmethod
    def get_deep_info():
        info = {}
        
        # 1. BASIC OS
        info["os"] = f"{platform.system()} {platform.release()}"
        info["version"] = platform.version()
        info["machine"] = platform.machine()
        info["hostname"] = socket.gethostname()
        info["ip_local"] = socket.gethostbyname(socket.gethostname())
        info["user"] = os.getlogin()

        # 2. DISK SPACE (Current Drive)
        total, used, free = shutil.disk_usage(".")
        info["disk_total"] = f"{total // (2**30)} GB"
        info["disk_free"] = f"{free // (2**30)} GB"

        # 3. CPU & RAM (Windows Specific via WMIC for portability)
        if platform.system() == "Windows":
            try:
                # Get CPU Name
                cpu = subprocess.check_output("wmic cpu get name", shell=True).decode().split('\n')[1].strip()
                info["cpu"] = cpu
                
                # Get RAM
                mem = subprocess.check_output("wmic computersystem get totalphysicalmemory", shell=True).decode().split('\n')[1].strip()
                info["ram_total"] = f"{int(mem) // (1024**3):.1f} GB"
            except:
                info["cpu"] = "Unknown"
                info["ram_total"] = "Unknown"
        else:
            # Linux Placeholder (can expand later)
            info["cpu"] = "Linux CPU"
            info["ram_total"] = "Linux RAM"

        return info