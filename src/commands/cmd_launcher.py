import sys
import json
import subprocess
from pathlib import Path
from src.core.host_bridge import HostBridge

class Launcher:
    def __init__(self):
        self.root = Path(__file__).parent.parent.parent
        self.config_path = self.root / "data" / "config" / "commands.json"
        self.library_path = self.root / "library"

    def load_commands(self):
        if not self.config_path.exists():
            return {}
        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
                return data.get("commands", {})
        except:
            return {}

    def list_commands(self):
        cmds = self.load_commands()
        if not cmds: return
        print("\n⚡ CUSTOM COMMANDS (from commands.json):")
        print(f"{'COMMAND':<15} {'DESCRIPTION'}")
        print("-" * 40)
        for name, data in cmds.items():
            print(f"{name:<15} {data.get('description', '')}")
        print("")

    def run(self, command_name):
        commands = self.load_commands()
        
        if command_name not in commands:
            return False # Command not found

        cfg = commands[command_name]
        print(f"🚀 Launching: {cfg.get('description', command_name)}...")

        # 1. HANDLE CONFIRMATION
        if cfg.get("confirm", False):
            ask = input("⚠️  Are you sure? (y/n): ")
            if ask.lower() != "y":
                print("🛑 Cancelled.")
                return True

        # 2. EXECUTE SCRIPT
        try:
            if cfg['type'] == 'script':
                # Auto-detect script location
                script_path = self.library_path / Path(cfg['path']).name
                # If path in json was relative/full, try that too
                if not script_path.exists():
                    script_path = self.root / cfg['path']
                
                HostBridge.launch(str(script_path))
                
            elif cfg['type'] == 'shell':
                # Run raw command (e.g., "ping google.com")
                subprocess.run(cfg['cmd'], shell=True)
                
            print("✅ Execution Complete.")
        except Exception as e:
            print(f"❌ Error: {e}")
            
        return True