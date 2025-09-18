#!/usr/bin/env python3
"""
测试AI大模型曝光率分析功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ai_exposure_analyzer import AIExposureAnalyzer
from ai_data_collector import AIDataCollector

def test_ai_exposure_analyzer():
    """测试AI曝光率分析器"""
    print("=== 测试AI曝光率分析器 ===")
    
    # 创建分析器实例
    analyzer = AIExposureAnalyzer()
    
    # 测试获取汇总统计
    print("\n1. 测试获取汇总统计:")
    summary = analyzer.get_summary_stats()
    print(f"总问题量: {summary.get('total_questions', 0)}")
    print(f"收录问题: {summary.get('included_questions', 0)}")
    print(f"品牌词量: {summary.get('brand_keywords', 0)}")
    print(f"覆盖平台: {summary.get('covered_platforms', 0)}")
    
    # 测试获取平台统计
    print("\n2. 测试获取平台统计:")
    platforms = analyzer.get_platform_stats()
    for platform in platforms:
        print(f"{platform['platform']}: {platform['exposure_rate']}% ({platform['included_questions']}条)")
    
    # 测试获取问题数据
    print("\n3. 测试获取问题数据:")
    questions = analyzer.get_questions_data()
    print(f"问题总数: {len(questions)}")
    if questions:
        print("前3个问题:")
        for i, q in enumerate(questions[:3]):
            print(f"  {i+1}. {q['training_word']} - {q['question']} ({q['platform']})")
    
    # 测试搜索功能
    print("\n4. 测试搜索功能:")
    search_results = analyzer.search_questions("柚木柜")
    print(f"搜索'柚木柜'结果: {len(search_results)}条")
    
    # 测试图表数据
    print("\n5. 测试图表数据:")
    chart_data = analyzer.get_platform_contribution_chart_data()
    print(f"平台贡献图表数据: {len(chart_data['labels'])}个平台")
    
    device_data = analyzer.get_device_distribution_data()
    print(f"设备分布图表数据: {len(device_data['labels'])}个平台")

def test_ai_data_collector():
    """测试AI数据采集器"""
    print("\n=== 测试AI数据采集器 ===")
    
    # 创建分析器和采集器实例
    analyzer = AIExposureAnalyzer()
    collector = AIDataCollector(analyzer)
    
    # 测试生成模拟数据
    print("\n1. 测试生成模拟数据:")
    mock_data = collector.generate_mock_data(days=7)  # 生成7天的数据
    print(f"生成问题数: {len(mock_data.get('questions', []))}")
    print(f"平台数: {len(mock_data.get('platforms', {}))}")
    print(f"品牌关键词数: {len(mock_data.get('brand_keywords', []))}")
    
    # 测试更新数据
    print("\n2. 测试更新数据:")
    collector.update_data_from_collection(mock_data)
    print("数据更新完成")
    
    # 测试生成采集报告
    print("\n3. 测试生成采集报告:")
    report = collector.export_collection_report()
    print(f"采集报告生成完成")
    print(f"总问题数: {report['total_questions']}")
    print(f"平台数量: {report['platforms_count']}")
    print(f"热门关键词TOP3:")
    for keyword, count in report['top_keywords'][:3]:
        print(f"  {keyword}: {count}次")

def test_api_endpoints():
    """测试API端点（需要服务器运行）"""
    print("\n=== 测试API端点 ===")
    print("注意: 此测试需要服务器运行在 http://localhost:8000")
    
    import requests
    
    try:
        # 测试获取汇总统计
        response = requests.get("http://localhost:8000/api/ai_exposure/summary")
        if response.status_code == 200:
            data = response.json()
            print("✓ 汇总统计API正常")
        else:
            print(f"✗ 汇总统计API错误: {response.status_code}")
        
        # 测试获取平台统计
        response = requests.get("http://localhost:8000/api/ai_exposure/platforms")
        if response.status_code == 200:
            data = response.json()
            print("✓ 平台统计API正常")
        else:
            print(f"✗ 平台统计API错误: {response.status_code}")
        
        # 测试获取问题数据
        response = requests.get("http://localhost:8000/api/ai_exposure/questions")
        if response.status_code == 200:
            data = response.json()
            print("✓ 问题数据API正常")
        else:
            print(f"✗ 问题数据API错误: {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"✗ API测试出错: {e}")

def main():
    """主函数"""
    print("AI大模型曝光率分析系统测试")
    print("=" * 50)
    
    # 测试分析器
    test_ai_exposure_analyzer()
    
    # 测试采集器
    test_ai_data_collector()
    
    # 测试API端点
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("\n使用说明:")
    print("1. 运行 'python geo_app.py' 启动服务器")
    print("2. 访问 'http://localhost:8000' 查看前端界面")
    print("3. 点击侧边栏的 'AI曝光率分析' 查看仪表板")
    print("4. 使用 '生成模拟数据' 按钮创建测试数据")

if __name__ == "__main__":
    main()
