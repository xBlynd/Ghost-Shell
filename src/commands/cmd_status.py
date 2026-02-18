"""
Command: status
System health dashboard — engines, commands by tier, boot diagnostics, vault stats.
"""

MANIFEST = {
    "name": "status",
    "description": "Show system health status",
    "version": "2.0.0",
    "usage": "status",
    "author": "xsvStudio",
    "required_role": "GUEST",
    "engine_deps": ["ghost_core", "security", "heartbeat", "vault", "legion", "eve"],
}
DESCRIPTION = MANIFEST["description"]
USAGE = MANIFEST["usage"]
REQUIRED_ROLE = MANIFEST["required_role"]


def execute(kernel, args):
    """Display system status."""
    lines = []

    # ── System / Node ──────────────────────────────────────────────────────────
    core = kernel.get_engine("ghost_core")
    if core:
        state = core.get_state()
        lines.append("\n  ┌─ GHOST SHELL PHOENIX ─────────────────────┐")
        lines.append(f"  │ Node:     {state['node_id']}")
        lines.append(f"  │ Type:     {state['node_type']}")
        lines.append(f"  │ OS:       {state['os']} ({state['hostname']})")
        lines.append(f"  │ Python:   {state['python']}")
        lines.append(f"  │ Portable: {'Yes' if state['portable'] else 'No'}")
        lines.append(f"  │ Version:  {kernel.VERSION}")
    else:
        lines.append("\n  ┌─ GHOST SHELL PHOENIX ─────────────────────┐")
        lines.append(f"  │ Version: {kernel.VERSION}")

    # ── Security ───────────────────────────────────────────────────────────────
    sec = kernel.get_engine("security")
    if sec:
        lines.append(f"  │ Role:     {sec.current_role}")
        lines.append(f"  │ Auth:     {'Yes' if sec.authenticated else 'No'}")

    # ── Health ─────────────────────────────────────────────────────────────────
    heartbeat = kernel.get_engine("heartbeat")
    if heartbeat:
        health = heartbeat.check_health()
        lines.append(f"  │ Status:   {health['status']}")
        lines.append(f"  │ Uptime:   {health['uptime_seconds']}s")
        lines.append(f"  │ Threads:  {health['threads']}")
        mem = health.get("memory", {})
        if mem.get("rss_mb") != "unknown":
            lines.append(f"  │ Memory:   {mem.get('rss_mb', '?')} MB")

    # ── Engines ────────────────────────────────────────────────────────────────
    lines.append("  │")
    lines.append("  │ Engines:")
    for name, engine in kernel.engines.items():
        if engine is not None:
            ver = getattr(engine, 'ENGINE_VERSION', '?')
            lines.append(f"  │   ✓ {name:<14} v{ver}")
        else:
            lines.append(f"  │   ✗ {name:<14} FAILED")

    # ── Commands by Tier ───────────────────────────────────────────────────────
    lines.append("  │")
    loader = kernel.get_engine("loader")
    if loader:
        tiers = loader.get_commands_by_tier()
        system_cmds = tiers.get("system", {})
        custom_cmds = tiers.get("custom", {})
        lib_scripts = loader.list_library_scripts()
        unregistered = loader.unregistered

        lines.append(f"  │ Commands: {len(kernel.commands)} loaded")

        # System commands
        if system_cmds:
            lines.append(f"  │   System ({len(system_cmds)}):")
            for name in sorted(system_cmds):
                flag = " [!]" if name in unregistered else ""
                lines.append(f"  │     {name}{flag}")

        # Custom commands
        if custom_cmds:
            lines.append(f"  │   Custom ({len(custom_cmds)}):")
            for name in sorted(custom_cmds):
                flag = " [!]" if name in unregistered else ""
                lines.append(f"  │     {name}{flag}")

        # Library scripts
        if lib_scripts:
            lines.append(f"  │   Library ({len(lib_scripts)}):")
            for name, info in lib_scripts.items():
                lines.append(f"  │     {name} ({info['extension']})")
        else:
            lines.append(f"  │   Library: (empty)")

        if unregistered:
            lines.append(f"  │   [!] {len(unregistered)} command(s) missing MANIFEST")
    else:
        lines.append(f"  │ Commands: {len(kernel.commands)} loaded")

    # ── Boot Diagnostics ───────────────────────────────────────────────────────
    if heartbeat:
        diag = heartbeat.get_last_diagnostics()
        if diag:
            lines.append("  │")
            if diag["clean"]:
                lines.append("  │ Boot Diagnostics: ✓ Clean")
            else:
                lines.append("  │ Boot Diagnostics: ⚠ Issues found")
                for err in diag.get("syntax_errors", []):
                    lines.append(f"  │   [syntax] {err['file']}")
                for d in diag.get("missing_dirs", []):
                    lines.append(f"  │   [missing] {d}/")

    # ── Vault ──────────────────────────────────────────────────────────────────
    vault = kernel.get_engine("vault")
    if vault:
        stats = vault.get_stats()
        lines.append(f"  │")
        lines.append(f"  │ Journal:  {stats['journal_entries']} entries")
        lines.append(f"  │ Todos:    {stats['active_todos']} active, {stats['completed_todos']} done")

    # ── Legion ─────────────────────────────────────────────────────────────────
    legion = kernel.get_engine("legion")
    if legion:
        lstatus = legion.get_status()
        lines.append(f"  │ Legion:   {'Online' if lstatus['operational'] else 'Standby'} ({lstatus['known_nodes']} nodes)")

    # ── Eve AI ─────────────────────────────────────────────────────────────────
    eve = kernel.get_engine("eve")
    if eve:
        estatus = eve.get_status()
        lines.append(f"  │ Eve AI:   Tier={estatus['active_tier']} Ollama={'✓' if estatus['ollama_local'] else '✗'}")

    lines.append("  └─────────────────────────────────────────┘")

    return "\n".join(lines)
