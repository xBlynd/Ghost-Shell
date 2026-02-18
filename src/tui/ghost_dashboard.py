"""
Ghost Shell Dashboard — Textual TUI
======================================
Live system dashboard with engine status, todos, reminders, and recent journal.
Requires: pip install textual

This module is ONLY imported when textual is available (checked by cmd_dashboard).
"""

import time
from datetime import datetime

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable, Label
from textual.containers import Horizontal, Vertical
from textual import work


class EngineStatusPanel(Static):
    """Panel showing engine load status."""

    def __init__(self, kernel, **kwargs):
        super().__init__(**kwargs)
        self.kernel = kernel

    def render(self):
        lines = ["[bold]Engines[/bold]"]
        for name, engine in self.kernel.engines.items():
            status = "✓" if engine is not None else "✗"
            color = "green" if engine is not None else "red"
            ver = getattr(engine, "ENGINE_VERSION", "?") if engine else "—"
            lines.append(f"[{color}]{status}[/{color}] {name:<14} v{ver}")
        return "\n".join(lines)


class TodoPanel(Static):
    """Panel showing active todos."""

    def __init__(self, kernel, **kwargs):
        super().__init__(**kwargs)
        self.kernel = kernel

    def render(self):
        vault = self.kernel.get_engine("vault")
        if not vault:
            return "[dim]Vault unavailable[/dim]"

        result = vault.todo_list()
        items = result.get("items", [])
        if not items:
            return "[bold]Todos[/bold]\n[dim](none)[/dim]"

        lines = ["[bold]Todos[/bold]"]
        for item in items[:8]:
            priority = item.get("priority", "normal")
            color = "red" if priority == "critical" else "yellow" if priority == "high" else "white"
            lines.append(f"[{color}]○[/{color}] #{item['id']} {item['text'][:45]}")
        if len(items) > 8:
            lines.append(f"[dim]... and {len(items) - 8} more[/dim]")
        return "\n".join(lines)


class ReminderPanel(Static):
    """Panel showing pending reminders with countdown."""

    def __init__(self, kernel, **kwargs):
        super().__init__(**kwargs)
        self.kernel = kernel

    def render(self):
        pulse = self.kernel.get_engine("pulse")
        if not pulse:
            return "[dim]Pulse unavailable[/dim]"

        pending = pulse.list_reminders()
        if not pending:
            return "[bold]Reminders[/bold]\n[dim](none)[/dim]"

        lines = ["[bold]Reminders[/bold]"]
        for r in pending[:5]:
            lines.append(f"⏰ [{r['fire_at_str']}] in {r['remaining_str']}: {r['text'][:40]}")
        return "\n".join(lines)


class SystemInfoPanel(Static):
    """Panel showing system info."""

    def __init__(self, kernel, **kwargs):
        super().__init__(**kwargs)
        self.kernel = kernel

    def render(self):
        core = self.kernel.get_engine("ghost_core")
        heartbeat = self.kernel.get_engine("heartbeat")

        lines = ["[bold]System[/bold]"]

        if core:
            state = core.get_state()
            lines.append(f"OS:      {state['os']} ({state['hostname']})")
            lines.append(f"Node:    {state['node_id']}")
            lines.append(f"Python:  {state['python']}")

        if heartbeat:
            health = heartbeat.check_health()
            lines.append(f"Uptime:  {health['uptime_seconds']}s")
            lines.append(f"Threads: {health['threads']}")
            lines.append(f"Status:  {health['status']}")
            mem = health.get("memory", {})
            if mem.get("rss_mb") != "unknown":
                lines.append(f"Memory:  {mem.get('rss_mb', '?')} MB")

        lines.append(f"Time:    {datetime.now().strftime('%H:%M:%S')}")
        return "\n".join(lines)


class JournalPanel(Static):
    """Panel showing recent journal entries."""

    def __init__(self, kernel, **kwargs):
        super().__init__(**kwargs)
        self.kernel = kernel

    def render(self):
        vault = self.kernel.get_engine("vault")
        if not vault:
            return "[dim]Vault unavailable[/dim]"

        result = vault.journal_list(last_n=3)
        entries = result.get("entries", [])
        if not entries:
            return "[bold]Journal[/bold]\n[dim](no entries)[/dim]"

        lines = ["[bold]Journal[/bold]"]
        for e in entries:
            lines.append(f"📓 {e['date']}  ({e['size_bytes']} bytes)")
        return "\n".join(lines)


class GhostDashboardApp(App):
    """Ghost Shell Live Dashboard — powered by Textual."""

    CSS = """
    Screen {
        background: $surface;
    }
    EngineStatusPanel {
        border: solid $primary;
        padding: 1;
        width: 30%;
        height: 100%;
    }
    TodoPanel {
        border: solid $success;
        padding: 1;
        width: 35%;
        height: 50%;
    }
    ReminderPanel {
        border: solid $warning;
        padding: 1;
        width: 35%;
        height: 50%;
    }
    SystemInfoPanel {
        border: solid $accent;
        padding: 1;
        width: 35%;
        height: 50%;
    }
    JournalPanel {
        border: solid $primary-darken-1;
        padding: 1;
        width: 35%;
        height: 50%;
    }
    """

    TITLE = "Ghost Shell Phoenix Dashboard"
    SUB_TITLE = "v6.5 — Press Q to quit"
    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self, kernel, **kwargs):
        super().__init__(**kwargs)
        self.kernel = kernel

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield EngineStatusPanel(self.kernel, id="engines")
            with Vertical():
                with Horizontal():
                    yield SystemInfoPanel(self.kernel, id="sysinfo")
                    yield TodoPanel(self.kernel, id="todos")
                with Horizontal():
                    yield ReminderPanel(self.kernel, id="reminders")
                    yield JournalPanel(self.kernel, id="journal")
        yield Footer()

    def on_mount(self):
        """Start auto-refresh on mount."""
        self.set_interval(5, self._refresh_all)

    def _refresh_all(self):
        """Refresh all panels."""
        for panel_id in ("engines", "sysinfo", "todos", "reminders", "journal"):
            panel = self.query_one(f"#{panel_id}")
            if panel:
                panel.refresh()
