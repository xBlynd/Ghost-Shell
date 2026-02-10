"""
Module: reminder_engine
Description: The active pulse tracker that scans the vault for due tasks.
"""
from datetime import datetime
from src.core.vault_api import VaultAPI

class ReminderEngine:
    @staticmethod
    def check_reminders(test_mode=False):
        """
        Scans all categories. Returns tasks due NOW or OVERDUE.
        """
        if test_mode:
            return [{"category": "SYSTEM", "task": {"title": "TEST ALERT: Engine is Alive!", "id": 999}}]

        v = VaultAPI()
        all_tasks = v.get_all_due_tasks()
        due_now = []
        now = datetime.now()
        
        for item in all_tasks:
            cat = item['category']
            task = item['task']
            
            try:
                # Handle HH:MM format
                due_time = datetime.strptime(task['due_date'], "%H:%M").replace(
                    year=now.year, month=now.month, day=now.day
                )
                
                # TRIGGER: If current time is >= due time and not yet notified
                if now >= due_time and not task.get("notified"):
                    due_now.append(item)
            except:
                continue 
                
        return due_now

    @staticmethod
    def silence(category, task_id):
        if task_id == 999: return # Don't silence the test
        v = VaultAPI()
        tasks = v.get_tasks(category)
        for t in tasks:
            if t['id'] == task_id:
                t['notified'] = True
                break
        v.save_tasks(category, tasks)