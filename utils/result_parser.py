import json
import csv

def parse_json_results(file_path):
    """解析JSON格式的结果文件"""
    with open(file_path, 'r') as f:
        return json.load(f)

def save_results_to_csv(results, csv_path):
    """将结果保存为CSV格式"""
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['benchmark', 'score', 'time_seconds', 'success']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for benchmark, result in results.items():
            writer.writerow({
                'benchmark': benchmark,
                'score': result.get('score', 0),
                'time_seconds': result.get('time_seconds', 0),
                'success': result.get('success', False)
            })
