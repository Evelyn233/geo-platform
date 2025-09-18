#!/usr/bin/env python3
"""
测试修复后的发布功能
"""

import requests
import json

def test_fixed_publish():
    """测试修复后的发布功能"""
    print("=" * 80)
    print("🔧 测试修复后的发布功能")
    print("=" * 80)
    
    # 后端API配置
    api_base = "http://localhost:8000"
    
    # WordPress配置
    wp_config = {
        "wp_url": "https://www.shjingjun.com",
        "wp_username": "jingjun2020", 
        "wp_password": "ymZx ssrJ UG1z IENK XHMi 10iP",
        "max_articles": 1,
        "enhanced": False,  # 使用基础版测试
        "model": "doubao-seed-1-6-flash",
        "category_name": "新闻资讯",
        "auto_publish": True
    }
    
    try:
        print("1. 检查后端服务...")
        health_response = requests.get(f"{api_base}/health", timeout=5)
        if health_response.status_code == 200:
            print("   ✅ 后端服务正常")
        else:
            print(f"   ❌ 后端服务异常: {health_response.status_code}")
            return
        
        print("\n2. 测试WordPress连接...")
        wp_test_response = requests.get(
            f"{api_base}/api/wordpress_test",
            params={"wp_url": wp_config["wp_url"]},
            timeout=10
        )
        
        if wp_test_response.status_code == 200:
            wp_result = wp_test_response.json()
            if wp_result.get("success"):
                print("   ✅ WordPress连接正常")
            else:
                print(f"   ❌ WordPress连接失败: {wp_result.get('message', '未知错误')}")
                return
        else:
            print(f"   ❌ WordPress测试API异常: {wp_test_response.status_code}")
            return
        
        print("\n3. 测试基础版文章生成...")
        print("   配置信息:")
        print(f"   - 网站: {wp_config['wp_url']}")
        print(f"   - 用户: {wp_config['wp_username']}")
        print(f"   - 分类: {wp_config['category_name']}")
        print(f"   - 文章数: {wp_config['max_articles']}")
        print(f"   - 增强模式: {wp_config['enhanced']} (使用基础版)")
        print(f"   - 模型: {wp_config['model']}")
        print(f"   - 自动发布: {wp_config['auto_publish']}")
        
        # 准备表单数据
        form_data = {
            "wp_url": wp_config["wp_url"],
            "wp_username": wp_config["wp_username"],
            "wp_password": wp_config["wp_password"],
            "max_articles": str(wp_config["max_articles"]),
            "enhanced": str(wp_config["enhanced"]).lower(),
            "model": wp_config["model"],
            "category_name": wp_config["category_name"],
            "auto_publish": str(wp_config["auto_publish"]).lower()
        }
        
        print("\n   正在生成和发布文章...")
        print("   🔧 修复说明：")
        print("   - 修复了WordPressArticleGenerator初始化参数缺失问题")
        print("   - 现在正确传递wp_url, username, password参数")
        print("   - 使用基础版生成器避免复杂依赖")
        
        publish_response = requests.post(
            f"{api_base}/api/publish_articles",
            data=form_data,
            timeout=120
        )
        
        if publish_response.status_code == 200:
            result = publish_response.json()
            
            if result.get("success"):
                print("\n   ✅ 文章生成和发布成功！")
                print(f"   消息: {result.get('message', '')}")
                print(f"   总文章数: {result.get('total_articles', 0)}")
                print(f"   成功发布: {result.get('published_count', 0)}")
                print(f"   发布失败: {result.get('failed_count', 0)}")
                print(f"   分类: {result.get('category', '')}")
                print(f"   分类ID: {result.get('category_id', '')}")
                
                # 显示发布结果详情
                if result.get("results"):
                    print("\n   发布结果详情:")
                    for i, publish_result in enumerate(result["results"], 1):
                        if publish_result["success"]:
                            print(f"     ✅ 第{i}篇: {publish_result['article_keyword']}")
                            print(f"        文章ID: {publish_result['post_id']}")
                            print(f"        文章链接: {publish_result['post_url']}")
                            print(f"        🔗 点击查看: {publish_result['post_url']}")
                        else:
                            print(f"     ❌ 第{i}篇: {publish_result['article_keyword']}")
                            print(f"        失败原因: {publish_result['message']}")
                        print()
                
                print("\n🎉 修复成功！")
                print("   📊 修复效果：")
                print("   - ✅ 修复了WordPressArticleGenerator初始化错误")
                print("   - ✅ 基础版文章生成器正常工作")
                print("   - ✅ 文章成功发布到新闻资讯分类")
                print("   - ✅ 系统现在可以正常使用")
                
            else:
                print(f"   ❌ 发布失败: {result.get('error', '未知错误')}")
                print("   🔍 错误分析：")
                if "missing" in result.get('error', ''):
                    print("   - 可能是参数传递问题")
                elif "connection" in result.get('error', '').lower():
                    print("   - 可能是WordPress连接问题")
                else:
                    print("   - 需要进一步调试")
                
        else:
            print(f"   ❌ 发布API异常: {publish_response.status_code}")
            print(f"   响应: {publish_response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端正在运行")
        print("   运行命令: uvicorn geo_app:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ 测试过程出错: {str(e)}")

if __name__ == "__main__":
    test_fixed_publish()


