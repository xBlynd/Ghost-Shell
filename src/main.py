import sys
import importlib
from pathlib import Path

# --- CONFIGURATION (EDIT THIS ONLY WHEN RELEASING NEW VERSIONS) ---
APP_NAME = "xsvCommandCenter"
VERSION = "v5.1-Live"

# --- BOOTSTRAP PATHS ---
# Add project root to system path so imports like 'from src.core...' work
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import Dependencies
from src.core.host_engine import HostEngine
from src.commands import cmd_launcher

def get_installed_commands():
    """
    Scans the 'src/commands' directory for any file named 'cmd_*.py'.
    Returns a list of command names (e.g., ['host', 'journal', 'network']).
    """
    # FIX: correctly locate the 'commands' folder relative to this script
    command_dir = Path(__file__).parent / "commands"
    commands = []
    
    if command_dir.exists():
        for file in command_dir.glob("cmd_*.py"):
            # cmd_host.py -> host
            name = file.stem.replace("cmd_", "")
            # Exclude internal files
            if name not in ["launcher", "__init__"]:
                commands.append(name)
    return sorted(commands)

def main():
    if len(sys.argv) < 2:
        HostEngine.clear_screen()
        print(f"{APP_NAME} [{VERSION}]")
        print("-" * 40)
        
        # 1. DYNAMICALLY DISCOVER & PRINT MODULES
        # This loop ensures you NEVER have to manually update the menu.
        installed = get_installed_commands()
        for cmd in installed:
            print(f"  {cmd:<15} - [Module]")
            
        # 2. PRINT CUSTOM MAGIC COMMANDS (from commands.json)
        cmd_launcher.Launcher().list_commands()
        return

    # User input: "xsv host info" -> cmd="host", args=["info"]
    cmd_name = sys.argv[1].lower()
    cmd_args = sys.argv[2:]

    # --- DYNAMIC DISPATCHER ---
    # 1. Check if a module exists in src/commands/cmd_{cmd_name}.py
    try:
        # Dynamically import the module (e.g., src.commands.cmd_host)
        module_path = f"src.commands.cmd_{cmd_name}"
        module = importlib.import_module(module_path)
        
        # Run the module's run() function
        module.run(cmd_args)
        
    except ModuleNotFoundError:
        # 2. If no module found, try the Magic Launcher (commands.json)
        launcher = cmd_launcher.Launcher()
        found = launcher.run(cmd_name)
        
        if not found:
            print(f"❌ Unknown command: '{cmd_name}'")
            print("   (It's not a module in src/commands/ and not in commands.json)")

if __name__ == "__main__":
    main()