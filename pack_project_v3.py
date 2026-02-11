import os
import ast
import time

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
OUTPUT_FILE = "GHOST_FULL_SOURCE.md"
IGNORE_DIRS = {'.git', '__pycache__', 'venv', 'env', '.idea', '.vscode', 'dist', 'build', 'node_modules', 'loot'}
IGNORE_FILES = {'.DS_Store', 'Thumbs.db', 'package-lock.json', OUTPUT_FILE, os.path.basename(__file__)}
ALLOWED_EXTENSIONS = {'.py', '.md', '.json', '.bat', '.sh', '.txt', '.yml', '.yaml', '.ini'}

def is_allowed(filename):
    return any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS)

def get_file_symbols(filepath):
    """Extracts Class and Function names from Python files."""
    symbols = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=filepath)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    symbols.append(f"  [C] {node.name}")
                elif isinstance(node, ast.FunctionDef):
                    # Only list top-level functions or key methods if needed
                    symbols.append(f"  [F] {node.name}")
    except:
        pass # Ignore parse errors for non-python files
    return symbols

def generate_index_and_content(startpath):
    tree_lines = []
    content_lines = []
    index_lines = []
    
    # Header
    content_lines.append(f"# 👻 Ghost Shell Source Dump")
    content_lines.append(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
    content_lines.append(f"**Root:** `{os.path.basename(os.getcwd())}`\n")

    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        # 1. Build Visual Tree
        level = root.replace(startpath, '').count(os.sep)
        indent = '│   ' * (level - 1) + '├── ' if level > 0 else ''
        if level == 0:
            tree_lines.append(f"📂 **{os.path.basename(root)}**")
        else:
            tree_lines.append(f"{indent}📂 {os.path.basename(root)}/")
        
        subindent = '│   ' * level + '├── '
        
        for f in files:
            if f in IGNORE_FILES or not is_allowed(f):
                continue
                
            filepath = os.path.join(root, f)
            relpath = os.path.relpath(filepath, startpath).replace("\\", "/")
            
            # Tree Entry
            tree_lines.append(f"{subindent}📄 {f}")
            
            # 2. Extract Symbols (for Index)
            if f.endswith('.py'):
                symbols = get_file_symbols(filepath)
                if symbols:
                    index_lines.append(f"- **{relpath}**")
                    index_lines.extend([f"  - `{s.strip()}`" for s in symbols])

            # 3. Pack Content
            ext = f.split('.')[-1]
            content_lines.append(f"\n{'='*60}")
            content_lines.append(f"## 📄 FILE: {relpath}")
            content_lines.append(f"{'='*60}")
            content_lines.append(f"```{ext}")
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as file_content:
                    content_lines.append(file_content.read())
            except Exception as e:
                content_lines.append(f"!! ERROR READING FILE: {e}")
            
            content_lines.append("```\n")

    # Assemble Final Output
    final_output = []
    
    final_output.append("## 🗺️ PROJECT STRUCTURE")
    final_output.append("```text")
    final_output.append("\n".join(tree_lines))
    final_output.append("```\n")
    
    final_output.append("## 🧠 CODE INDEX (Symbols)")
    final_output.append("> Quick reference of all Classes [C] and Functions [F]")
    final_output.append("\n".join(index_lines))
    final_output.append("\n---\n")
    
    final_output.extend(content_lines)
    
    return "\n".join(final_output)

if __name__ == "__main__":
    print("📦 Packing Ghost Shell (AI-Optimized V3)...")
    cwd = os.getcwd()
    full_text = generate_index_and_content(cwd)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(full_text)
        
    print(f"✅ Done! Upload '{OUTPUT_FILE}' to the chat.")
    print("   (Includes Symbol Index for better AI analysis)")