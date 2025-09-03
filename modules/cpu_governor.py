import subprocess
import os

class CpuGovernor:
    def __init__(self, config):
        self.name = "cpu_governor"
        self.config = config
        self.original_governor = None
        self.new_governor = config.get("cpu_governor", "performance")
        self.cpu_count = os.cpu_count()
        self.governor_files = []

        # 检查每个CPU的调速器文件是否存在
        for i in range(self.cpu_count):
            governor_file = f"/sys/devices/system/cpu/cpu{i}/cpufreq/scaling_governor"
            if os.path.exists(governor_file):
                self.governor_files.append(governor_file)

    def apply(self):
        """设置 CPU 调速器为性能模式"""
        if not self.governor_files:
            print("系统不支持CPU调速器设置，跳过")
            return

        try:
            # 获取当前调速器（从第一个可用的CPU）
            with open(self.governor_files[0], "r") as f:
                self.original_governor = f.read().strip()

            # 设置所有可用的CPU调速器
            for governor_file in self.governor_files:
                with open(governor_file, "w") as f:
                    f.write(self.new_governor)

            print(f"已设置 CPU 调速器为 {self.new_governor} 模式")
        except Exception as e:
            print(f"设置 CPU 调速器失败: {e}")

    def reset(self):
        """恢复原始 CPU 调速器设置"""
        if self.original_governor and self.governor_files:
            try:
                for governor_file in self.governor_files:
                    with open(governor_file, "w") as f:
                        f.write(self.original_governor)

                print(f"已恢复 CPU 调速器为 {self.original_governor} 模式")
            except Exception as e:
                print(f"恢复 CPU 调速器失败: {e}")
