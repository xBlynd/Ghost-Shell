"""
Command: dashboard
Launch the Textual TUI live dashboard (optional dependency).
"""

MANIFEST = {
    "name": "dashboard",
    "description": "Launch live TUI dashboard (requires textual)",
    "version": "1.0.0",
    "usage": "dashboard",
    "author": "xsvStudio",
    "required_role": "GUEST",
    "engine_deps": ["interface"],
}
DESCRIPTION = MANIFEST["description"]
USAGE = MANIFEST["usage"]
REQUIRED_ROLE = MANIFEST["required_role"]


def execute(kernel, args):
    """Launch the Textual dashboard or show install instructions."""
    iface = kernel.get_engine("interface")

    # Check Textual availability via InterfaceEngine flag
    has_textual = getattr(iface, "has_textual", False) if iface else False

    if not has_textual:
        return (
            "\n  Dashboard requires the Textual library.\n\n"
            "  To install:\n"
            "    pip install textual\n\n"
            "  Once installed, restart Ghost Shell and run `dashboard` again.\n"
            "  (Textual is optional — Ghost Shell works without it.)"
        )

    # Launch the TUI
    try:
        from src.tui.ghost_dashboard import GhostDashboardApp
        app = GhostDashboardApp(kernel=kernel)
        app.run()
        return None  # Dashboard was closed
    except Exception as e:
        return f"  [!] Dashboard failed to launch: {e}"
