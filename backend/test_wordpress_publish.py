#!/usr/bin/env python3
"""
测试WordPress自动发布功能
"""

import requests
import json
from wordpress_publisher import WordPressPublisher

def test_wordpress_connection():
    """测试WordPress连接"""
    print("=" * 60)
    print("🔗 测试WordPress连接")
    print("=" * 60)
    
    # 请替换为你的WordPress信息
    wp_url = "https://your-wordpress-site.com"
    username = "your-username"
    password = "your-app-password"
    
    publisher = WordPressPublisher(wp_url, username, password)
    
    # 测试连接
    result = publisher.test_connection()
    print(f"连接结果: {result}")
    
    if result["success"]:
        print("✅ WordPress连接成功！")
        return True
    else:
        print("❌ WordPress连接失败！")
        return False

def test_category_management():
    """测试分类管理"""
    print("\n" + "=" * 60)
    print("📂 测试分类管理")
    print("=" * 60)
    
    wp_url = "https://your-wordpress-site.com"
    username = "your-username"
    password = "your-app-password"
    
    publisher = WordPressPublisher(wp_url, username, password)
    
    # 获取现有分类
    print("获取现有分类...")
    categories = publisher.get_categories()
    print(f"现有分类数量: {len(categories)}")
    
    for category in categories[:5]:  # 只显示前5个
        print(f"  - {category['name']} (ID: {category['id']})")
    
    # 测试创建分类
    print("\n测试创建分类...")
    category_id = publisher.find_or_create_category("测试分类")
    if category_id:
        print(f"✅ 分类创建成功，ID: {category_id}")
    else:
        print("❌ 分类创建失败")

def test_article_publishing():
    """测试文章发布"""
    print("\n" + "=" * 60)
    print("📝 测试文章发布")
    print("=" * 60)
    
    wp_url = "https://your-wordpress-site.com"
    username = "your-username"
    password = "your-app-password"
    
    publisher = WordPressPublisher(wp_url, username, password)
    
    # 测试文章数据
    test_article = {
        "title": "测试文章：WordPress自动发布功能",
        "content": """这是一篇测试文章，用于验证WordPress自动发布功能。

## 功能特点

• 自动生成高质量内容
• 基于百度推广数据优化
• 支持多种AI模型
• 批量发布到指定分类

## 技术优势

• 节省大量手动时间
• 提高内容更新频率
• 优化SEO效果
• 数据驱动的内容策略

## 使用建议

建议定期检查发布的内容质量，并根据数据反馈调整生成策略。""",
        "excerpt": "测试WordPress自动发布功能，验证系统集成效果。",
        "keyword": "WordPress自动发布",
        "score": 95.5,
        "clicks": 25,
        "conversion_rate": 0.85,
        "enhanced": True
    }
    
    print("发布测试文章...")
    result = publisher.publish_article(test_article, "测试分类")
    print(f"发布结果: {result}")
    
    if result["success"]:
        print("✅ 文章发布成功！")
        print(f"文章ID: {result['post_id']}")
        print(f"文章链接: {result['post_url']}")
    else:
        print("❌ 文章发布失败！")

def test_batch_publishing():
    """测试批量发布"""
    print("\n" + "=" * 60)
    print("📚 测试批量发布")
    print("=" * 60)
    
    wp_url = "https://your-wordpress-site.com"
    username = "your-username"
    password = "your-app-password"
    
    publisher = WordPressPublisher(wp_url, username, password)
    
    # 测试文章列表
    test_articles = [
        {
            "title": "批量发布测试文章 1",
            "content": "这是第一篇批量测试文章。",
            "excerpt": "批量测试文章1",
            "keyword": "测试关键词1",
            "score": 85.0,
            "clicks": 15,
            "conversion_rate": 0.75,
            "enhanced": False
        },
        {
            "title": "批量发布测试文章 2",
            "content": "这是第二篇批量测试文章。",
            "excerpt": "批量测试文章2",
            "keyword": "测试关键词2",
            "score": 90.0,
            "clicks": 20,
            "conversion_rate": 0.80,
            "enhanced": True
        }
    ]
    
    print("批量发布测试文章...")
    results = publisher.publish_multiple_articles(test_articles, "测试分类")
    
    success_count = sum(1 for r in results if r["success"])
    print(f"批量发布结果: 成功 {success_count}/{len(results)} 篇")
    
    for i, result in enumerate(results):
        if result["success"]:
            print(f"  ✅ 第{i+1}篇: {result['post_title']}")
        else:
            print(f"  ❌ 第{i+1}篇: {result['message']}")

def test_api_endpoints():
    """测试API端点"""
    print("\n" + "=" * 60)
    print("🌐 测试API端点")
    print("=" * 60)
    
    api_base = "http://localhost:8000"
    
    # 测试发布文章API
    print("测试发布文章API...")
    try:
        response = requests.post(f"{api_base}/api/publish_articles", 
                               data={
                                   "wp_url": "https://your-site.com",
                                   "wp_username": "test",
                                   "wp_password": "test",
                                   "max_articles": 1,
                                   "enhanced": True,
                                   "model": "doubao-seed-1-6-flash",
                                   "category_name": "测试分类",
                                   "auto_publish": False
                               }, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"API响应: {result}")
        else:
            print(f"API错误: {response.status_code}")
    except Exception as e:
        print(f"API测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 WordPress自动发布功能测试")
    print("请先修改脚本中的WordPress信息！")
    
    # 取消注释以下行来运行测试
    # test_wordpress_connection()
    # test_category_management()
    # test_article_publishing()
    # test_batch_publishing()
    # test_api_endpoints()
    
    print("\n" + "=" * 60)
    print("📋 测试完成")
    print("=" * 60)
    print("请检查WordPress后台确认文章是否成功发布！")

if __name__ == "__main__":
    main()


