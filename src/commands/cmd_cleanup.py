"""
Command: cleanup
Remove __pycache__, .pyc files, and clear data/cache/.
"""

MANIFEST = {
    "name": "cleanup",
    "description": "Remove pycache and temp files",
    "version": "1.0.0",
    "usage": "cleanup",
    "author": "xsvStudio",
    "required_role": "GUEST",
    "engine_deps": ["root"],
}
DESCRIPTION = MANIFEST["description"]
USAGE = MANIFEST["usage"]
REQUIRED_ROLE = MANIFEST["required_role"]

import os


def execute(kernel, args):
    """Clean up temporary files."""
    root = kernel.get_engine("root")
    if not root:
        return "  [!] Root engine unavailable"

    # Show cache size before cleanup
    cache_dir = os.path.join(kernel.root_dir, "data", "cache")
    before_count = _count_items(cache_dir)

    result = root.cleanup_temp()

    lines = [
        "\n  ┌─ CLEANUP ──────────────────────────────────┐",
        f"  │ __pycache__ dirs removed: {result['pycache_dirs_removed']}",
        f"  │ .pyc files removed:       {result['pyc_files_removed']}",
        f"  │ cache/ items cleared:     {result['cache_items_cleared']} (was {before_count})",
        "  └─────────────────────────────────────────────┘",
    ]
    return "\n".join(lines)


def _count_items(directory):
    """Count items in a directory, return 0 if missing."""
    if not os.path.exists(directory):
        return 0
    try:
        return len(os.listdir(directory))
    except Exception:
        return 0
