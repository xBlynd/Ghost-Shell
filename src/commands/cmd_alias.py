import sys
import shutil
import os
from pathlib import Path

def run(args):
    if not args:
        print("Usage:")
        print("  xsv alias add <name>   - Create new command (e.g., 'magic')")
        print("  xsv alias list         - Show all active aliases")
        print("  xsv alias nuke <name>  - Delete an alias")
        return

    cmd = args[0].lower()
    root = Path(__file__).parent.parent.parent
    
    # --- ADD ---
    if cmd == "add":
        if len(args) < 2:
            print("❌ Usage: xsv alias add <name>")
            return
        
        new_name = args[1]
        
        # We allow creating aliases from xsv.bat OR xsv (for linux)
        # Assuming Windows for .bat creation mostly
        source = root / "xsv.bat"
        target = root / f"{new_name}.bat"

        if not source.exists():
            print("❌ Critical: xsv.bat source not found.")
            return

        try:
            shutil.copy(source, target)
            print(f"✅ Alias Created! You can now type: {new_name}")
        except Exception as e:
            print(f"❌ Error: {e}")

    # --- LIST ---
    elif cmd == "list":
        print("\n🔗 Active Command Aliases:")
        # Find all .bat files in root that look like launchers
        count = 0
        for f in root.glob("*.bat"):
            # Filter out setup scripts or non-launchers if strictly needed
            if f.name not in ["setup_xsv.bat", "setup_path.bat"]: 
                print(f"  🔹 {f.stem}")
                count += 1
        if count == 0:
            print("  (None found)")
        print("")

    # --- NUKE ---
    elif cmd == "nuke":
        if len(args) < 2: return
        target_name = args[1]
        target_file = root / f"{target_name}.bat"
        
        if target_name.lower() == "xsv":
            print("❌ You cannot nuke the original 'xsv' command!")
            return

        if target_file.exists():
            try:
                os.remove(target_file)
                print(f"🗑️  Alias '{target_name}' deleted.")
            except Exception as e:
                print(f"❌ Error deleting: {e}")
        else:
            print(f"❌ Alias '{target_name}' not found.")
            
    else:
        # Implicit 'add' if they just type: xsv alias magic
        # This handles your previous request: "xsv alias magic"
        print(f"Did you mean: xsv alias add {cmd} ?")