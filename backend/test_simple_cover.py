#!/usr/bin/env python3
"""
简单测试封面图片功能
"""

import requests
import json

def test_simple_cover():
    """简单测试封面图片"""
    print("=" * 80)
    print("🖼️ 简单测试封面图片功能")
    print("=" * 80)
    
    # 后端API配置 - 自动检测端口
    possible_ports = [8000, 8001, 8002, 8080]
    api_base = None
    
    for port in possible_ports:
        try:
            test_url = f"http://localhost:{port}/api/status"
            test_response = requests.get(test_url, timeout=2)
            if test_response.status_code == 200:
                api_base = f"http://localhost:{port}"
                print(f"✅ 找到后端服务在端口 {port}")
                break
        except:
            continue
    
    if not api_base:
        print("❌ 未找到运行中的后端服务")
        return
    
    try:
        print("1. 生成文章...")
        
        # 调用文章生成API
        generate_data = {
            "max_articles": 1,
            "enhanced": True,
            "model": "doubao-seed-1-6-flash"
        }
        
        response = requests.post(
            f"{api_base}/api/generate_articles",
            json=generate_data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                articles = result.get("articles", [])
                if articles:
                    article = articles[0]
                    
                    print("✅ 文章生成成功！")
                    print(f"标题: {article.get('title', 'N/A')}")
                    
                    # 检查封面图片
                    featured_image = article.get('featured_image')
                    if featured_image:
                        print(f"\n🎯 封面图片信息:")
                        print(f"标题: {featured_image['title']}")
                        print(f"来源: {featured_image['source']}")
                        print(f"URL: {featured_image['url']}")
                        
                        # 测试发布
                        print(f"\n2. 测试发布到WordPress...")
                        test_publish(article)
                    else:
                        print(f"❌ 未找到封面图片")
                else:
                    print("❌ 未生成任何文章")
            else:
                print(f"❌ 文章生成失败: {result.get('error', '未知错误')}")
        else:
            print(f"❌ API调用失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_publish(article):
    """测试发布"""
    try:
        # 准备发布数据
        publish_data = {
            "title": article["title"],
            "content": article["content"],
            "category_name": "新闻资讯"
        }
        
        # 添加封面图片
        if article.get("featured_image"):
            publish_data["featured_image"] = article["featured_image"]
            print(f"✅ 封面图片已添加到发布数据")
        else:
            print(f"❌ 没有封面图片")
        
        print(f"发布数据准备完成")
        print(f"标题: {publish_data['title']}")
        print(f"有封面图片: {'是' if 'featured_image' in publish_data else '否'}")
        
        # 这里可以添加实际的发布测试
        print(f"💡 可以在前端界面中点击'🚀 发布到WordPress'按钮进行实际发布测试")
        
    except Exception as e:
        print(f"❌ 准备发布数据失败: {e}")

if __name__ == "__main__":
    test_simple_cover()
