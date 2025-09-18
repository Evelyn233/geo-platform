#!/usr/bin/env python3
"""
设置新闻资讯分类
"""

import requests
import base64

def setup_news_category():
    """设置新闻资讯分类"""
    print("=" * 60)
    print("📰 设置新闻资讯分类")
    print("=" * 60)
    
    # WordPress配置
    wp_url = "https://www.shjingjun.com"
    username = "jingjun2020"
    app_password = "ymZx ssrJ UG1z IENK XHMi 10iP"  # 你的应用密码
    
    # 设置认证头
    credentials = f"{username}:{app_password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/json',
        'User-Agent': 'GEO-System/1.0'
    }
    
    try:
        # 1. 获取所有分类
        print("1. 获取现有分类...")
        response = requests.get(f"{wp_url}/wp-json/wp/v2/categories", headers=headers, timeout=10)
        
        if response.status_code == 200:
            categories = response.json()
            print(f"   找到 {len(categories)} 个分类")
            
            # 查找新闻资讯分类
            news_category = None
            for cat in categories:
                if "新闻" in cat['name'] or "资讯" in cat['name'] or "news" in cat['name'].lower():
                    news_category = cat
                    break
            
            if news_category:
                print(f"   ✅ 找到新闻分类: {news_category['name']} (ID: {news_category['id']})")
                return news_category['id']
            else:
                print("   ❌ 未找到新闻分类，准备创建...")
                
                # 2. 创建新闻资讯分类
                print("2. 创建新闻资讯分类...")
                category_data = {
                    "name": "新闻资讯",
                    "slug": "news",
                    "description": "GEO系统自动生成的文章分类"
                }
                
                create_response = requests.post(f"{wp_url}/wp-json/wp/v2/categories", 
                                              headers=headers, json=category_data, timeout=10)
                
                if create_response.status_code == 201:
                    new_category = create_response.json()
                    print(f"   ✅ 成功创建分类: {new_category['name']} (ID: {new_category['id']})")
                    return new_category['id']
                else:
                    print(f"   ❌ 创建分类失败: {create_response.status_code} - {create_response.text}")
                    return None
        else:
            print(f"   ❌ 获取分类失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 设置分类异常: {str(e)}")
        return None

def test_news_publishing():
    """测试新闻发布"""
    print("\n" + "=" * 60)
    print("📝 测试新闻发布")
    print("=" * 60)
    
    # WordPress配置
    wp_url = "https://www.shjingjun.com"
    username = "jingjun2020"
    app_password = "ymZx ssrJ UG1z IENK XHMi 10iP"
    
    # 设置认证头
    credentials = f"{username}:{app_password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/json',
        'User-Agent': 'GEO-System/1.0'
    }
    
    # 获取新闻分类ID
    news_category_id = setup_news_category()
    if not news_category_id:
        print("❌ 无法获取新闻分类ID，测试终止")
        return
    
    try:
        # 创建测试文章
        test_article = {
            "title": "GEO系统测试文章 - 新闻资讯分类",
            "content": """<p>这是通过GEO系统自动发布到新闻资讯分类的测试文章。</p>
            <p>如果您看到这篇文章，说明：</p>
            <ul>
            <li>✅ WordPress连接正常</li>
            <li>✅ 应用密码认证成功</li>
            <li>✅ 新闻资讯分类创建成功</li>
            <li>✅ 文章发布功能正常</li>
            </ul>
            <p>现在可以开始使用GEO系统自动生成和发布文章了！</p>""",
            "status": "publish",
            "categories": [news_category_id]
        }
        
        print("3. 发布测试文章...")
        response = requests.post(f"{wp_url}/wp-json/wp/v2/posts", 
                               headers=headers, json=test_article, timeout=30)
        
        if response.status_code == 201:
            post_data = response.json()
            print("   ✅ 测试文章发布成功！")
            print(f"   文章ID: {post_data['id']}")
            print(f"   文章标题: {post_data['title']['rendered']}")
            print(f"   文章链接: {post_data['link']}")
            print(f"   分类ID: {post_data['categories']}")
            
            # 验证文章在新闻分类中
            print("\n4. 验证文章分类...")
            verify_response = requests.get(f"{wp_url}/wp-json/wp/v2/posts?categories={news_category_id}", 
                                         headers=headers, timeout=10)
            
            if verify_response.status_code == 200:
                posts = verify_response.json()
                print(f"   ✅ 新闻分类中现有 {len(posts)} 篇文章")
                for post in posts[:3]:  # 显示前3篇
                    print(f"   - {post['title']['rendered']} (ID: {post['id']})")
            
        else:
            print(f"   ❌ 发布失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 测试发布异常: {str(e)}")

if __name__ == "__main__":
    test_news_publishing()


