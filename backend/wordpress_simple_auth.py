#!/usr/bin/env python3
"""
简化的WordPress认证方案
直接使用应用密码，避免会话登录问题
"""

import requests
import base64
import json
from typing import Dict, List, Optional

class SimpleWordPressAuth:
    """简化的WordPress认证类"""
    
    def __init__(self, wp_url: str, username: str, password: str):
        self.wp_url = wp_url.rstrip('/')
        self.username = username
        self.password = password  # 这里应该是应用密码
        self.api_url = f"{self.wp_url}/wp-json/wp/v2"
        
        # 设置认证头
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        self.headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json',
            'User-Agent': 'GEO-System/1.0'
        }
    
    def test_connection(self) -> Dict:
        """测试WordPress连接"""
        try:
            # 测试基本连接
            response = requests.get(f"{self.api_url}/users/me", headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "success": True,
                    "message": "WordPress连接成功！",
                    "user": user_data.get("name", "未知用户"),
                    "user_id": user_data.get("id", 0)
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "message": "认证失败：用户名或密码错误，请检查应用密码是否正确"
                }
            else:
                return {
                    "success": False,
                    "message": f"连接失败：HTTP {response.status_code} - {response.text[:200]}"
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "message": "无法连接到WordPress，请检查URL是否正确"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"连接测试失败：{str(e)}"
            }
    
    def get_categories(self) -> List[Dict]:
        """获取WordPress分类"""
        try:
            response = requests.get(f"{self.api_url}/categories", headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"获取分类失败：{response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"获取分类异常：{e}")
            return []
    
    def create_category(self, name: str) -> Dict:
        """创建分类"""
        try:
            data = {"name": name}
            response = requests.post(f"{self.api_url}/categories", headers=self.headers, json=data, timeout=10)
            
            if response.status_code == 201:
                return {
                    "success": True,
                    "category": response.json(),
                    "message": f"分类 '{name}' 创建成功"
                }
            else:
                return {
                    "success": False,
                    "message": f"创建分类失败：{response.status_code} - {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"创建分类异常：{str(e)}"
            }
    
    def publish_article(self, title: str, content: str, category_id: int = None, status: str = "publish", featured_media_url: str = None) -> Dict:
        """发布文章"""
        try:
            data = {
                "title": title,
                "content": content,
                "status": status
            }
            
            if category_id:
                data["categories"] = [category_id]
            
            # 如果有封面图片URL，先上传图片
            if featured_media_url:
                try:
                    print(f"开始上传封面图片: {featured_media_url}")
                    media_id = self.upload_image_from_url(featured_media_url, title)
                    if media_id:
                        data["featured_media"] = media_id
                        print(f"✅ 已设置封面图片，媒体ID: {media_id}")
                    else:
                        print(f"❌ 封面图片上传失败，媒体ID为空")
                except Exception as e:
                    print(f"❌ 上传封面图片异常: {e}")
                    # 继续发布文章，只是没有封面图片
            else:
                print("⚠️ 没有提供封面图片URL")
            
            print(f"📝 发布文章数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            response = requests.post(f"{self.api_url}/posts", headers=self.headers, json=data, timeout=30)
            
            if response.status_code == 201:
                post_data = response.json()
                print(f"✅ 文章发布成功，ID: {post_data['id']}")
                
                # 如果设置了封面图片，验证是否成功
                if "featured_media" in data:
                    print(f"🔍 验证封面图片设置...")
                    # 获取文章详情来验证封面图片
                    post_detail_response = requests.get(f"{self.api_url}/posts/{post_data['id']}", headers=self.headers)
                    if post_detail_response.status_code == 200:
                        post_detail = post_detail_response.json()
                        featured_media_id = post_detail.get('featured_media')
                        if featured_media_id:
                            print(f"✅ 封面图片设置成功，媒体ID: {featured_media_id}")
                        else:
                            print(f"❌ 封面图片设置失败")
                
                return {
                    "success": True,
                    "post_id": post_data["id"],
                    "post_url": post_data["link"],
                    "message": "文章发布成功"
                }
            else:
                print(f"❌ 文章发布失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return {
                    "success": False,
                    "message": f"发布失败：{response.status_code} - {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"发布异常：{str(e)}"
            }
    
    def upload_image_from_url(self, image_url: str, title: str) -> int:
        """从URL上传图片到WordPress媒体库"""
        try:
            print(f"正在上传封面图片: {title}")
            print(f"图片URL: {image_url}")
            
            # 下载图片
            response = requests.get(image_url, timeout=30)
            if response.status_code != 200:
                raise Exception(f"无法下载图片: {response.status_code}")
            
            # 检查图片大小
            content_length = len(response.content)
            if content_length < 1000:  # 小于1KB可能是无效图片
                raise Exception(f"图片文件太小: {content_length} bytes")
            
            # 获取文件扩展名
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = 'jpg'
            elif 'png' in content_type:
                ext = 'png'
            elif 'gif' in content_type:
                ext = 'gif'
            elif 'webp' in content_type:
                ext = 'webp'
            else:
                ext = 'jpg'  # 默认
            
            # 清理标题，移除特殊字符
            clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{clean_title[:50]}.{ext}"
            
            # 准备上传数据
            files = {
                'file': (filename, response.content, content_type)
            }
            
            data = {
                'title': title,
                'alt_text': title,
                'caption': f"封面图片 - {title}"
            }
            
            print(f"上传文件: {filename} ({content_length} bytes)")
            
            # 上传到WordPress
            upload_response = requests.post(
                f"{self.api_url}/media",
                headers=self.headers,
                files=files,
                data=data,
                timeout=30
            )
            
            if upload_response.status_code == 201:
                media_data = upload_response.json()
                print(f"✅ 图片上传成功，媒体ID: {media_data['id']}")
                return media_data['id']
            else:
                print(f"❌ 图片上传失败: {upload_response.status_code}")
                print(f"响应内容: {upload_response.text}")
                raise Exception(f"上传失败: {upload_response.status_code} - {upload_response.text}")
                
        except Exception as e:
            print(f"❌ 图片上传异常: {e}")
            return None
    
    def get_published_articles(self, category_id: Optional[int] = None) -> List[Dict]:
        """获取已发布的文章"""
        try:
            params = {"status": "publish"}
            if category_id:
                params["categories"] = category_id
            
            response = requests.get(f"{self.api_url}/posts", headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"获取文章失败：{response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"获取文章异常：{e}")
            return []

def test_simple_auth():
    """测试简化认证"""
    print("=" * 60)
    print("🔐 简化WordPress认证测试")
    print("=" * 60)
    
    # 使用你的WordPress信息
    wp_url = "https://www.shjingjun.com"  # 注意：不要包含 /wp-admin/
    username = "jingjun2020"
    password = "shjingjun20201919."  # 这里需要是应用密码
    
    print(f"测试URL: {wp_url}")
    print(f"用户名: {username}")
    print(f"密码: {password[:10]}...")
    
    auth = SimpleWordPressAuth(wp_url, username, password)
    
    # 测试连接
    print("\n1. 测试连接...")
    result = auth.test_connection()
    print(f"   结果: {result['message']}")
    
    if result["success"]:
        print(f"   用户: {result.get('user', '未知')}")
        print(f"   用户ID: {result.get('user_id', 0)}")
        
        # 测试获取分类
        print("\n2. 获取分类...")
        categories = auth.get_categories()
        print(f"   找到 {len(categories)} 个分类")
        for cat in categories[:5]:  # 只显示前5个
            print(f"   - {cat['name']} (ID: {cat['id']})")
        
        # 测试发布文章
        print("\n3. 测试发布文章...")
        test_article = {
            "title": "GEO系统测试文章",
            "content": "<p>这是通过GEO系统自动发布的测试文章。</p><p>如果您看到这篇文章，说明自动发布功能正常工作！</p>"
        }
        
        publish_result = auth.publish_article(test_article["title"], test_article["content"])
        print(f"   结果: {publish_result['message']}")
        
        if publish_result["success"]:
            print(f"   文章ID: {publish_result['post_id']}")
            print(f"   文章链接: {publish_result['post_url']}")
    else:
        print("\n❌ 连接失败，可能的原因：")
        print("1. 密码不是应用密码（需要创建应用密码）")
        print("2. WordPress REST API未启用")
        print("3. 安全插件阻止了API访问")
        print("4. 用户名或密码错误")
        
        print("\n💡 解决方案：")
        print("1. 登录 https://www.shjingjun.com/wp-admin/")
        print("2. 进入 用户 → 个人资料")
        print("3. 找到'应用密码'部分")
        print("4. 创建名为'GEO系统'的应用密码")
        print("5. 复制生成的密码（不是登录密码）")

if __name__ == "__main__":
    test_simple_auth()
