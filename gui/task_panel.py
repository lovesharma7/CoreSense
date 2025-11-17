import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import datetime, timedelta
from core.task_manager import TaskManager
import json

class TaskPanel:
    
    def __init__(self, parent):
        self.parent = parent
        self.task_manager = TaskManager()
        self.current_task_id = None
        
        parent.configure(bg='#f2f6fc')
        
        self._create_toolbar()
        self._create_main_layout()
        
        self.refresh_task_list()
        self.update_statistics()
    
    def _create_toolbar(self):
        toolbar = tk.Frame(self.parent, bg='#ecf0f1', height=45)
        toolbar.pack(fill='x', padx=0, pady=0)
        
        tk.Label(toolbar, text="Quick Filter:", bg='#ecf0f1', font=('Segoe UI', 9)).pack(side='left', padx=(10, 5), pady=8)
        
        ttk.Button(toolbar, text="Today", command=lambda: self.quick_filter('today'), width=8).pack(side='left', padx=2)
        ttk.Button(toolbar, text="This Week", command=lambda: self.quick_filter('week'), width=10).pack(side='left', padx=2)
        ttk.Button(toolbar, text="Overdue", command=lambda: self.quick_filter('overdue'), width=8).pack(side='left', padx=2)
        ttk.Button(toolbar, text="High Priority", command=lambda: self.quick_filter('high'), width=12).pack(side='left', padx=2)
        
        ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=10, pady=5)
        ttk.Button(toolbar, text="Export", command=self.export_tasks, width=8).pack(side='left', padx=2)
        ttk.Button(toolbar, text="Import", command=self.import_tasks, width=8).pack(side='left', padx=2)
        
        ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=10, pady=5)
        ttk.Button(toolbar, text="Expand All", command=self.expand_all, width=10).pack(side='left', padx=2)
        ttk.Button(toolbar, text="Collapse All", command=self.collapse_all, width=10).pack(side='left', padx=2)
    
    def _create_main_layout(self):
        main_container = tk.Frame(self.parent, bg='#f2f6fc')
        main_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        left_panel = tk.Frame(main_container, bg='#f2f6fc')
        left_panel.pack(side='left', fill='both', expand=True)
        
        right_panel = tk.Frame(main_container, bg='#f2f6fc', width=300)
        right_panel.pack(side='right', fill='y', padx=(10, 0))
        right_panel.pack_propagate(False)
        
        self._create_statistics_section(right_panel)
        self._create_filter_section(right_panel)
        self._create_quick_add_section(right_panel)
        
        self._create_task_list_section(left_panel)
        self._create_task_details_section(left_panel)
    
    def _create_statistics_section(self, parent):
        stats_frame = ttk.LabelFrame(parent, text=" Statistics", padding=8)
        stats_frame.pack(fill='x', pady=(0, 10))
        
        self.stat_cards = {}
        stats_data = [
            ('total', 'Total'),
            ('pending', 'Pending'),
            ('completed', 'Done'),
            ('overdue', 'Overdue')
        ]
        
        for i, (key, label) in enumerate(stats_data):
            row = i // 2
            col = i % 2
            
            card = tk.Frame(stats_frame, bg='white', relief='flat')
            card.grid(row=row, column=col, padx=3, pady=3, sticky='ew', ipady=5)
            
            value = tk.Label(card, text="0", font=('Segoe UI', 18, 'bold'), bg='white', fg='black')
            value.pack(pady=(5, 0))
            
            name = tk.Label(card, text=label, font=('Segoe UI', 8), bg='white', fg='black')
            name.pack(pady=(0, 5))
            
            self.stat_cards[key] = value
        
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(stats_frame, text="Overall Progress:", font=('Segoe UI', 9, 'bold')).grid(row=2, column=0, columnspan=2, pady=(8, 2))
        self.progress_bar = ttk.Progressbar(stats_frame, mode='determinate', length=200)
        self.progress_bar.grid(row=3, column=0, columnspan=2, pady=(0, 5))
        
        self.progress_label = tk.Label(stats_frame, text="0%", font=('Segoe UI', 10, 'bold'))
        self.progress_label.grid(row=4, column=0, columnspan=2)
    
    def _create_filter_section(self, parent):
        filter_frame = ttk.LabelFrame(parent, text=" Filters", padding=8)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(filter_frame, text="Search:", font=('Segoe UI', 9)).grid(row=0, column=0, sticky='w', pady=3)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.apply_filters())
        ttk.Entry(filter_frame, textvariable=self.search_var, width=25).grid(row=0, column=1, pady=3, sticky='ew')
        
        tk.Label(filter_frame, text="Status:", font=('Segoe UI', 9)).grid(row=1, column=0, sticky='w', pady=3)
        self.status_filter = tk.StringVar(value='All')
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_filter,
                                    values=['All', 'Pending', 'In Progress', 'Completed', 'Overdue'],
                                    state='readonly', width=22)
        status_combo.grid(row=1, column=1, pady=3, sticky='ew')
        status_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
        
        tk.Label(filter_frame, text="Priority:", font=('Segoe UI', 9)).grid(row=2, column=0, sticky='w', pady=3)
        self.priority_filter = tk.StringVar(value='All')
        priority_combo = ttk.Combobox(filter_frame, textvariable=self.priority_filter,
                                     values=['All', 'Low', 'Medium', 'High', 'Critical'],
                                     state='readonly', width=22)
        priority_combo.grid(row=2, column=1, pady=3, sticky='ew')
        priority_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
        
        tk.Label(filter_frame, text="Category:", font=('Segoe UI', 9)).grid(row=3, column=0, sticky='w', pady=3)
        self.category_filter = tk.StringVar(value='All')
        cat_combo = ttk.Combobox(filter_frame, textvariable=self.category_filter,
                                values=['All', 'Work', 'Personal', 'Study', 'Meeting', 'Other'],
                                state='readonly', width=22)
        cat_combo.grid(row=3, column=1, pady=3, sticky='ew')
        cat_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
        
        ttk.Button(filter_frame, text="Clear All Filters", command=self.clear_filters).grid(row=4, column=0, columnspan=2, pady=(8, 0))
        
        filter_frame.grid_columnconfigure(1, weight=1)
    
    def _create_quick_add_section(self, parent):
        quick_frame = ttk.LabelFrame(parent, text=" Quick Add Task", padding=8)
        quick_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(quick_frame, text="Task:", font=('Segoe UI', 9)).grid(row=0, column=0, sticky='w', pady=3)
        self.quick_task_entry = ttk.Entry(quick_frame, width=25)
        self.quick_task_entry.grid(row=0, column=1, pady=3, sticky='ew')
        self.quick_task_entry.bind('<Return>', lambda e: self.quick_add_task())
        
        ttk.Button(quick_frame, text="Add Task", command=self.quick_add_task).grid(row=1, column=0, columnspan=2, pady=5, sticky='ew')
        
        quick_frame.grid_columnconfigure(1, weight=1)
    
    def _create_task_list_section(self, parent):
        list_frame = ttk.LabelFrame(parent, text=" Task View", padding=5)
        list_frame.pack(fill='both', expand=True)
        
        columns = ('Priority', 'Category', 'Description', 'Progress', 'Deadline', 'Status')
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings',
                                      selectmode='browse', height=15)
        
        self.task_tree.heading('#0', text='Task ID')
        self.task_tree.column('#0', width=80, stretch=False)
        
        self.task_tree.heading('Priority', text='Priority')
        self.task_tree.column('Priority', width=70, stretch=False)
        
        self.task_tree.heading('Category', text='Category')
        self.task_tree.column('Category', width=80, stretch=False)
        
        self.task_tree.heading('Description', text='Description')
        self.task_tree.column('Description', width=280, stretch=True)
        
        self.task_tree.heading('Progress', text='Progress')
        self.task_tree.column('Progress', width=80, stretch=False)
        
        self.task_tree.heading('Deadline', text='Deadline')
        self.task_tree.column('Deadline', width=90, stretch=False)
        
        self.task_tree.heading('Status', text='Status')
        self.task_tree.column('Status', width=90, stretch=False)
        
        v_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.task_tree.yview)
        h_scroll = ttk.Scrollbar(list_frame, orient='horizontal', command=self.task_tree.xview)
        self.task_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.task_tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        self.task_tree.bind('<<TreeviewSelect>>', self.on_task_select)
        self.task_tree.bind('<Double-Button-1>', self.edit_task_dialog)
    
    def _create_task_details_section(self, parent):
        details_frame = ttk.LabelFrame(parent, text=" Task Details & Actions", padding=8)
        details_frame.pack(fill='x', pady=(10, 0))
        
        self.detail_text = tk.Text(details_frame, height=6, width=80, wrap='word',
                                   font=('Segoe UI', 9), relief='flat', bg='#f9f9f9')
        self.detail_text.pack(fill='x', pady=(0, 8))
        
        btn_frame = tk.Frame(details_frame)
        btn_frame.pack(fill='x')
        
        ttk.Button(btn_frame, text="Add Task", command=self.add_task_dialog, width=11).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Edit", command=self.edit_task_dialog, width=9).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_task, width=9).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Complete", command=self.mark_complete, width=10).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Add Note", command=self.add_note_dialog, width=10).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Add Subtask", command=self.add_subtask_dialog, width=11).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Edit Subtasks", command=self.edit_subtask_progress_dialog, width=12).pack(side='left', padx=2)
   
    def refresh_task_list(self, tasks=None):
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        if tasks is None:
            tasks = self.task_manager.get_all_tasks()
        
        for task in tasks:
            task_progress = self.task_manager.get_task_weighted_progress(task)
            status = self._get_task_status(task)
            
            progress_indicator = ""
            if task.get('subtasks'):
                progress_indicator = ""
            
            parent_id = self.task_tree.insert('', 'end', 
                iid=f"task_{task['id']}", 
                text=f"Task #{task['id']}",
                values=(
                    task['priority'],
                    task.get('category', 'Other'),
                    task['description'][:45] + '...' if len(task['description']) > 45 else task['description'],
                    f"{task_progress}%{progress_indicator}",
                    task.get('deadline', 'None'),
                    status
                ),
                tags=(status.lower(),),
                open=False
            )
            
            for subtask in task.get('subtasks', []):
                subtask_status = '✓ Done' if subtask.get('completed', False) else '○ Pending'
                self.task_tree.insert(parent_id, 'end',
                    text=f"  └─ Subtask {subtask['id']}",
                    values=(
                        '',
                        '',
                        f"  {subtask['description']}",
                        f"{subtask.get('progress', 0)}%",
                        '',
                        subtask_status
                    ),
                    tags=('subtask',))
        
        self.task_tree.tag_configure('completed', foreground='green', font=('Segoe UI', 9))
        self.task_tree.tag_configure('in progress', foreground='blue', font=('Segoe UI', 9))
        self.task_tree.tag_configure('pending', foreground='gray', font=('Segoe UI', 9))
        self.task_tree.tag_configure('overdue', foreground='red', font=('Segoe UI', 9))
        self.task_tree.tag_configure('subtask', foreground='gray', font=('Segoe UI', 8, 'italic'))
        
        self.update_statistics()
    
    def _get_task_status(self, task):
        if task['status'] == 'Completed':
            return 'Completed'
        
        if task.get('deadline'):
            try:
                deadline = datetime.strptime(task['deadline'], '%Y-%m-%d')
                if deadline.date() < datetime.now().date():
                    return 'Overdue'
            except:
                pass
        
        progress = self.task_manager.get_task_weighted_progress(task)
        if progress > 0 and progress < 100:
            return 'In Progress'
        
        return task['status']
    
    def expand_all(self):
        def expand_children(item):
            self.task_tree.item(item, open=True)
            for child in self.task_tree.get_children(item):
                expand_children(child)
        
        for item in self.task_tree.get_children():
            expand_children(item)
    
    def collapse_all(self):
        def collapse_children(item):
            self.task_tree.item(item, open=False)
            for child in self.task_tree.get_children(item):
                collapse_children(child)
        
        for item in self.task_tree.get_children():
            collapse_children(item)
    
    def on_task_select(self, event):
        selection = self.task_tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        
        if not item_id.startswith('task_'):
            return
        
        task_id = int(item_id.replace('task_', ''))
        task = self.task_manager.get_task(task_id)
        
        if task:
            self.current_task_id = task_id
            task_progress = self.task_manager.get_task_weighted_progress(task)
            
            self.detail_text.delete('1.0', tk.END)
            
            self.detail_text.tag_configure('bold', font=('Segoe UI', 9, 'bold'))
            self.detail_text.tag_configure('title', font=('Segoe UI', 11, 'bold'))
            self.detail_text.tag_configure('normal', font=('Segoe UI', 9))
            
            self.detail_text.insert(tk.END, f"Task #{task['id']}: ", 'bold')
            self.detail_text.insert(tk.END, f"{task['description']}\n\n")
            
            self.detail_text.insert(tk.END, "Priority: ", 'bold')
            self.detail_text.insert(tk.END, f"{task['priority']}  |  ", 'normal')
            
            self.detail_text.insert(tk.END, "Category: ", 'bold')
            self.detail_text.insert(tk.END, f"{task.get('category', 'Other')}  |  ", 'normal')
            
            self.detail_text.insert(tk.END, "Status: ", 'bold')
            self.detail_text.insert(tk.END, f"{task['status']}\n", 'normal')
            
            self.detail_text.insert(tk.END, "Progress: ", 'bold')
            progress_note = f" (auto-calculated from {len(task.get('subtasks', []))} subtasks)" if task.get('subtasks') else ""
            self.detail_text.insert(tk.END, f"{task_progress}%{progress_note}\n", 'normal')
            
            self.detail_text.insert(tk.END, "Deadline: ", 'bold')
            self.detail_text.insert(tk.END, f"{task.get('deadline', 'Not set')}  |  ", 'normal')
            
            self.detail_text.insert(tk.END, "Created: ", 'bold')
            self.detail_text.insert(tk.END, f"{task['created_at']}\n", 'normal')
            
            self.detail_text.insert(tk.END, "Tags: ", 'bold')
            self.detail_text.insert(tk.END, f"{', '.join(task.get('tags', [])) or 'None'}\n\n", 'normal')
            
            self.detail_text.insert(tk.END, "Notes:\n", 'bold')
            notes = task.get('notes', '')
            if notes:
                self.detail_text.insert(tk.END, f"{notes}\n\n", 'normal')
            else:
                self.detail_text.insert(tk.END, "No notes added\n\n", 'normal')
            
            subtasks = task.get('subtasks', [])
            self.detail_text.insert(tk.END, f"Subtasks ({len(subtasks)}):\n", 'bold')
            
            if not subtasks:
                self.detail_text.insert(tk.END, "No subtasks added\n", 'normal')
            else:
                for st in subtasks:
                    status_icon = '✓' if st.get('completed') else '○'
                    self.detail_text.insert(tk.END, f"  {status_icon} {st['description']} ({st.get('progress', 0)}%)\n", 'normal')
 
    def add_task_dialog(self):
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add New Task")
        dialog.geometry("600x500")
        dialog.transient(self.parent)
        dialog.grab_set()
                
        tk.Label(dialog, text="Description:", font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky='w', padx=10, pady=15)
        desc_entry = ttk.Entry(dialog, width=55)
        desc_entry.grid(row=0, column=1, padx=10, pady=5, columnspan=2, sticky='ew')
        desc_entry.focus_set()
        
        tk.Label(dialog, text="Priority:", font=('Segoe UI', 9, 'bold')).grid(row=1, column=0, sticky='w', padx=10, pady=5)
        priority_var = tk.StringVar(value='Medium')
        ttk.Combobox(dialog, textvariable=priority_var, values=['Low', 'Medium', 'High', 'Critical'],
                    state='readonly', width=15).grid(row=1, column=1, sticky='w', padx=10, pady=5)
        
        tk.Label(dialog, text="Category:", font=('Segoe UI', 9, 'bold')).grid(row=2, column=0, sticky='w', padx=10, pady=5)
        category_var = tk.StringVar(value='Personal')
        ttk.Combobox(dialog, textvariable=category_var, values=['Work', 'Personal', 'Study', 'Meeting', 'Other'],
                    state='readonly', width=15).grid(row=2, column=1, sticky='w', padx=10, pady=5)
        
        tk.Label(dialog, text="Deadline:", font=('Segoe UI', 9, 'bold')).grid(row=3, column=0, sticky='w', padx=10, pady=5)
        deadline_entry = ttk.Entry(dialog, width=18)
        deadline_entry.insert(0, (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'))
        deadline_entry.grid(row=3, column=1, sticky='w', padx=10, pady=5)
        tk.Label(dialog, text="(YYYY-MM-DD)", font=('Segoe UI', 8, 'italic')).grid(row=3, column=2, sticky='w')
        
        tk.Label(dialog, text="Progress:", font=('Segoe UI', 9, 'bold')).grid(row=4, column=0, sticky='w', padx=10, pady=5)
        progress_var = tk.IntVar(value=0)
        progress_scale = ttk.Scale(dialog, from_=0, to=100, variable=progress_var, orient='horizontal', length=250)
        progress_scale.grid(row=4, column=1, sticky='w', padx=10, pady=5)
        progress_label = tk.Label(dialog, text="0%", font=('Segoe UI', 9))
        progress_label.grid(row=4, column=2, sticky='w', padx=5)
        
        def update_progress(*args):
            progress_label.config(text=f"{progress_var.get()}%")
        progress_var.trace('w', update_progress)
        
        tk.Label(dialog, text="Tags:", font=('Segoe UI', 9, 'bold')).grid(row=6, column=0, sticky='w', padx=10, pady=5)
        tags_entry = ttk.Entry(dialog, width=55)
        tags_entry.grid(row=6, column=1, columnspan=2, padx=10, pady=5, sticky='ew')
        tk.Label(dialog, text="(Comma-separated)", 
                font=('Segoe UI', 8, 'italic')).grid(row=7, column=1, columnspan=2, sticky='w', padx=10)
        
        tk.Label(dialog, text="Notes:", font=('Segoe UI', 9, 'bold')).grid(row=8, column=0, sticky='nw', padx=10, pady=5)
        notes_text = scrolledtext.ScrolledText(dialog, width=55, height=8, wrap='word')
        notes_text.grid(row=8, column=1, columnspan=2, padx=10, pady=5, sticky='ew')
        
        def save_task():
            desc = desc_entry.get().strip()
            if not desc:
                messagebox.showwarning("Input Error", "Please enter a description")
                return
            
            tags = [t.strip() for t in tags_entry.get().split(',') if t.strip()]
            notes = notes_text.get('1.0', tk.END).strip()
            
            self.task_manager.add_task(
                description=desc,
                priority=priority_var.get(),
                category=category_var.get(),
                deadline=deadline_entry.get(),
                progress=progress_var.get(),
                tags=tags,
                notes=notes
            )
            
            self.refresh_task_list()
            dialog.destroy()
            messagebox.showinfo("Success", "Task added successfully!")
        
        btn_frame = tk.Frame(dialog)
        btn_frame.grid(row=9, column=0, columnspan=3, pady=15)
        ttk.Button(btn_frame, text="Save Task", command=save_task, width=15).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15).pack(side='left', padx=5)
        
        dialog.grid_columnconfigure(1, weight=1)
    
    def edit_task_dialog(self, event=None):
        if not self.current_task_id:
            messagebox.showwarning("Selection Error", "Please select a task to edit")
            return
        
        task = self.task_manager.get_task(self.current_task_id)
        if not task:
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Edit Task #{task['id']}")
        dialog.geometry("600x525")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        tk.Label(dialog, text="Description:", font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky='w', padx=10, pady=15)
        desc_entry = ttk.Entry(dialog, width=55)
        desc_entry.insert(0, task['description'])
        desc_entry.grid(row=0, column=1, padx=10, pady=5, columnspan=2, sticky='ew')
        
        tk.Label(dialog, text="Priority:", font=('Segoe UI', 9, 'bold')).grid(row=1, column=0, sticky='w', padx=10, pady=5)
        priority_var = tk.StringVar(value=task['priority'])
        ttk.Combobox(dialog, textvariable=priority_var, values=['Low', 'Medium', 'High', 'Critical'],
                    state='readonly', width=15).grid(row=1, column=1, sticky='w', padx=10, pady=5)
        
        tk.Label(dialog, text="Category:", font=('Segoe UI', 9, 'bold')).grid(row=2, column=0, sticky='w', padx=10, pady=5)
        category_var = tk.StringVar(value=task.get('category', 'Work'))
        ttk.Combobox(dialog, textvariable=category_var, values=['Work', 'Personal', 'Study', 'Meeting', 'Other'],
                    state='readonly', width=15).grid(row=2, column=1, sticky='w', padx=10, pady=5)
        
        tk.Label(dialog, text="Status:", font=('Segoe UI', 9, 'bold')).grid(row=3, column=0, sticky='w', padx=10, pady=5)
        status_var = tk.StringVar(value=task['status'])
        ttk.Combobox(dialog, textvariable=status_var, values=['Pending', 'In Progress', 'Completed'],
                    state='readonly', width=15).grid(row=3, column=1, sticky='w', padx=10, pady=5)
        
        tk.Label(dialog, text="Deadline:", font=('Segoe UI', 9, 'bold')).grid(row=4, column=0, sticky='w', padx=10, pady=5)
        deadline_entry = ttk.Entry(dialog, width=18)
        deadline_entry.insert(0, task.get('deadline', ''))
        deadline_entry.grid(row=4, column=1, sticky='w', padx=10, pady=5)
        
        has_subtasks = len(task.get('subtasks', [])) > 0
        
        tk.Label(dialog, text="Progress:", font=('Segoe UI', 9, 'bold')).grid(row=5, column=0, sticky='w', padx=10, pady=5)
        progress_var = tk.IntVar(value=task.get('progress', 0))
        progress_scale = ttk.Scale(dialog, from_=0, to=100, variable=progress_var, orient='horizontal', length=250)
        progress_scale.grid(row=5, column=1, sticky='w', padx=10, pady=5)
        progress_label = tk.Label(dialog, text=f"{task.get('progress', 0)}%", font=('Segoe UI', 9))
        progress_label.grid(row=5, column=2, sticky='w', padx=5)
        
        if has_subtasks:
            progress_scale.config(state='disabled')
            warning_label = tk.Label(dialog,
                text=f"⚠️ Progress auto-calculated from {len(task['subtasks'])} subtasks. Use 'Edit Subtasks' to change.",
                font=('Segoe UI', 8, 'italic'), foreground='#e67e22', wraplength=480, justify='left')
            warning_label.grid(row=6, column=0, columnspan=3, sticky='w', padx=10)
        else:
            def update_progress(*args):
                progress_label.config(text=f"{progress_var.get()}%")
            progress_var.trace('w', update_progress)
        
        tk.Label(dialog, text="Tags:", font=('Segoe UI', 9, 'bold')).grid(row=7, column=0, sticky='w', padx=10, pady=5)
        tags_entry = ttk.Entry(dialog, width=55)
        tags_entry.insert(0, ', '.join(task.get('tags', [])))
        tags_entry.grid(row=7, column=1, columnspan=2, padx=10, pady=5, sticky='ew')
        
        tk.Label(dialog, text="Notes:", font=('Segoe UI', 9, 'bold')).grid(row=8, column=0, sticky='nw', padx=10, pady=5)
        notes_text = scrolledtext.ScrolledText(dialog, width=55, height=8, wrap='word')
        notes_text.insert('1.0', task.get('notes', ''))
        notes_text.grid(row=8, column=1, columnspan=2, padx=10, pady=5, sticky='ew')
        
        def update_task_action():
            desc = desc_entry.get().strip()
            if not desc:
                messagebox.showwarning("Input Error", "Please enter a description")
                return
            
            tags = [t.strip() for t in tags_entry.get().split(',') if t.strip()]
            notes = notes_text.get('1.0', tk.END).strip()
            
            update_data = {
                'description': desc,
                'priority': priority_var.get(),
                'category': category_var.get(),
                'status': status_var.get(),
                'deadline': deadline_entry.get(),
                'tags': tags,
                'notes': notes
            }
            
            if not has_subtasks:
                update_data['progress'] = progress_var.get()
            
            self.task_manager.update_task(self.current_task_id, **update_data)
            
            self.refresh_task_list()
            self.on_task_select(None)
            dialog.destroy()
            messagebox.showinfo("Success", "Task updated successfully!")
        
        btn_frame = tk.Frame(dialog)
        btn_frame.grid(row=9, column=0, columnspan=3, pady=15)
        ttk.Button(btn_frame, text="Update Task", command=update_task_action, width=15).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15).pack(side='left', padx=5)
        
        dialog.grid_columnconfigure(1, weight=1)
    
    def add_note_dialog(self):
        if not self.current_task_id:
            messagebox.showwarning("Selection Error", "Please select a task")
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Note")
        dialog.geometry("500x380")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        tk.Label(dialog, text="Add Note to Task:", font=('Segoe UI', 10, 'bold')).pack(pady=10, padx=10, anchor='w')
        
        note_text = scrolledtext.ScrolledText(dialog, width=55, height=12, wrap='word', font=('Segoe UI', 9))
        note_text.pack(padx=10, pady=10)
        note_text.focus_set()
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        def save_note():
            note = note_text.get('1.0', tk.END).strip()
            if note:
                task = self.task_manager.get_task(self.current_task_id)
                existing = task.get('notes', '')
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
                new_notes = f"{existing}\n\n[{timestamp}]\n{note}" if existing else f"[{timestamp}]\n{note}"
                self.task_manager.update_task(self.current_task_id, notes=new_notes)
                self.refresh_task_list()
                self.on_task_select(None)
                dialog.destroy()
                messagebox.showinfo("Success", "Note added successfully!")
            else:
                messagebox.showwarning("Input Error", "Please enter a note")
        
        ttk.Button(btn_frame, text="Save Note", command=save_note, width=15).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15).pack(side='left', padx=5)
    
    def add_subtask_dialog(self):
        if not self.current_task_id:
            messagebox.showwarning("Selection Error", "Please select a parent task")
            return
        
        task = self.task_manager.get_task(self.current_task_id)
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Subtask")
        dialog.geometry("520x250")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        if task['status'] == 'Completed':
            warning = tk.Label(dialog, 
                text="⚠️ This task is marked as Completed. Adding a subtask will change it to 'In Progress'.",
                font=('Segoe UI', 9, 'bold'), foreground='#e67e22', wraplength=480, justify='left', bg='#fff3cd', pady=8)
            warning.pack(fill='x', padx=10, pady=10)
        
        tk.Label(dialog, text="Subtask Description:", font=('Segoe UI', 9, 'bold')).pack(pady=10, padx=10, anchor='w')
        subtask_entry = ttk.Entry(dialog, width=55, font=('Segoe UI', 9))
        subtask_entry.pack(padx=10, pady=5)
        subtask_entry.focus_set()
        
        tk.Label(dialog, text="Initial Progress (%):", font=('Segoe UI', 9, 'bold')).pack(pady=(10, 5), padx=10, anchor='w')
        
        progress_frame = tk.Frame(dialog)
        progress_frame.pack(padx=10, pady=5)
        
        progress_var = tk.IntVar(value=0)
        ttk.Scale(progress_frame, from_=0, to=100, variable=progress_var, orient='horizontal', length=380).pack(side='left', padx=5)
        progress_label = tk.Label(progress_frame, text="0%", font=('Segoe UI', 9, 'bold'), width=5)
        progress_label.pack(side='left', padx=5)
        
        def update_label(*args):
            progress_label.config(text=f"{progress_var.get()}%")
        progress_var.trace('w', update_label)
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=15)
        
        def save_subtask():
            desc = subtask_entry.get().strip()
            if desc:
                self.task_manager.add_subtask(self.current_task_id, desc, progress_var.get())
                self.refresh_task_list()
                self.task_tree.item(f"task_{self.current_task_id}", open=True)
                self.on_task_select(None)
                dialog.destroy()
                messagebox.showinfo("Success", "Subtask added! Parent task progress auto-updated.")
            else:
                messagebox.showwarning("Input Error", "Please enter a subtask description")
        
        ttk.Button(btn_frame, text="Add Subtask", command=save_subtask, width=15).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15).pack(side='left', padx=5)
    
    def edit_subtask_progress_dialog(self):
        if not self.current_task_id:
            messagebox.showwarning("Selection Error", "Please select a task first")
            return
        
        task = self.task_manager.get_task(self.current_task_id)
        if not task or not task.get('subtasks'):
            messagebox.showinfo("No Subtasks", "This task has no subtasks to edit")
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Edit Subtasks - Task #{self.current_task_id}")
        dialog.geometry("620x580")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        tk.Label(dialog, text="Update Subtask Progress (Parent task auto-updates):", 
                font=('Segoe UI', 11, 'bold')).pack(pady=10)
        
        list_frame = tk.Frame(dialog)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(list_frame, bg='white')
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        progress_vars = []
        
        for i, subtask in enumerate(task['subtasks']):
            subtask_frame = tk.LabelFrame(scrollable_frame, text=f"Subtask {subtask['id']}", 
                                          font=('Segoe UI', 9, 'bold'), bg='white', padx=10, pady=8)
            subtask_frame.pack(fill='x', padx=5, pady=5)
            
            tk.Label(subtask_frame, text=subtask['description'], font=('Segoe UI', 9), 
                    bg='white', wraplength=480).pack(anchor='w', pady=(0, 5))
            
            progress_frame = tk.Frame(subtask_frame, bg='white')
            progress_frame.pack(fill='x', pady=5)
            
            tk.Label(progress_frame, text="Progress:", font=('Segoe UI', 9), bg='white').pack(side='left', padx=(0, 10))
            
            progress_var = tk.IntVar(value=subtask.get('progress', 0))
            progress_vars.append((i, progress_var))
            
            scale = ttk.Scale(progress_frame, from_=0, to=100, variable=progress_var, orient='horizontal', length=380)
            scale.pack(side='left', padx=5)
            
            progress_label = tk.Label(progress_frame, text=f"{subtask.get('progress', 0)}%", 
                                     font=('Segoe UI', 9, 'bold'), width=5, bg='white')
            progress_label.pack(side='left', padx=5)
            
            progress_var.trace('w', lambda *args, l=progress_label, v=progress_var: l.config(text=f"{v.get()}%"))
            
            completed_var = tk.BooleanVar(value=subtask.get('completed', False))
            
            def on_complete_toggle(idx=i, var=completed_var, pvar=progress_var):
                if var.get():
                    pvar.set(100)
                else:
                    pvar.set(0)
            
            ttk.Checkbutton(subtask_frame, text="Mark as Completed", variable=completed_var, 
                           command=lambda idx=i, v=completed_var, p=progress_var: on_complete_toggle(idx, v, p)).pack(anchor='w')
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        def save_changes():
            for idx, progress_var in progress_vars:
                task['subtasks'][idx]['progress'] = progress_var.get()
                task['subtasks'][idx]['completed'] = progress_var.get() >= 100
            
            self.task_manager.update_subtasks(self.current_task_id)
            
            self.refresh_task_list()
            self.on_task_select(None)
            dialog.destroy()
            messagebox.showinfo("Success", "Subtask progress updated! Parent task auto-updated.")
        
        ttk.Button(btn_frame, text="Save Changes", command=save_changes, width=15).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15).pack(side='left', padx=5)
    
    def mark_complete(self):
        if not self.current_task_id:
            messagebox.showwarning("Selection Error", "Please select a task")
            return
        
        task = self.task_manager.get_task(self.current_task_id)
        
        if task.get('subtasks'):
            incomplete_subtasks = [st for st in task['subtasks'] if st.get('progress', 0) < 100]
            if incomplete_subtasks:
                if not messagebox.askyesno("Incomplete Subtasks",
                    f"This task has {len(incomplete_subtasks)} incomplete subtask(s).\n\n" +
                    "Marking the task as complete will also mark all subtasks as 100% complete.\n\n" +
                    "Continue?"):
                    return
                
                for subtask in task['subtasks']:
                    subtask['progress'] = 100
                    subtask['completed'] = True
        
        self.task_manager.update_task(self.current_task_id, status='Completed', progress=100)
        self.refresh_task_list()
        messagebox.showinfo("Success", "Task marked as completed!")
    
    def delete_task(self):
        if not self.current_task_id:
            messagebox.showwarning("Selection Error", "Please select a task")
            return
        
        if messagebox.askyesno("Confirm", "Delete this task and all its subtasks?"):
            self.task_manager.delete_task(self.current_task_id)
            self.current_task_id = None
            self.detail_text.delete('1.0', tk.END)
            self.refresh_task_list()
    
    def quick_add_task(self):
        desc = self.quick_task_entry.get().strip()
        if desc:
            self.task_manager.add_task(description=desc, priority='Medium')
            self.quick_task_entry.delete(0, tk.END)
            self.refresh_task_list()
    
    def apply_filters(self):
        search = self.search_var.get().lower()
        status = self.status_filter.get()
        priority = self.priority_filter.get()
        category = self.category_filter.get()
        
        filtered = []
        for task in self.task_manager.get_all_tasks():
            task_status = self._get_task_status(task)
            
            if status != 'All' and task_status != status:
                continue
            if priority != 'All' and task['priority'] != priority:
                continue
            if category != 'All' and task.get('category', 'Other') != category:
                continue
            if search and search not in task['description'].lower():
                continue
            
            filtered.append(task)
        
        self.refresh_task_list(filtered)
    
    def clear_filters(self):
        self.search_var.set('')
        self.status_filter.set('All')
        self.priority_filter.set('All')
        self.category_filter.set('All')
        self.refresh_task_list()
    
    def quick_filter(self, filter_type):
        self.clear_filters()
        
        if filter_type == 'today':
            today = datetime.now().strftime('%Y-%m-%d')
            filtered = [t for t in self.task_manager.get_all_tasks() if t.get('deadline') == today]
            self.refresh_task_list(filtered)
        elif filter_type == 'week':
            week_end = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            filtered = [t for t in self.task_manager.get_all_tasks() 
                       if t.get('deadline') and t.get('deadline') <= week_end]
            self.refresh_task_list(filtered)
        elif filter_type == 'overdue':
            self.status_filter.set('Overdue')
            self.apply_filters()
        elif filter_type == 'high':
            self.priority_filter.set('High')
            self.apply_filters()
    
    def export_tasks(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", 
                                                filetypes=[("JSON files", "*.json")])
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.task_manager.get_all_tasks(), f, indent=4)
                messagebox.showinfo("Success", f"Tasks exported!")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
    
    def import_tasks(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            try:
                with open(filename, 'r') as f:
                    tasks = json.load(f)
                for task in tasks:
                    self.task_manager.tasks.append(task)
                self.refresh_task_list()
                messagebox.showinfo("Success", "Tasks imported!")
            except Exception as e:
                messagebox.showerror("Error", f"Import failed: {e}")
    
    def update_statistics(self):
        stats = self.task_manager.get_statistics()
        
        self.stat_cards['total'].config(text=str(stats['total']))
        self.stat_cards['pending'].config(text=str(stats['pending']))
        self.stat_cards['completed'].config(text=str(stats['completed']))
        self.stat_cards['overdue'].config(text=str(stats.get('overdue', 0)))
        
        overall_progress = self.task_manager.get_overall_progress()
        self.progress_bar['value'] = overall_progress
        self.progress_label.config(text=f"{overall_progress:.1f}%")
    
    def save_tasks(self):
        if self.task_manager.save_to_file():
            messagebox.showinfo("Success", "Tasks saved!")
    
    def load_tasks(self):
        if self.task_manager.load_from_file():
            self.refresh_task_list()
            messagebox.showinfo("Success", "Tasks loaded!")
