#!/usr/bin/env python3
"""
测试封面图片功能
"""

import requests
import json
import time

def test_cover_image_functionality():
    """测试封面图片功能"""
    print("=" * 80)
    print("🖼️ 测试封面图片功能")
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
        
        print("\n2. 测试文章生成（包含封面图片）...")
        
        # 调用文章生成API
        generate_data = {
            "max_articles": 1,
            "enhanced": True,
            "model": "doubao-seed-1-6-flash"
        }
        
        print("   正在生成包含封面图片的文章...")
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
                    
                    # 检查封面图片
                    featured_image = article.get('featured_image')
                    if featured_image:
                        print(f"\n   🎯 封面图片信息:")
                        print(f"      标题: {featured_image['title']}")
                        print(f"      来源: {featured_image['source']}")
                        print(f"      质量评分: {featured_image.get('quality_score', 0):.2f}")
                        print(f"      URL: {featured_image['url']}")
                        
                        # 验证封面图片URL
                        if _is_valid_image_url(featured_image['url']):
                            print(f"      ✅ 封面图片URL有效")
                        else:
                            print(f"      ❌ 封面图片URL无效")
                    else:
                        print(f"   ⚠️ 未找到封面图片")
                    
                    # 检查所有图片
                    images = article.get('images', [])
                    if images:
                        print(f"\n   🖼️ 所有图片信息 ({len(images)} 张):")
                        for i, img in enumerate(images):
                            print(f"      {i+1}. {img['title']}")
                            print(f"         来源: {img['source']}")
                            print(f"         质量评分: {img.get('quality_score', 0):.2f}")
                            print(f"         URL: {img['url'][:80]}...")
                            
                            # 检查图片有效性
                            if _is_valid_image_url(img['url']):
                                print(f"         ✅ 图片URL有效")
                            else:
                                print(f"         ❌ 图片URL无效")
                    else:
                        print(f"   ⚠️ 未找到任何图片")
                    
                    # 测试WordPress发布
                    print(f"\n3. 测试WordPress发布（包含封面图片）...")
                    test_wordpress_publish_with_cover(article)
                    
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

def test_wordpress_publish_with_cover(article):
    """测试WordPress发布（包含封面图片）"""
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
            featured_image = article["featured_image"]
            publish_data["featured_image"] = featured_image
            print(f"   🖼️ 将使用封面图片:")
            print(f"      标题: {featured_image['title']}")
            print(f"      来源: {featured_image['source']}")
            print(f"      质量评分: {featured_image.get('quality_score', 0):.2f}")
            print(f"      URL: {featured_image['url']}")
            
            # 验证封面图片
            if _is_valid_image_url(featured_image['url']):
                print(f"      ✅ 封面图片URL验证通过")
            else:
                print(f"      ❌ 封面图片URL验证失败")
        else:
            print(f"   ⚠️ 没有封面图片")
        
        print("   💡 提示：可以在前端界面中点击'🚀 发布到WordPress'按钮进行发布测试")
        print("   📝 发布数据已准备就绪")
        
    except Exception as e:
        print(f"   ❌ 准备发布数据失败: {e}")

def _is_valid_image_url(url: str) -> bool:
    """检查图片URL是否有效"""
    try:
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
        
        # 检查是否是真实图片服务
        trusted_domains = [
            'googleusercontent.com', 'gstatic.com',
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

def test_direct_image_search():
    """直接测试图片搜索功能"""
    print("\n" + "=" * 80)
    print("🔍 直接测试图片搜索功能")
    print("=" * 80)
    
    try:
        from image_search import ImageSearcher
        
        searcher = ImageSearcher()
        keyword = "抛光风布轮厂家"
        
        print(f"搜索关键词: {keyword}")
        images = searcher.search_images(keyword, max_results=3)
        
        if images:
            print(f"✅ 找到 {len(images)} 张图片:")
            for i, img in enumerate(images):
                print(f"\n  📸 图片 {i+1}:")
                print(f"     标题: {img['title']}")
                print(f"     来源: {img['source']}")
                print(f"     质量评分: {img.get('quality_score', 0):.2f}")
                print(f"     URL: {img['url'][:80]}...")
                
                # 检查图片有效性
                if _is_valid_image_url(img['url']):
                    print(f"     ✅ 图片URL有效")
                else:
                    print(f"     ❌ 图片URL无效")
            
            # 测试封面图片选择
            print(f"\n🎯 测试封面图片选择:")
            featured_image = searcher.get_best_image_for_featured(images)
            if featured_image:
                print(f"   选择的封面图片: {featured_image['title']}")
                print(f"   来源: {featured_image['source']}")
                print(f"   质量评分: {featured_image.get('quality_score', 0):.2f}")
                print(f"   URL: {featured_image['url']}")
                
                if _is_valid_image_url(featured_image['url']):
                    print(f"   ✅ 封面图片URL有效")
                else:
                    print(f"   ❌ 封面图片URL无效")
            else:
                print(f"   ❌ 未选择封面图片")
        else:
            print("❌ 未找到任何图片")
            
    except Exception as e:
        print(f"❌ 直接测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("选择测试模式:")
    print("1. 完整封面图片测试（需要后端运行）")
    print("2. 直接图片搜索测试")
    print("3. 全部测试")
    
    choice = input("请输入选择 (1/2/3): ").strip()
    
    if choice == "1":
        test_cover_image_functionality()
    elif choice == "2":
        test_direct_image_search()
    elif choice == "3":
        test_cover_image_functionality()
        test_direct_image_search()
    else:
        print("无效选择，运行完整测试...")
        test_cover_image_functionality()
        test_direct_image_search()

