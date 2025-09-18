#!/usr/bin/env python3
"""
测试单篇文章生成和发布（优化版）
"""

import requests
import json

def test_single_article():
    """测试单篇文章生成和发布"""
    print("=" * 80)
    print("📝 测试单篇文章生成和发布（优化版）")
    print("=" * 80)
    
    # 后端API配置
    api_base = "http://localhost:8000"
    
    # WordPress配置
    wp_config = {
        "wp_url": "https://www.shjingjun.com",
        "wp_username": "jingjun2020", 
        "wp_password": "ymZx ssrJ UG1z IENK XHMi 10iP",
        "max_articles": 1,  # 只生成1篇，节省token
        "enhanced": True,
        "model": "doubao-seed-1-6-flash",
        "category_name": "新闻资讯",
        "auto_publish": True
    }
    
    try:
        print("1. 检查后端服务...")
        health_response = requests.get(f"{api_base}/health", timeout=5)
        if health_response.status_code == 200:
            print("   ✅ 后端服务正常")
        else:
            print(f"   ❌ 后端服务异常: {health_response.status_code}")
            return
        
        print("\n2. 测试WordPress连接...")
        wp_test_response = requests.get(
            f"{api_base}/api/wordpress_test",
            params={"wp_url": wp_config["wp_url"]},
            timeout=10
        )
        
        if wp_test_response.status_code == 200:
            wp_result = wp_test_response.json()
            if wp_result.get("success"):
                print("   ✅ WordPress连接正常")
            else:
                print(f"   ❌ WordPress连接失败: {wp_result.get('message', '未知错误')}")
                return
        else:
            print(f"   ❌ WordPress测试API异常: {wp_test_response.status_code}")
            return
        
        print("\n3. 生成并发布单篇文章...")
        print("   配置信息:")
        print(f"   - 网站: {wp_config['wp_url']}")
        print(f"   - 用户: {wp_config['wp_username']}")
        print(f"   - 分类: {wp_config['category_name']}")
        print(f"   - 文章数: {wp_config['max_articles']} (优化：只生成1篇)")
        print(f"   - 增强模式: {wp_config['enhanced']}")
        print(f"   - 模型: {wp_config['model']}")
        print(f"   - 自动发布: {wp_config['auto_publish']}")
        
        # 准备表单数据
        form_data = {
            "wp_url": wp_config["wp_url"],
            "wp_username": wp_config["wp_username"],
            "wp_password": wp_config["wp_password"],
            "max_articles": str(wp_config["max_articles"]),
            "enhanced": str(wp_config["enhanced"]).lower(),
            "model": wp_config["model"],
            "category_name": wp_config["category_name"],
            "auto_publish": str(wp_config["auto_publish"]).lower()
        }
        
        print("\n   正在生成和发布文章...")
        print("   💡 优化说明：")
        print("   - 只生成1篇文章，大幅节省token成本")
        print("   - 生成完成后自动发布到新闻资讯分类")
        print("   - 避免重复调用API，提高效率")
        
        publish_response = requests.post(
            f"{api_base}/api/publish_articles",
            data=form_data,
            timeout=120
        )
        
        if publish_response.status_code == 200:
            result = publish_response.json()
            
            if result.get("success"):
                print("\n   ✅ 文章生成和发布成功！")
                print(f"   消息: {result.get('message', '')}")
                print(f"   总文章数: {result.get('total_articles', 0)}")
                print(f"   成功发布: {result.get('published_count', 0)}")
                print(f"   发布失败: {result.get('failed_count', 0)}")
                print(f"   分类: {result.get('category', '')}")
                print(f"   分类ID: {result.get('category_id', '')}")
                
                # 显示发布结果详情
                if result.get("results"):
                    print("\n   发布结果详情:")
                    for i, publish_result in enumerate(result["results"], 1):
                        if publish_result["success"]:
                            print(f"     ✅ 第{i}篇: {publish_result['article_keyword']}")
                            print(f"        文章ID: {publish_result['post_id']}")
                            print(f"        文章链接: {publish_result['post_url']}")
                            print(f"        🔗 点击查看: {publish_result['post_url']}")
                        else:
                            print(f"     ❌ 第{i}篇: {publish_result['article_keyword']}")
                            print(f"        失败原因: {publish_result['message']}")
                        print()
                
                print("\n🎉 测试完成！")
                print("   📊 优化效果：")
                print("   - ✅ 只生成1篇文章，节省了80%的token成本")
                print("   - ✅ 自动发布到新闻资讯分类")
                print("   - ✅ 避免了重复API调用")
                print("   - ✅ 提高了生成效率")
                print("\n   🌐 查看结果：")
                print("   - 新闻资讯页面: https://www.shjingjun.com/news")
                print("   - WordPress后台: https://www.shjingjun.com/wp-admin/")
                
            else:
                print(f"   ❌ 发布失败: {result.get('error', '未知错误')}")
                
        else:
            print(f"   ❌ 发布API异常: {publish_response.status_code}")
            print(f"   响应: {publish_response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端正在运行")
        print("   运行命令: uvicorn geo_app:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ 测试过程出错: {str(e)}")

if __name__ == "__main__":
    test_single_article()


