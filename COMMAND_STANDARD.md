# Ghost Shell Command Standard
# For AI assistants and contributors building commands or library scripts.
# Last Updated: 2026-02-18

---

## Three Tiers of Commands

| Tier | Location | Integration | Use For |
|------|----------|-------------|---------|
| **System** | `src/commands/cmd_*.py` | Full kernel access | Core features — touch carefully |
| **Custom** | `src/commands/custom/cmd_*.py` | Full kernel access | Personal tools — safe to experiment |
| **Library** | `library/*` | None (standalone) | Quick scripts — any language |

**The Promotion Pipeline:**
```
💡 Idea → 📝 Script → 📂 Library (test it) → 🔧 Custom Command → ⚙️ System Command (rare)
```

---

## Custom Command Pattern (Full Integration)

Place in `src/commands/custom/cmd_yourcommand.py`

```python
"""
Command: yourcommand
Brief description of what it does.
"""

MANIFEST = {
    "name": "yourcommand",
    "description": "One-line description shown in help",
    "version": "1.0.0",
    "usage": "yourcommand <args>",
    "author": "your-name",
    "required_role": "GUEST",        # GUEST | ADMIN | GOD
    "engine_deps": ["vault", "root"], # engines this command needs
}

# Keep module-level attrs for backwards compatibility
DESCRIPTION = MANIFEST["description"]
USAGE = MANIFEST["usage"]
REQUIRED_ROLE = MANIFEST["required_role"]


def execute(kernel, args):
    """
    Entry point. ALWAYS named execute(kernel, args).

    Args:
        kernel: GhostKernel instance — your gateway to everything
        args: str — everything after the command name (may be empty string)

    Returns:
        str | None — returned string is printed by shell. Return None to print nothing.
    """
    # Access engines through kernel — NEVER import engines directly
    vault = kernel.get_engine("vault")
    root = kernel.get_engine("root")

    # Always check if engine is available before using it
    if not vault:
        return "[!] Vault engine unavailable"

    # Parse args
    parts = args.strip().split()
    if not parts:
        return f"Usage: {MANIFEST['usage']}"

    # Do your thing
    return "Hello from my command!"
```

---

## MANIFEST Dict Spec

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | str | Yes | Command name (no spaces, lowercase) |
| `description` | str | Yes | One-line description for help menu |
| `version` | str | Yes | Semantic version string |
| `usage` | str | Yes | Usage pattern shown in help |
| `author` | str | No | Creator name/handle |
| `required_role` | str | Yes | `GUEST`, `ADMIN`, or `GOD` |
| `engine_deps` | list | No | Engine names this command needs |

---

## Engine Access Pattern

```python
# CORRECT — always through kernel
vault = kernel.get_engine("vault")
root = kernel.get_engine("root")
pulse = kernel.get_engine("pulse")

# WRONG — never import engines directly
from src.core.vault_engine import VaultEngine  # DO NOT DO THIS
```

Available engines: `ghost_core`, `security`, `heartbeat`, `loader`, `root`,
`pulse`, `vault`, `interface`, `blackbox`, `ghost`, `sync`, `legion`, `eve`

---

## Error Handling Rules

```python
def execute(kernel, args):
    engine = kernel.get_engine("vault")

    # 1. Always check if engine loaded
    if not engine:
        return "[!] Required engine unavailable"

    # 2. Wrap risky operations
    try:
        result = engine.do_something()
    except Exception as e:
        return f"[!] Error: {e}"

    # 3. Never let the command crash the shell
    # Return an error string, never raise unhandled exceptions
    return "Success"
```

---

## Cross-Platform Rules

```python
import platform
import os

os_type = platform.system().upper()  # WINDOWS, LINUX, DARWIN

if os_type == "WINDOWS":
    # Windows-specific logic
    pass
else:
    # Linux/Mac/Android fallback
    pass

# Paths: ALWAYS use pathlib or os.path — never string concat
import pathlib
config_path = pathlib.Path(kernel.root_dir) / "data" / "config" / "settings.json"

# HTTP: ALWAYS use urllib — NEVER use requests library
import urllib.request
response = urllib.request.urlopen("https://example.com")
```

---

## Library Scripts (No Integration Required)

Drop any executable in `library/`. Type its name (without extension) in the shell.

```
library/
├── my_script.py      # Run as: my_script
├── backup.ps1        # Run as: backup
├── deploy.sh         # Run as: deploy
└── tool.bat          # Run as: tool
```

**Rules for library scripts:**
- No engine access (no kernel, no Ghost Shell APIs)
- Any language (.py, .ps1, .sh, .bat, .js, .exe)
- Standalone — must work when run directly
- Args passed through as-is from the shell

---

## Minimal vs Full Example

**Minimal (quick tools):**
```python
MANIFEST = {
    "name": "hello",
    "description": "Say hello",
    "version": "1.0.0",
    "usage": "hello [name]",
    "required_role": "GUEST",
    "engine_deps": [],
}
DESCRIPTION = MANIFEST["description"]
USAGE = MANIFEST["usage"]
REQUIRED_ROLE = MANIFEST["required_role"]

def execute(kernel, args):
    name = args.strip() or "Ghost"
    return f"Hello, {name}!"
```

**Full (production tool):**
```python
"""
Command: notes
Quick note-taking backed by VaultEngine.
"""

MANIFEST = {
    "name": "notes",
    "description": "Quick notes to vault",
    "version": "1.0.0",
    "usage": "notes <text> | notes list | notes clear",
    "author": "xsvStudio",
    "required_role": "GUEST",
    "engine_deps": ["vault"],
}
DESCRIPTION = MANIFEST["description"]
USAGE = MANIFEST["usage"]
REQUIRED_ROLE = MANIFEST["required_role"]


def execute(kernel, args):
    vault = kernel.get_engine("vault")
    if not vault:
        return "[!] Vault unavailable"

    parts = args.strip().split(None, 1)
    subcmd = parts[0].lower() if parts else ""

    if subcmd == "list":
        data = vault.journal_list()
        entries = data.get("entries", [])
        if not entries:
            return "  No notes yet."
        lines = ["\n  ┌─ NOTES ─┐"]
        for e in entries:
            lines.append(f"  │ {e['date']}")
        lines.append("  └─────────┘")
        return "\n".join(lines)

    elif not args.strip():
        return f"Usage: {MANIFEST['usage']}"

    else:
        result = vault.journal_add(args.strip(), tags=["note"])
        return f"  [✓] Note saved ({result['timestamp']})"
```
