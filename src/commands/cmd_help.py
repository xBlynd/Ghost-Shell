import sys
from pathlib import Path
from src.core.host_engine import HostEngine
from src.commands import cmd_launcher

def get_modules():
    """Scans the commands folder for files named cmd_*.py"""
    cmd_dir = Path(__file__).parent
    modules = []
    if cmd_dir.exists():
        for f in cmd_dir.glob("cmd_*.py"):
            name = f.stem.replace("cmd_", "")
            if name not in ["launcher", "__init__"]:
                modules.append(name)
    return sorted(modules)

def run(args):
    HostEngine.clear_screen()
    print("\n🔮 xsvCommandCenter [System Menu]")
    print("=" * 40)
    
    print("📦 MODULES (Built-in Tools)")
    print("-" * 40)
    for mod in get_modules():
        print(f"  • {mod:<15}")

    print("\n⚡ MAGIC COMMANDS (Custom Scripts)")
    print("-" * 40)
    cmd_launcher.Launcher().list_commands()
    
    print("=" * 40)
    print("Usage: xsv <command> [args]\n")