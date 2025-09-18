#!/usr/bin/env python3
"""
测试Google图片搜索集成
"""

import requests
import json
import time

def test_google_integration():
    """测试Google搜索集成"""
    print("=" * 80)
    print("🔍 测试Google图片搜索集成")
    print("=" * 80)
    
    # 后端API配置
    api_base = "http://localhost:8000"
    
    try:
        print("1. 检查后端服务...")
        health_response = requests.get(f"{api_base}/health", timeout=5)
        if health_response.status_code == 200:
            print("   ✅ 后端服务正常")
        else:
            print(f"   ❌ 后端服务异常: {health_response.status_code}")
            return
        
        print("\n2. 测试Google图片搜索集成...")
        
        # 调用文章生成API
        generate_data = {
            "max_articles": 1,
            "enhanced": True,
            "model": "doubao-seed-1-6-flash"
        }
        
        print("   正在生成包含Google图片搜索的文章...")
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
                    
                    print("   ✅ 文章生成成功！")
                    print(f"   标题: {article.get('title', 'N/A')}")
                    print(f"   内容长度: {len(article.get('content', ''))} 字符")
                    print(f"   是否增强版: {article.get('enhanced', False)}")
                    
                    # 检查图片信息
                    images = article.get('images', [])
                    if images:
                        print(f"   🖼️ 找到 {len(images)} 张图片:")
                        for i, img in enumerate(images):
                            print(f"      {i+1}. {img['title']}")
                            print(f"         来源: {img['source']}")
                            print(f"         质量评分: {img.get('quality_score', 0):.2f}")
                            print(f"         URL: {img['url'][:80]}...")
                    else:
                        print("   ⚠️ 未找到图片")
                    
                    # 检查封面图片
                    featured_image = article.get('featured_image')
                    if featured_image:
                        print(f"   🎯 封面图片: {featured_image['title']}")
                        print(f"      来源: {featured_image['source']}")
                        print(f"      质量评分: {featured_image.get('quality_score', 0):.2f}")
                    else:
                        print("   ⚠️ 未选择封面图片")
                    
                    # 保存文章到文件
                    save_article_with_google_images(article)
                    
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

def save_article_with_google_images(article):
    """保存包含Google图片的文章"""
    try:
        content = article.get('content', '')
        title = article.get('title', '测试文章')
        images = article.get('images', [])
        
        # 创建完整的HTML页面
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.8;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        h3 {{
            color: #7f8c8d;
            margin-top: 25px;
        }}
        .article-info {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #28a745;
        }}
        .image-info {{
            background: #e8f5e8;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .image-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        .image-item {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        .image-item:hover {{
            transform: translateY(-5px);
        }}
        .image-item img {{
            width: 100%;
            height: 200px;
            object-fit: cover;
        }}
        .image-caption {{
            padding: 12px;
        }}
        .source-badge {{
            display: inline-block;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            margin-left: 5px;
        }}
        .source-google {{
            background: #4285f4;
            color: white;
        }}
        .source-local {{
            background: #28a745;
            color: white;
        }}
        .source-fallback {{
            background: #ffc107;
            color: black;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    
    <div class="article-info">
        <h3>📊 文章信息</h3>
        <p><strong>生成时间:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>文章类型:</strong> {'增强版（包含Google图片搜索）' if article.get('enhanced') else '基础版'}</p>
        <p><strong>内容长度:</strong> {len(content)} 字符</p>
        <p><strong>图片数量:</strong> {len(images)} 张</p>
        {f'<p><strong>封面图片:</strong> {article["featured_image"]["title"]} (来源: {article["featured_image"]["source"]}, 评分: {article["featured_image"].get("quality_score", 0):.1f})</p>' if article.get('featured_image') else ''}
    </div>
    
    <div class="image-info">
        <h3>🖼️ 图片搜索信息</h3>
        <p><strong>搜索策略:</strong> Google图片搜索 → 本地图片库 → 在线搜索</p>
        <p><strong>图片来源分布:</strong></p>
        <ul>
        {get_source_distribution(images)}
        </ul>
    </div>
    
    {content}
    
    <div style="margin-top: 50px; padding: 20px; background: #f8f9fa; border-radius: 8px; text-align: center;">
        <h3>🎉 Google图片搜索集成完成！</h3>
        <p>这篇文章使用了Google图片搜索，能够找到更准确、更相关的工业图片。</p>
        <p>现在可以在WordPress中发布这篇文章了！</p>
    </div>
</body>
</html>
        """
        
        with open('google_integration_test.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"   📄 包含Google图片的文章已保存到: google_integration_test.html")
        print(f"   🌐 可以在浏览器中打开查看效果")
        
    except Exception as e:
        print(f"   ❌ 保存文章失败: {e}")

def get_source_distribution(images):
    """获取图片来源分布"""
    sources = {}
    for img in images:
        source = img.get('source', 'Unknown')
        sources[source] = sources.get(source, 0) + 1
    
    html = ""
    for source, count in sources.items():
        badge_class = f"source-{source.lower().replace(' ', '-')}"
        html += f"<li><span class='source-badge {badge_class}'>{source}</span>: {count} 张</li>"
    
    return html

def test_direct_google_search():
    """直接测试Google搜索功能"""
    print("\n" + "=" * 80)
    print("🔍 直接测试Google搜索功能")
    print("=" * 80)
    
    try:
        from google_image_search import GoogleImageSearcher
        
        searcher = GoogleImageSearcher()
        keyword = "抛光风布轮厂家"
        
        print(f"搜索关键词: {keyword}")
        images = searcher.search_google_images(keyword, max_results=3)
        
        if images:
            print(f"✅ 找到 {len(images)} 张图片:")
            for i, img in enumerate(images):
                print(f"\n  📸 图片 {i+1}:")
                print(f"     标题: {img['title']}")
                print(f"     来源: {img['source']}")
                print(f"     质量评分: {img.get('quality_score', 0):.2f}")
                print(f"     尺寸: {img.get('size', 'N/A')}")
                print(f"     URL: {img['url'][:80]}...")
        else:
            print("❌ 未找到任何图片")
            
    except Exception as e:
        print(f"❌ 直接测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("选择测试模式:")
    print("1. 完整集成测试（需要后端运行）")
    print("2. 直接Google搜索测试")
    print("3. 全部测试")
    
    choice = input("请输入选择 (1/2/3): ").strip()
    
    if choice == "1":
        test_google_integration()
    elif choice == "2":
        test_direct_google_search()
    elif choice == "3":
        test_google_integration()
        test_direct_google_search()
    else:
        print("无效选择，运行完整测试...")
        test_google_integration()
        test_direct_google_search()

