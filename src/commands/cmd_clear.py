"""
Command: clear
Clear the terminal screen.
"""

MANIFEST = {
    "name": "clear",
    "description": "Clear the screen",
    "version": "1.0.0",
    "usage": "clear",
    "author": "xsvStudio",
    "required_role": "GUEST",
    "engine_deps": [],
}
DESCRIPTION = MANIFEST["description"]
USAGE = MANIFEST["usage"]
REQUIRED_ROLE = MANIFEST["required_role"]


import os


def execute(kernel, args):
    """Clear the terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')
    return None
