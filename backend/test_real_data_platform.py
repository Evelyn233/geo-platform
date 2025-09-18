#!/usr/bin/env python3
"""
测试真实AI数据采集平台
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from real_data_platform import RealDataPlatform, AIPlatformConfig
from data_collection_scheduler import DataCollectionScheduler

async def test_real_data_platform():
    """测试真实数据采集平台"""
    print("=== 真实AI数据采集平台测试 ===")
    
    # 创建平台实例
    platform = RealDataPlatform()
    
    # 测试关键词
    keywords = ["静钧抛光", "抛光布轮", "尼龙打磨片"]
    
    print(f"\n1. 测试关键词: {keywords}")
    
    # 检查平台配置
    print("\n2. 检查平台配置:")
    for name, collector in platform.collectors.items():
        print(f"  {name}: {'已配置' if collector else '未配置'}")
    
    # 测试平台状态检查
    print("\n3. 检查平台状态:")
    try:
        status = await platform.get_platform_status()
        for platform_name, info in status.items():
            print(f"  {platform_name}: {info.get('status', 'unknown')}")
    except Exception as e:
        print(f"  状态检查失败: {e}")
    
    # 测试数据采集（需要有效的API密钥）
    print("\n4. 测试数据采集:")
    print("  注意: 需要有效的API密钥才能进行真实数据采集")
    
    try:
        # 只测试一个关键词，减少API调用
        test_keywords = ["静钧抛光"]
        results = await platform.collect_data(test_keywords, ["豆包"])
        
        print(f"  采集结果: {len(results)} 个问题")
        
        if results:
            print("  前3个结果:")
            for i, result in enumerate(results[:3]):
                print(f"    {i+1}. [{result.platform}] {result.question}")
        
        # 保存结果
        if results:
            filename = platform.save_results()
            print(f"  结果已保存到: {filename}")
        
    except Exception as e:
        print(f"  数据采集测试失败: {e}")
        print("  这通常是因为API密钥未配置或无效")
    
    # 测试统计功能
    print("\n5. 测试统计功能:")
    stats = platform.get_statistics()
    print(f"  总问题数: {stats['total']}")
    print(f"  平台分布: {stats['platforms']}")
    print(f"  关键词分布: {dict(list(stats['keywords'].items())[:3])}")

async def test_scheduler():
    """测试数据采集调度器"""
    print("\n=== 数据采集调度器测试 ===")
    
    try:
        scheduler = DataCollectionScheduler()
        
        # 创建测试任务
        task_id = scheduler.create_task(
            keywords=["静钧抛光"],
            platforms=["豆包"],
            priority=1
        )
        
        print(f"1. 创建测试任务: {task_id}")
        
        # 获取调度器状态
        status = scheduler.get_status()
        print(f"2. 调度器状态:")
        print(f"   运行中: {status['is_running']}")
        print(f"   工作线程数: {status['worker_count']}")
        print(f"   队列大小: {status['queue_size']}")
        print(f"   总任务数: {status['total_tasks']}")
        
        # 获取任务状态
        task_status = scheduler.get_task_status(task_id)
        if task_status:
            print(f"3. 任务状态:")
            print(f"   任务ID: {task_status['task_id']}")
            print(f"   状态: {task_status['status']}")
            print(f"   关键词: {task_status['keywords']}")
            print(f"   平台: {task_status['platforms']}")
        
    except Exception as e:
        print(f"调度器测试失败: {e}")

def test_config_files():
    """测试配置文件"""
    print("\n=== 配置文件测试 ===")
    
    # 检查配置文件是否存在
    config_files = [
        "ai_platform_config.json",
        "scheduler_config.json"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✓ {config_file} 存在")
        else:
            print(f"✗ {config_file} 不存在")
    
    # 检查API配置
    try:
        import json
        with open("ai_platform_config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"\n平台配置:")
        for platform in config.get("platforms", []):
            name = platform.get("name", "Unknown")
            enabled = platform.get("enabled", False)
            has_key = bool(platform.get("api_key", "").strip())
            print(f"  {name}: {'启用' if enabled else '禁用'} | {'有密钥' if has_key else '无密钥'}")
    
    except Exception as e:
        print(f"配置文件检查失败: {e}")

async def test_api_endpoints():
    """测试API端点（需要服务器运行）"""
    print("\n=== API端点测试 ===")
    print("注意: 此测试需要服务器运行在 http://localhost:8000")
    
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            # 测试平台状态API
            try:
                async with session.get("http://localhost:8000/api/real_data/platforms/status") as response:
                    if response.status == 200:
                        data = await response.json()
                        print("✓ 平台状态API正常")
                    else:
                        print(f"✗ 平台状态API错误: {response.status}")
            except Exception as e:
                print(f"✗ 平台状态API连接失败: {e}")
            
            # 测试数据采集API
            try:
                test_data = {
                    "keywords": ["静钧抛光"],
                    "platforms": ["豆包"]
                }
                async with session.post("http://localhost:8000/api/real_data/collect", json=test_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success"):
                            print("✓ 数据采集API正常")
                        else:
                            print(f"✗ 数据采集API错误: {data.get('error')}")
                    else:
                        print(f"✗ 数据采集API错误: {response.status}")
            except Exception as e:
                print(f"✗ 数据采集API连接失败: {e}")
    
    except ImportError:
        print("✗ aiohttp未安装，无法测试API端点")
    except Exception as e:
        print(f"✗ API测试失败: {e}")

async def main():
    """主函数"""
    print("真实AI数据采集平台测试")
    print("=" * 50)
    
    # 测试配置文件
    test_config_files()
    
    # 测试真实数据平台
    await test_real_data_platform()
    
    # 测试调度器
    await test_scheduler()
    
    # 测试API端点
    await test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    
    print("\n使用说明:")
    print("1. 配置API密钥:")
    print("   - 编辑 ai_platform_config.json")
    print("   - 填入真实的API密钥")
    print("   - 启用要使用的平台")
    
    print("\n2. 启动系统:")
    print("   - 运行 'python geo_app.py'")
    print("   - 访问 'http://localhost:8000'")
    print("   - 点击 'AI曝光率分析'")
    
    print("\n3. 开始采集:")
    print("   - 输入关键词")
    print("   - 选择AI平台")
    print("   - 点击 '开始真实采集'")
    
    print("\n4. 查看结果:")
    print("   - 在仪表板中查看统计数据")
    print("   - 使用搜索功能筛选数据")
    print("   - 导出数据进行分析")

if __name__ == "__main__":
    asyncio.run(main())
