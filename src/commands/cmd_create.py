import sys
import os
from pathlib import Path

# CONFIG
PROJECT_ROOT = Path(__file__).parent.parent.parent
CUSTOM_DIR = PROJECT_ROOT / "src" / "commands" / "custom"

def get_multiline_input():
    print(" [?] Enter Code below.")
    print(" [?] Type 'END' on a new line to finish.")
    print("-" * 40)
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines)

def create_command(name=None):
    print("\n 🛠️  CREATE CUSTOM COMMAND")
    print(" " + "="*30)

    # 1. Get Name
    if not name:
        name = input(" [?] Command Name (One word): ").lower().strip()
    
    if not name:
        print(" ❌ Name required.")
        return

    # Check for conflicts
    filename = f"cmd_{name}.py"
    filepath = CUSTOM_DIR / filename
    
    if filepath.exists():
        print(f" ⚠️  Warning: '{name}' already exists in Custom.")
        if input("     Overwrite? (y/n): ").lower() != 'y':
            return

    # 2. Get Description
    desc = input(" [?] Description: ").strip()

    # 3. Get Code
    print("\n [?] Paste your Python code now.")
    print("     (No need to write 'def run(args):', just paste the logic).")
    user_code = get_multiline_input()

    # 4. Wrap & Write
    # We indent the user's code to fit inside the run() function
    indented_code = "\n    ".join(user_code.splitlines())
    
    file_content = f'''import sys
import os
import platform

# Module: {name}
# Description: {desc}

def run(args):
    print("\\n🚀 Running Custom Command: {name}...")
    
    # --- USER CODE START ---
    {indented_code}
    # --- USER CODE END ---
    
    print("\\n✅ {name} finished.")
'''

    # Ensure dir exists
    CUSTOM_DIR.mkdir(parents=True, exist_ok=True)
    # Ensure __init__.py exists
    (CUSTOM_DIR / "__init__.py").touch()

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(file_content)

    print("\n" + "="*30)
    print(f" ✅ SUCCESS: Created 'src/commands/custom/{filename}'")
    print(f" 🚀 Usage: Type '{name}' in the shell to run it.")

def run(args):
    # Determine if name was passed in args
    name = args[0] if args else None
    create_command(name)