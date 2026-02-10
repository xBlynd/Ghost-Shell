"""
Module: todo
Description: Advanced task manager for Work, Home, and xsv projects.
"""
import argparse
import datetime
from src.core.vault_api import VaultAPI
from src.core.host_bridge import HostBridge

def run(args):
    v = VaultAPI()
    
    parser = argparse.ArgumentParser(prog="todo")
    parser.add_argument("action", choices=["add", "list", "done", "del", "open"], nargs="?", default=None)
    parser.add_argument("title", nargs="?", default="")
    parser.add_argument("--cat", default="work")
    parser.add_argument("--due", default=None)
    parser.add_argument("--desc", default="")
    
    if not args:
        print("\n📝 xsv TASK MANAGER")
        print("Usage: todo <add|list|done|open> [args]")
        return

    # Parse args and handle the 'p' definition
    try:
        p = parser.parse_args(args)
    except SystemExit:
        return

    if p.action == "add":
        tasks = v.get_tasks(p.cat)
        new_task = {
            "id": len(tasks) + 1,
            "title": p.title,
            "desc": p.desc,
            "created_at": str(datetime.datetime.now()),
            "due_date": p.due,
            "status": "pending",
            "notified": False
        }
        tasks.append(new_task)
        v.save_tasks(p.cat, tasks)
        print(f"✅ Saved to {p.cat}.")

    elif p.action == "list":
        tasks = v.get_tasks(p.cat)
        print(f"\n📋 {p.cat.upper()} LIST")
        for t in tasks:
            mark = "[x]" if t['status'] == 'completed' else "[ ]"
            due = f" 🔔 {t['due_date']}" if t['due_date'] else ""
            print(f" {t['id']}. {mark} {t['title']}{due}")

    elif p.action == "open":
        file_path = v.folders["todo"] / f"{p.cat.lower()}.json"
        print(f"📂 Opening {p.cat} vault for editing...")
        HostBridge.launch(str(file_path))

    elif p.action == "done":
        tasks = v.get_tasks(p.cat)
        for t in tasks:
            if str(t['id']) == p.title:
                t['status'] = 'completed'
                v.save_tasks(p.cat, tasks)
                print("✅ Task complete.")
                break