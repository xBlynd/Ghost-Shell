import sys
import os
import socket
import subprocess
import shlex
import getpass
import importlib
import json
from pathlib import Path
from src.core.host_engine import HostEngine
from src.commands import cmd_launcher
from src.core.reminder_engine import ReminderEngine

# CONFIG
DEFAULT_USER = "admin"
DEFAULT_PASS = "admin"

def get_version_display():
    try:
        path = Path(__file__).parent.parent.parent / "data" / "version.json"
        if path.exists():
            with open(path, "r") as f:
                d = json.load(f)
                return f"v{d['major']}.{d['minor']}.{d['patch']} (Build {d['build']})"
    except: pass
    return "v6.0-Ghost"

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
    ver_tag = get_version_display()
    
    print(f"\n👻 GHOST SHELL ONLINE [{ver_tag}]")
    print(f"   Target: {username}@{hostname}")
    print("-" * 40)
    print("Type 'help' for options. Type 'exit' to disconnect.")
    print("Type 'reload' to refresh commands after editing.")

    # THE CONSOLIDATED LOOP
    while True:
        try:
            # 1. THE PULSE (Check for real reminders)
            due = ReminderEngine.check_reminders()
            for item in due:
                print(f"\n🔔 [REMINDER] ({item['category'].upper()})")
                print(f"   > {item['task']['title']}")
                ReminderEngine.silence(item['category'], item['task']['id'])

            # 2. THE PROMPT
            cwd = os.getcwd()
            display_cwd = cwd if len(cwd) <= 30 else "..." + cwd[-30:]
            prompt = f"xsv@{hostname} [{display_cwd}] > "
            user_input = input(prompt).strip()
            
            if not user_input: continue

            # 3. INTERNAL ENGINE COMMANDS
            if user_input == "test-pulse":
                due = ReminderEngine.check_reminders(test_mode=True)
                for item in due:
                    print(f"\n🔔 [PULSE CHECK] {item['task']['title']}")
                continue

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

            if cmd == "reload":
                if cmd_args:
                    target = cmd_args[0]
                    found = False
                    for mod_name in list(sys.modules.keys()):
                        if mod_name.endswith(f"cmd_{target}"):
                            try:
                                importlib.reload(sys.modules[mod_name])
                                print(f"✅ Reloaded {mod_name}")
                                found = True
                            except Exception as e: print(f"❌ Error: {e}")
                    if not found: print(f"⚠️  Module '{target}' not in memory.")
                else:
                    importlib.invalidate_caches()
                    print("✅ Global Cache Cleared.")
                continue

            # 4. SMART ROUTING (System -> Custom -> Library -> OS)
            try:
                module = importlib.import_module(f"src.commands.cmd_{cmd}")
                module.run(cmd_args)
                continue
            except ModuleNotFoundError: pass 

            try:
                module = importlib.import_module(f"src.commands.custom.cmd_{cmd}")
                module.run(cmd_args)
                continue
            except ModuleNotFoundError: pass 

            launcher = cmd_launcher.Launcher()
            if launcher.run(cmd, cmd_args): continue

            # 5. FALLBACK (Host OS)
            subprocess.run(user_input, shell=True)

        except KeyboardInterrupt:
            print("\nType 'exit' to quit.")