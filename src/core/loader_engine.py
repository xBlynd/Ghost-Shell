"""
Engine 10: Loader Engine - The Nervous System
================================================
Scans src/commands/ for cmd_*.py files, dynamic import, hot reload.
Supports three tiers: system commands, custom commands, library scripts.

The Drop-In Pattern:
- System command: create src/commands/cmd_whatever.py
- Custom command: create src/commands/custom/cmd_whatever.py
- Library script: drop any executable in library/ (any language)
All are automatically discovered on next boot.

Compartmentalization:
- ONLY manages command loading/reloading
- Does NOT execute commands (kernel does that)
"""

import importlib
import os
import sys


# Supported library script extensions and their interpreters
LIBRARY_EXTENSIONS = {
    ".py":   "python",
    ".ps1":  "powershell",
    ".sh":   "bash",
    ".bat":  "batch",
    ".cmd":  "batch",
    ".js":   "node",
    ".exe":  "native",
}


class LoaderEngine:
    """The Nervous System - dynamic command management."""

    ENGINE_NAME = "loader"
    ENGINE_VERSION = "2.0.0"

    def __init__(self, kernel):
        self.kernel = kernel
        self.root_dir = kernel.root_dir
        self.commands_dir = os.path.join(self.root_dir, "src", "commands")
        self.custom_commands_dir = os.path.join(self.commands_dir, "custom")
        self.library_dir = os.path.join(self.root_dir, "library")

        self._loaded_modules = {}       # {cmd_name: module}
        self._command_tier = {}         # {cmd_name: "system" | "custom"}
        self.library_scripts = {}       # {script_name: {path, extension, interpreter}}
        self.unregistered = set()       # commands without MANIFEST dict

        # Ensure directories exist
        os.makedirs(self.custom_commands_dir, exist_ok=True)
        os.makedirs(self.library_dir, exist_ok=True)

    # =========================================================================
    # COMMAND DISCOVERY
    # =========================================================================

    def discover_commands(self):
        """
        Scan src/commands/ AND src/commands/custom/ for cmd_*.py files.
        Returns dict of {command_name: module}.
        Custom commands are loaded after system commands; name conflicts
        favour the custom command (override behaviour).
        """
        commands = {}

        # System commands
        system_cmds = self._scan_directory(self.commands_dir, tier="system")
        commands.update(system_cmds)

        # Custom commands (override system if same name)
        custom_cmds = self._scan_directory(self.custom_commands_dir, tier="custom")
        commands.update(custom_cmds)

        return commands

    def _scan_directory(self, directory, tier="system"):
        """Scan a single directory for cmd_*.py files."""
        commands = {}
        if not os.path.exists(directory):
            return commands

        for filename in os.listdir(directory):
            if not (filename.startswith("cmd_") and filename.endswith(".py")):
                continue

            cmd_name = filename[4:-3]  # strip 'cmd_' prefix and '.py'

            try:
                # Build module path relative to project root
                if tier == "custom":
                    module_path = f"src.commands.custom.{filename[:-3]}"
                else:
                    module_path = f"src.commands.{filename[:-3]}"

                module = importlib.import_module(module_path)
                commands[cmd_name] = module
                self._loaded_modules[cmd_name] = module
                self._command_tier[cmd_name] = tier

                # Check for MANIFEST — flag commands without one
                if not hasattr(module, "MANIFEST"):
                    self.unregistered.add(cmd_name)
                else:
                    self.unregistered.discard(cmd_name)

            except Exception as e:
                if self.kernel.debug:
                    print(f"   [!] Failed to load command '{cmd_name}': {e}")

        return commands

    # =========================================================================
    # LIBRARY SCRIPT DISCOVERY
    # =========================================================================

    def discover_library_scripts(self):
        """
        Scan library/ for executable scripts of any supported type.
        Stores results in self.library_scripts keyed by script name (no extension).
        Returns dict of {name: info}.
        """
        self.library_scripts = {}

        if not os.path.exists(self.library_dir):
            return self.library_scripts

        for filename in os.listdir(self.library_dir):
            base, ext = os.path.splitext(filename)
            ext_lower = ext.lower()

            if ext_lower not in LIBRARY_EXTENSIONS:
                continue

            full_path = os.path.join(self.library_dir, filename)
            if not os.path.isfile(full_path):
                continue

            interpreter = LIBRARY_EXTENSIONS[ext_lower]
            self.library_scripts[base.lower()] = {
                "name": base,
                "filename": filename,
                "path": full_path,
                "extension": ext_lower,
                "interpreter": interpreter,
            }

        return self.library_scripts

    def get_library_info(self, name):
        """Get info about a library script by name."""
        return self.library_scripts.get(name.lower())

    def list_library_scripts(self):
        """Return all discovered library scripts sorted by name."""
        return dict(sorted(self.library_scripts.items()))

    # =========================================================================
    # HOT RELOAD
    # =========================================================================

    def reload_command(self, cmd_name):
        """
        Hot reload a single command module.
        Edit cmd_ping.py and run `reload ping` — no restart needed!
        """
        if cmd_name not in self._loaded_modules:
            return False, f"Command '{cmd_name}' not loaded"

        try:
            module = self._loaded_modules[cmd_name]
            importlib.reload(module)
            self.kernel.commands[cmd_name] = module

            # Re-check MANIFEST after reload
            if not hasattr(module, "MANIFEST"):
                self.unregistered.add(cmd_name)
            else:
                self.unregistered.discard(cmd_name)

            return True, f"Command '{cmd_name}' reloaded"
        except Exception as e:
            return False, f"Reload failed: {e}"

    def reload_all(self):
        """Reload all loaded commands and re-scan library scripts."""
        results = {}
        for cmd_name in list(self._loaded_modules.keys()):
            success, msg = self.reload_command(cmd_name)
            results[cmd_name] = {"success": success, "message": msg}

        # Re-scan library
        self.discover_library_scripts()
        results["__library__"] = {
            "success": True,
            "message": f"{len(self.library_scripts)} library scripts rescanned",
        }
        return results

    # =========================================================================
    # METADATA
    # =========================================================================

    def get_command_info(self, cmd_name):
        """Get metadata about a command. Prefers MANIFEST over module-level attrs."""
        if cmd_name not in self._loaded_modules:
            return None

        module = self._loaded_modules[cmd_name]
        manifest = getattr(module, "MANIFEST", None)

        if manifest:
            return {
                "name": manifest.get("name", cmd_name),
                "description": manifest.get("description", "No description"),
                "required_role": manifest.get("required_role", "GUEST"),
                "usage": manifest.get("usage"),
                "version": manifest.get("version", "?"),
                "author": manifest.get("author", ""),
                "engine_deps": manifest.get("engine_deps", []),
                "tier": self._command_tier.get(cmd_name, "system"),
                "file": getattr(module, "__file__", "unknown"),
                "has_manifest": True,
            }
        else:
            # Fall back to module-level attributes
            return {
                "name": cmd_name,
                "description": getattr(module, "DESCRIPTION", "No description"),
                "required_role": getattr(module, "REQUIRED_ROLE", "GUEST"),
                "usage": getattr(module, "USAGE", None),
                "version": "?",
                "author": "",
                "engine_deps": [],
                "tier": self._command_tier.get(cmd_name, "system"),
                "file": getattr(module, "__file__", "unknown"),
                "has_manifest": False,
            }

    def list_commands(self):
        """List all discovered commands with metadata."""
        return {
            name: self.get_command_info(name)
            for name in sorted(self._loaded_modules.keys())
        }

    def get_commands_by_tier(self):
        """Return commands grouped by tier: system, custom."""
        system = {}
        custom = {}
        for name in sorted(self._loaded_modules.keys()):
            tier = self._command_tier.get(name, "system")
            info = self.get_command_info(name)
            if tier == "custom":
                custom[name] = info
            else:
                system[name] = info
        return {"system": system, "custom": custom}
