"""
CoreSense - Hybrid Task Management & System Monitoring Application
Entry Point: Handles DPI awareness and launches main application
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Fix for Windows 11 blurry display on high DPI screens
# Must be called BEFORE creating the root window
if sys.platform == 'win32':
    try:
        from ctypes import windll
        # SetProcessDpiAwareness(2) for per-monitor DPI awareness
        # This prevents blurring on Windows 11 with high DPI displays
        windll.shcore.SetProcessDpiAwareness(2)
    except Exception as e:
        print(f"Could not set DPI awareness: {e}")

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import CoreSenseApp

def main():
    """
    Main entry point for CoreSense application
    Creates root window and starts the application
    """
    root = tk.Tk()
    app = CoreSenseApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
