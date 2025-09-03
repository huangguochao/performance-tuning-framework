import subprocess
import os

class SysctlTuner:
    def __init__(self, config):
        self.name = "sysctl_tuner"
        self.config = config
        self.original_values = {}
        self.tunable_params = config.get("sysctl_tuning", {})

    def _parameter_exists(self, param):
        """检查sysctl参数是否存在"""
        try:
            subprocess.run(
                ["sysctl", "-n", param],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5
            )
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def apply(self):
        """应用 sysctl 调优设置"""
        for param, value in self.tunable_params.items():
            # 检查参数是否存在
            if not self._parameter_exists(param):
                print(f"参数 {param} 不存在，跳过设置")
                continue

            # 保存原始值
            try:
                current_value = subprocess.check_output(
                    ["sysctl", "-n", param],
                    text=True,
                    timeout=5
                ).strip()
                self.original_values[param] = current_value
            except Exception as e:
                self.original_values[param] = "unknown"
                print(f"无法获取参数 {param} 的当前值: {e}")
                continue

            # 设置新值
            try:
                result = subprocess.run(
                    ["sysctl", "-w", f"{param}={value}"],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                print(f"已设置 {param} = {value}")
            except subprocess.CalledProcessError as e:
                print(f"设置 {param} 失败: {e.stderr}")

    def reset(self):
        """恢复原始 sysctl 设置"""
        for param, original_value in self.original_values.items():
            if original_value != "unknown":
                try:
                    # 检查参数是否仍然存在
                    if not self._parameter_exists(param):
                        print(f"参数 {param} 不存在，跳过恢复")
                        continue

                    subprocess.run(
                        ["sysctl", "-w", f"{param}={original_value}"],
                        check=True,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    print(f"已恢复 {param} = {original_value}")
                except subprocess.CalledProcessError as e:
                    print(f"恢复 {param} 失败: {e.stderr}")
