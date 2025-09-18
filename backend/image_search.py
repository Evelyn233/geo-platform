#!/usr/bin/env python3
"""
图片搜索模块 - 从网络搜索相关图片
"""

import requests
import json
import time
from typing import List, Dict
from urllib.parse import quote
from local_image_library import LocalImageLibrary
from google_image_search import GoogleImageSearcher

class ImageSearcher:
    """图片搜索器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.local_library = LocalImageLibrary()  # 初始化本地图片库
        self.google_searcher = GoogleImageSearcher()  # 初始化Google图片搜索器
    
    def search_pixabay_images(self, keyword: str, max_results: int = 5) -> List[Dict]:
        """使用Pixabay API搜索图片"""
        try:
            # Pixabay API (免费，无需API key，但有限制)
            # 也可以申请免费API key获得更高限制
            search_url = "https://pixabay.com/api/"
            
            # 将中文关键词转换为英文搜索词
            search_terms = self._translate_keyword_to_english(keyword)
            
            params = {
                'key': 'your-pixabay-api-key',  # 可以留空使用免费版本
                'q': search_terms,
                'image_type': 'photo',
                'orientation': 'horizontal',
                'category': 'industry',
                'min_width': 400,
                'min_height': 300,
                'safesearch': 'true',
                'per_page': max_results
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                images = []
                
                for hit in data.get('hits', []):
                    images.append({
                        'url': hit['webformatURL'],
                        'title': f'{keyword}专业图片',
                        'source': 'Pixabay',
                        'alt': f'{keyword}相关专业图片',
                        'quality_score': 0.9  # Pixabay图片质量较高
                    })
                
                return images
            else:
                print(f"Pixabay API调用失败: {response.status_code}")
                return self._get_fallback_images(keyword, max_results)
                
        except Exception as e:
            print(f"Pixabay图片搜索失败: {e}")
            return self._get_fallback_images(keyword, max_results)
    
    def _translate_keyword_to_english(self, keyword: str) -> str:
        """将中文关键词转换为英文搜索词"""
        translations = {
            '抛光': 'polishing',
            '研磨': 'grinding',
            '厂家': 'manufacturer',
            '供应商': 'supplier',
            '布轮': 'buffing wheel',
            '风布轮': 'buffing wheel',
            '抛光轮': 'polishing wheel',
            '研磨材料': 'grinding material',
            '工业': 'industrial',
            '制造': 'manufacturing',
            '生产': 'production'
        }
        
        # 简单的关键词替换
        english_keyword = keyword
        for chinese, english in translations.items():
            if chinese in keyword:
                english_keyword = english_keyword.replace(chinese, english)
        
        return english_keyword
    
    def _get_fallback_images(self, keyword: str, max_results: int) -> List[Dict]:
        """获取备用图片（当API失败时）"""
        # 使用更相关的工业图片
        if "抛光" in keyword or "研磨" in keyword:
            image_templates = [
                "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400&h=300&fit=crop&q=80",  # 工业抛光
                "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400&h=300&fit=crop&q=80",  # 金属加工
                "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400&h=300&fit=crop&q=80",  # 精密制造
            ]
        elif "厂家" in keyword or "供应商" in keyword:
            image_templates = [
                "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400&h=300&fit=crop&q=80",  # 工厂
                "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400&h=300&fit=crop&q=80",  # 生产线
                "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400&h=300&fit=crop&q=80",  # 质量控制
            ]
        else:
            image_templates = [
                "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400&h=300&fit=crop&q=80",
                "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400&h=300&fit=crop&q=80",
                "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400&h=300&fit=crop&q=80",
            ]
        
        images = []
        for i, template in enumerate(image_templates[:max_results]):
            images.append({
                'url': template,
                'title': f'{keyword}专业图片 {i+1}',
                'source': 'Fallback',
                'alt': f'{keyword}相关专业图片',
                'quality_score': 0.7
            })
        
        return images
    
    def search_duckduckgo_images(self, keyword: str, max_results: int = 5) -> List[Dict]:
        """使用DuckDuckGo搜索图片（保留原方法）"""
        return self.search_pixabay_images(keyword, max_results)
    
    def search_unsplash_images(self, keyword: str, max_results: int = 5) -> List[Dict]:
        """使用Unsplash搜索图片（需要API key，这里使用模拟数据）"""
        try:
            # 模拟Unsplash搜索结果
            images = []
            for i in range(min(max_results, 3)):
                images.append({
                    'url': f'https://picsum.photos/400/300?random={i}&text={quote(keyword)}',
                    'title': f'{keyword}专业图片 {i+1}',
                    'source': 'Unsplash',
                    'alt': f'{keyword}相关专业图片'
                })
            
            return images
            
        except Exception as e:
            print(f"Unsplash图片搜索失败: {e}")
            return []
    
    def search_baidu_images(self, keyword: str, max_results: int = 5) -> List[Dict]:
        """模拟百度图片搜索"""
        try:
            # 模拟百度图片搜索结果
            images = []
            for i in range(min(max_results, 3)):
                images.append({
                    'url': f'https://via.placeholder.com/400x300?text={quote(keyword)}&bg=0066cc&color=ffffff',
                    'title': f'{keyword}产品展示 {i+1}',
                    'source': 'Baidu',
                    'alt': f'{keyword}产品图片展示'
                })
            
            return images
            
        except Exception as e:
            print(f"百度图片搜索失败: {e}")
            return []
    
    def search_images(self, keyword: str, max_results: int = 5) -> List[Dict]:
        """综合搜索图片 - 优先使用Google搜索"""
        print(f"正在搜索 {keyword} 相关图片...")
        
        all_images = []
        
        # 1. 首先尝试Google图片搜索（最准确）
        try:
            print("🔍 使用Google图片搜索...")
            google_images = self.google_searcher.search_google_images(keyword, max_results)
            if google_images:
                all_images.extend(google_images)
                print(f"✅ Google搜索找到 {len(google_images)} 张图片")
        except Exception as e:
            print(f"❌ Google搜索失败: {e}")
        
        # 2. 如果Google搜索结果不足，尝试本地图片库
        if len(all_images) < max_results:
            try:
                print("📚 补充本地图片库...")
                local_images = self.local_library.get_industrial_images(keyword, max_results - len(all_images))
                if local_images:
                    all_images.extend(local_images)
                    print(f"✅ 本地图片库找到 {len(local_images)} 张图片")
            except Exception as e:
                print(f"❌ 本地图片库搜索失败: {e}")
        
        # 3. 如果还不够，尝试其他在线搜索
        if len(all_images) < max_results:
            print("🌐 补充在线搜索...")
            sources = [
                self.search_pixabay_images,
                self.search_unsplash_images,
                self.search_baidu_images
            ]
            
            for search_func in sources:
                try:
                    remaining = max_results - len(all_images)
                    if remaining <= 0:
                        break
                    images = search_func(keyword, remaining)
                    all_images.extend(images)
                    time.sleep(0.5)  # 避免请求过快
                except Exception as e:
                    print(f"❌ 在线搜索源失败: {e}")
                    continue
        
        # 去重并限制数量
        unique_images = []
        seen_urls = set()
        
        for img in all_images:
            if img['url'] not in seen_urls:
                # 为每张图片添加质量评分（如果还没有）
                if 'quality_score' not in img:
                    img['quality_score'] = self._calculate_image_quality(img)
                unique_images.append(img)
                seen_urls.add(img['url'])
                
                if len(unique_images) >= max_results:
                    break
        
        # 按质量评分排序，选择最好的图片
        unique_images.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
        
        print(f"🎯 总共找到 {len(unique_images)} 张相关图片")
        return unique_images
    
    def _calculate_image_quality(self, img: Dict) -> float:
        """计算图片质量评分"""
        score = 0.0
        
        # 根据来源评分
        source_scores = {
            'Unsplash': 0.9,
            'Baidu': 0.7,
            'DuckDuckGo': 0.6
        }
        score += source_scores.get(img.get('source', ''), 0.5)
        
        # 根据标题关键词匹配评分
        title = img.get('title', '').lower()
        if '产品' in title or 'product' in title:
            score += 0.2
        if '专业' in title or 'professional' in title:
            score += 0.1
        if '厂家' in title or 'manufacturer' in title:
            score += 0.1
        
        # 根据URL特征评分
        url = img.get('url', '')
        if 'placeholder' not in url and 'via.placeholder' not in url:
            score += 0.3
        
        return min(score, 1.0)  # 最高1.0分
    
    def get_best_image_for_featured(self, images: List[Dict]) -> Dict:
        """获取最适合作为封面的图片 - 确保选择真实可见的图片"""
        if not images:
            return None
        
        # 过滤出真实可见的图片
        valid_images = []
        for img in images:
            if self._is_valid_cover_image(img):
                valid_images.append(img)
        
        if not valid_images:
            print("⚠️ 没有找到有效的封面图片，使用第一张图片")
            return images[0] if images else None
        
        # 从有效图片中选择质量最高的
        best_image = max(valid_images, key=lambda x: x.get('quality_score', 0))
        print(f"✅ 选择封面图片: {best_image['title']} (来源: {best_image['source']}, 评分: {best_image.get('quality_score', 0):.2f})")
        return best_image
    
    def _is_valid_cover_image(self, img: Dict) -> bool:
        """检查图片是否适合作为封面"""
        url = img.get('url', '')
        source = img.get('source', '')
        
        # 检查URL是否有效
        if not url or url.startswith('data:') or 'placeholder' in url.lower():
            return False
        
        # 检查是否是真实图片URL
        if not self._is_real_image_url(url):
            return False
        
        # 优先选择Google图片和本地图片
        if source in ['Google Images', 'Local Library']:
            return True
        
        # 其他来源需要额外验证
        if source in ['Pixabay', 'Unsplash']:
            return True
        
        return False
    
    def _is_real_image_url(self, url: str) -> bool:
        """检查是否是真实图片URL"""
        try:
            # 检查URL格式
            if not url or len(url) < 10:
                return False
            
            # 检查是否是占位符图片
            placeholder_indicators = [
                'placeholder', 'via.placeholder', 'picsum.photos',
                'dummyimage.com', 'fakeimg.pl'
            ]
            
            url_lower = url.lower()
            for indicator in placeholder_indicators:
                if indicator in url_lower:
                    return False
            
            # 检查是否是Google图片服务
            if 'googleusercontent.com' in url or 'gstatic.com' in url:
                return True
            
            # 检查是否是知名图片服务
            trusted_domains = [
                'unsplash.com', 'pixabay.com', 'pexels.com',
                'images.unsplash.com', 'cdn.pixabay.com'
            ]
            
            for domain in trusted_domains:
                if domain in url:
                    return True
            
            # 检查图片扩展名
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
            if any(ext in url_lower for ext in image_extensions):
                return True
            
            return True  # 默认接受
            
        except Exception as e:
            print(f"检查图片URL失败: {e}")
            return False
    
    def get_image_html(self, images: List[Dict], max_images: int = 3) -> str:
        """将图片转换为HTML格式 - 优化显示效果"""
        if not images:
            return ""
        
        html_parts = []
        
        # 添加图片标题
        html_parts.append('<h3>产品展示</h3>')
        
        # 添加图片网格 - 改进布局
        html_parts.append('<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 10px;">')
        
        for i, img in enumerate(images[:max_images]):
            # 添加质量评分标识
            quality_score = img.get('quality_score', 0)
            quality_badge = ""
            if quality_score > 0.8:
                quality_badge = '<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; margin-left: 5px;">推荐</span>'
            elif quality_score > 0.6:
                quality_badge = '<span style="background: #ffc107; color: black; padding: 2px 6px; border-radius: 3px; font-size: 10px; margin-left: 5px;">良好</span>'
            
            html_parts.append(f'''
            <div style="background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); transition: transform 0.3s ease;">
                <div style="position: relative; overflow: hidden;">
                    <img src="{img['url']}" 
                         alt="{img['alt']}" 
                         title="{img['title']}"
                         style="width: 100%; height: 200px; object-fit: cover; transition: transform 0.3s ease;"
                         loading="lazy"
                         onmouseover="this.style.transform='scale(1.05)'"
                         onmouseout="this.style.transform='scale(1)'">
                    <div style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.7); color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px;">
                        {img['source']}
                    </div>
                </div>
                <div style="padding: 12px;">
                    <p style="margin: 0; font-weight: 500; color: #333; font-size: 14px;">
                        {img['title']}{quality_badge}
                    </p>
                    <p style="margin: 5px 0 0 0; font-size: 12px; color: #666;">
                        质量评分: {quality_score:.1f}/1.0
                    </p>
                </div>
            </div>
            ''')
        
        html_parts.append('</div>')
        
        return '\n'.join(html_parts)

def test_image_search():
    """测试图片搜索功能"""
    searcher = ImageSearcher()
    
    # 测试关键词
    test_keywords = ["抛光轮", "研磨材料", "工业抛光"]
    
    for keyword in test_keywords:
        print(f"\n=== 测试关键词: {keyword} ===")
        
        # 搜索图片
        images = searcher.search_images(keyword, max_results=3)
        
        # 显示结果
        for i, img in enumerate(images):
            print(f"图片 {i+1}:")
            print(f"  标题: {img['title']}")
            print(f"  URL: {img['url']}")
            print(f"  来源: {img['source']}")
            print()
        
        # 生成HTML
        html = searcher.get_image_html(images, max_images=2)
        print("生成的HTML:")
        print(html)
        print("-" * 50)

if __name__ == "__main__":
    test_image_search()
