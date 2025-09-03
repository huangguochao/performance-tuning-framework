import subprocess
import os

class MemoryTuner:
    def __init__(self, config):
        self.name = "memory_tuner"
        self.config = config
        self.original_values = {}
        self.tunable_params = config.get("memory_tuning", {})

    def apply(self):
        """应用内存调优设置"""
        # 设置透明大页面
        if self.tunable_params.get("transparent_hugepages", {}).get("enable", True):
            try:
                with open("/sys/kernel/mm/transparent_hugepage/enabled", "r") as f:
                    self.original_values["thp_enabled"] = f.read().strip()

                with open("/sys/kernel/mm/transparent_hugepage/enabled", "w") as f:
                    f.write("always")
                print("已启用透明大页面")
            except Exception as e:
                print(f"设置透明大页面失败: {e}")

        # 设置大页面
        if self.tunable_params.get("hugepages", {}).get("enable", False):
            try:
                # 获取当前大页面设置
                result = subprocess.run(
                    ["sysctl", "-n", "vm.nr_hugepages"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                self.original_values["nr_hugepages"] = result.stdout.strip()

                # 设置新的大页面数量
                hugepages_count = self.tunable_params["hugepages"].get("count", 1024)
                subprocess.run(
                    ["sysctl", "-w", f"vm.nr_hugepages={hugepages_count}"],
                    check=True,
                    capture_output=True
                )
                print(f"已设置大页面数量: {hugepages_count}")
            except Exception as e:
                print(f"设置大页面失败: {e}")

    def reset(self):
        """恢复原始内存设置"""
        # 恢复透明大页面设置
        if "thp_enabled" in self.original_values:
            try:
                with open("/sys/kernel/mm/transparent_hugepage/enabled", "w") as f:
                    f.write(self.original_values["thp_enabled"])
                print("已恢复透明大页面设置")
            except Exception as e:
                print(f"恢复透明大页面设置失败: {e}")

        # 恢复大页面设置
        if "nr_hugepages" in self.original_values:
            try:
                subprocess.run(
                    ["sysctl", "-w", f"vm.nr_hugepages={self.original_values['nr_hugepages']}"],
                    check=True,
                    capture_output=True
                )
                print("已恢复大页面设置")
            except Exception as e:
                print(f"恢复大页面设置失败: {e}")
