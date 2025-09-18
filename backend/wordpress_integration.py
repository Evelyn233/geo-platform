#!/usr/bin/env python3
"""
WordPress网站内容接入RAG数据库
支持通过REST API获取WordPress内容并存储到RAG-Anything知识库
"""

import os
import sys
import json
import requests
import asyncio
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# 添加项目路径
PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

class WordPressRAGIntegration:
    def __init__(self, wp_url: str, wp_username: str = None, wp_password: str = None):
        """
        初始化WordPress集成
        
        Args:
            wp_url: WordPress网站URL (如: https://www.shjingjun.com)
            wp_username: WordPress用户名 (可选，用于认证)
            wp_password: WordPress密码 (可选，用于认证)
        """
        self.wp_url = wp_url.rstrip('/')
        self.wp_username = wp_username
        self.wp_password = wp_password
        self.session = requests.Session()
        
        # 设置认证
        if wp_username and wp_password:
            self.session.auth = (wp_username, wp_password)
    
    def get_posts(self, per_page: int = 100, page: int = 1) -> List[Dict]:
        """获取WordPress文章"""
        try:
            url = f"{self.wp_url}/wp-json/wp/v2/posts"
            params = {
                'per_page': per_page,
                'page': page,
                'status': 'publish',
                '_embed': True
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            posts = response.json()
            print(f"获取到 {len(posts)} 篇文章")
            return posts
            
        except Exception as e:
            print(f"获取文章失败: {e}")
            return []
    
    def get_pages(self, per_page: int = 100, page: int = 1) -> List[Dict]:
        """获取WordPress页面"""
        try:
            url = f"{self.wp_url}/wp-json/wp/v2/pages"
            params = {
                'per_page': per_page,
                'page': page,
                'status': 'publish',
                '_embed': True
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            pages = response.json()
            print(f"获取到 {len(pages)} 个页面")
            return pages
            
        except Exception as e:
            print(f"获取页面失败: {e}")
            return []
    
    def get_categories(self) -> List[Dict]:
        """获取分类"""
        try:
            url = f"{self.wp_url}/wp-json/wp/v2/categories"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            categories = response.json()
            print(f"获取到 {len(categories)} 个分类")
            return categories
            
        except Exception as e:
            print(f"获取分类失败: {e}")
            return []
    
    def get_tags(self) -> List[Dict]:
        """获取标签"""
        try:
            url = f"{self.wp_url}/wp-json/wp/v2/tags"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            tags = response.json()
            print(f"获取到 {len(tags)} 个标签")
            return tags
            
        except Exception as e:
            print(f"获取标签失败: {e}")
            return []
    
    def extract_content(self, post: Dict) -> Dict[str, Any]:
        """提取文章内容"""
        import re
        
        def clean_html(text):
            if not text:
                return ""
            # 移除HTML标签
            clean = re.compile('<.*?>')
            return re.sub(clean, '', text)
        
        def extract_images(html_content):
            """提取HTML中的图片URL"""
            if not html_content:
                return []
            
            # 查找img标签中的src属性
            img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
            images = re.findall(img_pattern, html_content)
            
            # 查找背景图片
            bg_pattern = r'background-image:\s*url\(["\']?([^"\']+)["\']?\)'
            bg_images = re.findall(bg_pattern, html_content)
            
            all_images = images + bg_images
            
            # 过滤和清理图片URL
            clean_images = []
            for img_url in all_images:
                if img_url.startswith('http'):
                    clean_images.append(img_url)
                elif img_url.startswith('/'):
                    clean_images.append(f"{self.wp_url}{img_url}")
                elif img_url.startswith('./') or img_url.startswith('../'):
                    clean_images.append(f"{self.wp_url}/{img_url}")
            
            return list(set(clean_images))  # 去重
        
        # 获取原始HTML内容
        raw_content = post.get('content', {}).get('rendered', '')
        raw_excerpt = post.get('excerpt', {}).get('rendered', '')
        
        content = {
            'id': post.get('id'),
            'title': clean_html(post.get('title', {}).get('rendered', '')),
            'content': clean_html(raw_content),
            'excerpt': clean_html(raw_excerpt),
            'raw_content': raw_content,  # 保留原始HTML用于图片提取
            'images': extract_images(raw_content),  # 提取图片
            'date': post.get('date'),
            'modified': post.get('modified'),
            'slug': post.get('slug'),
            'link': post.get('link'),
            'type': post.get('type', 'post'),
            'status': post.get('status'),
            'categories': [],
            'tags': []
        }
        
        # 提取分类
        if '_embedded' in post and 'wp:term' in post['_embedded']:
            for term_group in post['_embedded']['wp:term']:
                for term in term_group:
                    if term.get('taxonomy') == 'category':
                        content['categories'].append({
                            'id': term.get('id'),
                            'name': term.get('name'),
                            'slug': term.get('slug')
                        })
                    elif term.get('taxonomy') == 'post_tag':
                        content['tags'].append({
                            'id': term.get('id'),
                            'name': term.get('name'),
                            'slug': term.get('slug')
                        })
        
        return content
    
    def save_to_rag_storage(self, content_list: List[Dict], output_dir: str = "./rag_storage"):
        """保存内容到RAG存储"""
        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 保存为JSON文件
            output_file = os.path.join(output_dir, f"wordpress_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(content_list, f, ensure_ascii=False, indent=2)
            
            print(f"内容已保存到: {output_file}")
            
            # 同时保存到RAG-Anything格式
            self.save_for_rag_anything(content_list, output_dir)
            
        except Exception as e:
            print(f"保存内容失败: {e}")
    
    def save_for_rag_anything(self, content_list: List[Dict], output_dir: str):
        """保存为RAG-Anything可处理的格式"""
        try:
            # 创建文档内容摘要
            doc_content = []
            
            for item in content_list:
                # 构建包含图片信息的文本
                images_text = ""
                if item.get('images'):
                    images_text = f"\n\n图片: {', '.join(item['images'])}\n"
                
                doc_item = {
                    'type': 'text',
                    'text': f"标题: {item['title']}\n\n内容: {item['content']}\n\n摘要: {item['excerpt']}\n\n链接: {item['link']}\n\n分类: {', '.join([cat['name'] for cat in item['categories']])}\n\n标签: {', '.join([tag['name'] for tag in item['tags']])}\n\n发布时间: {item['date']}\n\n修改时间: {item['modified']}{images_text}\n---\n\n"
                }
                doc_content.append(doc_item)
                
                # 如果有图片，为每个图片创建单独的条目
                for img_url in item.get('images', []):
                    img_item = {
                        'type': 'image',
                        'img_path': img_url,
                        'text': f"图片来自文章: {item['title']}\n链接: {item['link']}\n图片URL: {img_url}"
                    }
                    doc_content.append(img_item)
            
            # 保存为RAG-Anything可处理的格式
            rag_file = os.path.join(output_dir, "wordpress_rag_content.json")
            with open(rag_file, 'w', encoding='utf-8') as f:
                json.dump(doc_content, f, ensure_ascii=False, indent=2)
            
            print(f"RAG格式内容已保存到: {rag_file}")
            
        except Exception as e:
            print(f"保存RAG格式失败: {e}")
    
    def sync_all_content(self, output_dir: str = "./rag_storage"):
        """同步所有WordPress内容"""
        print(f"开始同步WordPress网站: {self.wp_url}")
        
        all_content = []
        
        # 获取所有文章
        page = 1
        while True:
            posts = self.get_posts(per_page=100, page=page)
            if not posts:
                break
            
            for post in posts:
                content = self.extract_content(post)
                all_content.append(content)
            
            page += 1
            if len(posts) < 100:  # 如果返回的文章少于100篇，说明已经到最后一页
                break
        
        # 获取所有页面
        page = 1
        while True:
            pages = self.get_pages(per_page=100, page=page)
            if not pages:
                break
            
            for page_item in pages:
                content = self.extract_content(page_item)
                all_content.append(content)
            
            page += 1
            if len(pages) < 100:
                break
        
        print(f"总共获取到 {len(all_content)} 个内容项")
        
        # 保存内容
        if all_content:
            self.save_to_rag_storage(all_content, output_dir)
        
        return all_content

def main():
    """主函数"""
    # 配置你的WordPress网站
    wp_url = "https://www.shjingjun.com"
    wp_username = os.getenv("WP_USERNAME")  # 可选
    wp_password = os.getenv("WP_PASSWORD")  # 可选
    
    # 创建集成实例
    wp_integration = WordPressRAGIntegration(wp_url, wp_username, wp_password)
    
    # 同步所有内容
    content = wp_integration.sync_all_content()
    
    print(f"同步完成！共获取 {len(content)} 个内容项")

if __name__ == "__main__":
    main()
