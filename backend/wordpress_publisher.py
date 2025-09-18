#!/usr/bin/env python3
"""
WordPress自动发布模块
支持将生成的文章自动发布到WordPress的新闻资讯分类
"""

import requests
import base64
import json
from typing import Dict, List, Optional
from datetime import datetime

class WordPressPublisher:
    def __init__(self, wp_url: str, username: str, password: str):
        """
        初始化WordPress发布器
        
        Args:
            wp_url: WordPress网站URL
            username: WordPress用户名
            password: WordPress应用密码
        """
        self.wp_url = wp_url.rstrip('/')
        self.username = username
        self.password = password
        self.api_url = f"{self.wp_url}/wp-json/wp/v2"
        
        # 创建认证头
        credentials = f"{username}:{password}"
        token = base64.b64encode(credentials.encode()).decode('utf-8')
        self.headers = {
            'Authorization': f'Basic {token}',
            'Content-Type': 'application/json'
        }
    
    def test_connection(self) -> Dict:
        """测试WordPress连接"""
        try:
            response = requests.get(f"{self.api_url}/users/me", headers=self.headers, timeout=10)
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "success": True,
                    "message": "WordPress连接成功",
                    "user": user_data.get("name", "未知用户")
                }
            else:
                return {
                    "success": False,
                    "message": f"连接失败: {response.status_code} - {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"连接异常: {str(e)}"
            }
    
    def get_categories(self) -> List[Dict]:
        """获取所有分类"""
        try:
            response = requests.get(f"{self.api_url}/categories", headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"获取分类失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"获取分类异常: {e}")
            return []
    
    def find_or_create_category(self, category_name: str = "新闻资讯") -> Optional[int]:
        """查找或创建分类"""
        try:
            # 先查找现有分类
            categories = self.get_categories()
            for category in categories:
                if category.get("name") == category_name:
                    print(f"找到现有分类: {category_name} (ID: {category['id']})")
                    return category["id"]
            
            # 如果没找到，创建新分类
            print(f"创建新分类: {category_name}")
            category_data = {
                "name": category_name,
                "slug": category_name.lower().replace(" ", "-"),
                "description": f"自动生成的{category_name}分类"
            }
            
            response = requests.post(
                f"{self.api_url}/categories",
                headers=self.headers,
                json=category_data,
                timeout=10
            )
            
            if response.status_code == 201:
                new_category = response.json()
                print(f"成功创建分类: {category_name} (ID: {new_category['id']})")
                return new_category["id"]
            else:
                print(f"创建分类失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"分类操作异常: {e}")
            return None
    
    def publish_article(self, article_data: Dict, category_name: str = "新闻资讯") -> Dict:
        """
        发布文章到WordPress
        
        Args:
            article_data: 文章数据，包含title, content, excerpt等
            category_name: 分类名称，默认为"新闻资讯"
        
        Returns:
            发布结果
        """
        try:
            # 获取或创建分类ID
            category_id = self.find_or_create_category(category_name)
            if not category_id:
                return {
                    "success": False,
                    "message": f"无法获取或创建分类: {category_name}"
                }
            
            # 准备文章数据
            post_data = {
                "title": article_data.get("title", ""),
                "content": article_data.get("content", ""),
                "excerpt": article_data.get("excerpt", ""),
                "status": "publish",  # 直接发布
                "categories": [category_id],
                "meta": {
                    "article_keyword": article_data.get("keyword", ""),
                    "article_score": article_data.get("score", 0),
                    "article_clicks": article_data.get("clicks", 0),
                    "article_conversion_rate": article_data.get("conversion_rate", 0),
                    "generated_time": datetime.now().isoformat(),
                    "enhanced": article_data.get("enhanced", False)
                }
            }
            
            # 添加标签
            if article_data.get("keyword"):
                post_data["tags"] = [article_data["keyword"]]
            
            # 发布文章
            print(f"正在发布文章: {article_data.get('title', '')}")
            response = requests.post(
                f"{self.api_url}/posts",
                headers=self.headers,
                json=post_data,
                timeout=30
            )
            
            if response.status_code == 201:
                post_result = response.json()
                return {
                    "success": True,
                    "message": "文章发布成功",
                    "post_id": post_result["id"],
                    "post_url": post_result["link"],
                    "post_title": post_result["title"]["rendered"]
                }
            else:
                return {
                    "success": False,
                    "message": f"发布失败: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"发布异常: {str(e)}"
            }
    
    def publish_multiple_articles(self, articles: List[Dict], category_name: str = "新闻资讯") -> List[Dict]:
        """批量发布文章"""
        results = []
        
        for i, article in enumerate(articles):
            print(f"发布第 {i+1}/{len(articles)} 篇文章...")
            result = self.publish_article(article, category_name)
            result["article_index"] = i + 1
            result["article_keyword"] = article.get("keyword", "")
            results.append(result)
            
            # 添加延迟避免请求过快
            import time
            time.sleep(2)
        
        return results
    
    def get_published_articles(self, category_id: Optional[int] = None) -> List[Dict]:
        """获取已发布的文章"""
        try:
            url = f"{self.api_url}/posts"
            params = {"status": "publish", "per_page": 20}
            
            if category_id:
                params["categories"] = category_id
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"获取文章失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"获取文章异常: {e}")
            return []

def test_wordpress_publisher():
    """测试WordPress发布功能"""
    # 测试配置
    wp_url = "https://your-wordpress-site.com"
    username = "your-username"
    password = "your-app-password"
    
    publisher = WordPressPublisher(wp_url, username, password)
    
    # 测试连接
    print("测试WordPress连接...")
    connection_result = publisher.test_connection()
    print(f"连接结果: {connection_result}")
    
    if connection_result["success"]:
        # 测试文章发布
        test_article = {
            "title": "测试文章标题",
            "content": "这是一篇测试文章的内容。",
            "excerpt": "测试文章摘要",
            "keyword": "测试关键词",
            "score": 85.5,
            "clicks": 10,
            "conversion_rate": 0.75,
            "enhanced": True
        }
        
        print("\n测试文章发布...")
        publish_result = publisher.publish_article(test_article)
        print(f"发布结果: {publish_result}")

if __name__ == "__main__":
    test_wordpress_publisher()


