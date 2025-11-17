import psutil
import platform
from datetime import datetime


class SystemMonitor:
    def __init__(self):
        self.system_info = self._get_system_info()

    def _get_system_info(self):
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            processor = platform.processor()
            processor = ' '.join(processor.split())
            if '@' in processor:
                processor = processor.split('@')[0].strip()
            
            return {
                'os_name': platform.system(),
                'os_version': platform.version(),
                'os_release': platform.release(),
                'architecture': platform.machine(),
                'processor': processor,
                'hostname': platform.node(),
                'cpu_count_physical': psutil.cpu_count(logical=False),
                'cpu_count_logical': psutil.cpu_count(logical=True),
                'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S'),
                'uptime_days': uptime.days,
                'uptime_hours': uptime.seconds // 3600,
                'uptime_minutes': (uptime.seconds % 3600) // 60
            }
        except Exception as e:
            print(f"Error getting system info: {e}")
            return {}

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
                'total_gb': mem.total / (1024 ** 3),
                'available_gb': mem.available / (1024 ** 3),
                'used_gb': mem.used / (1024 ** 3),
                'free_gb': mem.free / (1024 ** 3)
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
                'total_gb': disk.total / (1024 ** 3),
                'used_gb': disk.used / (1024 ** 3),
                'free_gb': disk.free / (1024 ** 3)
            }
        except Exception as e:
            print(f"Error getting disk usage: {e}")
            return {}

    def get_top_processes(self, limit=50, sort_by='memory_percent'):
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    if info.get('cpu_percent') is None:
                        info['cpu_percent'] = 0.0
                    if info.get('memory_percent') is None:
                        info['memory_percent'] = 0.0
                    processes.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            processes.sort(key=lambda x: x.get(sort_by, 0), reverse=True)
            return processes[:limit]
        except Exception as e:
            print(f"Error getting processes: {e}")
            return []

    def search_processes(self, search_term):
        try:
            search_term = search_term.lower()
            matches = []
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if search_term in proc.info['name'].lower():
                        proc_data = proc.as_dict(attrs=['pid', 'name', 'cpu_percent', 'memory_percent'])
                        if proc_data.get('cpu_percent') is None:
                            proc_data['cpu_percent'] = 0.0
                        if proc_data.get('memory_percent') is None:
                            proc_data['memory_percent'] = 0.0
                        matches.append(proc_data)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return matches
        except Exception as e:
            print(f"Error searching processes: {e}")
            return []

    def kill_process(self, pid):
        try:
            proc = psutil.Process(pid)
            name = proc.name()
            proc.terminate()
            proc.wait(timeout=3)
            return (True, f"Process '{name}' (PID: {pid}) terminated successfully")
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
