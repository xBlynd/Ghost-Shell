import sys
import os
import threading  # <--- 1. Import This
import tkinter as tk
from tkinter import messagebox

# Module: scare
# Description: Scare the wife

# 2. Move your logic into a separate function
def popup_logic():
    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning("SYSTEM ERROR", "Critical Warning: You have been HACKED!")
    root.destroy()

def run(args):
    print("\n🚀 Running Custom Command: scare...")
    print("   (Sending to background...)")
    
    # 3. Launch it as a Background Thread
    # 'daemon=True' means it will close if you close the main shell
    t = threading.Thread(target=popup_logic, daemon=True)
    t.start()
    
    print("✅ scare launched. (Terminal is free).")