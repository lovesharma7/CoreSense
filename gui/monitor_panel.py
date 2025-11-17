import tkinter as tk
from tkinter import ttk, messagebox
from core.system_monitor import SystemMonitor
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from collections import deque
import threading
import time
import numpy as np


class MonitorPanel:
    def __init__(self, parent):
        self.parent = parent
        self.monitor = SystemMonitor()
        self.monitoring = False
        self.refreshing = False
        self.monitor_thread = None
        self.cpu_data = deque([0] * 60, maxlen=60)
        self.mem_data = deque([0] * 60, maxlen=60)
        parent.configure(bg='#f2f6fc')

        self._create_main_layout()

    def _create_main_layout(self):
        main_container = tk.Frame(self.parent, bg='#f2f6fc')
        main_container.pack(fill='both', expand=True, padx=10, pady=5)

        left_panel = tk.Frame(main_container, bg='#f2f6fc')
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 5))
        right_panel = tk.Frame(main_container, bg='#f2f6fc', width=400)
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 0))

        self._create_system_info_section(left_panel)
        self._create_control_panel(left_panel)
        self._create_stats_display(left_panel)
        self._create_graph_buttons(left_panel)

        self._create_search_bar(right_panel)
        self._create_process_list(right_panel)

    def _create_system_info_section(self, parent):
        info = self.monitor.system_info
        info_frame = ttk.LabelFrame(parent, text=" System Information", padding=8)
        info_frame.pack(fill='x', pady=(0, 10))

        mem_info = self.monitor.get_memory_usage()
        disk_info = self.monitor.get_disk_usage('/' if info.get('os_name') != 'Windows' else 'C:\\')

        items = [
            ("OS:", f"{info.get('os_name', 'N/A')} {info.get('os_release', '')}"),
            ("Version:", (info.get('os_version', 'N/A')[:50] + '...') if len(info.get('os_version', '')) > 50 else info.get('os_version', 'N/A')),
            ("Hostname:", info.get('hostname', 'N/A')),
            ("Architecture:", info.get('architecture', 'N/A')),
            ("CPU Cores:", f"{info.get('cpu_count_physical', 'N/A')} Physical, {info.get('cpu_count_logical', 'N/A')} Logical"),
            ("RAM Total:", f"{mem_info['total_gb']:.2f} GB"),
            ("Disk Total:", f"{disk_info.get('total_gb', 0):.2f} GB (Free: {disk_info.get('free_gb', 0):.2f} GB)"),
            ("Uptime:", f"{info.get('uptime_days', 0)}d {info.get('uptime_hours', 0)}h {info.get('uptime_minutes', 0)}m")
        ]

        for i, (key, value) in enumerate(items):
            tk.Label(info_frame, text=key, font=('Segoe UI', 9, 'bold')).grid(row=i, column=0, sticky='w', padx=5, pady=2)
            tk.Label(info_frame, text=value, font=('Segoe UI', 9)).grid(row=i, column=1, sticky='w', padx=5, pady=2)


    def _create_control_panel(self, parent):
        control_frame = ttk.LabelFrame(parent, text=" Monitoring Control", padding=8)
        control_frame.pack(fill='x', pady=(0, 10))
        self.start_stop_btn = ttk.Button(control_frame, text="▶ Start Monitoring", command=self.toggle_monitoring, width=20)
        self.start_stop_btn.pack(side='left', padx=5)
        self.status_label = tk.Label(control_frame, text="● Stopped", foreground='red', font=('Segoe UI', 10, 'bold'), bg='white')
        self.status_label.pack(side='left', padx=15)
        ttk.Button(control_frame, text="🔄 Refresh", command=self.refresh_data_async, width=12).pack(side='left', padx=5)

    def _create_stats_display(self, parent):
        stats_frame = ttk.LabelFrame(parent, text=" System Resources", padding=8)
        stats_frame.pack(fill='x', pady=(0, 10))
        stats_frame.grid_columnconfigure(2, weight=1)

        tk.Label(stats_frame, text="CPU Usage", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.cpu_label = tk.Label(stats_frame, text="0.0%", font=('Segoe UI', 10), foreground='#3498db')
        self.cpu_label.grid(row=0, column=1, sticky='w', pady=5)
        self.cpu_progress = ttk.Progressbar(stats_frame, mode='determinate', length=250)
        self.cpu_progress.grid(row=0, column=2, sticky='ew', padx=5, pady=5)

        tk.Label(stats_frame, text="Memory Usage", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5, padx=5)
        self.mem_label = tk.Label(stats_frame, text="0.0%", font=('Segoe UI', 10), foreground='#27ae60')
        self.mem_label.grid(row=1, column=1, sticky='w', pady=5)
        self.mem_progress = ttk.Progressbar(stats_frame, mode='determinate', length=250)
        self.mem_progress.grid(row=1, column=2, sticky='ew', padx=5, pady=5)

        self.mem_details = tk.Label(stats_frame, text="Used: 0.00 GB / Total: 0.00 GB", font=('Segoe UI', 8))
        self.mem_details.grid(row=2, column=0, columnspan=3, sticky='w', pady=3, padx=5)

    def _create_graph_buttons(self, parent):
        graph_frame = ttk.LabelFrame(parent, text=" Performance Graphs", padding=8)
        graph_frame.pack(fill='x', pady=(0, 10))
        
        cpu_btn = ttk.Button(
            graph_frame,
            text="Show CPU Usage Graph",
            command=self.show_cpu_graph
        )
        cpu_btn.pack(side='top', fill='x', pady=4, ipady=8)
        
        mem_btn = ttk.Button(
            graph_frame,
            text="Show Memory Usage Graph",
            command=self.show_memory_graph
        )
        mem_btn.pack(side='top', fill='x', pady=4, ipady=8)

    def _create_search_bar(self, parent):
        search_frame = ttk.LabelFrame(parent, text=" Search Processes", padding=6)
        search_frame.pack(fill='x', pady=(0, 8))
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var, width=25).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_processes, width=8).pack(side='left', padx=2)
        ttk.Button(search_frame, text="Clear", command=self.clear_search, width=8).pack(side='left', padx=2)

    def _create_process_list(self, parent):
        list_frame = ttk.LabelFrame(parent, text=" Running Processes", padding=5)
        list_frame.pack(fill='both', expand=True, pady=(0, 0))
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.loading_overlay = tk.Frame(list_frame, bg='#ecf0f1', relief='flat')
        
        loading_content = tk.Frame(self.loading_overlay, bg='#ecf0f1')
        loading_content.place(relx=0.5, rely=0.5, anchor='center')
        
        self.loading_label = tk.Label(
            loading_content,
            text="Refreshing...",
            font=('Segoe UI', 13, 'bold'),
            fg='gray',
            bg='#ecf0f1'
        )
        self.loading_label.pack(pady=10)
        
        self.loading_dots_label = tk.Label(
            loading_content,
            text="",
            font=('Segoe UI', 11),
            fg='#7f8c8d',
            bg='#ecf0f1'
        )
        self.loading_dots_label.pack()

        columns = ('PID', 'Name', 'CPU %', 'Memory %')
        self.process_tree = ttk.Treeview(list_frame, columns=columns, show='headings', selectmode='browse', height=15)
        self.process_tree.heading('PID', text='PID')
        self.process_tree.column('PID', width=60, stretch=False)
        self.process_tree.heading('Name', text='Process')
        self.process_tree.column('Name', width=180, stretch=True)
        self.process_tree.heading('CPU %', text='CPU %')
        self.process_tree.column('CPU %', width=70, stretch=False)
        self.process_tree.heading('Memory %', text='Mem %')
        self.process_tree.column('Memory %', width=70, stretch=False)

        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=v_scrollbar.set)
        self.process_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        
        button_frame = tk.Frame(list_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(5, 0))
        ttk.Button(button_frame, text="❌ Terminate Process", command=self.kill_process, width=25).pack(pady=5)

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
            
            self.monitor_thread = threading.Thread(target=self._continuous_monitor, daemon=True)
            self.monitor_thread.start()

    def stop_monitoring(self):
        if self.monitoring:
            self.monitoring = False
            self.start_stop_btn.config(text="▶ Start Monitoring")
            self.status_label.config(text="● Stopped", foreground='red')

    def _continuous_monitor(self):
        while self.monitoring:
            try:
                self._update_system_stats()
                if not self.loading_overlay.winfo_ismapped():
                    self._update_process_list()
                time.sleep(1)
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(1)

    def show_loading_overlay(self):
        self.loading_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.loading_overlay.lift()
        self.animate_loading_dots()

    def hide_loading_overlay(self):
        self.loading_overlay.place_forget()

    def animate_loading_dots(self, dots=0):
        if self.loading_overlay.winfo_ismapped():
            dot_patterns = ["", ".", "..", "..."]
            self.loading_dots_label.config(text=dot_patterns[dots % 4])
            self.parent.after(200, lambda: self.animate_loading_dots(dots + 1))

    def refresh_data_async(self):
        if self.refreshing:
            return
        
        self.refreshing = True
        self.loading_label.config(text="Refreshing...")
        self.show_loading_overlay()
        
        def refresh_thread():
            try:
                def clear_tree():
                    for item in self.process_tree.get_children():
                        self.process_tree.delete(item)
                self.parent.after(0, clear_tree)
                
                time.sleep(0.3)
                
                self._update_system_stats()
                self._update_process_list()
                
                time.sleep(0.2)
                
            finally:
                self.refreshing = False
                self.parent.after(0, self.hide_loading_overlay)
        
        threading.Thread(target=refresh_thread, daemon=True).start()

    def _update_system_stats(self):
        try:
            cpu_percent = self.monitor.get_cpu_usage(interval=0.1)
            self.cpu_data.append(cpu_percent)
            
            def update_ui():
                self.cpu_label.config(text=f"{cpu_percent:.1f}%")
                self.cpu_progress['value'] = cpu_percent
                if cpu_percent > 80:
                    self.cpu_label.config(foreground='#e74c3c')
                elif cpu_percent > 50:
                    self.cpu_label.config(foreground='#f39c12')
                else:
                    self.cpu_label.config(foreground='#27ae60')
            
            self.parent.after(0, update_ui)
            
            mem_info = self.monitor.get_memory_usage()
            self.mem_data.append(mem_info['percent'])
            
            def update_mem_ui():
                self.mem_label.config(text=f"{mem_info['percent']:.1f}%")
                self.mem_progress['value'] = mem_info['percent']
                self.mem_details.config(text=f"Used: {mem_info['used_gb']:.2f} GB / Total: {mem_info['total_gb']:.2f} GB")
                if mem_info['percent'] > 80:
                    self.mem_label.config(foreground='#e74c3c')
                elif mem_info['percent'] > 50:
                    self.mem_label.config(foreground='#f39c12')
                else:
                    self.mem_label.config(foreground='#27ae60')
            
            self.parent.after(0, update_mem_ui)
            
        except Exception as e:
            print(f"Stats update error: {e}")

    def _update_process_list(self):
        try:
            processes = self.monitor.get_top_processes(limit=50)
            
            def update_tree():
                for item in self.process_tree.get_children():
                    self.process_tree.delete(item)
                for proc in processes:
                    self.process_tree.insert('', 'end', values=(
                        proc['pid'],
                        proc['name'][:30],
                        f"{proc['cpu_percent']:.1f}",
                        f"{proc['memory_percent']:.1f}"
                    ))
            
            self.parent.after(0, update_tree)
            
        except Exception as e:
            print(f"Process list update error: {e}")

    def search_processes(self):
        search_term = self.search_var.get().strip()
        if not search_term:
            messagebox.showwarning("Search", "Please enter a process name")
            return
        
        was_monitoring = self.monitoring
        if was_monitoring:
            self.monitoring = False
        
        self.loading_label.config(text="Searching...")
        self.show_loading_overlay()
        
        def search_thread():
            try:
                time.sleep(0.1)
                
                def clear_tree():
                    for item in self.process_tree.get_children():
                        self.process_tree.delete(item)
                self.parent.after(0, clear_tree)
                
                processes = self.monitor.search_processes(search_term)
                
                def update_results():
                    self.loading_label.config(text="Refreshing...")
                    
                    if not processes:
                        self.hide_loading_overlay()
                        messagebox.showinfo("Search", f"No processes found matching '{search_term}'")
                        if was_monitoring:
                            self.monitoring = True
                        return
                    
                    for proc in processes:
                        self.process_tree.insert('', 'end', values=(
                            proc['pid'],
                            proc['name'][:30],
                            f"{proc['cpu_percent']:.1f}",
                            f"{proc['memory_percent']:.1f}"
                        ))
                    
                    self.hide_loading_overlay()
                    
                time.sleep(0.3)
                self.parent.after(0, update_results)
                
            except Exception as e:
                self.parent.after(0, lambda: self.loading_label.config(text="Refreshing..."))
                self.parent.after(0, self.hide_loading_overlay)
                self.parent.after(0, lambda: messagebox.showerror("Error", f"Search failed: {e}"))
                if was_monitoring:
                    self.parent.after(0, lambda: setattr(self, 'monitoring', True))
        
        threading.Thread(target=search_thread, daemon=True).start()

    def clear_search(self):
        self.search_var.set('')
        self.loading_label.config(text="Refreshing...")
        self.show_loading_overlay()
        
        def restore_thread():
            try:
                self._update_process_list()
                time.sleep(0.2)
            finally:
                self.parent.after(0, self.hide_loading_overlay)
                if self.start_stop_btn.cget('text') == "⏸ Stop Monitoring":
                    self.parent.after(0, lambda: setattr(self, 'monitoring', True))
        
        threading.Thread(target=restore_thread, daemon=True).start()

    def show_cpu_graph(self):
        self._show_graph("CPU Usage", self.cpu_data, "CPU %", "#BAD7F6", "#3498db")

    def show_memory_graph(self):
        self._show_graph("Memory Usage", self.mem_data, "Memory %", "#b8f2df", "#27ae60")

    def _show_graph(self, title, data_deque, ylabel, gradient_color, line_color):
        graph_window = tk.Toplevel(self.parent)
        graph_window.title(title)
        graph_window.geometry("600x400")
        graph_window.configure(bg='#f8f9fa')
        graph_window.resizable(False, False)

        fig = Figure(figsize=(6, 3), facecolor='#f8f9fa', dpi=100)
        ax = fig.add_subplot(111)

        ax.set_title(title, fontsize=12, fontweight='bold', pad=10, color='#222222')
        ax.set_xlabel("Time (seconds)", fontsize=10, color='#626973')
        ax.set_ylabel(ylabel, fontsize=10, color='#626973')
        ax.set_ylim(0, 100)
        ax.set_xlim(-59, 0)
        ax.grid(True, alpha=0.15, linestyle='-', linewidth=1)
        ax.set_facecolor('#fcfcfc')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#dedede')
        ax.spines['bottom'].set_color('#dedede')

        x_data = np.arange(-59, 1, 1)
        y_data = list(data_deque)
        line, = ax.plot(x_data, y_data, color=line_color, linewidth=2.5, antialiased=True)
        ax.fill_between(x_data, y_data, color=gradient_color, alpha=0.22)

        value_annot = ax.annotate(
            f"{y_data[-1]:.1f}%",
            xy=(0, y_data[-1]),
            xytext=(-10, 10),
            textcoords='offset points',
            fontsize=10,
            color='#444',
            bbox=dict(boxstyle='round,pad=0.22', fc='#eeeeee', ec='#bbbbbb', alpha=0.95)
        )

        fig.tight_layout(pad=2.0)

        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.get_tk_widget().pack(pady=20, padx=20)
        canvas.draw()

        def animate(frame):
            y_data = list(data_deque)
            x_data = np.arange(-len(y_data) + 1, 1, 1)
            
            line.set_data(x_data, y_data)
            
            for coll in ax.collections[:]:
                coll.remove()
            ax.fill_between(x_data, y_data, color=gradient_color, alpha=0.22)
            
            val = y_data[-1] if y_data else 0
            value_annot.set_text(f"{val:.1f}%")
            value_annot.xy = (0, val)
            
            ax.set_xlim(x_data[0] if len(x_data) > 0 else -59, 0)
            
            return line, value_annot

        ani = animation.FuncAnimation(fig, animate, interval=1000, blit=False, cache_frame_data=False)
        
        graph_window.ani = ani
        
        graph_window.protocol("WM_DELETE_WINDOW", graph_window.destroy)

    def kill_process(self):
        selected = self.process_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a process")
            return
        values = self.process_tree.item(selected[0])['values']
        pid = int(values[0])
        name = values[1]
        if messagebox.askyesno("Confirm", f"⚠️ Terminate process '{name}' (PID: {pid})?"):
            success, message = self.monitor.kill_process(pid)
            if success:
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)
