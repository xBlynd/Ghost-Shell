"""
LoaderEngine - The Nervous System
Dynamic command loading, hot-swap, manifest parsing
"""
import sys
import importlib
import json
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).parent.parent.parent

class LoaderEngine:
    """
    Dynamically loads commands from src/commands/ and library/
    """
    
    def __init__(self):
        self.commands = {}  # name -> module_path
        self.manifests = {}  # name -> manifest dict
        self.custom_commands = {}
        self.library_commands = {}
    
    def initialize(self):
        """Scan and load all available commands"""
        self.scan_system_commands()
        self.scan_custom_commands()
        self.scan_library_commands()
        print(f"LoaderEngine: {len(self.commands)} commands loaded")
    
    def scan_system_commands(self):
        """Scan src/commands/cmd_*.py"""
        commands_dir = ROOT / 'src' / 'commands'
        
        for file in commands_dir.glob('cmd_*.py'):
            if file.stem == 'cmd_shell':  # Skip shell itself
                continue
            
            cmd_name = file.stem.replace('cmd_', '')
            module_path = f'src.commands.{file.stem}'
            
            try:
                module = importlib.import_module(module_path)
                
                # Get manifest if available
                if hasattr(module, 'MANIFEST'):
                    self.manifests[cmd_name] = module.MANIFEST
                
                self.commands[cmd_name] = {
                    'type': 'system',
                    'module': module_path,
                    'instance': module
                }
            except Exception as e:
                print(f"⚠ Failed to load {cmd_name}: {e}")
    
    def scan_custom_commands(self):
        """Scan src/commands/custom/cmd_*.py"""
        custom_dir = ROOT / 'src' / 'commands' / 'custom'
        if not custom_dir.exists():
            return
        
        for file in custom_dir.glob('cmd_*.py'):
            cmd_name = file.stem.replace('cmd_', '')
            module_path = f'src.commands.custom.{file.stem}'
            
            try:
                module = importlib.import_module(module_path)
                
                if hasattr(module, 'MANIFEST'):
                    self.manifests[cmd_name] = module.MANIFEST
                
                self.custom_commands[cmd_name] = {
                    'type': 'custom',
                    'module': module_path,
                    'instance': module
                }
                self.commands[cmd_name] = self.custom_commands[cmd_name]
            except Exception as e:
                print(f"⚠ Failed to load custom {cmd_name}: {e}")
    
    def scan_library_commands(self):
        """Load commands.json library links"""
        commands_json = ROOT / 'data' / 'config' / 'commands.json'
        
        if commands_json.exists():
            with open(commands_json, 'r') as f:
                library = json.load(f)
            
            for name, config in library.items():
                self.library_commands[name] = config
                self.commands[name] = {
                    'type': 'library',
                    'config': config
                }
    
    def get_command(self, name: str) -> Optional[Dict]:
        """Get command info by name"""
        return self.commands.get(name)
    
    def run_command(self, name: str, args: List[str]) -> bool:
        """Execute a command by name"""
        cmd = self.get_command(name)
        if not cmd:
            return False
        
        try:
            if cmd['type'] in ['system', 'custom']:
                # Python module command
                module = cmd['instance']
                if hasattr(module, 'run'):
                    module.run(args)
                    return True
            
            elif cmd['type'] == 'library':
                # Library script command
                config = cmd['config']
                script_path = ROOT / config['path']
                
                if config.get('type') == 'python':
                    import subprocess
                    subprocess.run([sys.executable, str(script_path)] + args)
                    return True
                elif config.get('type') == 'bash':
                    import subprocess
                    subprocess.run(['bash', str(script_path)] + args)
                    return True
        
        except Exception as e:
            print(f"❌ Error running {name}: {e}")
            return False
        
        return False
    
    def get_manifest(self, name: str) -> Optional[Dict]:
        """Get command manifest"""
        return self.manifests.get(name)
    
    def list_commands(self, category: str = None) -> Dict:
        """List all commands, optionally filtered by category"""
        if not category:
            return self.commands
        
        if category == 'system':
            return {k: v for k, v in self.commands.items() if v['type'] == 'system'}
        elif category == 'custom':
            return self.custom_commands
        elif category == 'library':
            return self.library_commands
        
        return {}
    
    def reload_command(self, name: str) -> bool:
        """Hot-reload a command module"""
        cmd = self.get_command(name)
        if not cmd or cmd['type'] not in ['system', 'custom']:
            return False
        
        try:
            module = importlib.reload(cmd['instance'])
            cmd['instance'] = module
            
            if hasattr(module, 'MANIFEST'):
                self.manifests[name] = module.MANIFEST
            
            return True
        except Exception as e:
            print(f"⚠ Failed to reload {name}: {e}")
            return False
    
    def shutdown(self):
        """Cleanup"""
        pass
