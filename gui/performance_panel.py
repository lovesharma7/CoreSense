import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import psutil
import json
import os
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")     
import matplotlib.pyplot as plt

HISTORY_PATH = os.path.join(os.path.dirname(__file__), '..', 'boost_history.json')


class PerformanceBoosterPanel:
    def __init__(self, master):
        self.master = master
        self.master.configure(bg='#f9fbfe')
        self.master.pack(fill="both", expand=True)

        container = tk.Frame(self.master, bg='#f9fbfe')
        container.pack(fill='both', expand=True, padx=20, pady=10)

        mode_frame = ttk.LabelFrame(container, text=" Booster Modes ", padding=8)
        mode_frame.pack(fill="x")

        self.boost_mode = tk.StringVar(value="fast")

        ttk.Radiobutton(mode_frame, text="Fast Boost (CPU only)", variable=self.boost_mode,
                        value="fast").pack(side='left', padx=10)

        ttk.Radiobutton(mode_frame, text="Deep Boost (CPU + RAM + Temp)", variable=self.boost_mode,
                        value="deep").pack(side='left', padx=10)

        ttk.Radiobutton(mode_frame, text="Extreme Boost (Aggressive)", variable=self.boost_mode,
                        value="extreme").pack(side='left', padx=10)

        ctrl = ttk.LabelFrame(container, text=" Controls ", padding=8)
        ctrl.pack(fill="x", pady=(15, 5))

        ttk.Button(ctrl, text="⚡ Run Booster", width=18, command=self.start_boost).pack(side='left', padx=5)
        ttk.Button(ctrl, text="Scan Only", width=12, command=self.scan_only).pack(side='left', padx=5)
        ttk.Button(ctrl, text="Show Graphs (Last Boost)", width=25,
                   command=self.show_last_graphs).pack(side='left', padx=5)
        ttk.Button(ctrl, text="Show History", width=12, command=self.show_history).pack(side='left', padx=5)

        self.status = tk.Label(ctrl, text="Idle", bg='white')
        self.status.pack(side='left', padx=15)
        self.progress = ttk.Progressbar(ctrl, mode="indeterminate", length=200)
        self.progress.pack(side='right')

        out_frame = ttk.LabelFrame(container, text=" Booster Output ", padding=8)
        out_frame.pack(fill='both', expand=True, pady=10)

        self.output = tk.Text(out_frame, height=18, bg='white')
        self.output.pack(fill='both', expand=True)

        try:
            os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
        except:
            pass

    def set_status(self, text):
        self.status.config(text=text)
        self.master.update_idletasks()

    def start_boost(self):
        t = threading.Thread(target=self.safe_run, daemon=True)
        t.start()
        self.progress.start(10)
        self.set_status("Running...")

    def safe_run(self):
        try:
            self.run_booster()
        except Exception as e:
            messagebox.showerror("Booster Error", str(e))
        finally:
            self.progress.stop()
            self.set_status("Idle")

    def scan_only(self):
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, "Scanning for heavy processes...\n")

        try:
            from core.system_monitor import SystemMonitor
            sm = SystemMonitor()
            heavy = sm.get_heavy_processes()

            if not heavy:
                self.output.insert(tk.END, "No heavy processes found.\n")
                return

            for p in heavy:
                self.output.insert(tk.END,
                    f"PID {p['pid']} {p['name']}  CPU:{p['cpu']}%  RAM:{p['ram_mb']}MB\n"
                )
        except Exception as e:
            self.output.insert(tk.END, f"Scan failed: {e}\n")

    def run_booster(self):
        from core.system_monitor import SystemMonitor
        sm = SystemMonitor()

        mode = self.boost_mode.get()
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, f"Starting {mode.upper()} boost...\n\n")

        cpu_before = sm.get_cpu_usage(interval=0.1)
        mem_before = sm.get_memory_usage().get('used_gb', 0.0)

        heavy = sm.get_heavy_processes(cpu_limit=35, ram_limit=200)

        if not heavy:
            self.output.insert(tk.END, "No heavy processes found.\n")
        else:
            for p in heavy:
                pid = p['pid']
                name = (p['name'] or "").lower()
                cpu = p['cpu'] or 0.0

                if pid in (0, 4) or name in ("system", "system idle process"):
                    self.output.insert(tk.END, f"Skipped protected: {name} (PID {pid})\n")
                    continue

                if pid == os.getpid():
                    self.output.insert(tk.END, f"Skipped self: {name} (PID {pid})\n")
                    continue

                safe_names = ["coresense", "python", "pythonw", "py", "main"]
                if any(s in name for s in safe_names):
                    self.output.insert(tk.END, f"Skipped (CoreSense Safe): {name}\n")
                    continue

                ok, msg = sm.kill_process(pid)
                self.output.insert(tk.END, msg + "\n")

        if mode == "deep":
            self.output.insert(tk.END, "\nCleaning temp files...\n")
            threading.Thread(target=sm.clear_temp_files, daemon=True).start()

        time.sleep(1)

        cpu_after = psutil.cpu_percent(interval=0.5)
        mem_after = sm.get_memory_usage().get('used_gb', 0.0)

        self.output.insert(tk.END,
            f"\n--- PERFORMANCE REPORT ---\n"
            f"CPU: {cpu_before:.1f}% → {cpu_after:.1f}%\n"
            f"RAM: {mem_before:.2f}GB → {mem_after:.2f}GB\n"
            f"--------------------------\n"
            f"\n✔ Booster Completed!\n"
        )

        self._last_boost = {
            'timestamp': datetime.now().isoformat(),
            'mode': mode,
            'cpu_before': cpu_before,
            'cpu_after': cpu_after,
            'mem_before': mem_before,
            'mem_after': mem_after
        }

        self._save_history_entry(mode, cpu_before, cpu_after, mem_before, mem_after)


    def handle_processes(self, heavy, sm, mode):
        for p in heavy:
            pid = p["pid"]
            name = p["name"] or ""
            cpu = p["cpu"] or 0.0

            if pid in (0, 4) or name.lower() in ("system", "system idle process"):
                self.output.insert(tk.END, f"Skipped protected: {name} (PID {pid})\n")
                continue

            if mode == "fast":
                sm.lower_priority(pid)
                if cpu > 85:
                    ok, msg = sm.kill_process(pid)
                    self.output.insert(tk.END, msg + "\n")
                else:
                    self.output.insert(tk.END, f"Lowered priority: {name}\n")

            elif mode == "deep":
                sm.lower_priority(pid)
                time.sleep(0.02)
                if cpu > 70:
                    ok, msg = sm.kill_process(pid)
                    self.output.insert(tk.END, msg + "\n")

            elif mode == "extreme":
                current_pid = os.getpid()
                if pid == current_pid:
                    self.output.insert(tk.END, f"Skipped self: {name}\n")
                    continue

                if any(x in name.lower() for x in ["chrome", "firefox", "edge", "code"]):
                    ok, msg = sm.kill_process(pid)
                    self.output.insert(tk.END, msg + "\n")
                else:
                    sm.lower_priority(pid)
                    self.output.insert(tk.END, f"Lowered priority: {name}\n")

    def _save_history_entry(self, mode, cpu_b, cpu_a, mem_b, mem_a):
        entry = {
            "time": datetime.now().isoformat(),
            "mode": mode,
            "cpu_before": cpu_b,
            "cpu_after": cpu_a,
            "mem_before": mem_b,
            "mem_after": mem_a
        }

        try:
            hist = []
            if os.path.exists(HISTORY_PATH):
                with open(HISTORY_PATH, "r") as f:
                    hist = json.load(f)

            hist.insert(0, entry)
            hist = hist[:30]

            with open(HISTORY_PATH, "w") as f:
                json.dump(hist, f, indent=2)
        except:
            pass

    def show_history(self):
        try:
            with open(HISTORY_PATH, "r") as f:
                hist = json.load(f)
        except:
            messagebox.showinfo("History", "No history available.")
            return

        win = tk.Toplevel(self.master)
        win.title("Boost History")
        win.geometry("600x400")

        txt = tk.Text(win)
        txt.pack(fill='both', expand=True)

        for e in hist:
            txt.insert(tk.END,
                f"{e['time']} | {e['mode'].upper()} | "
                f"CPU {e['cpu_before']:.1f}% → {e['cpu_after']:.1f}% | "
                f"RAM {e['mem_before']:.2f} → {e['mem_after']:.2f} GB\n"
            )

    def show_last_graphs(self):
        self.master.after(10, self._open_graph_window)

    def _open_graph_window(self):
        if not hasattr(self, "_last_boost"):
            messagebox.showinfo("Graphs", "No boost performed yet.")
            return

        lb = self._last_boost

        fig, axs = plt.subplots(1, 2, figsize=(10, 4))

        axs[0].bar(["Before", "After"], [lb["cpu_before"], lb["cpu_after"]], color="skyblue")
        axs[0].set_title("CPU Before vs After")
        axs[0].set_ylabel("CPU %")

        axs[1].bar(["Before", "After"], [lb["mem_before"], lb["mem_after"]], color="lightgreen")
        axs[1].set_title("RAM Before vs After")
        axs[1].set_ylabel("Used RAM (GB)")

        fig.suptitle("Boost Performance Summary", fontsize=14)
        plt.tight_layout()
        plt.show()
