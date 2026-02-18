"""
Command: sysinfo
Display detailed system information about the host machine.
"""

MANIFEST = {
    "name": "sysinfo",
    "description": "Show host system information",
    "version": "2.0.0",
    "usage": "sysinfo",
    "author": "xsvStudio",
    "required_role": "GUEST",
    "engine_deps": ["ghost_core", "root"],
}
DESCRIPTION = MANIFEST["description"]
USAGE = MANIFEST["usage"]
REQUIRED_ROLE = MANIFEST["required_role"]

import platform
import sys
import os


def execute(kernel, args):
    """Show system information."""
    lines = [
        "\n  ┌─ SYSTEM INFO ─────────────────────────────┐",
        f"  │ OS:           {platform.system()} {platform.release()}",
        f"  │ Version:      {platform.version()}",
        f"  │ Architecture: {platform.machine()}",
        f"  │ Processor:    {platform.processor() or 'unknown'}",
        f"  │ Hostname:     {platform.node()}",
        f"  │ Python:       {sys.version.split()[0]}",
        f"  │ Working Dir:  {os.getcwd()}",
    ]

    core = kernel.get_engine("ghost_core")
    if core:
        lines.append(f"  │ Ghost Root:   {core.root_dir}")
        lines.append(f"  │ Portable:     {'Yes (USB)' if core.is_portable else 'No (Local)'}")

    # Disk and RAM via RootEngine
    root = kernel.get_engine("root")
    if root:
        sys_info = root.get_system_info()

        # RAM
        ram = sys_info.get("ram", {})
        if ram.get("total_gb") and ram["total_gb"] != "?":
            used_pct = ram.get("used_pct", "?")
            lines.append(
                f"  │ RAM:          {ram['available_gb']} GB free / {ram['total_gb']} GB total "
                f"({used_pct}% used)"
            )

        # Disks
        disks = sys_info.get("disks", [])
        if disks:
            lines.append("  │ Disks:")
            for disk in disks:
                lines.append(
                    f"  │   {disk['drive']:<4}  {disk['free_gb']} GB free / {disk['total_gb']} GB total"
                )
    else:
        # Fallback: statvfs (Linux only)
        try:
            if hasattr(os, 'statvfs'):
                st = os.statvfs('/')
                total_gb = (st.f_blocks * st.f_frsize) / (1024 ** 3)
                free_gb = (st.f_bavail * st.f_frsize) / (1024 ** 3)
                lines.append(f"  │ Disk:         {free_gb:.1f} GB free / {total_gb:.1f} GB total")
        except Exception:
            pass

    lines.append("  └─────────────────────────────────────────┘")
    return "\n".join(lines)
