"""
Command: sync
Vault backup (export/import) and SyncThing health check.
"""

MANIFEST = {
    "name": "sync",
    "description": "Vault backup, restore, and sync status",
    "version": "1.0.0",
    "usage": "sync export [path] | sync import <file> | sync status",
    "author": "xsvStudio",
    "required_role": "ADMIN",
    "engine_deps": ["sync", "vault"],
}
DESCRIPTION = MANIFEST["description"]
USAGE = MANIFEST["usage"]
REQUIRED_ROLE = MANIFEST["required_role"]

import os


def execute(kernel, args):
    """Sync operations."""
    sync = kernel.get_engine("sync")
    if not sync:
        return "  [!] Sync engine unavailable"

    parts = args.strip().split(None, 1)
    if not parts:
        return _show_usage()

    subcmd = parts[0].lower()
    rest = parts[1] if len(parts) > 1 else ""

    if subcmd == "export":
        return _cmd_export(sync, rest.strip() or None)
    elif subcmd == "import":
        if not rest.strip():
            return "  Usage: sync import <backup_file.zip>"
        return _cmd_import(sync, rest.strip())
    elif subcmd == "status":
        return _cmd_status(sync)
    else:
        return _show_usage()


def _cmd_export(sync, output_path):
    """Export vault to zip."""
    try:
        result_path = sync.export_vault(output_path=output_path)
        size_kb = os.path.getsize(result_path) // 1024
        return (
            f"  ✓ Vault exported successfully\n"
            f"    File: {result_path}\n"
            f"    Size: {size_kb} KB"
        )
    except Exception as e:
        return f"  [!] Export failed: {e}"


def _cmd_import(sync, zip_path):
    """Import vault from zip with confirmation."""
    if not os.path.exists(zip_path):
        return f"  [!] File not found: {zip_path}"

    print(f"\n  [WARNING] This will restore vault from:")
    print(f"    {zip_path}")
    print("  Current vault will be backed up first.")
    confirm = input("  Type 'yes' to proceed: ").strip().lower()
    if confirm != "yes":
        return "  Import cancelled."

    try:
        result = sync.import_vault(zip_path)
        lines = [
            f"  ✓ Vault restored successfully",
            f"    Files restored: {result['restored_files']}",
            f"    Vault dir:      {result['vault_dir']}",
        ]
        if result.get("backup_path"):
            lines.append(f"    Pre-restore backup: {result['backup_path']}")
        return "\n".join(lines)
    except Exception as e:
        return f"  [!] Import failed: {e}"


def _cmd_status(sync):
    """Show vault sync status."""
    status = sync.check_status()

    lines = ["\n  ┌─ SYNC STATUS ────────────────────────────────┐"]
    lines.append(f"  │ Vault dir:  {status['vault_dir']}")
    lines.append(f"  │ Exists:     {'Yes' if status['vault_exists'] else 'No'}")
    lines.append(f"  │ Portable:   {'Yes (USB)' if status['portable'] else 'No (Local)'}")
    lines.append(f"  │ Queue:      {status['pending_queue']} pending ops")

    if status.get("vault_exists"):
        counts = status.get("file_counts", {})
        lines.append(f"  │ Total files: {counts.get('total', 0)}")

        by_type = counts.get("by_type", {})
        if by_type:
            type_str = "  ".join(f"{k}: {v}" for k, v in sorted(by_type.items()))
            lines.append(f"  │ By type:    {type_str}")

        conflicts = status.get("conflicts", [])
        if conflicts:
            lines.append(f"  │")
            lines.append(f"  │ ⚠ SyncThing conflicts ({len(conflicts)}):")
            for c in conflicts[:5]:
                lines.append(f"  │   {c}")
            if len(conflicts) > 5:
                lines.append(f"  │   ... and {len(conflicts) - 5} more")
        else:
            lines.append("  │ Conflicts:   ✓ None")

    lines.append("  └──────────────────────────────────────────────┘")
    return "\n".join(lines)


def _show_usage():
    return (
        "  Sync Commands:\n"
        "    sync export              Export vault to timestamped zip in cache/\n"
        "    sync export <path>       Export vault to specific location\n"
        "    sync import <file.zip>   Restore vault from backup (with confirmation)\n"
        "    sync status              Show vault health and SyncThing conflicts"
    )
