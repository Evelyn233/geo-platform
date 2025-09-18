#!/usr/bin/env python3
"""
调试封面图片设置问题
"""

import requests
import json
import time

def debug_cover_image():
    """调试封面图片设置"""
    print("=" * 80)
    print("🔍 调试封面图片设置问题")
    print("=" * 80)
    
    # 后端API配置 - 尝试多个端口
    possible_ports = [8000, 8001, 8002, 8080]
    api_base = None
    
    for port in possible_ports:
        try:
            test_url = f"http://localhost:{port}/api/status"
            test_response = requests.get(test_url, timeout=2)
            if test_response.status_code == 200:
                api_base = f"http://localhost:{port}"
                print(f"   ✅ 找到后端服务在端口 {port}")
                break
        except:
            continue
    
    if not api_base:
        print("   ❌ 未找到运行中的后端服务")
        print("   请确保后端服务正在运行：")
        print("   uvicorn geo_app:app --host 0.0.0.0 --port 8000")
        return
    
    try:
        print("1. 检查后端服务...")
        status_response = requests.get(f"{api_base}/api/status", timeout=5)
        if status_response.status_code == 200:
            print("   ✅ 后端服务正常")
        else:
            print(f"   ❌ 后端服务异常: {status_response.status_code}")
            return
        
        print("\n2. 生成文章并检查封面图片...")
        
        # 调用文章生成API - 使用Form数据
        generate_data = {
            "wp_url": "https://www.shjingjun.com",
            "wp_username": "jingjun2020", 
            "wp_password": "shjingjun20201919.",
            "max_articles": 1,
            "enhanced": True,
            "model": "doubao-seed-1-6-flash"
        }
        
        print("   正在生成文章...")
        response = requests.post(
            f"{api_base}/api/generate_articles",
            data=generate_data,  # 使用data而不是json
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
                    
                    # 详细检查封面图片
                    featured_image = article.get('featured_image')
                    if featured_image:
                        print(f"\n   🎯 封面图片详细信息:")
                        print(f"      标题: {featured_image['title']}")
                        print(f"      来源: {featured_image['source']}")
                        print(f"      质量评分: {featured_image.get('quality_score', 0):.2f}")
                        print(f"      URL: {featured_image['url']}")
                        
                        # 测试图片URL是否可访问
                        test_image_accessibility(featured_image['url'])
                        
                        # 测试WordPress发布
                        print(f"\n3. 测试WordPress发布（调试模式）...")
                        test_wordpress_publish_debug(article)
                        
                    else:
                        print(f"   ❌ 未找到封面图片")
                        
                        # 检查所有图片
                        images = article.get('images', [])
                        if images:
                            print(f"   📸 找到 {len(images)} 张图片，但没有选择封面图片")
                            for i, img in enumerate(images):
                                print(f"      {i+1}. {img['title']} (来源: {img['source']})")
                        else:
                            print(f"   ❌ 未找到任何图片")
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
        print(f"❌ 调试过程出错: {str(e)}")
        import traceback
        traceback.print_exc()

def test_image_accessibility(url):
    """测试图片URL是否可访问"""
    try:
        print(f"   🔍 测试图片可访问性...")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            content_length = len(response.content)
            content_type = response.headers.get('content-type', '')
            print(f"      ✅ 图片可访问")
            print(f"      大小: {content_length} bytes")
            print(f"      类型: {content_type}")
            
            if content_length < 1000:
                print(f"      ⚠️ 图片文件太小，可能无效")
            else:
                print(f"      ✅ 图片大小正常")
        else:
            print(f"      ❌ 图片不可访问: {response.status_code}")
    except Exception as e:
        print(f"      ❌ 测试图片访问失败: {e}")

def test_wordpress_publish_debug(article):
    """测试WordPress发布（调试模式）"""
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
        
        # 检查封面图片数据
        featured_image = article.get("featured_image")
        if featured_image:
            print(f"\n   🖼️ 封面图片数据:")
            print(f"      完整数据: {json.dumps(featured_image, ensure_ascii=False, indent=2)}")
            
            # 提取URL
            cover_url = featured_image.get("url")
            if cover_url:
                print(f"      提取的URL: {cover_url}")
                publish_data["featured_image"] = featured_image
                print(f"      ✅ 封面图片数据已添加到发布数据")
            else:
                print(f"      ❌ 封面图片数据中没有URL字段")
        else:
            print(f"   ❌ 文章数据中没有封面图片")
        
        print(f"\n   📝 发布数据预览:")
        print(f"      标题: {publish_data['title']}")
        print(f"      内容长度: {len(publish_data['content'])} 字符")
        print(f"      分类: {publish_data['category_name']}")
        if 'featured_image' in publish_data:
            print(f"      封面图片: {publish_data['featured_image']['title']}")
        else:
            print(f"      封面图片: 无")
        
        print(f"\n   💡 调试建议:")
        print(f"   1. 检查封面图片URL是否有效")
        print(f"   2. 检查WordPress上传权限")
        print(f"   3. 检查图片格式是否支持")
        print(f"   4. 查看后端日志了解详细错误")
        
    except Exception as e:
        print(f"   ❌ 准备发布数据失败: {e}")

def test_direct_image_search_debug():
    """直接测试图片搜索（调试模式）"""
    print("\n" + "=" * 80)
    print("🔍 直接测试图片搜索（调试模式）")
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
                print(f"     完整数据: {json.dumps(img, ensure_ascii=False, indent=2)}")
                
                # 测试图片可访问性
                test_image_accessibility(img['url'])
            
            # 测试封面图片选择
            print(f"\n🎯 测试封面图片选择:")
            featured_image = searcher.get_best_image_for_featured(images)
            if featured_image:
                print(f"   选择的封面图片:")
                print(f"   完整数据: {json.dumps(featured_image, ensure_ascii=False, indent=2)}")
                
                # 测试图片可访问性
                test_image_accessibility(featured_image['url'])
            else:
                print(f"   ❌ 未选择封面图片")
        else:
            print("❌ 未找到任何图片")
            
    except Exception as e:
        print(f"❌ 直接测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("选择调试模式:")
    print("1. 完整调试（需要后端运行）")
    print("2. 直接图片搜索调试")
    print("3. 全部调试")
    
    choice = input("请输入选择 (1/2/3): ").strip()
    
    if choice == "1":
        debug_cover_image()
    elif choice == "2":
        test_direct_image_search_debug()
    elif choice == "3":
        debug_cover_image()
        test_direct_image_search_debug()
    else:
        print("无效选择，运行完整调试...")
        debug_cover_image()
        test_direct_image_search_debug()
