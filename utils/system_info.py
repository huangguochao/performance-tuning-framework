import subprocess
import platform
import psutil
import json

class SystemInfo:
    def __init__(self):
        pass

    def collect_all(self):
        """收集所有系统信息"""
        return {
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disk": self.get_disk_info(),
            "os": self.get_os_info(),
            "kernel": self.get_kernel_info(),
            "processes": self.get_process_info()
        }

    def get_cpu_info(self):
        """获取 CPU 信息"""
        return {
            "model": platform.processor(),
            "cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None,
            "usage": psutil.cpu_percent(interval=1)
        }

    def get_memory_info(self):
        """获取内存信息"""
        mem = psutil.virtual_memory()
        return {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent
        }

    def get_disk_info(self):
        """获取磁盘信息"""
        disk = psutil.disk_usage('/')
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }

    def get_os_info(self):
        """获取操作系统信息"""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine()
        }

    def get_kernel_info(self):
        """获取内核信息"""
        try:
            result = subprocess.check_output(["uname", "-r"], text=True).strip()
            return result
        except:
            return "unknown"

    def get_process_info(self):
        """获取进程信息"""
        return {
            "total": len(psutil.pids()),
            "running": len([p for p in psutil.process_iter(['status']) if p.info['status'] == 'running'])
        }
