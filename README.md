# performance-tuning-framework
--------------------------------------------------------------------
# 使用方法

安装依赖：
sudo dnf install -y python3-psutil gcc make wget
pip install -r requirements.txt

运行框架：
#基本运行
python main.py

#指定配置和输出文件
python main.py --config config/my_config.conf --output results/my_tuning_results.json

#只运行特定测试和调优模块
python main.py --benchmark himeno --tuner sysctl_tuner cpu_governor

--------------------------------------------------------------------
# 扩展框架

要添加新的基准测试工具：
1) 在 modules/ 目录下创建新的 Python 文件
2) 实现一个类，包含 run() 方法返回测试结果
3) 在配置文件中添加相应的配置选项

要添加新的调优模块：
1) 在 modules/ 目录下创建新的 Python 文件
2) 实现一个类，包含 apply() 和 reset() 方法
3) 在配置文件中添加相应的配置选项

--------------------------------------------------------------------

# 注意事项
1) 需要 root 权限来修改系统参数
2) 在生产环境使用前，请在测试环境中充分验证
3) 某些调优可能不适用于所有硬件配置
4) 框架会尝试恢复原始设置，但建议在调优前备份重要系统配置

这个框架提供了良好的扩展性，可以轻松添加新的基准测试和调优模块，同时保持了代码的清晰结构和可维护性。
