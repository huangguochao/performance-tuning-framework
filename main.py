#!/usr/bin/env python3

import argparse
import importlib
import json
import os
import sys
from datetime import datetime
from utils.logger import setup_logger
from utils.system_info import SystemInfo

class PerformanceTuningFramework:
    def __init__(self, config_path="config/default.conf"):
        self.logger = setup_logger()
        self.system_info = SystemInfo()
        self.config = self._load_config(config_path)
        self.tuners = []
        self.benchmarks = []

    def _load_config(self, config_path):
        """加载配置文件"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"配置文件 {config_path} 不存在")
            sys.exit(1)

    def register_tuner(self, tuner_module):
        """注册调优模块"""
        try:
            module = importlib.import_module(f"modules.{tuner_module}")
            tuner_class = getattr(module, tuner_module.title().replace("_", ""))
            self.tuners.append(tuner_class(self.config))
            self.logger.info(f"已注册调优模块: {tuner_module}")
        except Exception as e:
            self.logger.error(f"注册调优模块失败 {tuner_module}: {e}")

    def register_benchmark(self, benchmark_module):
        """注册基准测试模块"""
        try:
            module = importlib.import_module(f"modules.{benchmark_module}")
            benchmark_class = getattr(module, benchmark_module.title().replace("_", ""))
            self.benchmarks.append(benchmark_class(self.config))
            self.logger.info(f"已注册基准测试模块: {benchmark_module}")
        except Exception as e:
            self.logger.error(f"注册基准测试模块失败 {benchmark_module}: {e}")

    def run_benchmarks(self):
        """运行所有基准测试"""
        results = {}
        for benchmark in self.benchmarks:
            self.logger.info(f"开始运行基准测试: {benchmark.name}")
            result = benchmark.run()
            results[benchmark.name] = result
            self.logger.info(f"{benchmark.name} 测试完成: {result}")
        return results

    def apply_tunings(self):
        """应用所有调优设置"""
        for tuner in self.tuners:
            self.logger.info(f"开始应用调优: {tuner.name}")
            try:
                tuner.apply()
                self.logger.info(f"{tuner.name} 调优应用成功")
            except Exception as e:
                self.logger.error(f"{tuner.name} 调优应用失败: {e}")

    def reset_tunings(self):
        """重置所有调优设置"""
        for tuner in self.tuners:
            self.logger.info(f"开始重置调优: {tuner.name}")
            try:
                tuner.reset()
                self.logger.info(f"{tuner.name} 调优重置成功")
            except Exception as e:
                self.logger.error(f"{tuner.name} 调优重置失败: {e}")

    def save_results(self, results, filename=None):
        """保存测试结果"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results/{timestamp}_results.json"

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(results, f, indent=4)
        self.logger.info(f"结果已保存至: {filename}")

def main():
    parser = argparse.ArgumentParser(description="CentOS 9 自动化性能调优框架")
    parser.add_argument("--config", default="config/default.conf", help="配置文件路径")
    parser.add_argument("--benchmark", nargs="+", default=["himeno"], help="要运行的基准测试")
    parser.add_argument("--tuner", nargs="+", default=["sysctl_tuner", "cpu_governor"], help="要使用的调优模块")
    parser.add_argument("--output", help="结果输出文件")
    args = parser.parse_args()

    # 初始化框架
    framework = PerformanceTuningFramework(args.config)

    # 注册模块
    for tuner in args.tuner:
        framework.register_tuner(tuner)

    for benchmark in args.benchmark:
        framework.register_benchmark(benchmark)

    # 记录初始系统状态
    initial_system_info = framework.system_info.collect_all()

    # 运行初始基准测试
    initial_results = framework.run_benchmarks()
    framework.save_results({
        "initial_system_info": initial_system_info,
        "initial_results": initial_results
    }, "results/initial_results.json")

    # 应用调优设置
    framework.apply_tunings()

    # 运行调优后的基准测试
    tuned_results = framework.run_benchmarks()

    # 保存最终结果
    final_system_info = framework.system_info.collect_all()
    framework.save_results({
        "initial_system_info": initial_system_info,
        "initial_results": initial_results,
        "tuned_results": tuned_results,
        "final_system_info": final_system_info,
        "improvement": calculate_improvement(initial_results, tuned_results)
    }, args.output)

    # 重置调优设置（可选）
    framework.reset_tunings()

    # 打印改进情况
    print_improvement(initial_results, tuned_results)

def calculate_improvement(initial, tuned):
    """计算性能改进百分比"""
    improvement = {}
    for benchmark in initial:
        if benchmark in tuned:
            initial_score = initial[benchmark].get("score", 0)
            tuned_score = tuned[benchmark].get("score", 0)
            if initial_score > 0:
                improvement[benchmark] = (tuned_score - initial_score) / initial_score * 100
    return improvement

def print_improvement(initial, tuned):
    """打印性能改进情况"""
    print("\n性能改进报告:")
    print("=" * 50)
    for benchmark in initial:
        if benchmark in tuned:
            initial_score = initial[benchmark].get("score", 0)
            tuned_score = tuned[benchmark].get("score", 0)
            improvement = calculate_improvement(initial, tuned).get(benchmark, 0)
            print(f"{benchmark}:")
            print(f"  初始成绩: {initial_score}")
            print(f"  调优后成绩: {tuned_score}")
            print(f"  改进: {improvement:.2f}%")
    print("=" * 50)

if __name__ == "__main__":
    main()
