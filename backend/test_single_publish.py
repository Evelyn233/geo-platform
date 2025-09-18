#!/usr/bin/env python3
"""
测试单篇文章发布功能
"""

import requests
import json

def test_single_publish():
    """测试单篇文章发布功能"""
    print("=" * 80)
    print("📝 测试单篇文章发布功能")
    print("=" * 80)
    
    # 后端API配置
    api_base = "http://localhost:8000"
    
    # 测试文章数据
    test_article = {
        "title": "抛光风布轮厂家 - 上海静钧研磨专业供应商",
        "content": """在五金加工、汽车制造、家具生产等精密抛光领域，抛光风布轮是提升工件表面光洁度、降低加工成本的核心工具。作为专注20年的抛光风布轮厂家，上海静钧研磨始终以"源头品质+技术赋能"为核心，为客户提供从产品选型到工艺优化的一站式解决方案。

## 一、抛光风布轮厂家的核心优势

作为资深抛光风布轮厂家，我们区别于中间商的核心优势在于"全产业链自主把控"。从原材料采购到成品检验，每一个环节均由自有技术团队主导，确保产品性能稳定、品质可控。

## 二、技术参数详解

抛光风布轮的性能取决于材料、结构与工艺，以下技术参数是判断产品质量的关键：

- **基材**：采用2106D高密度棉布或16安士以上纯棉布
- **直径**：常规规格50-500mm，可按客户需求定制
- **厚度**：3-30mm，根据抛光压力需求调整

## 三、为什么选择上海静钧研磨？

作为深耕抛光领域20年的源头厂家，我们不仅提供高品质产品，更能为客户提供"技术+服务"的双重保障。

选择源头厂家，让抛光效率提升30%，让您的产品更具竞争力！""",
        "category_name": "新闻资讯"
    }
    
    # WordPress配置
    wp_config = {
        "wp_url": "https://www.shjingjun.com",
        "wp_username": "jingjun2020", 
        "wp_password": "ymZx ssrJ UG1z IENK XHMi 10iP"
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
        
        print("\n3. 测试单篇文章发布...")
        print("   文章信息:")
        print(f"   - 标题: {test_article['title']}")
        print(f"   - 内容长度: {len(test_article['content'])} 字符")
        print(f"   - 分类: {test_article['category_name']}")
        
        # 准备请求数据
        request_data = {
            "wp_url": wp_config["wp_url"],
            "wp_username": wp_config["wp_username"],
            "wp_password": wp_config["wp_password"],
            "article": test_article
        }
        
        print("\n   正在发布文章...")
        print("   🔧 修复说明：")
        print("   - 使用新的单篇文章发布API")
        print("   - 直接传递已生成的文章内容")
        print("   - 避免重复生成，节省token成本")
        
        publish_response = requests.post(
            f"{api_base}/api/publish_single_article",
            headers={"Content-Type": "application/json"},
            json=request_data,
            timeout=60
        )
        
        if publish_response.status_code == 200:
            result = publish_response.json()
            
            if result.get("success"):
                print("\n   ✅ 文章发布成功！")
                print(f"   消息: {result.get('message', '')}")
                print(f"   文章标题: {result.get('article_title', '')}")
                print(f"   文章ID: {result.get('post_id', '')}")
                print(f"   文章链接: {result.get('post_url', '')}")
                print(f"   分类ID: {result.get('category_id', '')}")
                
                print(f"\n🎉 单篇文章发布功能测试成功！")
                print(f"   📊 优化效果：")
                print(f"   - ✅ 修复了'没有生成任何文章'的错误")
                print(f"   - ✅ 直接使用已生成的文章内容")
                print(f"   - ✅ 避免重复API调用，节省成本")
                print(f"   - ✅ 提供专门的单篇文章发布接口")
                
                print(f"\n   🌐 查看结果：")
                print(f"   - 文章链接: {result.get('post_url', '')}")
                print(f"   - 新闻资讯页面: https://www.shjingjun.com/news")
                
            else:
                print(f"   ❌ 发布失败: {result.get('error', '未知错误')}")
                print("   🔍 错误分析：")
                if "连接失败" in result.get('error', ''):
                    print("   - 可能是WordPress连接问题")
                elif "分类" in result.get('error', ''):
                    print("   - 可能是分类创建问题")
                else:
                    print("   - 需要进一步调试")
                
        else:
            print(f"   ❌ 发布API异常: {publish_response.status_code}")
            print(f"   响应: {publish_response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端正在运行")
        print("   运行命令: uvicorn geo_app:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ 测试过程出错: {str(e)}")

if __name__ == "__main__":
    test_single_publish()


