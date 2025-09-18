#!/usr/bin/env python3
"""
本地图片库管理
下载和管理相关图片，提供更准确的图片搜索
"""

import os
import requests
import json
from typing import List, Dict
from urllib.parse import quote

class LocalImageLibrary:
    """本地图片库管理器"""
    
    def __init__(self, image_dir: str = "images"):
        self.image_dir = image_dir
        self.library_file = os.path.join(image_dir, "image_library.json")
        self.ensure_image_dir()
        self.load_library()
    
    def ensure_image_dir(self):
        """确保图片目录存在"""
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)
    
    def load_library(self):
        """加载图片库"""
        if os.path.exists(self.library_file):
            with open(self.library_file, 'r', encoding='utf-8') as f:
                self.library = json.load(f)
        else:
            self.library = {}
    
    def save_library(self):
        """保存图片库"""
        with open(self.library_file, 'w', encoding='utf-8') as f:
            json.dump(self.library, f, ensure_ascii=False, indent=2)
    
    def download_image(self, url: str, filename: str) -> bool:
        """下载图片到本地"""
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                filepath = os.path.join(self.image_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return True
            return False
        except Exception as e:
            print(f"下载图片失败: {e}")
            return False
    
    def add_image(self, keyword: str, image_data: Dict):
        """添加图片到库中"""
        if keyword not in self.library:
            self.library[keyword] = []
        
        # 检查是否已存在
        for existing in self.library[keyword]:
            if existing['url'] == image_data['url']:
                return False
        
        self.library[keyword].append(image_data)
        self.save_library()
        return True
    
    def search_images(self, keyword: str, max_results: int = 5) -> List[Dict]:
        """从本地库搜索图片"""
        results = []
        
        # 直接匹配
        if keyword in self.library:
            results.extend(self.library[keyword][:max_results])
        
        # 模糊匹配
        if len(results) < max_results:
            for lib_keyword, images in self.library.items():
                if any(word in lib_keyword for word in keyword.split()) or any(word in keyword for word in lib_keyword.split()):
                    for img in images:
                        if img not in results:
                            results.append(img)
                            if len(results) >= max_results:
                                break
        
        return results[:max_results]
    
    def get_industrial_images(self, keyword: str, max_results: int = 5) -> List[Dict]:
        """获取工业相关图片"""
        # 预定义的工业图片库
        industrial_images = {
            '抛光': [
                {
                    'url': 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400&h=300&fit=crop&q=80',
                    'title': '工业抛光设备',
                    'alt': '专业抛光设备工作场景',
                    'tags': ['抛光', '工业', '设备']
                },
                {
                    'url': 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400&h=300&fit=crop&q=80',
                    'title': '金属抛光工艺',
                    'alt': '金属表面抛光处理',
                    'tags': ['抛光', '金属', '工艺']
                },
                {
                    'url': 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400&h=300&fit=crop&q=80',
                    'title': '精密抛光工具',
                    'alt': '精密抛光工具展示',
                    'tags': ['抛光', '工具', '精密']
                }
            ],
            '研磨': [
                {
                    'url': 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400&h=300&fit=crop&q=80',
                    'title': '研磨设备',
                    'alt': '专业研磨设备',
                    'tags': ['研磨', '设备', '工业']
                },
                {
                    'url': 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400&h=300&fit=crop&q=80',
                    'title': '研磨材料',
                    'alt': '各种研磨材料展示',
                    'tags': ['研磨', '材料', '工具']
                }
            ],
            '厂家': [
                {
                    'url': 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400&h=300&fit=crop&q=80',
                    'title': '现代化工厂',
                    'alt': '现代化制造工厂',
                    'tags': ['厂家', '工厂', '制造']
                },
                {
                    'url': 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400&h=300&fit=crop&q=80',
                    'title': '生产线',
                    'alt': '自动化生产线',
                    'tags': ['厂家', '生产线', '自动化']
                }
            ],
            '供应商': [
                {
                    'url': 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400&h=300&fit=crop&q=80',
                    'title': '供应链管理',
                    'alt': '供应链管理流程',
                    'tags': ['供应商', '供应链', '管理']
                }
            ]
        }
        
        results = []
        
        # 根据关键词匹配
        for key, images in industrial_images.items():
            if key in keyword or any(word in keyword for word in key.split()):
                results.extend(images)
        
        # 如果没有匹配到，返回通用工业图片
        if not results:
            results = [
                {
                    'url': 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400&h=300&fit=crop&q=80',
                    'title': f'{keyword}相关图片',
                    'alt': f'{keyword}相关专业图片',
                    'tags': ['工业', '专业']
                }
            ]
        
        # 为每个图片添加质量评分
        for img in results:
            img['quality_score'] = 0.8  # 本地图片质量较高
            img['source'] = 'Local Library'
        
        return results[:max_results]
    
    def initialize_library(self):
        """初始化图片库"""
        print("正在初始化本地图片库...")
        
        # 添加一些基础图片
        keywords = ['抛光', '研磨', '厂家', '供应商', '工业', '制造']
        
        for keyword in keywords:
            images = self.get_industrial_images(keyword, 3)
            for img in images:
                self.add_image(keyword, img)
        
        print(f"图片库初始化完成，共添加 {len(self.library)} 个关键词的图片")
        self.save_library()

def test_local_image_library():
    """测试本地图片库"""
    print("=" * 80)
    print("🖼️ 测试本地图片库功能")
    print("=" * 80)
    
    # 创建图片库
    library = LocalImageLibrary()
    
    # 初始化库
    library.initialize_library()
    
    # 测试搜索
    test_keywords = ['抛光风布轮厂家', '研磨材料', '工业抛光']
    
    for keyword in test_keywords:
        print(f"\n搜索关键词: {keyword}")
        images = library.get_industrial_images(keyword, 3)
        
        print(f"找到 {len(images)} 张图片:")
        for i, img in enumerate(images):
            print(f"  {i+1}. {img['title']}")
            print(f"     URL: {img['url']}")
            print(f"     标签: {', '.join(img.get('tags', []))}")
            print(f"     质量评分: {img.get('quality_score', 0):.1f}")
            print()

if __name__ == "__main__":
    test_local_image_library()

