#!/usr/bin/env python3
"""
测试改进后的文章生成功能
"""

import requests
import json
import time

def test_improved_generation():
    """测试改进后的文章生成"""
    print("=" * 80)
    print("🚀 测试改进后的文章生成功能")
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
        
        print("\n2. 测试改进后的文章生成...")
        
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
                    
                    # 检查文章质量
                    content = article.get('content', '')
                    
                    # 检查是否包含HTML标签
                    if '<h1>' in content and '<h2>' in content:
                        print("   ✅ 包含完整的HTML结构")
                    else:
                        print("   ⚠️ HTML结构不完整")
                    
                    # 检查是否包含服务电话
                    if '13331805825' in content:
                        print("   ✅ 包含更新的服务电话")
                    else:
                        print("   ⚠️ 未找到更新的服务电话")
                    
                    # 检查文章质量指标
                    quality_indicators = [
                        '技术参数', '应用案例', '服务保障', '立即联系',
                        '市场验证', '技术优势', '产品特性'
                    ]
                    
                    found_indicators = [indicator for indicator in quality_indicators if indicator in content]
                    print(f"   📊 质量指标: {len(found_indicators)}/{len(quality_indicators)} 个")
                    print(f"      包含: {', '.join(found_indicators)}")
                    
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
                    else:
                        print("   ⚠️ 未选择封面图片")
                    
                    # 保存文章到文件
                    save_article_to_file(article)
                    
                    # 显示文章内容预览
                    print(f"\n3. 文章内容预览:")
                    print("   " + "="*60)
                    
                    # 显示前800个字符
                    preview = content[:800]
                    print(f"   {preview}...")
                    
                    if len(content) > 800:
                        print(f"   ... (还有 {len(content) - 800} 个字符)")
                    
                    print("   " + "="*60)
                    
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
        .quality-indicators {{
            background: #e8f5e8;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .quality-indicators h4 {{
            margin-top: 0;
            color: #28a745;
        }}
        .indicator {{
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            margin: 2px;
            font-size: 12px;
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
    
    <div class="quality-indicators">
        <h4>✅ 质量检查</h4>
        <p>服务电话: {'✅ 包含 13331805825' if '13331805825' in content else '❌ 未找到'}</p>
        <p>HTML结构: {'✅ 完整' if '<h1>' in content and '<h2>' in content else '❌ 不完整'}</p>
        <p>图片内容: {'✅ 包含' if '<img' in content else '❌ 未包含'}</p>
    </div>
    
    {content}
    
    <div style="margin-top: 50px; padding: 20px; background: #f8f9fa; border-radius: 8px; text-align: center;">
        <h3>🎉 改进后的文章生成完成！</h3>
        <p>这篇文章使用了增强版基础模板，确保即使API调用失败也能生成高质量内容。</p>
        <p>现在可以在WordPress中发布这篇文章了！</p>
    </div>
</body>
</html>
        """
        
        with open('improved_article_test.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"   📄 改进后的文章已保存到: improved_article_test.html")
        print(f"   🌐 可以在浏览器中打开查看效果")
        
    except Exception as e:
        print(f"   ❌ 保存文章失败: {e}")

if __name__ == "__main__":
    test_improved_generation()

