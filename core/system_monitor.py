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

            processor = platform.processor() or ""
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
        except Exception:
            return {}

    def get_cpu_usage(self, interval=0.1):
        try:
            return psutil.cpu_percent(interval=interval)
        except Exception:
            return 0.0

    def get_cpu_per_core(self):
        try:
            return psutil.cpu_percent(interval=0.1, percpu=True)
        except Exception:
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
        except Exception:
            return {'total':0, 'available':0, 'used':0, 'free':0, 'percent':0.0}

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
        except Exception:
            return {}

    def get_top_processes(self, limit=50, sort_by='memory_percent'):
        try:
            procs = []
            for proc in psutil.process_iter(['pid','name','cpu_percent','memory_percent']):
                try:
                    info = proc.info
                    info['cpu_percent'] = info.get('cpu_percent') or 0.0
                    info['memory_percent'] = info.get('memory_percent') or 0.0
                    procs.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            procs.sort(key=lambda x: x.get(sort_by,0), reverse=True)
            return procs[:limit]
        except Exception:
            return []

    def search_processes(self, search_term):
        try:
            s = (search_term or "").lower()
            matches = []
            for proc in psutil.process_iter(['pid','name']):
                try:
                    name = (proc.info.get('name') or "").lower()
                    if s in name:
                        info = proc.as_dict(attrs=['pid','name','cpu_percent','memory_percent'])
                        info['cpu_percent'] = info.get('cpu_percent') or 0.0
                        info['memory_percent'] = info.get('memory_percent') or 0.0
                        matches.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return matches
        except Exception:
            return []

    def kill_process(self, pid):
        try:
            if pid in (0, 4):
                return False, 
            proc = psutil.Process(pid)
            name = proc.name()
            try:
                proc.terminate()
                return True, f"Terminated: {name} (PID {pid})"
            except psutil.AccessDenied:
                return False, "Permission denied"
            except Exception as e:
                return False, str(e)
        except psutil.NoSuchProcess:
            return False, "Process not found"
        except psutil.AccessDenied:
            return False, "Permission denied"
        except Exception as e:
            return False, str(e)

    def lower_priority(self, pid):
        try:
            if pid in (0,4):
                return False
            proc = psutil.Process(pid)
            if platform.system() == "Windows":
                try:
                    proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                except Exception:
                    proc.nice(psutil.IDLE_PRIORITY_CLASS)
            else:
                proc.nice(10)
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
        except Exception:
            return False

    def get_heavy_processes(self, cpu_limit=40, ram_limit=500):
        heavy = []
        skip_pids = {0,4}
        skip_names = {"system", "system idle process", "idle", "registry", "smss.exe"}

        for proc in psutil.process_iter(['pid','name']):
            try:
                pid = proc.pid
                name = (proc.info.get('name') or "").lower()

                if pid in skip_pids or name in skip_names:
                    continue

                cpu = proc.cpu_percent(interval=0) or 0.0
                try:
                    mem = proc.memory_info().rss / (1024 * 1024)
                except Exception:
                    mem = 0.0

                if cpu > cpu_limit or mem > ram_limit:
                    heavy.append({
                        'pid': pid,
                        'name': proc.info.get('name'),
                        'cpu': round(cpu,1),
                        'ram_mb': round(mem,1)
                    })

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            except Exception:
                continue

        heavy.sort(key=lambda x: (x['cpu'], x['ram_mb']), reverse=True)
        return heavy[:10]

    def clear_temp_files(self):
        try:
            import tempfile, os, shutil
            temp_path = tempfile.gettempdir()
            cleaned = 0
            for entry in os.listdir(temp_path):
                full = os.path.join(temp_path, entry)
                try:
                    if os.path.isfile(full) or os.path.islink(full):
                        os.remove(full)
                        cleaned += 1
                    elif os.path.isdir(full):
                        shutil.rmtree(full, ignore_errors=True)
                        cleaned += 1
                except PermissionError:
                    continue
                except Exception:
                    continue
            return True
        except Exception:
            return False
