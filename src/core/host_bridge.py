import os
import sys
import platform
import subprocess
import shutil
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
        """Clears terminal window."""
        command = "cls" if os.name == "nt" else "clear"
        os.system(command)

    @staticmethod
    def launch(path):
        """Universal 'Open File' command."""
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

    # --- NEW NAVIGATOR FEATURES ---

    @staticmethod
    def list_path(target="."):
        """Returns a list of dictionaries with file info."""
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
            # Sort: Directories first, then files
            return sorted(items, key=lambda x: (x["type"] == "FILE", x["name"]))
        except Exception as e:
            print(f"❌ Error listing directory: {e}")
            return []

    @staticmethod
    def nuke_path(target):
        """Force deletes a file or directory."""
        p = Path(target)
        if not p.exists(): return False
        
        try:
            if p.is_dir():
                shutil.rmtree(p) # Recursive delete
            else:
                os.remove(p)
            return True
        except Exception as e:
            print(f"❌ Nuke Failed: {e}")
            return False

    @staticmethod
    def get_processes():
        """Returns list of running process names (Cross-platformish)."""
        system = HostBridge.get_os_type()
        cmd = ["tasklist"] if system == "windows" else ["ps", "-e"]
        
        try:
            result = subprocess.check_output(cmd, encoding="utf-8")
            return result.splitlines()
        except:
            return []

    @staticmethod
    def get_system_info():
        return {
            "os": platform.system(),
            "release": platform.release(),
            "user": os.getlogin()
        }