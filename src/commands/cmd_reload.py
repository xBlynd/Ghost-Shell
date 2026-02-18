"""
Command: reload
Hot reload commands without restarting Ghost Shell.
Edit a cmd_*.py file and run `reload <name>` to pick up changes instantly.
"""

MANIFEST = {
    "name": "reload",
    "description": "Hot reload commands",
    "version": "1.0.0",
    "usage": "reload <command> | reload all",
    "author": "xsvStudio",
    "required_role": "ADMIN",
    "engine_deps": ["loader"],
}
DESCRIPTION = MANIFEST["description"]
USAGE = MANIFEST["usage"]
REQUIRED_ROLE = MANIFEST["required_role"]


def execute(kernel, args):
    """Hot reload commands."""
    loader = kernel.get_engine("loader")
    if not loader:
        return "  [!] Loader engine not available"

    target = args.strip().lower()

    if not target:
        return "  Usage: reload <command_name> | reload all"

    if target == "all":
        results = loader.reload_all()
        lines = ["\n  Reload results:"]
        for name, result in results.items():
            status = "✓" if result["success"] else "✗"
            lines.append(f"    {status} {name}: {result['message']}")
        return "\n".join(lines)

    success, msg = loader.reload_command(target)
    return f"  {'✓' if success else '✗'} {msg}"
