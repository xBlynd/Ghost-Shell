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