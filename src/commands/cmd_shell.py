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
# TODO: Move this to data/config/secrets.json in next update
DEFAULT_USER = "admin"
DEFAULT_PASS = "admin"

def login():
    """Simple Security Check"""
    HostEngine.clear_screen()
    print("🔒 xsvCommandCenter | SECURE SESSION")
    print("-" * 35)
    
    # Simple loop
    while True:
        try:
            u = input("User: ")
            p = getpass.getpass("Pass: ")
            if u == DEFAULT_USER and p == DEFAULT_PASS:
                return True
            print("❌ Access Denied.")
        except KeyboardInterrupt:
            print("\nUse Ctrl+C again to force quit.")
            return False

def get_xsv_modules():
    """Scans src/commands for cmd_*.py"""
    cmd_dir = Path(__file__).parent
    cmds = []
    for f in cmd_dir.glob("cmd_*.py"):
        name = f.stem.replace("cmd_", "")
        if name not in ["launcher", "shell", "__init__"]:
            cmds.append(name)
    return cmds

def run(args):
    # 1. AUTHENTICATE
    if not login(): return

    # 2. INITIALIZE SESSION
    HostEngine.clear_screen()
    hostname = socket.gethostname()
    username = os.getlogin()
    print(f"\n👻 GHOST SHELL ONLINE")
    print(f"   Target: {username}@{hostname}")
    print(f"   Core:   Active")
    print("-" * 40)
    print("Type 'help' for options. Type 'exit' to disconnect.\n")

    # 3. INTERACTIVE LOOP
    while True:
        try:
            # Dynamic Prompt
            cwd = os.getcwd()
            # Shorten path if too long
            if len(cwd) > 30: cwd = "..." + cwd[-30:]
            
            prompt = f"xsv@{hostname} [{cwd}] > "
            user_input = input(prompt).strip()
            
            if not user_input: continue

            # Parse input
            parts = shlex.split(user_input)
            cmd = parts[0].lower()
            cmd_args = parts[1:]

            # --- A. SHELL COMMANDS ---
            if cmd in ["exit", "quit", "logout"]:
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

            # --- B. XSV MODULES (host, journal, todo) ---
            # We look for cmd_{cmd}.py
            module_name = f"src.commands.cmd_{cmd}"
            try:
                module = importlib.import_module(module_name)
                # Success! It's a module. Run it.
                module.run(cmd_args)
                continue
            except ModuleNotFoundError:
                pass # Not a module, keep checking

            # --- C. MAGIC COMMANDS (commands.json) ---
            launcher = cmd_launcher.Launcher()
            if launcher.run(cmd):
                continue

            # --- D. ALIASES FOR CONVENIENCE ---
            # You asked to just type 'info' instead of 'host info'
            if cmd == "info":
                # Route 'info' directly to 'host info'
                import src.commands.cmd_host as h
                h.run(["info"])
                continue
                
            if cmd == "ps":
                import src.commands.cmd_host as h
                h.run(["ps"])
                continue

            # --- E. HOST OS COMMANDS ---
            # If nothing else matches, run it as a Windows/Linux command
            try:
                subprocess.run(user_input, shell=True)
            except Exception as e:
                print(f"❌ System Error: {e}")

        except KeyboardInterrupt:
            print("\nType 'exit' to quit.")