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
        if not self.config_path.exists(): return {}
        try:
            with open(self.config_path, "r") as f:
                return json.load(f).get("commands", {})
        except: return {}

    def list_commands(self):
        cmds = self.load_commands()
        if not cmds: return
        print("\n⚡ MAGIC COMMANDS (commands.json):")
        print(f"{'COMMAND':<15} {'DESCRIPTION'}")
        print("-" * 40)
        for name, data in cmds.items():
            print(f"{name:<15} {data.get('description', '')}")
        print("")

    def run(self, command_name):
        commands = self.load_commands()
        if command_name not in commands: return False

        cfg = commands[command_name]
        print(f"🚀 Launching: {cfg.get('description', command_name)}...")

        if cfg.get("confirm", False):
            if input("⚠️  Are you sure? (y/n): ").lower() != "y":
                print("🛑 Cancelled.")
                return True

        try:
            if cfg['type'] == 'script':
                # Check library first, then relative path
                script_path = self.library_path / Path(cfg['path']).name
                if not script_path.exists():
                    script_path = self.root / cfg['path']
                
                HostBridge.launch(str(script_path))
                
            elif cfg['type'] == 'shell':
                subprocess.run(cfg['cmd'], shell=True)
                
            print("✅ Done.")
        except Exception as e:
            print(f"❌ Error: {e}")
        return True