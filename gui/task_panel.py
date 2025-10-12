"""
Task Management Panel
Provides interface for creating, editing, deleting, and managing user tasks
"""

import tkinter as tk
from tkinter import ttk, messagebox
from core.task_manager import TaskManager

class TaskPanel:
    """
    Task management interface with CRUD operations
    """
    
    def __init__(self, parent):
        """
        Initialize task panel
        
        Args:
            parent: Parent frame to contain this panel
        """
        self.parent = parent
        self.task_manager = TaskManager()
        
        # Configure parent grid
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        self._create_panel_header()
        self._create_task_list()
        self._create_input_area()
        self._create_button_area()
        
        # Load existing tasks
        self.refresh_task_list()
    
    def _create_panel_header(self):
        """Create panel title header"""
        header = ttk.Label(
            self.parent,
            text="📋 Task Management",
            style='PanelTitle.TLabel'
        )
        header.grid(row=0, column=0, sticky='ew')
    
    def _create_task_list(self):
        """Create treeview widget to display tasks"""
        # Frame for treeview and scrollbar
        list_frame = ttk.Frame(self.parent)
        list_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Create treeview with columns
        columns = ('Status', 'Priority', 'Description')
        self.task_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='tree headings',
            selectmode='browse',
            height=15
        )
        
        # Configure columns
        self.task_tree.heading('#0', text='ID')
        self.task_tree.column('#0', width=50, stretch=False)
        
        self.task_tree.heading('Status', text='Status')
        self.task_tree.column('Status', width=120, stretch=False)
        
        self.task_tree.heading('Priority', text='Priority')
        self.task_tree.column('Priority', width=100, stretch=False)
        
        self.task_tree.heading('Description', text='Description')
        self.task_tree.column('Description', width=500, stretch=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            list_frame,
            orient='vertical',
            command=self.task_tree.yview
        )
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        self.task_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Bind double-click to edit
        self.task_tree.bind('<Double-Button-1>', self.on_task_double_click)
    
    def _create_input_area(self):
        """Create input fields for task details"""
        input_frame = ttk.LabelFrame(
            self.parent,
            text="Task Details",
            padding=10
        )
        input_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=5)
        
        # Task description
        ttk.Label(input_frame, text="Description:").grid(
            row=0, column=0, sticky='w', pady=5
        )
        self.desc_entry = ttk.Entry(input_frame, width=50)
        self.desc_entry.grid(row=0, column=1, columnspan=2, sticky='ew', pady=5, padx=5)
        
        # Priority selection
        ttk.Label(input_frame, text="Priority:").grid(
            row=1, column=0, sticky='w', pady=5
        )
        self.priority_var = tk.StringVar(value='Medium')
        priority_combo = ttk.Combobox(
            input_frame,
            textvariable=self.priority_var,
            values=['Low', 'Medium', 'High'],
            state='readonly',
            width=15
        )
        priority_combo.grid(row=1, column=1, sticky='w', pady=5, padx=5)
        
        input_frame.grid_columnconfigure(1, weight=1)
    
    def _create_button_area(self):
        """Create action buttons"""
        button_frame = ttk.Frame(self.parent)
        button_frame.grid(row=3, column=0, sticky='ew', padx=10, pady=10)
        
        # Add task button
        ttk.Button(
            button_frame,
            text="➕ Add Task",
            command=self.add_task
        ).pack(side='left', padx=5)
        
        # Mark complete button
        ttk.Button(
            button_frame,
            text="✓ Mark Complete",
            command=self.mark_complete
        ).pack(side='left', padx=5)
        
        # Mark pending button
        ttk.Button(
            button_frame,
            text="⏳ Mark Pending",
            command=self.mark_pending
        ).pack(side='left', padx=5)
        
        # Delete task button
        ttk.Button(
            button_frame,
            text="🗑 Delete",
            command=self.delete_task
        ).pack(side='left', padx=5)
        
        # Save button
        ttk.Button(
            button_frame,
            text="💾 Save",
            command=self.save_tasks
        ).pack(side='right', padx=5)
        
        # Load button
        ttk.Button(
            button_frame,
            text="📂 Load",
            command=self.load_tasks
        ).pack(side='right', padx=5)
    
    def refresh_task_list(self):
        """Refresh the task list display"""
        # Clear existing items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Add all tasks
        for task in self.task_manager.get_all_tasks():
            status_icon = '✓' if task['status'] == 'Completed' else '⏳'
            self.task_tree.insert(
                '',
                'end',
                text=task['id'],
                values=(
                    f"{status_icon} {task['status']}",
                    task['priority'],
                    task['description']
                ),
                tags=(task['status'].lower(),)
            )
        
        # Configure tags for visual distinction
        self.task_tree.tag_configure('completed', foreground='green')
        self.task_tree.tag_configure('pending', foreground='blue')
    
    def add_task(self):
        """Add a new task"""
        description = self.desc_entry.get().strip()
        priority = self.priority_var.get()
        
        if not description:
            messagebox.showwarning("Input Error", "Please enter a task description")
            return
        
        self.task_manager.add_task(description, priority)
        self.refresh_task_list()
        
        # Clear input
        self.desc_entry.delete(0, tk.END)
        messagebox.showinfo("Success", "Task added successfully!")
    
    def mark_complete(self):
        """Mark selected task as completed"""
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a task")
            return
        
        task_id = int(self.task_tree.item(selected[0])['text'])
        self.task_manager.update_task_status(task_id, 'Completed')
        self.refresh_task_list()
    
    def mark_pending(self):
        """Mark selected task as pending"""
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a task")
            return
        
        task_id = int(self.task_tree.item(selected[0])['text'])
        self.task_manager.update_task_status(task_id, 'Pending')
        self.refresh_task_list()
    
    def delete_task(self):
        """Delete selected task"""
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a task")
            return
        
        task_id = int(self.task_tree.item(selected[0])['text'])
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
            self.task_manager.delete_task(task_id)
            self.refresh_task_list()
            messagebox.showinfo("Success", "Task deleted successfully!")
    
    def on_task_double_click(self, event):
        """Handle double-click on task to edit"""
        selected = self.task_tree.selection()
        if selected:
            values = self.task_tree.item(selected[0])['values']
            self.desc_entry.delete(0, tk.END)
            self.desc_entry.insert(0, values[2])  # Description
            # Extract priority without icon
            priority_text = values[1]
            self.priority_var.set(priority_text)
    
    def save_tasks(self):
        """Save tasks to file"""
        if self.task_manager.save_to_file():
            messagebox.showinfo("Success", "Tasks saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save tasks")
    
    def load_tasks(self):
        """Load tasks from file"""
        if self.task_manager.load_from_file():
            self.refresh_task_list()
            messagebox.showinfo("Success", "Tasks loaded successfully!")
        else:
            messagebox.showwarning("Warning", "No saved tasks found")
