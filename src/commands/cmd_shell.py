import sys
import os
import socket
import subprocess
import shlex
import getpass
import importlib
from pathlib import Path
from src.core.host_engine import HostEngine
from src.commands import cmd_launcher

# CONFIG
DEFAULT_USER = "admin"
DEFAULT_PASS = "admin"

def login():
    HostEngine.clear_screen()
    print("🔒 xsvCommandCenter | SECURE SESSION")
    print("-" * 35)
    while True:
        try:
            u = input("User: ")
            p = getpass.getpass("Pass: ")
            if u == DEFAULT_USER and p == DEFAULT_PASS: return True
            print("❌ Access Denied.")
        except KeyboardInterrupt: return False

def run(args):
    if not login(): return
    HostEngine.clear_screen()
    hostname = socket.gethostname()
    username = os.getlogin()
    print(f"\n👻 GHOST SHELL ONLINE")
    print(f"   Target: {username}@{hostname}")
    print("-" * 40)
    print("Type 'help' for options. Type 'exit' to disconnect.")
    print("Type 'reload' to refresh commands after editing.")

    while True:
        try:
            cwd = os.getcwd()
            display_cwd = cwd if len(cwd) <= 30 else "..." + cwd[-30:]
            prompt = f"xsv@{hostname} [{display_cwd}] > "
            user_input = input(prompt).strip()
            if not user_input: continue

            parts = shlex.split(user_input)
            cmd = parts[0].lower()
            cmd_args = parts[1:]

            if cmd in ["exit", "quit"]: break
            if cmd in ["clear", "cls"]: 
                HostEngine.clear_screen()
                continue
            if cmd == "cd":
                try: os.chdir(cmd_args[0] if cmd_args else ".")
                except Exception as e: print(f"❌ {e}")
                continue

            # --- 🔧 RELOAD COMMAND (HOT SWAP) ---
            if cmd == "reload":
                # Option A: Reload Specific Module (e.g., 'reload scare')
                if cmd_args:
                    target = cmd_args[0]
                    print(f"♻️  Reloading module: {target}...")
                    found = False
                    
                    # We scan loaded memory for anything matching 'cmd_target'
                    # This finds 'src.commands.cmd_target' AND 'src.commands.custom.cmd_target'
                    for mod_name in list(sys.modules.keys()):
                        if mod_name.endswith(f"cmd_{target}"):
                            try:
                                importlib.reload(sys.modules[mod_name])
                                print(f"✅ Reloaded {mod_name}")
                                found = True
                            except Exception as e:
                                print(f"❌ Error reloading {mod_name}: {e}")
                    
                    if not found:
                        print(f"⚠️  Module '{target}' is not in memory. (Try running it first, then reload).")
                
                # Option B: Global Reset (e.g., 'reload')
                else:
                    print("♻️  Clearing Global Import Cache...")
                    importlib.invalidate_caches()
                    print("✅ Cache Cleared. New files will now be detected.")
                continue

            # --- ⚡ ESCAPE HATCHES ---
            if cmd == "exec":
                subprocess.run(" ".join(parts[1:]), shell=True)
                continue

            if cmd in ["sh", "cmd", "bash", "powershell"]:
                shell_cmd = "cmd" if os.name == 'nt' else "bash"
                if cmd == "powershell": shell_cmd = "powershell"
                subprocess.call(shell_cmd, shell=True)
                continue

            # --- 🛣️ SMART ROUTING ---
            
            # 1. System Modules (Core)
            try:
                module = importlib.import_module(f"src.commands.cmd_{cmd}")
                module.run(cmd_args)
                continue
            except ModuleNotFoundError: pass 

            # 2. Custom Modules (Your Creations)
            try:
                module = importlib.import_module(f"src.commands.custom.cmd_{cmd}")
                module.run(cmd_args)
                continue
            except ModuleNotFoundError: pass 

            # 3. Aliases (JSON)
            if cmd == "info":
                import src.commands.cmd_host as h
                h.run(["info"])
                continue
            
            # 4. Magic Launcher
            launcher = cmd_launcher.Launcher()
            if launcher.run(cmd): continue

            # 5. Fallback (Host OS)
            try: subprocess.run(user_input, shell=True)
            except Exception as e: print(f"❌ System Error: {e}")

        except KeyboardInterrupt:
            print("\nType 'exit' to quit.")