import subprocess
import os
import re
import urllib.request
import tarfile
from datetime import datetime

class Himeno:
    def __init__(self, config):
        self.name = "himeno"
        self.config = config
        self.binary_path = config.get("himeno", {}).get("binary_path", "/usr/local/bin/himeno")
        self.compile_source = config.get("himeno", {}).get("compile_source", True)
        self.source_dir = config.get("himeno", {}).get("source_dir", "/tmp/himeno")

        if not os.path.exists(self.binary_path) and self.compile_source:
            self._download_and_compile_himeno()

    def _download_and_compile_himeno(self):
        """下载并编译 Himeno 基准测试程序"""
        os.makedirs(self.source_dir, exist_ok=True)

        # 下载 Himeno 基准测试源代码
        himeno_url = "http://accc.riken.jp/wp-content/uploads/2016/06/himenobmtxp_20160606.tar.gz"
        himeno_tar_path = os.path.join(self.source_dir, "himeno.tar.gz")

        try:
            print("正在下载 Himeno 基准测试源代码...")
            urllib.request.urlretrieve(himeno_url, himeno_tar_path)

            # 解压源代码
            print("正在解压源代码...")
            with tarfile.open(himeno_tar_path, "r:gz") as tar:
                tar.extractall(self.source_dir)

            # 查找 himeno.c 文件
            himeno_c_path = None
            for root, dirs, files in os.walk(self.source_dir):
                if "himeno.c" in files:
                    himeno_c_path = os.path.join(root, "himeno.c")
                    break

            if not himeno_c_path:
                raise FileNotFoundError("在下载的源代码中找不到 himeno.c 文件")

            # 编译 Himeno
            print("正在编译 Himeno...")
            compile_cmd = [
                "gcc", "-O3", "-march=native", "-mtune=native",
                "-o", self.binary_path,
                himeno_c_path,
                "-lm"
            ]

            result = subprocess.run(compile_cmd, check=True, capture_output=True, text=True)
            print("Himeno 编译成功")

            # 清理临时文件
            os.remove(himeno_tar_path)

        except Exception as e:
            print(f"Himeno 编译失败: {e}")
            # 尝试使用系统包管理器安装
            self._install_himeno_from_package()

    def _install_himeno_from_package(self):
        """尝试从系统包管理器安装 Himeno"""
        try:
            print("尝试通过包管理器安装 Himeno...")
            # 对于 CentOS/RHEL 系统
            result = subprocess.run(["sudo", "dnf", "install", "-y", "himeno-benchmark"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("Himeno 通过包管理器安装成功")
                # 更新二进制路径
                self.binary_path = "/usr/bin/himeno"
            else:
                print("无法通过包管理器安装 Himeno")
                raise Exception("Himeno 安装失败")
        except Exception as e:
            print(f"Himeno 安装失败: {e}")
            raise

    def run(self):
        """运行 Himeno 基准测试"""
        try:
            # 检查二进制文件是否存在
            if not os.path.exists(self.binary_path):
                raise FileNotFoundError(f"Himeno 二进制文件不存在: {self.binary_path}")

            # 设置运行参数
            run_cmd = [self.binary_path]
            if self.config.get("himeno", {}).get("problem_size"):
                run_cmd.extend(["-s", str(self.config["himeno"]["problem_size"])])

            # 执行测试
            start_time = datetime.now()
            result = subprocess.run(
                run_cmd,
                capture_output=True,
                text=True,
                timeout=self.config.get("himeno", {}).get("timeout", 300)
            )
            end_time = datetime.now()

            # 解析结果
            output = result.stdout
            error = result.stderr

            # 提取 MFLOPS 值
            mflops_match = re.search(r"MFLOPS\s*:\s*([\d.]+)", output)
            mflops = float(mflops_match.group(1)) if mflops_match else 0

            # 提取时间信息
            time_match = re.search(r"Time\s*:\s*([\d.]+)", output)
            time_taken = float(time_match.group(1)) if time_match else 0

            return {
                "score": mflops,
                "time_seconds": time_taken,
                "run_time": (end_time - start_time).total_seconds(),
                "output": output,
                "error": error,
                "success": result.returncode == 0
            }

        except subprocess.TimeoutExpired:
            return {
                "score": 0,
                "time_seconds": 0,
                "output": "",
                "error": "测试超时",
                "success": False
            }
        except Exception as e:
            return {
                "score": 0,
                "time_seconds": 0,
                "output": "",
                "error": str(e),
                "success": False
            }
