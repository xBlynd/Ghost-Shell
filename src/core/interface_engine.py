"""
Engine 09: Interface Engine - The Face
========================================
ASCII banners, theme management, output formatting.

Architecture Note:
- This engine returns STRINGS, it does not print directly.
- All visual presentation flows through here.
- Future: This becomes the adapter layer for GUI/Web/Mobile.
  Terminal output is just one "renderer". A web dashboard would
  be another renderer consuming the same data structures.

Compartmentalization:
- ONLY handles visual output
- NEVER performs business logic
"""

# Detect Textual availability at module level (graceful degradation)
try:
    import textual  # noqa: F401
    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False


class InterfaceEngine:
    """The Face - visual presentation and theming."""

    ENGINE_NAME = "interface"
    ENGINE_VERSION = "2.0.0"

    # === ASCII BANNERS ===
    BANNER_GOD = r"""
    ╔══════════════════════════════════════════════════════╗
    ║                                                      ║
    ║     ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗       ║
    ║    ██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝       ║
    ║    ██║  ███╗███████║██║   ██║███████╗   ██║          ║
    ║    ██║   ██║██╔══██║██║   ██║╚════██║   ██║          ║
    ║    ╚██████╔╝██║  ██║╚██████╔╝███████║   ██║          ║
    ║     ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝          ║
    ║                                                      ║
    ║           S H E L L   P H O E N I X                  ║
    ║              ⚡ G O D   M O D E ⚡                    ║
    ║                  v6.5 Phoenix                        ║
    ╚══════════════════════════════════════════════════════╝
    """

    BANNER_GUEST = r"""
    ╔══════════════════════════════════════════════════════╗
    ║          👻 GHOST SHELL PHOENIX v6.5                 ║
    ║              Guest Mode (Read-Only)                  ║
    ╚══════════════════════════════════════════════════════╝
    """

    BANNER_ADMIN = r"""
    ╔══════════════════════════════════════════════════════╗
    ║          👻 GHOST SHELL PHOENIX v6.5                 ║
    ║              ◆ Admin Mode                            ║
    ╚══════════════════════════════════════════════════════╝
    """

    def __init__(self, kernel):
        self.kernel = kernel
        self.theme = "default"
        self.has_textual = HAS_TEXTUAL

    def get_banner(self, role=None):
        """Get the appropriate banner for current role."""
        if role == "GOD":
            return self.BANNER_GOD
        elif role == "ADMIN":
            return self.BANNER_ADMIN
        else:
            return self.BANNER_GUEST

    # =========================================================================
    # OUTPUT FORMATTING
    # =========================================================================

    def format_table(self, headers, rows, title=None):
        """Format data as a text table."""
        if not rows:
            return "  (no data)"

        col_widths = [len(str(h)) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        lines = []
        if title:
            lines.append(f"\n  {title}")
            lines.append("  " + "─" * (sum(col_widths) + len(col_widths) * 3))

        header_line = "  "
        for i, h in enumerate(headers):
            header_line += f" {str(h):<{col_widths[i]}} │"
        lines.append(header_line)
        lines.append("  " + "─" * (sum(col_widths) + len(col_widths) * 3))

        for row in rows:
            row_line = "  "
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    row_line += f" {str(cell):<{col_widths[i]}} │"
            lines.append(row_line)

        return "\n".join(lines)

    def format_status_block(self, title, items):
        """Format a status block with key-value pairs."""
        lines = [f"\n  ┌─ {title} ─┐"]
        max_key = max(len(k) for k, v in items) if items else 0
        for key, value in items:
            lines.append(f"  │ {key:<{max_key}} : {value}")
        lines.append(f"  └{'─' * (max_key + 20)}┘")
        return "\n".join(lines)

    def format_ping_result(self, data):
        """Format ping results for display."""
        if data.get("status") == "UNREACHABLE":
            return f"  ✗ {data['host']} - UNREACHABLE ({data['packets_lost']}/{data['packets_sent']} lost)"

        status_icon = "✓" if data["status"] == "STABLE" else "⚠"
        lines = [
            f"  {status_icon} Ping {data['host']} - {data['status']}",
            f"    avg: {data['average_ms']}ms  min: {data['min_ms']}ms  max: {data['max_ms']}ms",
            f"    jitter: {data['jitter_ms']}ms  loss: {data['loss_pct']}%",
        ]
        return "\n".join(lines)

    def format_todo_list(self, items):
        """Format todo list for display."""
        if not items:
            return "  No active todos."

        lines = ["\n  ┌─ TODO ─┐"]
        for item in items:
            check = "✓" if item["done"] else "○"
            priority = ""
            if item.get("priority") == "high":
                priority = " [!]"
            elif item.get("priority") == "critical":
                priority = " [!!]"
            lines.append(f"  │ {check} #{item['id']}{priority} {item['text']}")
        lines.append(f"  └─────────┘")
        return "\n".join(lines)

    def format_help(self, commands):
        """Format the help menu showing all tiers."""
        loader = self.kernel.get_engine("loader")

        if loader:
            return self.format_command_list(
                system=loader.get_commands_by_tier().get("system", {}),
                custom=loader.get_commands_by_tier().get("custom", {}),
                library=loader.list_library_scripts(),
            )

        # Fallback: flat list
        lines = [
            "\n  ┌─ GHOST SHELL COMMANDS ─┐",
            "  │",
        ]
        for name, module in sorted(commands.items()):
            desc = getattr(module, 'DESCRIPTION', 'No description')
            role = getattr(module, 'REQUIRED_ROLE', 'GUEST')
            lines.append(f"  │  {name:<14} {desc:<40} [{role}]")
        lines.extend([
            "  │",
            "  │  Any other input passes through to host OS",
            "  └──────────────────────┘",
        ])
        return "\n".join(lines)

    def format_command_list(self, system, custom, library):
        """
        Format help output showing commands grouped by tier.

        Args:
            system: dict of {name: info} for system commands
            custom: dict of {name: info} for custom commands
            library: dict of {name: info} for library scripts
        """
        lines = ["\n  ┌─ GHOST SHELL COMMANDS ─────────────────────────────────────┐"]

        # System commands
        if system:
            lines.append("  │  ── System Commands ──")
            for name, info in sorted(system.items()):
                desc = info.get("description", "")[:38]
                role = info.get("required_role", "GUEST")
                lines.append(f"  │    {name:<14} {desc:<38} [{role}]")

        # Custom commands
        if custom:
            lines.append("  │")
            lines.append("  │  ── Custom Commands ──")
            for name, info in sorted(custom.items()):
                desc = info.get("description", "")[:38]
                role = info.get("required_role", "GUEST")
                lines.append(f"  │    {name:<14} {desc:<38} [{role}]")

        # Library scripts
        if library:
            lines.append("  │")
            lines.append("  │  ── Library Scripts ──")
            for name, info in sorted(library.items()):
                ext = info.get("extension", "")
                interp = info.get("interpreter", "")
                lines.append(f"  │    {name:<14} ({ext} — {interp})")

        lines.extend([
            "  │",
            "  │  Any other input passes through to host OS",
            "  └────────────────────────────────────────────────────────────┘",
        ])
        return "\n".join(lines)

    def format_result(self, data, style="default"):
        """
        Generic formatter for engine data (dict or list).
        Returns a formatted string suitable for terminal output.
        """
        if data is None:
            return "  (no data)"

        if isinstance(data, str):
            return data

        if isinstance(data, list):
            if not data:
                return "  (empty)"
            if all(isinstance(item, dict) for item in data):
                # List of dicts: render as table
                if data:
                    headers = list(data[0].keys())
                    rows = [[str(item.get(h, "")) for h in headers] for item in data]
                    return self.format_table(headers, rows)
            return "\n".join(f"  • {item}" for item in data)

        if isinstance(data, dict):
            if style == "table":
                headers = ["Key", "Value"]
                rows = [[str(k), str(v)] for k, v in data.items()]
                return self.format_table(headers, rows)
            # Default: key: value pairs
            lines = []
            for k, v in data.items():
                lines.append(f"  {k}: {v}")
            return "\n".join(lines)

        return str(data)
