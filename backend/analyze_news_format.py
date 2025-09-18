#!/usr/bin/env python3
"""
分析网站新闻资讯的排版格式
"""

import requests
from bs4 import BeautifulSoup
import json

def analyze_news_format():
    """分析新闻资讯的排版格式"""
    print("=" * 80)
    print("📰 分析网站新闻资讯排版格式")
    print("=" * 80)
    
    try:
        # 访问新闻页面
        print("1. 正在访问新闻资讯页面...")
        response = requests.get('https://www.shjingjun.com/news', timeout=10)
        
        if response.status_code == 200:
            print("   ✅ 页面访问成功")
        else:
            print(f"   ❌ 页面访问失败: {response.status_code}")
            return
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找文章
        articles = soup.find_all('article')
        print(f"   找到 {len(articles)} 篇文章")
        
        if not articles:
            # 尝试其他选择器
            articles = soup.find_all('div', class_=['post', 'entry', 'article'])
            print(f"   使用备用选择器找到 {len(articles)} 篇文章")
        
        if not articles:
            print("   ❌ 未找到文章，尝试查找所有可能的内容区域...")
            # 查找所有可能包含文章内容的div
            content_areas = soup.find_all('div', class_=lambda x: x and any(keyword in x.lower() for keyword in ['content', 'post', 'article', 'entry', 'news']))
            print(f"   找到 {len(content_areas)} 个可能的内容区域")
            
            for i, area in enumerate(content_areas[:3]):
                print(f"\n   === 内容区域 {i+1} ===")
                print(f"   class: {area.get('class', [])}")
                print(f"   内容预览: {area.get_text()[:200]}...")
                print(f"   HTML结构: {str(area)[:300]}...")
        
        # 分析前3篇文章的格式
        for i, article in enumerate(articles[:3]):
            print(f"\n   === 文章 {i+1} 分析 ===")
            
            # 查找标题
            title = article.find(['h1', 'h2', 'h3', 'h4'])
            if title:
                print(f"   标题: {title.get_text().strip()}")
                print(f"   标题标签: {title.name}")
            else:
                print("   标题: 未找到")
            
            # 查找内容
            content = article.find('div', class_=['entry-content', 'post-content', 'content'])
            if not content:
                content = article.find('div', class_=lambda x: x and 'content' in x.lower())
            if not content:
                content = article.find('p')
            
            if content:
                print(f"   内容预览: {content.get_text()[:200]}...")
                print(f"   内容标签: {content.name}")
                print(f"   内容class: {content.get('class', [])}")
            else:
                print("   内容: 未找到")
            
            # 分析HTML结构
            print(f"   文章HTML结构:")
            print(f"   {str(article)[:500]}...")
            
            # 查找图片
            images = article.find_all('img')
            if images:
                print(f"   图片数量: {len(images)}")
                for img in images[:2]:
                    print(f"   - 图片: {img.get('src', 'N/A')}")
            
            # 查找链接
            links = article.find_all('a')
            if links:
                print(f"   链接数量: {len(links)}")
                for link in links[:2]:
                    print(f"   - 链接: {link.get('href', 'N/A')}")
            
            print()
        
        # 分析整体页面结构
        print("\n2. 分析页面整体结构...")
        
        # 查找页面标题
        page_title = soup.find('title')
        if page_title:
            print(f"   页面标题: {page_title.get_text()}")
        
        # 查找主要内容区域
        main_content = soup.find('main') or soup.find('div', class_=lambda x: x and 'main' in x.lower())
        if main_content:
            print(f"   主要内容区域: {main_content.name}")
            print(f"   主要内容class: {main_content.get('class', [])}")
        
        # 查找侧边栏
        sidebar = soup.find('aside') or soup.find('div', class_=lambda x: x and 'sidebar' in x.lower())
        if sidebar:
            print(f"   侧边栏: {sidebar.name}")
            print(f"   侧边栏class: {sidebar.get('class', [])}")
        
        # 分析CSS类名模式
        print("\n3. 分析CSS类名模式...")
        all_classes = []
        for element in soup.find_all(class_=True):
            all_classes.extend(element.get('class', []))
        
        # 统计最常见的类名
        from collections import Counter
        class_counts = Counter(all_classes)
        common_classes = class_counts.most_common(10)
        
        print("   最常见的CSS类名:")
        for class_name, count in common_classes:
            print(f"   - {class_name}: {count} 次")
        
        # 生成WordPress文章格式建议
        print("\n4. 生成WordPress文章格式建议...")
        
        # 基于分析结果生成格式建议
        format_suggestions = {
            "title_format": "使用H1标签作为文章标题",
            "content_structure": "使用段落标签<p>包装正文内容",
            "heading_hierarchy": "使用H2、H3标签创建小标题",
            "list_format": "使用<ul>和<li>标签创建列表",
            "emphasis_format": "使用<strong>和<em>标签强调重要内容",
            "paragraph_spacing": "段落之间保持适当间距",
            "class_suggestions": []
        }
        
        # 基于发现的类名添加建议
        if any('entry' in cls for cls, _ in common_classes):
            format_suggestions["class_suggestions"].append("使用entry-content类包装文章内容")
        if any('post' in cls for cls, _ in common_classes):
            format_suggestions["class_suggestions"].append("使用post-content类包装文章内容")
        
        print("   建议的文章格式:")
        for key, value in format_suggestions.items():
            if isinstance(value, list):
                for item in value:
                    print(f"   - {item}")
            else:
                print(f"   - {value}")
        
        # 保存分析结果
        analysis_result = {
            "articles_found": len(articles),
            "common_classes": dict(common_classes),
            "format_suggestions": format_suggestions,
            "sample_articles": []
        }
        
        # 保存示例文章结构
        for i, article in enumerate(articles[:2]):
            article_data = {
                "index": i + 1,
                "title": article.find(['h1', 'h2', 'h3', 'h4']).get_text().strip() if article.find(['h1', 'h2', 'h3', 'h4']) else "N/A",
                "content_preview": article.find('div', class_=lambda x: x and 'content' in x.lower()).get_text()[:200] if article.find('div', class_=lambda x: x and 'content' in x.lower()) else "N/A",
                "html_structure": str(article)[:1000]
            }
            analysis_result["sample_articles"].append(article_data)
        
        # 保存到文件
        with open('news_format_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 分析完成！结果已保存到 news_format_analysis.json")
        
    except Exception as e:
        print(f"❌ 分析过程出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_news_format()

