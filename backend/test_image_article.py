#!/usr/bin/env python3
"""
测试带图片的文章生成功能
"""

import requests
import json

def test_image_article_generation():
    """测试带图片的文章生成"""
    print("=" * 80)
    print("🖼️ 测试带图片的文章生成功能")
    print("=" * 80)
    
    # 后端API配置
    api_base = "http://localhost:8000"
    
    # 测试关键词
    test_keyword = "抛光风布轮厂家"
    
    try:
        print("1. 检查后端服务...")
        health_response = requests.get(f"{api_base}/health", timeout=5)
        if health_response.status_code == 200:
            print("   ✅ 后端服务正常")
        else:
            print(f"   ❌ 后端服务异常: {health_response.status_code}")
            return
        
        print(f"\n2. 测试关键词: {test_keyword}")
        print("   正在生成带图片的文章...")
        
        # 调用文章生成API
        generate_data = {
            "max_articles": 1,
            "enhanced": True,
            "model": "doubao-seed-1-6-flash"
        }
        
        response = requests.post(
            f"{api_base}/api/generate_articles",
            json=generate_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                articles = result.get("articles", [])
                if articles:
                    article = articles[0]
                    
                    print("   ✅ 文章生成成功！")
                    print(f"   标题: {article.get('title', 'N/A')}")
                    print(f"   内容长度: {len(article.get('content', ''))} 字符")
                    print(f"   是否增强版: {article.get('enhanced', False)}")
                    
                    # 检查是否包含图片
                    content = article.get('content', '')
                    if '<img' in content:
                        print("   🖼️ 文章包含图片！")
                        # 统计图片数量
                        img_count = content.count('<img')
                        print(f"   图片数量: {img_count}")
                    else:
                        print("   ⚠️ 文章未包含图片")
                    
                    # 检查是否包含更新的电话
                    if '13331805825' in content:
                        print("   📞 包含更新的服务电话")
                    else:
                        print("   ⚠️ 未找到更新的服务电话")
                    
                    # 显示文章内容预览
                    print(f"\n3. 文章内容预览:")
                    print("   " + "="*60)
                    
                    # 显示前500个字符
                    preview = content[:500]
                    print(f"   {preview}...")
                    
                    if len(content) > 500:
                        print(f"   ... (还有 {len(content) - 500} 个字符)")
                    
                    print("   " + "="*60)
                    
                    # 保存完整文章到文件
                    with open('test_image_article.html', 'w', encoding='utf-8') as f:
                        f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{article.get('title', '测试文章')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h2 {{ color: #333; border-bottom: 2px solid #007cba; }}
        h3 {{ color: #555; }}
        img {{ max-width: 100%; height: auto; border-radius: 8px; }}
        .image-grid {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 20px 0; }}
        .image-item {{ flex: 1; min-width: 200px; max-width: 300px; }}
    </style>
</head>
<body>
    <h1>{article.get('title', '测试文章')}</h1>
    {content}
</body>
</html>
                        """)
                    
                    print(f"\n   📄 完整文章已保存到: test_image_article.html")
                    print(f"   🌐 可以在浏览器中打开查看效果")
                    
                    # 测试发布功能
                    print(f"\n4. 测试发布功能...")
                    print("   WordPress配置:")
                    print("   - URL: https://www.shjingjun.com")
                    print("   - 用户名: jingjun2020")
                    print("   - 应用密码: 已配置")
                    
                    # 这里可以添加发布测试代码
                    print("   💡 提示：可以在前端界面中点击'🚀 发布到WordPress'按钮进行发布测试")
                    
                else:
                    print("   ❌ 未生成任何文章")
            else:
                print(f"   ❌ 文章生成失败: {result.get('error', '未知错误')}")
                
        else:
            print(f"   ❌ API调用失败: {response.status_code}")
            print(f"   响应: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端正在运行")
        print("   运行命令: uvicorn geo_app:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ 测试过程出错: {str(e)}")
        import traceback
        traceback.print_exc()

def test_image_search_only():
    """仅测试图片搜索功能"""
    print("=" * 80)
    print("🔍 测试图片搜索功能")
    print("=" * 80)
    
    try:
        from image_search import ImageSearcher
        
        searcher = ImageSearcher()
        keyword = "抛光风布轮厂家"
        
        print(f"正在搜索关键词: {keyword}")
        images = searcher.search_images(keyword, max_results=3)
        
        if images:
            print(f"✅ 找到 {len(images)} 张图片:")
            for i, img in enumerate(images):
                print(f"   {i+1}. {img['title']}")
                print(f"      URL: {img['url']}")
                print(f"      来源: {img['source']}")
                print()
            
            # 生成HTML
            html = searcher.get_image_html(images, max_images=2)
            print("生成的HTML:")
            print(html)
        else:
            print("❌ 未找到任何图片")
            
    except Exception as e:
        print(f"❌ 图片搜索测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("选择测试模式:")
    print("1. 完整文章生成测试（需要后端运行）")
    print("2. 仅图片搜索测试")
    
    choice = input("请输入选择 (1/2): ").strip()
    
    if choice == "1":
        test_image_article_generation()
    elif choice == "2":
        test_image_search_only()
    else:
        print("无效选择，运行完整测试...")
        test_image_article_generation()

