"""
Command: remind
Fire-and-forget reminders via PulseEngine. Cross-platform toast notifications.
"""

MANIFEST = {
    "name": "remind",
    "description": "Set a reminder with toast notification",
    "version": "1.0.0",
    "usage": 'remind "message" <30s|15m|1h> | remind list | remind clear',
    "author": "xsvStudio",
    "required_role": "GUEST",
    "engine_deps": ["pulse"],
}
DESCRIPTION = MANIFEST["description"]
USAGE = MANIFEST["usage"]
REQUIRED_ROLE = MANIFEST["required_role"]

import shlex


def execute(kernel, args):
    """Manage reminders."""
    pulse = kernel.get_engine("pulse")
    if not pulse:
        return "  [!] Pulse engine unavailable"

    stripped = args.strip()
    if not stripped:
        return _show_usage()

    # Subcommands: list, clear
    if stripped.lower() == "list":
        return _cmd_list(pulse)
    if stripped.lower() == "clear":
        pulse.clear_reminders()
        return "  ✓ All pending reminders cleared"

    # remind "message" <duration>
    return _cmd_set(pulse, stripped)


def _cmd_set(pulse, args):
    """Parse and set a new reminder."""
    # Try to split into quoted message + duration
    # Formats: "message" 30s | message 30s (no quotes if single word)
    parts = None

    if args.startswith('"') or args.startswith("'"):
        # Quoted message
        try:
            parts = shlex.split(args)
        except ValueError as e:
            return f"  [!] Parse error: {e}"
    else:
        parts = args.split()

    if len(parts) < 2:
        return _show_usage()

    duration_str = parts[-1]
    message = " ".join(parts[:-1]).strip('"\'')

    if not message:
        return "  [!] Message cannot be empty"

    seconds = _parse_duration(duration_str)
    if seconds is None:
        return (
            f"  [!] Invalid duration: '{duration_str}'\n"
            "  Examples: 30s, 15m, 1h, 2h30m"
        )

    reminder = pulse.add_reminder(message, seconds)
    return (
        f"  ✓ Reminder set for {reminder['fire_at_str']}\n"
        f"    \"{message}\" (in {_format_duration(seconds)})"
    )


def _cmd_list(pulse):
    """List pending reminders."""
    pending = pulse.list_reminders()
    if not pending:
        return "  No pending reminders."

    lines = [f"\n  ┌─ REMINDERS ({len(pending)}) ─┐"]
    for r in pending:
        lines.append(f"  │ [{r['fire_at_str']}] in {r['remaining_str']}: {r['text']}")
    lines.append("  └────────────────────┘")
    return "\n".join(lines)


def _parse_duration(s):
    """
    Parse duration string into seconds.
    Supports: 30s, 15m, 1h, 2h30m, 90
    Returns int seconds or None on error.
    """
    s = s.strip().lower()
    if not s:
        return None

    # Pure number = seconds
    if s.isdigit():
        return int(s)

    total = 0
    current = ""

    for ch in s:
        if ch.isdigit():
            current += ch
        elif ch == 's':
            if current:
                total += int(current)
                current = ""
        elif ch == 'm':
            if current:
                total += int(current) * 60
                current = ""
        elif ch == 'h':
            if current:
                total += int(current) * 3600
                current = ""
        else:
            return None  # Invalid character

    if current:
        # Trailing number without unit = seconds
        total += int(current)

    return total if total > 0 else None


def _format_duration(seconds):
    """Format seconds as human-readable string."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{m}m {s}s" if s else f"{m}m"
    else:
        h, remainder = divmod(seconds, 3600)
        m, _ = divmod(remainder, 60)
        return f"{h}h {m}m" if m else f"{h}h"


def _show_usage():
    return (
        '  Usage:\n'
        '    remind "Call Ian" 15m          Set a reminder in 15 minutes\n'
        '    remind "Check server" 1h30m    Hours and minutes combined\n'
        '    remind "Quick note" 30s        Seconds\n'
        '    remind list                    Show pending reminders\n'
        '    remind clear                   Cancel all reminders'
    )
