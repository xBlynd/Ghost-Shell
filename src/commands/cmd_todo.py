"""
Module: todo
Description: Task manager with relative time parsing (e.g., 10m, 1h).
"""
import argparse
from src.core.vault_api import VaultAPI
from src.core.reminder_engine import ReminderEngine

def run(args):
    v = VaultAPI()
    parser = argparse.ArgumentParser(prog="todo")
    parser.add_argument("action", choices=["add", "list", "done", "open"])
    parser.add_argument("title", nargs="?", default="")
    parser.add_argument("--cat", default="work")
    parser.add_argument("--due", default=None)
    
    if not args:
        print("Usage: todo add \"Title\" --due 10m --cat home")
        return

    try: p = parser.parse_args(args)
    except: return

    if p.action == "add":
        # Badass Logic: Parse '10m' into an actual clock time
        final_time = ReminderEngine.parse_time(p.due) if p.due else None
        
        tasks = v.get_tasks(p.cat)
        tasks.append({
            "id": len(tasks) + 1,
            "title": p.title,
            "due_date": final_time,
            "notified": False,
            "status": "pending"
        })
        v.save_tasks(p.cat, tasks)
        print(f"✅ Added: {p.title} (Due: {final_time if final_time else 'N/A'})")

    elif p.action == "list":
        tasks = v.get_tasks(p.cat)
        for t in tasks:
            print(f" {t['id']}. [{'x' if t['status']=='completed' else ' '}] {t['title']} (🔔 {t['due_date']})")