"""
Command: host
Host file system navigator — ls, cd, pwd, open, find, nuke.
"""

MANIFEST = {
    "name": "host",
    "description": "Navigate the host file system",
    "version": "1.0.0",
    "usage": "host ls | host cd <path> | host pwd | host open <file> | host find <pattern> | host nuke <path>",
    "author": "xsvStudio",
    "required_role": "GUEST",
    "engine_deps": ["ghost_core"],
}
DESCRIPTION = MANIFEST["description"]
USAGE = MANIFEST["usage"]
REQUIRED_ROLE = MANIFEST["required_role"]

import os
import glob
import platform
import pathlib
import json
from datetime import datetime


def execute(kernel, args):
    """Host file system navigation."""
    core = kernel.get_engine("ghost_core")
    if not core:
        return "  [!] GhostCore engine unavailable"

    parts = args.strip().split(None, 1)
    if not parts:
        return _show_usage()

    subcmd = parts[0].lower()
    rest = parts[1] if len(parts) > 1 else ""

    if subcmd in ("ls", "dir"):
        return _cmd_ls(core, rest)
    elif subcmd == "cd":
        return _cmd_cd(core, rest)
    elif subcmd == "pwd":
        return _cmd_pwd(core)
    elif subcmd == "open":
        return _cmd_open(core, kernel, rest)
    elif subcmd == "find":
        return _cmd_find(core, rest)
    elif subcmd == "nuke":
        return _cmd_nuke(kernel, rest)
    else:
        return _show_usage()


# ─── ls ───────────────────────────────────────────────────────────────────────

def _cmd_ls(core, path_arg):
    """List files in current (or specified) directory."""
    if path_arg.strip():
        target = pathlib.Path(path_arg.strip())
        if not target.is_absolute():
            target = pathlib.Path(core.get_cwd()) / target
    else:
        target = pathlib.Path(core.get_cwd())

    if not target.exists():
        return f"  [!] Path not found: {target}"
    if not target.is_dir():
        return f"  [!] Not a directory: {target}"

    try:
        entries = sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except PermissionError:
        return f"  [!] Permission denied: {target}"

    if not entries:
        return f"  (empty directory: {target})"

    lines = [f"\n  ┌─ {target} ─┐"]
    lines.append(f"  │ {'Name':<35} {'Type':<6} {'Size':>10}  {'Modified'}")
    lines.append(f"  │ {'─'*35} {'─'*6} {'─'*10}  {'─'*16}")

    for entry in entries:
        try:
            stat = entry.stat()
            if entry.is_dir():
                ftype = "DIR"
                size_str = ""
            else:
                ftype = entry.suffix[1:].upper()[:6] if entry.suffix else "FILE"
                size_str = _format_size(stat.st_size)
            mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            name = entry.name
            if len(name) > 34:
                name = name[:31] + "..."
            lines.append(f"  │ {name:<35} {ftype:<6} {size_str:>10}  {mtime}")
        except Exception:
            lines.append(f"  │ {entry.name}")

    lines.append(f"  └─ {len(entries)} items ─┘")
    return "\n".join(lines)


# ─── cd ───────────────────────────────────────────────────────────────────────

def _cmd_cd(core, path_arg):
    """Change current working directory."""
    if not path_arg.strip():
        return f"  Usage: host cd <path>\n  Current: {core.get_cwd()}"

    path_str = path_arg.strip()
    current = pathlib.Path(core.get_cwd())

    if path_str == "..":
        new_path = current.parent
    elif path_str == "~":
        new_path = pathlib.Path.home()
    elif path_str == "-":
        # Can't easily track previous dir without more state — just go to root
        new_path = current.anchor
    elif pathlib.Path(path_str).is_absolute():
        new_path = pathlib.Path(path_str)
    else:
        new_path = current / path_str

    success, result = core.set_cwd(str(new_path))
    if success:
        return f"  → {result}"
    return f"  [!] {result}"


# ─── pwd ──────────────────────────────────────────────────────────────────────

def _cmd_pwd(core):
    """Print current working directory."""
    return f"  {core.get_cwd()}"


# ─── open ─────────────────────────────────────────────────────────────────────

def _cmd_open(core, kernel, args):
    """Open a file with default or specified application."""
    import subprocess

    parts = args.strip().split()
    if not parts:
        return "  Usage: host open <file> [--in vscode|excel|obsidian|notepad]"

    # Parse --in flag
    app_name = None
    if "--in" in parts:
        idx = parts.index("--in")
        if idx + 1 < len(parts):
            app_name = parts[idx + 1].lower()
            parts = parts[:idx] + parts[idx + 2:]

    file_arg = " ".join(parts)
    file_path = pathlib.Path(file_arg)
    if not file_path.is_absolute():
        file_path = pathlib.Path(core.get_cwd()) / file_path

    if not file_path.exists():
        return f"  [!] File not found: {file_path}"

    os_type = platform.system().upper()

    if app_name:
        # Load app paths from settings.json
        app_exe = _get_app_path(kernel, app_name, os_type)
        if not app_exe:
            return f"  [!] App '{app_name}' not configured. Use: config app {app_name} <exe_path>"
        try:
            subprocess.Popen([app_exe, str(file_path)])
            return f"  ✓ Opened {file_path.name} in {app_name}"
        except Exception as e:
            return f"  [!] Failed to open with {app_name}: {e}"
    else:
        # Default OS handler
        try:
            if os_type == "WINDOWS":
                os.startfile(str(file_path))
            elif os_type == "DARWIN":
                subprocess.Popen(["open", str(file_path)])
            else:
                subprocess.Popen(["xdg-open", str(file_path)])
            return f"  ✓ Opened {file_path.name}"
        except Exception as e:
            return f"  [!] Failed to open: {e}"


def _get_app_path(kernel, app_name, os_type):
    """Look up app exe path from settings.json, with sensible defaults."""
    # Sensible defaults
    defaults_windows = {
        "vscode": r"C:\Users\Blynd\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        "notepad": "notepad.exe",
        "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
        "obsidian": r"C:\Users\Blynd\AppData\Local\Obsidian\Obsidian.exe",
    }
    defaults_linux = {
        "vscode": "code",
        "notepad": "gedit",
        "obsidian": "obsidian",
    }

    # Try settings.json first
    settings_path = os.path.join(kernel.root_dir, "data", "config", "settings.json")
    if os.path.exists(settings_path):
        try:
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            app_paths = settings.get("app_paths", {})
            if app_name in app_paths:
                return app_paths[app_name]
        except Exception:
            pass

    # Fall back to defaults
    if os_type == "WINDOWS":
        return defaults_windows.get(app_name)
    else:
        return defaults_linux.get(app_name)


# ─── find ─────────────────────────────────────────────────────────────────────

def _cmd_find(core, pattern):
    """Find files matching a glob pattern in cwd subtree."""
    if not pattern.strip():
        return "  Usage: host find <pattern>\n  Example: host find *.py"

    cwd = core.get_cwd()
    search_pattern = os.path.join(cwd, "**", pattern.strip())

    try:
        matches = glob.glob(search_pattern, recursive=True)
    except Exception as e:
        return f"  [!] Find error: {e}"

    if not matches:
        return f"  No matches for '{pattern}' in {cwd}"

    lines = [f"\n  Found {len(matches)} match(es) for '{pattern}':"]
    for m in sorted(matches)[:50]:  # cap at 50 results
        rel = os.path.relpath(m, cwd)
        lines.append(f"    {rel}")

    if len(matches) > 50:
        lines.append(f"  ... and {len(matches) - 50} more")

    return "\n".join(lines)


# ─── nuke ─────────────────────────────────────────────────────────────────────

def nuke_requires_admin():
    """Marker — nuke needs ADMIN role."""
    pass


def _cmd_nuke(kernel, path_arg):
    """Delete a file or directory (ADMIN role required)."""
    import shutil

    # Role check
    sec = kernel.get_engine("security")
    if sec and not sec.has_permission("ADMIN"):
        return "  [!] Access Denied. nuke requires ADMIN role."

    if not path_arg.strip():
        return "  Usage: host nuke <file_or_dir>"

    core = kernel.get_engine("ghost_core")
    file_path = pathlib.Path(path_arg.strip())
    if core and not file_path.is_absolute():
        file_path = pathlib.Path(core.get_cwd()) / file_path

    if not file_path.exists():
        return f"  [!] Not found: {file_path}"

    # Confirmation prompt
    print(f"\n  [WARNING] About to permanently delete:")
    print(f"    {file_path}")
    confirm = input("  Type 'yes' to confirm: ").strip().lower()
    if confirm != "yes":
        return "  Nuke cancelled."

    try:
        if file_path.is_dir():
            shutil.rmtree(file_path)
            return f"  ✓ Directory deleted: {file_path}"
        else:
            file_path.unlink()
            return f"  ✓ File deleted: {file_path}"
    except Exception as e:
        return f"  [!] Delete failed: {e}"


# ─── helpers ──────────────────────────────────────────────────────────────────

def _format_size(size_bytes):
    """Format byte count as human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.1f} MB"
    else:
        return f"{size_bytes / 1024 ** 3:.1f} GB"


def _show_usage():
    return (
        "  Host Navigator:\n"
        "    host ls [path]          List directory contents\n"
        "    host cd <path>          Change directory (supports .., ~, absolute)\n"
        "    host pwd                Show current directory\n"
        "    host open <file>        Open file with default app\n"
        "    host open <file> --in vscode|notepad|excel|obsidian\n"
        "    host find <pattern>     Search for files (e.g., *.py)\n"
        "    host nuke <path>        Delete file/dir (ADMIN, with confirmation)"
    )
