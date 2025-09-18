#!/usr/bin/env python3
"""
测试封面图片上传功能
"""

import requests
import json

def test_cover_upload():
    """测试封面图片上传"""
    print("=" * 80)
    print("🖼️ 测试封面图片上传功能")
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
        
        # 调用文章生成API
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
                    
                    # 检查封面图片
                    featured_image = article.get('featured_image')
                    if featured_image:
                        print(f"\n🎯 封面图片信息:")
                        print(f"标题: {featured_image['title']}")
                        print(f"来源: {featured_image['source']}")
                        print(f"URL: {featured_image['url']}")
                        
                        # 测试图片URL
                        print(f"\n🌐 测试图片URL...")
                        try:
                            img_response = requests.get(featured_image['url'], timeout=10)
                            if img_response.status_code == 200:
                                print(f"✅ 图片URL可访问")
                                print(f"大小: {len(img_response.content)} bytes")
                                print(f"类型: {img_response.headers.get('content-type', 'unknown')}")
                                
                                # 测试WordPress上传
                                print(f"\n📤 测试WordPress上传...")
                                test_wordpress_upload(featured_image['url'], article['title'])
                            else:
                                print(f"❌ 图片URL不可访问: {img_response.status_code}")
                        except Exception as e:
                            print(f"❌ 测试图片访问失败: {e}")
                    else:
                        print(f"❌ 未找到封面图片")
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

def test_wordpress_upload(image_url, title):
    """测试WordPress图片上传"""
    try:
        from wordpress_simple_auth import SimpleWordPressAuth
        
        # 创建认证器
        auth = SimpleWordPressAuth(
            "https://www.shjingjun.com",
            "jingjun2020",
            "shjingjun20201919."
        )
        
        # 测试连接
        print("   测试WordPress连接...")
        connection_test = auth.test_connection()
        if not connection_test["success"]:
            print(f"   ❌ WordPress连接失败: {connection_test['message']}")
            return
        
        print("   ✅ WordPress连接成功")
        
        # 测试图片上传
        print("   测试图片上传...")
        media_id = auth.upload_image_from_url(image_url, title)
        
        if media_id:
            print(f"   ✅ 图片上传成功，媒体ID: {media_id}")
            
            # 测试发布文章
            print("   测试发布文章...")
            publish_result = auth.publish_article(
                title=f"测试文章 - {title}",
                content="<p>这是一个测试文章，用于验证封面图片功能。</p>",
                category_id=None,
                status="publish",
                featured_media_url=image_url
            )
            
            if publish_result["success"]:
                print(f"   ✅ 文章发布成功，ID: {publish_result['post_id']}")
                print(f"   文章链接: {publish_result['post_url']}")
            else:
                print(f"   ❌ 文章发布失败: {publish_result['message']}")
        else:
            print(f"   ❌ 图片上传失败")
            
    except Exception as e:
        print(f"   ❌ WordPress测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cover_upload()

