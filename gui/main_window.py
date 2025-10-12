"""
Main Window for CoreSense Application
Manages the overall layout with tabbed interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
from gui.task_panel import TaskPanel
from gui.monitor_panel import MonitorPanel

class CoreSenseApp:
    """
    Main application class that creates and manages the CoreSense interface
    """
    
    def __init__(self, root):
        """
        Initialize the main application window
        
        Args:
            root: tk.Tk instance - the main window
        """
        self.root = root
        self.root.title("CoreSense - Task & System Monitor")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        # Configure root grid weights for responsiveness
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Apply modern theme
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Modern theme
        
        # Configure custom styles for better appearance
        self._configure_styles()
        
        # Create UI components
        self._create_header()
        self._create_tabbed_interface()
        self._create_footer()
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _configure_styles(self):
        """Configure custom ttk styles for modern appearance"""
        # Header style
        self.style.configure('Header.TLabel', 
                           font=('Segoe UI', 16, 'bold'),
                           background='#2c3e50',
                           foreground='white',
                           padding=15)
        
        # Panel title style
        self.style.configure('PanelTitle.TLabel',
                           font=('Segoe UI', 12, 'bold'),
                           background='#34495e',
                           foreground='white',
                           padding=8)
        
        # Footer style
        self.style.configure('Footer.TLabel',
                           font=('Segoe UI', 9),
                           background='#ecf0f1',
                           padding=5)
        
        # Notebook tab styling
        self.style.configure('TNotebook', 
                           background='#ecf0f1',
                           borderwidth=0)
        
        self.style.configure('TNotebook.Tab',
                           font=('Segoe UI', 11, 'bold'),
                           padding=[20, 10],
                           background='#bdc3c7')
        
        self.style.map('TNotebook.Tab',
                      background=[('selected', '#3498db')],
                      foreground=[('selected', 'white'), ('!selected', '#2c3e50')],
                      expand=[('selected', [1, 1, 1, 0])])
    
    def _create_header(self):
        """Create application header with title"""
        header_frame = ttk.Frame(self.root, style='Header.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew')
        
        # Configure header background
        self.style.configure('Header.TFrame', background='#2c3e50')
        
        # Application title
        title_label = ttk.Label(
            header_frame,
            text="🔧 CoreSense - Hybrid Management System",
            style='Header.TLabel'
        )
        title_label.pack(fill='x')
    
    def _create_tabbed_interface(self):
        """Create notebook with tabs for different functionalities"""
        # Create notebook widget
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        
        # Tab 1: Task Management
        task_frame = ttk.Frame(self.notebook)
        self.task_panel = TaskPanel(task_frame)
        self.notebook.add(task_frame, text='📋 Task Manager')
        
        # Tab 2: System Monitor
        monitor_frame = ttk.Frame(self.notebook)
        self.monitor_panel = MonitorPanel(monitor_frame)
        self.notebook.add(monitor_frame, text='📊 System Monitor')
        
        # Bind tab change event
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
    
    def _create_footer(self):
        """Create footer with status information"""
        footer_frame = ttk.Frame(self.root)
        footer_frame.grid(row=2, column=0, sticky='ew')
        
        self.style.configure('Footer.TFrame', background='#ecf0f1')
        footer_frame.configure(style='Footer.TFrame')
        
        status_label = ttk.Label(
            footer_frame,
            text="Ready | CoreSense v1.0 | PBL Project",
            style='Footer.TLabel'
        )
        status_label.pack(side='left', padx=10)
    
    def on_tab_changed(self, event):
        """Handle tab change event"""
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab == 0:
            # Task Manager tab selected
            pass
        elif current_tab == 1:
            # System Monitor tab selected
            pass
    
    def on_closing(self):
        """Handle application close event"""
        # Stop monitoring thread before closing
        if hasattr(self, 'monitor_panel'):
            self.monitor_panel.stop_monitoring()
        
        # Save tasks before closing
        if hasattr(self, 'task_panel'):
            if messagebox.askokcancel("Quit", "Save tasks before closing?"):
                self.task_panel.save_tasks()
        
        self.root.destroy()
