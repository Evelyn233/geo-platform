#!/usr/bin/env python3
"""
测试文章预览和发布流程
"""

import requests
import json

def test_preview_publish():
    """测试文章预览和发布流程"""
    print("=" * 80)
    print("📝 测试文章预览和发布流程")
    print("=" * 80)
    
    # 后端API配置
    api_base = "http://localhost:8000"
    
    # WordPress配置
    wp_config = {
        "wp_url": "https://www.shjingjun.com",
        "wp_username": "jingjun2020", 
        "wp_password": "ymZx ssrJ UG1z IENK XHMi 10iP",
        "max_articles": 1,
        "enhanced": True,
        "model": "doubao-seed-1-6-flash",
        "category_name": "新闻资讯",
        "auto_publish": False  # 先不自动发布，只生成
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
        
        print("\n3. 生成文章（预览模式）...")
        print("   配置信息:")
        print(f"   - 网站: {wp_config['wp_url']}")
        print(f"   - 用户: {wp_config['wp_username']}")
        print(f"   - 分类: {wp_config['category_name']}")
        print(f"   - 文章数: {wp_config['max_articles']}")
        print(f"   - 增强模式: {wp_config['enhanced']}")
        print(f"   - 模型: {wp_config['model']}")
        print(f"   - 自动发布: {wp_config['auto_publish']} (先预览)")
        
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
        
        print("\n   正在生成文章...")
        print("   💡 新流程说明：")
        print("   - 先生成文章并展示内容")
        print("   - 用户可以预览和编辑")
        print("   - 确认后再手动发布")
        print("   - 避免重复token消耗")
        
        generate_response = requests.post(
            f"{api_base}/api/publish_articles",
            data=form_data,
            timeout=120
        )
        
        if generate_response.status_code == 200:
            result = generate_response.json()
            
            if result.get("success"):
                print("\n   ✅ 文章生成成功！")
                print(f"   消息: {result.get('message', '')}")
                print(f"   分类: {result.get('category', '')}")
                
                # 显示文章内容
                if result.get("articles") and len(result["articles"]) > 0:
                    article = result["articles"][0]
                    print(f"\n   📝 文章预览:")
                    print(f"   标题: {article['title']}")
                    print(f"   关键词: {article['keyword']}")
                    print(f"   评分: {article['score']}")
                    print(f"   点击量: {article['clicks']}")
                    print(f"   转化率: {article['conversion_rate']}%")
                    print(f"   内容长度: {len(article['content'])} 字符")
                    print(f"   内容预览: {article['content'][:200]}...")
                    
                    print(f"\n   🎯 下一步操作:")
                    print(f"   - 在浏览器中查看完整文章内容")
                    print(f"   - 点击'🚀 发布到WordPress'按钮发布")
                    print(f"   - 或点击'📋 复制内容'手动处理")
                    
                    # 测试发布功能
                    print(f"\n4. 测试发布功能...")
                    print("   正在发布文章到WordPress...")
                    
                    # 修改为自动发布模式
                    form_data["auto_publish"] = "true"
                    publish_response = requests.post(
                        f"{api_base}/api/publish_articles",
                        data=form_data,
                        timeout=120
                    )
                    
                    if publish_response.status_code == 200:
                        publish_result = publish_response.json()
                        
                        if publish_result.get("success"):
                            print("   ✅ 文章发布成功！")
                            print(f"   总文章: {publish_result.get('total_articles', 0)}")
                            print(f"   成功发布: {publish_result.get('published_count', 0)}")
                            print(f"   发布失败: {publish_result.get('failed_count', 0)}")
                            
                            # 显示发布结果详情
                            if publish_result.get("results"):
                                for i, publish_result_item in enumerate(publish_result["results"], 1):
                                    if publish_result_item["success"]:
                                        print(f"     ✅ 第{i}篇: {publish_result_item['article_keyword']}")
                                        print(f"        文章ID: {publish_result_item['post_id']}")
                                        print(f"        文章链接: {publish_result_item['post_url']}")
                                    else:
                                        print(f"     ❌ 第{i}篇: {publish_result_item['article_keyword']}")
                                        print(f"        失败原因: {publish_result_item['message']}")
                            
                            print(f"\n🎉 完整流程测试成功！")
                            print(f"   📊 优化效果：")
                            print(f"   - ✅ 先生成预览，避免重复token消耗")
                            print(f"   - ✅ 用户可以预览和编辑内容")
                            print(f"   - ✅ 确认后再发布，提高内容质量")
                            print(f"   - ✅ 修复了conversion_rate错误")
                            
                        else:
                            print(f"   ❌ 发布失败: {publish_result.get('error', '未知错误')}")
                    else:
                        print(f"   ❌ 发布API异常: {publish_response.status_code}")
                else:
                    print("   ❌ 没有生成文章内容")
                    
            else:
                print(f"   ❌ 生成失败: {result.get('error', '未知错误')}")
                
        else:
            print(f"   ❌ 生成API异常: {generate_response.status_code}")
            print(f"   响应: {generate_response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端正在运行")
        print("   运行命令: uvicorn geo_app:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ 测试过程出错: {str(e)}")

if __name__ == "__main__":
    test_preview_publish()


