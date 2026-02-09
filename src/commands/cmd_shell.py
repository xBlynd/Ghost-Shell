import sys
import os
import socket
import subprocess
import shlex
import getpass
import importlib
from pathlib import Path

# IMPORT THE NEW CORE
from src.core.host_engine import HostEngine
from src.commands import cmd_launcher

# --- CONFIGURATION ---
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
    print("Type 'reload' to refresh commands after editing.\n")

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

            # --- A. SHELL CONTROLS ---
            if cmd in ["exit", "quit"]:
                print("🔌 Disconnecting...")
                break
            
            if cmd in ["clear", "cls"]:
                HostEngine.clear_screen()
                continue
                
            if cmd == "cd":
                target = cmd_args[0] if cmd_args else "."
                try: os.chdir(target)
                except Exception as e: print(f"❌ {e}")
                continue

            # --- B. RELOAD COMMAND (The Fix) ---
            if cmd == "reload":
                print("♻️  Clearing Python Cache...")
                importlib.invalidate_caches()
                # We can't easily un-import modules in Python without a full restart,
                # but we can force re-import of specific ones if we track them.
                # For now, this clears the finder cache which helps with NEW files.
                print("✅ Cache Cleared. (For modified files, best to restart shell).")
                continue

            # --- C. ESCAPE HATCHES ---
            if cmd == "exec":
                full_cmd = " ".join(parts[1:])
                subprocess.run(full_cmd, shell=True)
                continue

            if cmd in ["sh", "cmd", "bash", "powershell"]:
                try:
                    shell_cmd = "cmd" if os.name == 'nt' else "bash"
                    if cmd == "powershell": shell_cmd = "powershell"
                    subprocess.call(shell_cmd, shell=True)
                except Exception as e: print(f"❌ Error: {e}")
                continue

            # --- D. SMART ROUTING (Core vs Custom) ---
            
            # 1. Check SYSTEM Commands (src/commands/cmd_*.py)
            try:
                module = importlib.import_module(f"src.commands.cmd_{cmd}")
                importlib.reload(module) # Force Reload on Execution
                module.run(cmd_args)
                continue
            except ModuleNotFoundError:
                pass 

            # 2. Check CUSTOM Commands (src/commands/custom/cmd_*.py)
            try:
                module = importlib.import_module(f"src.commands.custom.cmd_{cmd}")
                importlib.reload(module) # Force Reload on Execution
                module.run(cmd_args)
                continue
            except ModuleNotFoundError:
                pass 

            # --- E. ALIASES & MAGIC ---
            if cmd == "info":
                import src.commands.cmd_host as h
                h.run(["info"])
                continue

            launcher = cmd_launcher.Launcher()
            if launcher.run(cmd): continue

            # --- F. FALLBACK ---
            try: subprocess.run(user_input, shell=True)
            except Exception as e: print(f"❌ System Error: {e}")

        except KeyboardInterrupt:
            print("\nType 'exit' to quit.")