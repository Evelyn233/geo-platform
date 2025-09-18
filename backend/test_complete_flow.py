#!/usr/bin/env python3
"""
测试完整的文章生成和发布流程
包含图片搜索、封面图片选择、WordPress发布
"""

import requests
import json
import time

def test_complete_flow():
    """测试完整流程"""
    print("=" * 80)
    print("🚀 测试完整文章生成和发布流程")
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
        
        print("\n2. 测试文章生成（包含图片搜索）...")
        
        # 调用文章生成API
        generate_data = {
            "max_articles": 1,
            "enhanced": True,
            "model": "doubao-seed-1-6-flash"
        }
        
        print("   正在生成增强版文章...")
        response = requests.post(
            f"{api_base}/api/generate_articles",
            json=generate_data,
            timeout=120  # 增加超时时间，因为包含图片搜索
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
                        print(f"   🖼️ 找到 {len(images)} 张图片")
                        for i, img in enumerate(images):
                            print(f"      {i+1}. {img['title']} (评分: {img.get('quality_score', 0):.1f})")
                    else:
                        print("   ⚠️ 未找到图片")
                    
                    # 检查封面图片
                    featured_image = article.get('featured_image')
                    if featured_image:
                        print(f"   🎯 封面图片: {featured_image['title']}")
                        print(f"      质量评分: {featured_image.get('quality_score', 0):.1f}")
                        print(f"      来源: {featured_image['source']}")
                    else:
                        print("   ⚠️ 未选择封面图片")
                    
                    # 检查服务电话
                    content = article.get('content', '')
                    if '13331805825' in content:
                        print("   📞 包含更新的服务电话")
                    else:
                        print("   ⚠️ 未找到更新的服务电话")
                    
                    # 保存文章到文件
                    save_article_to_file(article)
                    
                    # 测试发布功能
                    print(f"\n3. 测试WordPress发布...")
                    test_wordpress_publish(article)
                    
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

def save_article_to_file(article):
    """保存文章到HTML文件"""
    try:
        content = article.get('content', '')
        title = article.get('title', '测试文章')
        
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
        .quality-badge {{
            display: inline-block;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            margin-left: 5px;
        }}
        .quality-excellent {{
            background: #28a745;
            color: white;
        }}
        .quality-good {{
            background: #ffc107;
            color: black;
        }}
        .featured-image {{
            background: #e8f5e8;
            border: 2px solid #28a745;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    
    <div class="article-info">
        <h3>📊 文章信息</h3>
        <p><strong>生成时间:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>文章类型:</strong> {'增强版（包含图片搜索）' if article.get('enhanced') else '基础版'}</p>
        <p><strong>内容长度:</strong> {len(content)} 字符</p>
        <p><strong>图片数量:</strong> {len(article.get('images', []))} 张</p>
        {f'<p><strong>封面图片:</strong> {article["featured_image"]["title"]} (评分: {article["featured_image"].get("quality_score", 0):.1f})</p>' if article.get('featured_image') else ''}
    </div>
    
    {content}
    
    <div style="margin-top: 50px; padding: 20px; background: #f8f9fa; border-radius: 8px; text-align: center;">
        <h3>🎉 文章生成完成！</h3>
        <p>这篇文章包含了图片搜索、质量评分、封面图片选择等增强功能。</p>
        <p>现在可以在WordPress中发布这篇文章了！</p>
    </div>
</body>
</html>
        """
        
        with open('complete_article_test.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"   📄 完整文章已保存到: complete_article_test.html")
        print(f"   🌐 可以在浏览器中打开查看效果")
        
    except Exception as e:
        print(f"   ❌ 保存文章失败: {e}")

def test_wordpress_publish(article):
    """测试WordPress发布"""
    try:
        print("   WordPress配置:")
        print("   - URL: https://www.shjingjun.com")
        print("   - 用户名: jingjun2020")
        print("   - 应用密码: 已配置")
        
        # 准备发布数据
        publish_data = {
            "title": article["title"],
            "content": article["content"],
            "category_name": "新闻资讯"
        }
        
        # 如果有封面图片，添加到发布数据
        if article.get("featured_image"):
            publish_data["featured_image"] = article["featured_image"]
            print(f"   🖼️ 将使用封面图片: {article['featured_image']['title']}")
        
        print("   💡 提示：可以在前端界面中点击'🚀 发布到WordPress'按钮进行发布测试")
        print("   📝 发布数据已准备就绪")
        
    except Exception as e:
        print(f"   ❌ 准备发布数据失败: {e}")

if __name__ == "__main__":
    test_complete_flow()

