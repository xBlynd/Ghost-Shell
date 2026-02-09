import sys
import importlib
from pathlib import Path

# CONFIGURATION
APP_NAME = "xsvCommandCenter"
VERSION = "v5.2-ModularHelp"
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.commands import cmd_launcher, cmd_help

def main():
    # If no arguments, run the HELP command
    if len(sys.argv) < 2:
        cmd_help.run([])
        return

    # Otherwise, run the requested command
    cmd_name = sys.argv[1].lower()
    cmd_args = sys.argv[2:]

    # 1. Try to find a Module (src/commands/cmd_*.py)
    try:
        module_path = f"src.commands.cmd_{cmd_name}"
        module = importlib.import_module(module_path)
        module.run(cmd_args)
        return
    except ModuleNotFoundError:
        pass # Not a module, try Magic Launcher

    # 2. Try Magic Launcher (commands.json)
    launcher = cmd_launcher.Launcher()
    if launcher.run(cmd_name):
        return

    # 3. If neither found
    print(f"❌ Unknown command: '{cmd_name}'")
    print("   Type 'xsv help' to see available tools.")

if __name__ == "__main__":
    main()