"""
Command: config
Manage Ghost Shell settings — vault path, app paths.
"""

MANIFEST = {
    "name": "config",
    "description": "Manage Ghost Shell settings",
    "version": "1.0.0",
    "usage": "config vault-path [<path>|local] | config apps | config app <name> <exe_path>",
    "author": "xsvStudio",
    "required_role": "ADMIN",
    "engine_deps": [],
}
DESCRIPTION = MANIFEST["description"]
USAGE = MANIFEST["usage"]
REQUIRED_ROLE = MANIFEST["required_role"]

import os
import json


def execute(kernel, args):
    """Manage settings."""
    parts = args.strip().split(None, 2)
    if not parts:
        return _show_usage()

    subcmd = parts[0].lower()

    if subcmd == "vault-path":
        value = parts[1] if len(parts) > 1 else None
        return _cmd_vault_path(kernel, value)

    elif subcmd == "apps":
        return _cmd_list_apps(kernel)

    elif subcmd == "app":
        if len(parts) < 3:
            return "  Usage: config app <name> <exe_path>"
        app_name = parts[1].lower()
        exe_path = parts[2]
        return _cmd_set_app(kernel, app_name, exe_path)

    else:
        return _show_usage()


def _cmd_vault_path(kernel, value):
    """Get or set vault path."""
    settings = _load_settings(kernel)

    if value is None:
        # Show current
        current = settings.get("vault_path") or "(local default)"
        return f"  Vault path: {current}"

    if value.lower() == "local":
        settings["vault_path"] = None
        _save_settings(kernel, settings)
        return "  ✓ Vault path reset to local (data/vault/)"

    # Validate the path
    if not os.path.isdir(value):
        return f"  [!] Path does not exist or is not a directory: {value}"

    settings["vault_path"] = value
    _save_settings(kernel, settings)
    return (
        f"  ✓ Vault path set to: {value}\n"
        "  Note: Restart Ghost Shell to use the new vault location."
    )


def _cmd_list_apps(kernel):
    """List configured app paths."""
    settings = _load_settings(kernel)
    app_paths = settings.get("app_paths", {})

    if not app_paths:
        return (
            "  No app paths configured.\n"
            "  Use: config app <name> <exe_path>\n"
            "  Then: host open <file> --in <name>"
        )

    lines = ["\n  ┌─ APP PATHS ─┐"]
    for name, path in sorted(app_paths.items()):
        lines.append(f"  │ {name:<16} {path}")
    lines.append("  └──────────────┘")
    return "\n".join(lines)


def _cmd_set_app(kernel, app_name, exe_path):
    """Register an app path."""
    settings = _load_settings(kernel)
    if "app_paths" not in settings:
        settings["app_paths"] = {}

    settings["app_paths"][app_name] = exe_path
    _save_settings(kernel, settings)
    return f"  ✓ App '{app_name}' → {exe_path}"


def _load_settings(kernel):
    """Load settings.json, returning defaults if missing."""
    settings_path = os.path.join(kernel.root_dir, "data", "config", "settings.json")
    if os.path.exists(settings_path):
        try:
            with open(settings_path, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {"vault_path": None, "app_paths": {}}


def _save_settings(kernel, settings):
    """Save settings.json."""
    settings_path = os.path.join(kernel.root_dir, "data", "config", "settings.json")
    os.makedirs(os.path.dirname(settings_path), exist_ok=True)
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=2)


def _show_usage():
    return (
        "  Config Commands:\n"
        "    config vault-path             Show current vault path\n"
        "    config vault-path <path>      Set custom vault directory\n"
        "    config vault-path local       Reset to local data/vault/\n"
        "    config apps                   List configured app paths\n"
        "    config app <name> <exe>       Register an app for 'host open --in'"
    )
