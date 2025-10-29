import psutil
import platform

class SystemMonitor:
    def __init__(self):
        self.system_info = self._get_system_info()
    
    def _get_system_info(self):
        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'cpu_count': psutil.cpu_count(logical=False),
            'cpu_count_logical': psutil.cpu_count(logical=True)
        }
    
    def get_cpu_usage(self, interval=1):
        try:
            return psutil.cpu_percent(interval=interval)
        except Exception as e:
            print(f"Error getting CPU usage: {e}")
            return 0.0
    
    def get_cpu_per_core(self):
        try:
            return psutil.cpu_percent(interval=1, percpu=True)
        except Exception as e:
            print(f"Error getting per-core CPU usage: {e}")
            return []
    
    def get_memory_usage(self):
        try:
            mem = psutil.virtual_memory()
            return {
                'total': mem.total,
                'available': mem.available,
                'used': mem.used,
                'free': mem.free,
                'percent': mem.percent,
                'total_gb': mem.total / (1024**3),
                'available_gb': mem.available / (1024**3),
                'used_gb': mem.used / (1024**3),
                'free_gb': mem.free / (1024**3)
            }
        except Exception as e:
            print(f"Error getting memory usage: {e}")
            return {
                'total': 0, 'available': 0, 'used': 0, 'free': 0,
                'percent': 0.0, 'total_gb': 0.0, 'available_gb': 0.0,
                'used_gb': 0.0, 'free_gb': 0.0
            }
    
    def get_disk_usage(self, path='/'):
        try:
            disk = psutil.disk_usage(path)
            return {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent,
                'total_gb': disk.total / (1024**3),
                'used_gb': disk.used / (1024**3),
                'free_gb': disk.free / (1024**3)
            }
        except Exception as e:
            print(f"Error getting disk usage: {e}")
            return {}
    
    def get_all_processes(self):
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            print(f"Error getting processes: {e}")
        
        return processes
    
    def get_top_processes(self, limit=10, sort_by='memory_percent'):
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info.get('cpu_percent') is None:
                        proc_info['cpu_percent'] = 0.0
                    if proc_info.get('memory_percent') is None:
                        proc_info['memory_percent'] = 0.0
                    processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            processes.sort(key=lambda x: x.get(sort_by, 0), reverse=True)
            return processes[:limit]
        except Exception as e:
            print(f"Error getting top processes: {e}")
            return []
    
    def get_process_info(self, pid):
        try:
            proc = psutil.Process(pid)
            return {
                'pid': proc.pid,
                'name': proc.name(),
                'status': proc.status(),
                'cpu_percent': proc.cpu_percent(interval=0.1),
                'memory_percent': proc.memory_percent(),
                'memory_info': proc.memory_info()._asdict(),
                'create_time': proc.create_time(),
                'num_threads': proc.num_threads()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"Error getting process info: {e}")
            return None
    
    def kill_process(self, pid):
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
            proc.terminate()
            
            proc.wait(timeout=3)
            
            return (True, f"Process '{proc_name}' (PID: {pid}) terminated successfully")
        except psutil.NoSuchProcess:
            return (False, f"Process with PID {pid} not found")
        except psutil.AccessDenied:
            return (False, f"Access denied: Cannot terminate process {pid}")
        except psutil.TimeoutExpired:
            try:
                proc.kill()
                return (True, f"Process {pid} forcefully killed")
            except Exception as e:
                return (False, f"Failed to kill process: {str(e)}")
        except Exception as e:
            return (False, f"Error terminating process: {str(e)}")
    
    def get_network_stats(self):
        try:
            net = psutil.net_io_counters()
            return {
                'bytes_sent': net.bytes_sent,
                'bytes_recv': net.bytes_recv,
                'packets_sent': net.packets_sent,
                'packets_recv': net.packets_recv,
                'mb_sent': net.bytes_sent / (1024**2),
                'mb_recv': net.bytes_recv / (1024**2)
            }
        except Exception as e:
            print(f"Error getting network stats: {e}")
            return {}
