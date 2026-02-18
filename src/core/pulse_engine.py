"""
Engine 06: Pulse Engine - The Heartbeat
=========================================
Background reminders, scheduled tasks, time-based triggers.
Uses daemon threads so it NEVER blocks the main shell or causes lag.

Compartmentalization:
- Runs in isolated daemon thread
- MUST NOT perform blocking I/O
- Communicates via kernel event bus
"""

import threading
import time
import os
import json
import platform
import subprocess
from datetime import datetime


class PulseEngine:
    """The Heartbeat - time and scheduling."""

    ENGINE_NAME = "pulse"
    ENGINE_VERSION = "2.0.0"

    def __init__(self, kernel):
        self.kernel = kernel
        self.root_dir = kernel.root_dir
        self.running = False
        self._thread = None
        self._tasks = []  # List of task dicts
        self._reminders = []  # List of reminder dicts
        self._lock = threading.Lock()
        self._os_type = platform.system().upper()

        # Register built-in periodic tasks
        self.register_task("session_autosave", 300, self._autosave_session)
        self.register_task("reminder_check", 5, self._check_reminders)

        # Load persisted reminders from previous session
        self.load_reminders()

    # =========================================================================
    # PULSE LOOP
    # =========================================================================

    def start(self):
        """Start the pulse loop in a daemon thread."""
        if self.running:
            return

        self.running = True
        self._thread = threading.Thread(
            target=self._pulse_loop,
            daemon=True,
            name="GhostPulse"
        )
        self._thread.start()

    def stop(self):
        """Stop the pulse loop."""
        self.running = False

    def register_task(self, name, interval_seconds, callback):
        """Register a periodic task."""
        with self._lock:
            self._tasks.append({
                "name": name,
                "interval": interval_seconds,
                "callback": callback,
                "last_run": 0,
            })

    def _pulse_loop(self):
        """Main pulse loop - runs in background thread."""
        while self.running:
            now = time.time()

            with self._lock:
                for task in self._tasks:
                    if now - task["last_run"] >= task["interval"]:
                        try:
                            task["callback"]()
                            task["last_run"] = now
                        except Exception:
                            pass

            # Sleep in small increments so we can stop quickly
            for _ in range(10):
                if not self.running:
                    break
                time.sleep(1)

    def _autosave_session(self):
        """Periodic session state save."""
        try:
            self.kernel._save_session()
        except Exception:
            pass

    # =========================================================================
    # REMINDERS
    # =========================================================================

    def add_reminder(self, text, seconds):
        """
        Schedule a reminder to fire in `seconds` seconds.
        Returns the reminder dict.
        """
        fire_at = time.time() + seconds
        reminder = {
            "text": text,
            "fire_at": fire_at,
            "fire_at_str": datetime.fromtimestamp(fire_at).strftime("%H:%M:%S"),
            "fired": False,
            "created": time.time(),
        }
        with self._lock:
            self._reminders.append(reminder)

        self.save_reminders()
        return reminder

    def _check_reminders(self):
        """Check if any reminders are due and fire them."""
        now = time.time()
        fired_any = False

        with self._lock:
            for reminder in self._reminders:
                if not reminder["fired"] and reminder["fire_at"] <= now:
                    reminder["fired"] = True
                    # Fire in a separate thread to avoid blocking pulse loop
                    text = reminder["text"]
                    t = threading.Thread(
                        target=self._fire_reminder,
                        args=(text,),
                        daemon=True,
                    )
                    t.start()
                    fired_any = True

        if fired_any:
            self.save_reminders()

    def _fire_reminder(self, text):
        """Fire a reminder notification. Cross-platform with graceful fallback."""
        if self._os_type == "WINDOWS":
            self._fire_windows(text)
        elif self._os_type == "LINUX":
            self._fire_linux(text)
        else:
            # Android/other — print fallback
            print(f"\a\n  🔔 REMINDER: {text}\n")

    def _fire_windows(self, text):
        """Windows notification: BurntToast → WScript popup → print fallback."""
        # Try BurntToast PowerShell module
        try:
            ps_cmd = (
                f"[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null;"
                f"[System.Windows.Forms.MessageBox]::Show('{text}', 'Ghost Shell Reminder')"
            )
            result = subprocess.Popen(
                ["powershell", "-WindowStyle", "Hidden", "-Command", ps_cmd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return
        except Exception:
            pass

        # Fallback: WScript popup (non-blocking via async)
        try:
            vbs = (
                f'Set objShell = CreateObject("WScript.Shell")\n'
                f'objShell.Popup "{text}", 10, "Ghost Shell Reminder", 64'
            )
            vbs_path = os.path.join(self.root_dir, "data", "cache", "_reminder.vbs")
            os.makedirs(os.path.dirname(vbs_path), exist_ok=True)
            with open(vbs_path, 'w') as f:
                f.write(vbs)
            subprocess.Popen(
                ["cscript", "//nologo", vbs_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return
        except Exception:
            pass

        # Final fallback: print with bell
        print(f"\a\n  🔔 REMINDER: {text}\n")

    def _fire_linux(self, text):
        """Linux notification via notify-send, fallback to print."""
        try:
            subprocess.Popen(
                ["notify-send", "Ghost Shell Reminder", text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return
        except Exception:
            pass

        print(f"\a\n  🔔 REMINDER: {text}\n")

    # =========================================================================
    # REMINDER PERSISTENCE
    # =========================================================================

    def save_reminders(self):
        """Persist reminders to data/session/reminders.json."""
        reminders_file = os.path.join(self.root_dir, "data", "session", "reminders.json")
        os.makedirs(os.path.dirname(reminders_file), exist_ok=True)
        try:
            # Only save reminders that haven't fired yet
            pending = [r for r in self._reminders if not r["fired"]]
            # Remove non-serialisable callback refs (none here, but be safe)
            with open(reminders_file, 'w') as f:
                json.dump(pending, f, indent=2)
        except Exception:
            pass

    def load_reminders(self):
        """Load reminders from data/session/reminders.json."""
        reminders_file = os.path.join(self.root_dir, "data", "session", "reminders.json")
        if not os.path.exists(reminders_file):
            return

        try:
            with open(reminders_file, 'r') as f:
                loaded = json.load(f)
            now = time.time()
            # Only load reminders that haven't passed yet
            valid = [r for r in loaded if r.get("fire_at", 0) > now and not r.get("fired", False)]
            with self._lock:
                self._reminders = valid
        except Exception:
            pass

    def list_reminders(self):
        """Return pending reminders with time remaining."""
        now = time.time()
        pending = []
        with self._lock:
            for r in self._reminders:
                if not r["fired"]:
                    remaining = max(0, r["fire_at"] - now)
                    pending.append({
                        "text": r["text"],
                        "fire_at_str": r["fire_at_str"],
                        "remaining_seconds": int(remaining),
                        "remaining_str": _format_duration(int(remaining)),
                    })
        return sorted(pending, key=lambda x: x["remaining_seconds"])

    def clear_reminders(self):
        """Cancel all pending reminders."""
        with self._lock:
            self._reminders = []
        self.save_reminders()

    # =========================================================================
    # STATUS
    # =========================================================================

    def get_status(self):
        """Return pulse engine status."""
        with self._lock:
            return {
                "running": self.running,
                "thread_alive": self._thread.is_alive() if self._thread else False,
                "registered_tasks": len(self._tasks),
                "pending_reminders": len([r for r in self._reminders if not r["fired"]]),
                "tasks": [
                    {
                        "name": t["name"],
                        "interval_s": t["interval"],
                        "last_run": datetime.fromtimestamp(t["last_run"]).isoformat() if t["last_run"] else "never",
                    }
                    for t in self._tasks
                ],
            }


# ─── helpers ──────────────────────────────────────────────────────────────────

def _format_duration(seconds):
    """Format seconds into human-readable duration string."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{m}m {s}s"
    else:
        h, remainder = divmod(seconds, 3600)
        m, s = divmod(remainder, 60)
        return f"{h}h {m}m"
