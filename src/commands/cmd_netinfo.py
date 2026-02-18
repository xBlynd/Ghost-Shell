"""
Command: netinfo
Detailed network diagnostics — interfaces, gateway, DNS, connectivity.
"""

MANIFEST = {
    "name": "netinfo",
    "description": "Show network info (IPs, DNS, gateway)",
    "version": "1.0.0",
    "usage": "netinfo | netinfo flush",
    "author": "xsvStudio",
    "required_role": "GUEST",
    "engine_deps": ["root"],
}
DESCRIPTION = MANIFEST["description"]
USAGE = MANIFEST["usage"]
REQUIRED_ROLE = MANIFEST["required_role"]


def execute(kernel, args):
    """Display network information."""
    root = kernel.get_engine("root")
    if not root:
        return "  [!] Root engine unavailable"

    subcmd = args.strip().lower()

    if subcmd == "flush":
        success, msg = root.flush_dns()
        icon = "✓" if success else "✗"
        return f"  {icon} {msg}"

    # Full network report
    info = root.get_network_info()
    lines = ["\n  ┌─ NETWORK INFO ─────────────────────────────┐"]

    # Connectivity
    conn_icon = "✓" if info["internet"] else "✗"
    lines.append(f"  │ Internet:  {conn_icon} {'Connected' if info['internet'] else 'Offline'}")
    lines.append(f"  │ Gateway:   {info.get('gateway') or 'unknown'}")

    # DNS servers
    dns = info.get("dns_servers", [])
    if dns:
        lines.append(f"  │ DNS:       {dns[0]}")
        for d in dns[1:3]:
            lines.append(f"  │            {d}")
    else:
        lines.append("  │ DNS:       (none detected)")

    # Interfaces with IPs
    lines.append("  │")
    lines.append("  │ Interfaces:")
    ifaces = info.get("interfaces", [])
    shown = 0
    for iface in ifaces:
        ips = iface.get("ips", [])
        if not ips:
            continue
        for ip in ips:
            lines.append(f"  │   {iface['name'][:20]:<20} {ip}")
            shown += 1
        if shown >= 8:
            break

    if shown == 0:
        lines.append("  │   (no IP addresses found)")

    lines.append("  │")
    lines.append("  │ netinfo flush  — flush DNS cache")
    lines.append("  └─────────────────────────────────────────────┘")

    return "\n".join(lines)
