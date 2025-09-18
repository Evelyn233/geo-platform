#!/usr/bin/env python3
"""
测试封面图片调试
"""

import requests
import json

def test_cover_debug():
    """测试封面图片调试"""
    print("=" * 80)
    print("🖼️ 测试封面图片调试")
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
        print("\n1. 生成文章...")
        
        # 调用文章生成API - 使用Form数据
        generate_data = {
            "wp_url": "https://www.shjingjun.com",
            "wp_username": "jingjun2020", 
            "wp_password": "shjingjun20201919.",
            "max_articles": 1,
            "enhanced": True,
            "model": "doubao-seed-1-6-flash"
        }
        
        response = requests.post(
            f"{api_base}/api/generate_articles",
            data=generate_data,
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
                    
                    # 详细检查封面图片数据
                    print(f"\n🔍 封面图片数据检查:")
                    featured_image = article.get('featured_image')
                    if featured_image:
                        print(f"✅ 找到封面图片数据:")
                        print(f"   完整数据: {json.dumps(featured_image, ensure_ascii=False, indent=2)}")
                        
                        # 检查关键字段
                        url = featured_image.get('url')
                        title = featured_image.get('title')
                        source = featured_image.get('source')
                        
                        print(f"\n📋 关键字段检查:")
                        print(f"   URL: {url}")
                        print(f"   标题: {title}")
                        print(f"   来源: {source}")
                        
                        if url:
                            print(f"   ✅ URL字段存在")
                        else:
                            print(f"   ❌ URL字段缺失")
                            
                        # 测试图片URL可访问性
                        print(f"\n🌐 测试图片URL可访问性:")
                        try:
                            img_response = requests.get(url, timeout=10)
                            if img_response.status_code == 200:
                                print(f"   ✅ 图片URL可访问")
                                print(f"   大小: {len(img_response.content)} bytes")
                                print(f"   类型: {img_response.headers.get('content-type', 'unknown')}")
                            else:
                                print(f"   ❌ 图片URL不可访问: {img_response.status_code}")
                        except Exception as e:
                            print(f"   ❌ 测试图片访问失败: {e}")
                        
                        # 测试发布数据格式
                        print(f"\n📝 测试发布数据格式:")
                        publish_data = {
                            "title": article["title"],
                            "content": article["content"],
                            "category_name": "新闻资讯",
                            "featured_image": featured_image
                        }
                        
                        # 提取封面图片URL（模拟发布API的逻辑）
                        featured_media_url = publish_data.get("featured_image", {}).get("url") if publish_data.get("featured_image") else None
                        print(f"   提取的封面图片URL: {featured_media_url}")
                        
                        if featured_media_url:
                            print(f"   ✅ 封面图片URL提取成功")
                        else:
                            print(f"   ❌ 封面图片URL提取失败")
                            
                    else:
                        print(f"❌ 未找到封面图片数据")
                        
                        # 检查所有图片
                        images = article.get('images', [])
                        if images:
                            print(f"📸 找到 {len(images)} 张图片:")
                            for i, img in enumerate(images):
                                print(f"   {i+1}. {img.get('title', 'N/A')} (来源: {img.get('source', 'N/A')})")
                        else:
                            print(f"❌ 未找到任何图片")
                            
                else:
                    print("❌ 未生成任何文章")
            else:
                print(f"❌ 文章生成失败: {result.get('error', '未知错误')}")
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"响应: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cover_debug()

