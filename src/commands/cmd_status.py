"""
Module: status
Description: Global diagnostic tool with real-time test output and error logging.
"""
import threading
import datetime
from pathlib import Path
from src.core.vault_api import VaultAPI
from src.core.info_engine import InfoEngine

def log_status_error(msg):
    # Log errors to a file for later troubleshooting
    log_path = Path(__file__).parent.parent.parent / "data" / "status_errors.log"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")

def run(args):
    print("\n🔍 xsv COMMAND CENTER - SYSTEM DIAGNOSTICS")
    print("=" * 45)
    
    # 1. CORE ENGINE HEALTH
    v = VaultAPI()
    threads = [t.name for t in threading.enumerate()]
    pulse_active = "ReminderPulse" in threads
    
    print(f"📂 VAULT STORAGE:  {'[ OK ]' if v.vault_dir.exists() else '[ ERROR ]'}")
    print(f"💓 CORE HEARTBEAT: {'[ ACTIVE ]' if pulse_active else '[ STOPPED ]'}")

    # 2. REAL-TIME INTEGRITY TESTING (The "Live Feed")
    print("\n🛠️  RUNNING COMMAND INTEGRITY TESTS...")
    print("-" * 45)
    
    # We pass a simple print function as the streamer
    def streamer(msg): print(msg)
    
    health_report = InfoEngine.verify_all_commands(verbose_callback=streamer)
    
    print("-" * 45)
    print("📊 INTEGRITY SUMMARY:")
    
    all_clear = True
    for category, cmds in health_report.items():
        if not cmds: continue
        broken = [c for c in cmds if "❌" in c[1]]
        
        if not broken:
            print(f"  [{category:<7}] ✅ All {len(cmds)} modules functioning.")
        else:
            all_clear = False
            print(f"  [{category:<7}] ⚠️  {len(broken)} Issues detected.")
            for name, status in broken:
                log_status_error(f"{category} | {name} | {status}")
                print(f"    -> {name:<12} {status}")

    # 3. ENGINE STATUS
    print("\n⚙️  ACTIVE ENGINES:")
    print(f"  Reminders:   [{'ONLINE' if pulse_active else 'OFFLINE'}]")
    print(f"  Diagnostics: [ READY ]")
    
    if not all_clear:
        print("\n⚠️  Errors detected. Check 'data/status_errors.log' for details.")
    print("-" * 45)