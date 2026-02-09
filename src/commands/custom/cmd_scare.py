import sys
import os
import tkinter as tk
from tkinter import messagebox

# Module: scare
# Description: Scare the wife

def run(args):
    print("\n🚀 Running Custom Command: scare...")
    
    # --- USER CODE START ---
    root = tk.Tk()
    root.withdraw() # Hide main window
    
    # This blocks the code until user clicks OK
    messagebox.showwarning("SYSTEM ERROR", "You have been HACKED!")
    
    # KEY FIX: Destroy the hidden window to release the thread
    root.destroy() 
    # --- USER CODE END ---
    
    print("\n✅ scare finished.")