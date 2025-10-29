import tkinter as tk
from tkinter import ttk
import sys
import os

if sys.platform == 'win32':
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(2)
    except Exception as e:
        print(f"Could not set DPI awareness: {e}")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import CoreSenseApp

def main():
    root = tk.Tk()
    app = CoreSenseApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
