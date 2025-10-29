import tkinter as tk
from tkinter import ttk, messagebox
from core.system_monitor import SystemMonitor

class MonitorPanel:
    def __init__(self, parent):
        self.parent = parent
        self.monitor = SystemMonitor()
        self.monitoring = False
        
        parent.grid_rowconfigure(2, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        self._create_panel_header()
        self._create_control_panel()
        self._create_stats_display()
        self._create_process_list()
        self._create_action_buttons()
    
    def _create_panel_header(self):
        header = ttk.Label(
            self.parent,
            text="System Monitor",
            style='PanelTitle.TLabel'
        )
        header.grid(row=0, column=0, sticky='ew')
    
    def _create_control_panel(self):
        control_frame = ttk.LabelFrame(
            self.parent,
            text="Monitoring Control",
            padding=10
        )
        control_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=10)
        
        self.start_stop_btn = ttk.Button(
            control_frame,
            text="▶ Start Monitoring",
            command=self.toggle_monitoring
        )
        self.start_stop_btn.pack(side='left', padx=5)
        
        self.status_label = ttk.Label(
            control_frame,
            text="● Stopped",
            foreground='red',
            font=('Segoe UI', 10, 'bold')
        )
        self.status_label.pack(side='left', padx=20)
    
    def _create_stats_display(self):
        stats_frame = ttk.LabelFrame(
            self.parent,
            text="System Resources",
            padding=10
        )
        stats_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=5)
        stats_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(stats_frame, text="CPU Usage:", font=('Segoe UI', 10, 'bold')).grid(
            row=0, column=0, sticky='w', pady=5, padx=5
        )
        self.cpu_label = ttk.Label(
            stats_frame,
            text="0.0%",
            font=('Segoe UI', 10),
            foreground='blue'
        )
        self.cpu_label.grid(row=0, column=1, sticky='w', pady=5)
        
        self.cpu_progress = ttk.Progressbar(
            stats_frame,
            mode='determinate',
            length=400
        )
        self.cpu_progress.grid(row=0, column=2, sticky='ew', padx=10, pady=5)
        
        ttk.Label(stats_frame, text="Memory Usage:", font=('Segoe UI', 10, 'bold')).grid(
            row=1, column=0, sticky='w', pady=5, padx=5
        )
        self.mem_label = ttk.Label(
            stats_frame,
            text="0.0%",
            font=('Segoe UI', 10),
            foreground='green'
        )
        self.mem_label.grid(row=1, column=1, sticky='w', pady=5)
        
        self.mem_progress = ttk.Progressbar(
            stats_frame,
            mode='determinate',
            length=400
        )
        self.mem_progress.grid(row=1, column=2, sticky='ew', padx=10, pady=5)
        
        self.mem_details = ttk.Label(
            stats_frame,
            text="Used: 0.00 GB / Total: 0.00 GB",
            font=('Segoe UI', 9)
        )
        self.mem_details.grid(row=2, column=0, columnspan=3, sticky='w', pady=5, padx=5)
        
        stats_frame.grid_columnconfigure(2, weight=1)
    
    def _create_process_list(self):
        list_frame = ttk.LabelFrame(
            self.parent,
            text="Running Processes (Top 50 by Memory Usage)",
            padding=5
        )
        list_frame.grid(row=3, column=0, sticky='nsew', padx=10, pady=5)
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        columns = ('PID', 'Name', 'CPU %', 'Memory %', 'Status')
        self.process_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            selectmode='browse',
            height=12
        )
        
        self.process_tree.heading('PID', text='PID')
        self.process_tree.column('PID', width=80, stretch=False)
        
        self.process_tree.heading('Name', text='Process Name')
        self.process_tree.column('Name', width=300, stretch=True)
        
        self.process_tree.heading('CPU %', text='CPU %')
        self.process_tree.column('CPU %', width=100, stretch=False)
        
        self.process_tree.heading('Memory %', text='Memory %')
        self.process_tree.column('Memory %', width=120, stretch=False)
        
        self.process_tree.heading('Status', text='Status')
        self.process_tree.column('Status', width=100, stretch=False)
        
        v_scrollbar = ttk.Scrollbar(
            list_frame,
            orient='vertical',
            command=self.process_tree.yview
        )
        h_scrollbar = ttk.Scrollbar(
            list_frame,
            orient='horizontal',
            command=self.process_tree.xview
        )
        self.process_tree.configure(
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        self.process_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
    
    def _create_action_buttons(self):
        button_frame = ttk.Frame(self.parent)
        button_frame.grid(row=4, column=0, sticky='ew', padx=10, pady=10)
        
        self.refresh_btn = ttk.Button(
            button_frame,
            text="🔄 Refresh Now",
            command=self.refresh_data,
            state='disabled'
        )
        self.refresh_btn.pack(side='left', padx=5)
        
        self.kill_btn = ttk.Button(
            button_frame,
            text="❌ Terminate Process",
            command=self.kill_process,
            state='disabled'
        )
        self.kill_btn.pack(side='left', padx=5)
    
    def toggle_monitoring(self):
        if not self.monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        if not self.monitoring:
            self.monitoring = True
            
            self.start_stop_btn.config(text="⏸ Stop Monitoring")
            self.status_label.config(text="● Active", foreground='green')
            
            self.refresh_btn.config(state='normal')
            self.kill_btn.config(state='normal')
            
            self.refresh_data()
    
    def stop_monitoring(self):
        if self.monitoring:
            self.monitoring = False
            
            self.start_stop_btn.config(text="▶ Start Monitoring")
            self.status_label.config(text="● Stopped", foreground='red')
            
            self.refresh_btn.config(state='disabled')
            self.kill_btn.config(state='disabled')
    
    def refresh_data(self):
        self._update_system_stats()
        self._update_process_list()
    
    def _update_system_stats(self):
        try:
            cpu_percent = self.monitor.get_cpu_usage(interval=0.1)
            self.cpu_label.config(text=f"{cpu_percent:.1f}%")
            self.cpu_progress['value'] = cpu_percent
            
            if cpu_percent > 80:
                self.cpu_label.config(foreground='red')
            elif cpu_percent > 50:
                self.cpu_label.config(foreground='orange')
            else:
                self.cpu_label.config(foreground='green')
            
            mem_info = self.monitor.get_memory_usage()
            self.mem_label.config(text=f"{mem_info['percent']:.1f}%")
            self.mem_progress['value'] = mem_info['percent']
            
            details_text = (
                f"Used: {mem_info['used_gb']:.2f} GB / "
                f"Total: {mem_info['total_gb']:.2f} GB"
            )
            self.mem_details.config(text=details_text)
            
            if mem_info['percent'] > 80:
                self.mem_label.config(foreground='red')
            elif mem_info['percent'] > 50:
                self.mem_label.config(foreground='orange')
            else:
                self.mem_label.config(foreground='green')
                
        except Exception as e:
            print(f"Stats update error: {e}")
    
    def _update_process_list(self):
        try:
            for item in self.process_tree.get_children():
                self.process_tree.delete(item)
            
            processes = self.monitor.get_top_processes(limit=50)
            
            for proc in processes:
                self.process_tree.insert(
                    '',
                    'end',
                    values=(
                        proc['pid'],
                        proc['name'],
                        f"{proc['cpu_percent']:.1f}",
                        f"{proc['memory_percent']:.1f}",
                        proc['status']
                    )
                )
        except Exception as e:
            print(f"Process list update error: {e}")
    
    def kill_process(self):
        selected = self.process_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a process")
            return
        
        values = self.process_tree.item(selected[0])['values']
        pid = int(values[0])
        name = values[1]
        
        warning_msg = (
            f"⚠️ WARNING: Terminating processes can cause data loss or system instability!\n\n"
            f"Process: {name}\n"
            f"PID: {pid}\n\n"
            f"Are you absolutely sure you want to terminate this process?"
        )
        
        if messagebox.askyesno("Confirm Termination", warning_msg):
            success, message = self.monitor.kill_process(pid)
            if success:
                messagebox.showinfo("Success", message)
                self.refresh_data()
            else:
                messagebox.showerror("Error", message)
