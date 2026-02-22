"""
Command: mc
Minecraft launcher and instance management.

Usage:
  mc prism instances                      → list Prism Launcher instances
  mc prism backup                         → ALL instances → Desktop
  mc prism backup vault                   → ALL instances → Vault
  mc prism backup "Minecraft PVP"         → single instance → Desktop
  mc prism backup "Minecraft PVP" vault   → single instance → Vault
  mc prism restore vault                  → latest ZIP from vault
  mc prism restore <path>                 → specific ZIP file
  mc prism launch                         → open Prism Launcher GUI
  mc prism launch "Minecraft PVP"         → launch specific instance
  mc server list                          → stub (expandable)
  mc server backup                        → stub (expandable)
  mc server start [name]                  → stub (expandable)
"""

import os
import shutil
import subprocess
import zipfile
import platform
import tempfile
from datetime import datetime
from pathlib import Path

DESCRIPTION = "Minecraft launcher and instance management (Prism, server stubs)"
USAGE = "mc <launcher|server> <subcommand> [args]"
REQUIRED_ROLE = "GUEST"
ENGINE_DEPS = ["vault"]

MANIFEST = {
    "name": "mc",
    "description": DESCRIPTION,
    "usage": USAGE,
    "required_role": REQUIRED_ROLE,
    "engine_deps": ENGINE_DEPS,
}

_USAGE_TEXT = """  mc — Minecraft Manager

  mc prism instances                       list all Prism instances
  mc prism backup                          ALL instances → Desktop
  mc prism backup vault                    ALL instances → Vault
  mc prism backup "<name>"                 single instance → Desktop
  mc prism backup "<name>" vault           single instance → Vault
  mc prism restore vault                   latest ZIP from vault
  mc prism restore <path>                  specific ZIP file
  mc prism launch                          open Prism Launcher GUI
  mc prism launch "<name>"                 launch specific instance

  mc server list                           list servers (stub)
  mc server backup                         backup server (stub)
  mc server start [name]                   start server (stub)"""

_DEST_KEYWORDS = {"vault"}
_DOC_FILES = {"MOD_LIST.txt", "RESTORE_INSTRUCTIONS.txt", "JAVA_ARGS.txt", "instance.cfg"}


# =============================================================================
# Shared helpers
# =============================================================================

def _get_prism_instances_dir():
    """Return the Prism Launcher instances directory path or None."""
    appdata = os.environ.get("APPDATA", "")
    if not appdata:
        return None
    path = Path(appdata) / "PrismLauncher" / "instances"
    return path if path.exists() else None


def _list_instances(instances_dir):
    """Return sorted list of instance folder names that contain a minecraft dir."""
    results = []
    for item in instances_dir.iterdir():
        if item.is_dir() and (item / "minecraft").exists():
            results.append(item.name)
    return sorted(results)


def _backup_instance(instance_name, prism_dir, output_dir, timestamp):
    """
    Back up a single instance to output_dir.
    Returns (zip_path, copied_count, mod_count) on success, or raises.
    """
    instance_path = prism_dir / instance_name
    minecraft_path = instance_path / "minecraft"

    archive_name = f"MC-Config-Backup-{instance_name}-{timestamp}"
    staging_dir = Path(tempfile.mkdtemp()) / archive_name
    staging_dir.mkdir(parents=True, exist_ok=True)

    config_targets = [
        "config", "options.txt", "servers.dat",
        "shaderpacks", "resourcepacks", "saves",
    ]
    copied = 0
    for target in config_targets:
        src = minecraft_path / target
        if src.exists():
            dst = staging_dir / target
            try:
                if src.is_dir():
                    shutil.copytree(str(src), str(dst))
                else:
                    shutil.copy2(str(src), str(dst))
                copied += 1
            except Exception as e:
                print(f"    [!] Could not copy {target}: {e}")

    mod_list_lines = [f"Mod List for instance: {instance_name}", f"Backup date: {timestamp}", ""]
    mod_count = 0
    mc_mods = minecraft_path / "mods"
    if mc_mods.exists():
        for f in sorted(mc_mods.iterdir()):
            if f.suffix in (".jar", ".zip") and f.is_file():
                mod_list_lines.append(f"  {f.name}")
                mod_count += 1
        mod_list_lines.append(f"\nTotal: {mod_count} mods")
    else:
        mod_list_lines.append("(No mods directory found)")
    (staging_dir / "MOD_LIST.txt").write_text("\n".join(mod_list_lines), encoding="utf-8")

    instance_cfg = instance_path / "instance.cfg"
    if instance_cfg.exists():
        shutil.copy2(str(instance_cfg), str(staging_dir / "instance.cfg"))

    instance_cfg_text = instance_cfg.read_text(encoding="utf-8", errors="replace") if instance_cfg.exists() else ""
    java_args_lines = [f"Java Args for instance: {instance_name}", ""]
    java_args_written = False
    for line in instance_cfg_text.splitlines():
        if "JvmArgs" in line or "MaxMemAlloc" in line or "MinMemAlloc" in line:
            java_args_lines.append(line.strip())
            java_args_written = True
    if not java_args_written:
        java_args_lines.append("(No Java args found in instance.cfg)")
    java_args_lines.append("\nTo restore: Prism Launcher → right-click instance → Edit → Java → paste above")
    (staging_dir / "JAVA_ARGS.txt").write_text("\n".join(java_args_lines), encoding="utf-8")

    restore_instructions = [
        "RESTORE INSTRUCTIONS",
        "====================",
        f"Instance: {instance_name}",
        "",
        "1. Install Prism Launcher on the target machine",
        f"2. Create a new instance named exactly: {instance_name}",
        "3. Launch it once to generate the minecraft/ folder, then close",
        "4. Run: mc prism restore <path_to_this_zip>",
        "   OR:  mc prism restore vault  (if backed up to vault and SyncThing synced)",
        "5. Download all mods listed in MOD_LIST.txt",
        "6. Set Java args from JAVA_ARGS.txt in Prism → Edit Instance → Java",
    ]
    (staging_dir / "RESTORE_INSTRUCTIONS.txt").write_text("\n".join(restore_instructions), encoding="utf-8")

    zip_path = output_dir / f"{archive_name}.zip"
    with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in staging_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(staging_dir)
                zf.write(str(file_path), str(arcname))

    try:
        shutil.rmtree(str(staging_dir.parent))
    except Exception:
        pass

    return zip_path, copied, mod_count


def _find_latest_vault_zip(vault_engine):
    """Return Path to most recent .zip in vault/mc_backups/, or None."""
    mc_backups = Path(vault_engine.vault_dir) / "mc_backups"
    if not mc_backups.exists():
        return None
    zips = [f for f in mc_backups.iterdir() if f.suffix == ".zip" and f.is_file()]
    if not zips:
        return None
    return max(zips, key=lambda f: f.stat().st_mtime)


def _detect_instance_name(zf):
    """Read instance.cfg from inside the ZIP and return the instance name, or None."""
    try:
        with zf.open("instance.cfg") as cfg:
            for line in cfg.read().decode("utf-8", errors="replace").splitlines():
                if line.startswith("name="):
                    return line.split("=", 1)[1].strip()
    except (KeyError, Exception):
        pass
    return None


def _prism_find_exe():
    """Locate PrismLauncher.exe from common install locations."""
    candidates = [
        Path(os.environ.get("APPDATA", "")) / "PrismLauncher" / "PrismLauncher.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "PrismLauncher" / "PrismLauncher.exe",
        Path(os.environ.get("HOMEPATH", "")) / "scoop" / "persist" / "prismlauncher" / "PrismLauncher.exe",
    ]
    return next((p for p in candidates if p.exists()), None)


# =============================================================================
# Prism subcommand handlers
# =============================================================================

def _prism_instances():
    prism_dir = _get_prism_instances_dir()
    if prism_dir is None:
        return "[!] Prism Launcher not found at %APPDATA%\\PrismLauncher\\instances\\"
    instances = _list_instances(prism_dir)
    if not instances:
        return "[i] No instances found (need minecraft/ folder inside instance)."
    lines = [f"  Prism instances ({len(instances)}):"]
    for name in instances:
        lines.append(f"    {name}")
    return "\n".join(lines)


def _prism_backup(kernel, parts):
    """mc prism backup [instance_name] [vault|<path>]"""
    if platform.system() != "Windows":
        return "[!] mc prism backup is Windows-only."

    instance_name = None
    dest_arg = None

    if len(parts) >= 1:
        first = parts[0]
        if first.lower() in _DEST_KEYWORDS or Path(first).is_absolute():
            dest_arg = first
        else:
            instance_name = first
            if len(parts) >= 2:
                dest_arg = parts[1]

    prism_dir = _get_prism_instances_dir()
    if prism_dir is None:
        return (
            "[!] Prism Launcher not found at %APPDATA%\\PrismLauncher\\instances\\\n"
            "    Install Prism Launcher first: https://prismlauncher.org"
        )

    available = _list_instances(prism_dir)
    if not available:
        return "[!] No Minecraft instances found in Prism Launcher."

    if instance_name is None:
        to_backup = available
        print(f"[i] Backing up all {len(to_backup)} instance(s): {', '.join(to_backup)}")
    else:
        if instance_name not in available:
            lines = [f"[!] Instance '{instance_name}' not found in Prism Launcher."]
            lines.append(f"    Available instances: {', '.join(available)}")
            return "\n".join(lines)
        to_backup = [instance_name]

    if dest_arg is None:
        output_dir = Path(os.environ.get("USERPROFILE", "~")) / "Desktop"
    elif dest_arg.lower() == "vault":
        vault_engine = kernel.get_engine("vault")
        output_dir = Path(vault_engine.vault_dir) / "mc_backups"
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = Path(dest_arg)
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return f"[!] Cannot create output directory '{output_dir}': {e}"

    if not output_dir.exists():
        return f"[!] Output directory does not exist: {output_dir}"

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    results = []

    for i, name in enumerate(to_backup, 1):
        print(f"[{i}/{len(to_backup)}] Backing up: {name}")
        try:
            zip_path, copied, mod_count = _backup_instance(name, prism_dir, output_dir, timestamp)
            results.append((name, zip_path, copied, mod_count, None))
            print(f"    Done → {zip_path.name}")
        except Exception as e:
            results.append((name, None, 0, 0, str(e)))
            print(f"    [!] Failed: {e}")

    succeeded = [r for r in results if r[4] is None]
    lines = ["", f"  Backup complete — {len(succeeded)}/{len(to_backup)} instance(s)", f"  Saved to: {output_dir}", ""]

    for name, zip_path, copied, mod_count, err in results:
        if err:
            lines.append(f"  [!] {name}: FAILED — {err}")
        else:
            lines.append(f"  [OK] {name}")
            lines.append(f"       {zip_path.name}")
            lines.append(f"       configs: {copied}  |  mods cataloged: {mod_count}")

    if dest_arg and dest_arg.lower() == "vault":
        lines.append("")
        lines.append("  SyncThing will carry these to your other machines automatically.")
        lines.append("  On laptop: mc prism restore vault")
    elif succeeded:
        lines.append("")
        lines.append("  Transfer the ZIP(s) to your laptop, then: mc prism restore \"<path_to_zip>\"")

    return "\n".join(lines)


def _prism_restore(kernel, parts):
    """mc prism restore vault|<path>"""
    if platform.system() != "Windows":
        return "[!] mc prism restore is Windows-only."

    if not parts:
        return "Usage: mc prism restore vault|<zip_path>"

    vault_engine = kernel.get_engine("vault")
    dest_arg = parts[0]

    if dest_arg.lower() in ("vault", "latest"):
        zip_path = _find_latest_vault_zip(vault_engine)
        if zip_path is None:
            vault_mc = Path(vault_engine.vault_dir) / "mc_backups"
            return (
                f"[!] No backups found in vault.\n"
                f"    Expected: {vault_mc}\n"
                f"    Run 'mc prism backup vault' on your source machine first."
            )
        print(f"[i] Using latest vault backup: {zip_path.name}")
    else:
        zip_path = Path(dest_arg)
        if not zip_path.exists():
            return f"[!] File not found: {zip_path}"

    if not zipfile.is_zipfile(str(zip_path)):
        return f"[!] Not a valid ZIP file: {zip_path}"

    with zipfile.ZipFile(str(zip_path), "r") as zf:
        all_names = zf.namelist()
        top_names = {n.split("/")[0] for n in all_names}
        if "MOD_LIST.txt" not in top_names and "instance.cfg" not in top_names:
            return (
                "[!] This doesn't look like an mc backup archive (no MOD_LIST.txt or instance.cfg).\n"
                "    Only ZIPs created by 'mc prism backup' can be restored with this command."
            )

        prism_dir = _get_prism_instances_dir()
        if prism_dir is None:
            return (
                "[!] Prism Launcher not found at %APPDATA%\\PrismLauncher\\instances\\\n"
                "    1. Install Prism Launcher: https://prismlauncher.org\n"
                "    2. Create a new instance\n"
                "    3. Launch it once to generate the minecraft/ folder\n"
                "    4. Run mc prism restore again"
            )

        instance_name = _detect_instance_name(zf)
        if instance_name is None:
            instance_name = "Minecraft PVP"
            print(f"[i] Could not detect instance name from backup. Defaulting to: {instance_name}")
        else:
            print(f"[i] Target instance: {instance_name}")

        instance_path = prism_dir / instance_name
        if not instance_path.exists():
            return (
                f"[!] Instance folder not found: {instance_path}\n"
                f"    1. Open Prism Launcher\n"
                f"    2. Create a new instance named exactly: {instance_name}\n"
                f"    3. Launch it once to generate the .minecraft folder, then close\n"
                f"    4. Run mc prism restore again"
            )

        minecraft_path = instance_path / "minecraft"
        if not minecraft_path.exists():
            print(f"[i] minecraft/ not found — creating: {minecraft_path}")
            minecraft_path.mkdir(parents=True, exist_ok=True)

        print(f"[1/3] Extracting files to {minecraft_path} ...")
        restored = 0
        skipped_docs = 0

        for member in zf.infolist():
            if member.filename.endswith("/"):
                continue
            top = member.filename.split("/")[0]
            if top in _DOC_FILES:
                skipped_docs += 1
                continue
            dest_file = minecraft_path / member.filename
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(member) as src, open(str(dest_file), "wb") as dst:
                dst.write(src.read())
            restored += 1

        print("[2/3] Mod list (you must download these manually):")
        mod_list_text = None
        try:
            with zf.open("MOD_LIST.txt") as f:
                mod_list_text = f.read().decode("utf-8", errors="replace")
        except KeyError:
            pass

        if mod_list_text:
            print("")
            for line in mod_list_text.splitlines():
                print(f"  {line}")
            print("")
        else:
            print("  (No MOD_LIST.txt in backup)")

        print("[3/3] Java args reminder:")
        java_args_text = None
        try:
            with zf.open("JAVA_ARGS.txt") as f:
                java_args_text = f.read().decode("utf-8", errors="replace")
        except KeyError:
            pass

        if java_args_text:
            print("")
            for line in java_args_text.splitlines():
                print(f"  {line}")
            print("")
        else:
            print("  (No JAVA_ARGS.txt in backup)")

    lines = [
        "",
        "  Restore complete!",
        f"  Source:          {zip_path.name}",
        f"  Instance:        {instance_name}",
        f"  Location:        {minecraft_path}",
        f"  Files restored:  {restored}",
        "",
        "  Next steps:",
        "    1. Download mods listed above into your instance's mods folder",
        "    2. Apply Java args in Prism: right-click instance → Edit → Java",
        "    3. Launch and enjoy",
    ]
    return "\n".join(lines)


def _prism_launch(parts):
    """mc prism launch [instance_name]"""
    if platform.system() != "Windows":
        return "[!] mc prism launch is Windows-only."

    prism_exe = _prism_find_exe()
    if not prism_exe:
        return "[!] PrismLauncher.exe not found. Checked APPDATA, LOCALAPPDATA, Scoop."

    if parts:
        subprocess.Popen([str(prism_exe), "--launch", parts[0]])
        return f"[i] Launching instance: {parts[0]}"

    subprocess.Popen([str(prism_exe)])
    return "[i] Prism Launcher opened."


def _cmd_prism(kernel, parts):
    """Dispatch mc prism <subcommand>."""
    sub = parts[0].lower() if parts else ""
    rest = parts[1:]

    if sub == "instances":
        return _prism_instances()
    if sub == "backup":
        return _prism_backup(kernel, rest)
    if sub == "restore":
        return _prism_restore(kernel, rest)
    if sub == "launch":
        return _prism_launch(rest)

    return (
        "  mc prism — Prism Launcher management\n\n"
        "  mc prism instances\n"
        "  mc prism backup [\"<name>\"] [vault|<path>]\n"
        "  mc prism restore vault|<path>\n"
        "  mc prism launch [\"<name>\"]"
    )


# =============================================================================
# Server subcommand stubs
# =============================================================================

def _cmd_server(parts):
    """Dispatch mc server <subcommand> (stubs, expandable)."""
    sub = parts[0].lower() if parts else ""

    if sub == "list":
        return "[i] mc server list — not yet implemented."
    if sub == "backup":
        return "[i] mc server backup — not yet implemented."
    if sub == "start":
        return "[i] mc server start — not yet implemented."

    return (
        "  mc server — Minecraft server management (stubs)\n\n"
        "  mc server list\n"
        "  mc server backup\n"
        "  mc server start [name]"
    )


# =============================================================================
# Entry point
# =============================================================================

def execute(kernel, args):
    import shlex
    try:
        parts = shlex.split(args) if args.strip() else []
    except ValueError:
        parts = args.strip().split()

    sub = parts[0].lower() if parts else ""
    rest = parts[1:]

    if sub == "prism":
        return _cmd_prism(kernel, rest)
    if sub == "server":
        return _cmd_server(rest)

    return _USAGE_TEXT
