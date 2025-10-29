import tkinter as tk
from tkinter import ttk, messagebox
from gui.task_panel import TaskPanel
from gui.monitor_panel import MonitorPanel

class CoreSenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CoreSense - Task & System Monitor")
        self.root.geometry("1200x900")
        self.root.minsize(1200, 900)

        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        self.style = ttk.Style()
        self._configure_styles()

        self._create_header()
        self._create_sidebar()
        self._create_content_area()
        self._create_footer()

        self.active_panel = None
        self.show_panel("tasks")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _configure_styles(self):
        self.style.configure('Header.TLabel',
            font=('Segoe UI', 16, 'bold'), padding=15)
        self.style.configure('Sidebar.TButton',
            font=('Segoe UI', 13, 'bold'), padding=18,
            background='#e2e6ea', foreground='#2c3e50')
        self.style.configure('ContentHeader.TLabel',
            font=('Segoe UI', 15, 'bold'), padding=14,
            foreground='white')
        self.style.configure('Footer.TLabel',
            font=('Segoe UI', 9), padding=5)

    def _create_header(self):
        header = ttk.Frame(self.root)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header_label = ttk.Label(
            header,
            text="CoreSense - Task & System Monitor",
            style='Header.TLabel'
        )
        header_label.pack(fill="x")

    def _create_sidebar(self):
        sidebar = ttk.Frame(self.root, width=170)
        sidebar.grid(row=1, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        self.btn_tasks = ttk.Button(sidebar, text="Task Manager", style='Sidebar.TButton',
                                   command=lambda: self.show_panel("tasks"))
        self.btn_tasks.pack(fill="x", pady=(10,6), padx=18)

        self.btn_monitor = ttk.Button(sidebar, text="System Monitor", style='Sidebar.TButton',
                                   command=lambda: self.show_panel("monitor"))
        self.btn_monitor.pack(fill="x", pady=6, padx=18)

    def _create_content_area(self):
        self.content_frame = tk.Frame(self.root, bg="#f9fbfe")
        self.content_frame.grid(row=1, column=1, sticky="nsew")
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        self.panel_header = tk.Label(self.content_frame, font=('Segoe UI', 15, 'bold'), pady=10, anchor="w")
        self.panel_header.pack(fill="x")

        self.panel_container = tk.Frame(self.content_frame, bg="#f9fbfe")
        self.panel_container.pack(fill="both", expand=True, padx=20, pady=16)

        self.task_panel_frame = tk.Frame(self.panel_container, bg="#f9fbfe")
        self.task_panel = TaskPanel(self.task_panel_frame)
        self.monitor_panel_frame = tk.Frame(self.panel_container, bg="#f9fbfe")
        self.monitor_panel = MonitorPanel(self.monitor_panel_frame)

    def show_panel(self, which):
        for frame in [self.task_panel_frame, self.monitor_panel_frame]:
            frame.pack_forget()
        if self.active_panel == "monitor":
            self.monitor_panel.stop_monitoring()
        if which == "tasks":
            self.panel_header.config(text="Task Manager")
            self.task_panel_frame.pack(fill="both", expand=True)
        else:
            self.panel_header.config(text="System Monitor")
            self.monitor_panel_frame.pack(fill="both", expand=True)
        self.active_panel = which

    def _create_footer(self):
        footer = ttk.Frame(self.root)
        footer.grid(row=2, column=0, columnspan=2, sticky="ew")
        footer_label = ttk.Label(
            footer,
            text="CoreSense v1.0",
            style='Footer.TLabel'
        )
        footer_label.pack(side='left', padx=10)

    def on_closing(self):
        if hasattr(self, 'monitor_panel'):
            self.monitor_panel.stop_monitoring()
        if hasattr(self, 'task_panel'):
            if messagebox.askokcancel("Quit", "Save tasks before closing?"):
                self.task_panel.save_tasks()
        self.root.destroy()
