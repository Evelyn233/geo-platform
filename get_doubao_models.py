#!/usr/bin/env python3
"""
获取豆包API的可用模型列表
"""

import requests
import os
import json


def get_available_models():
    """从豆包API获取可用模型列表"""
    api_key = os.getenv("ARK_API_KEY", "ecaa1600-6dab-4700-8655-63a260492b8c")
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        # 尝试获取模型列表
        resp = requests.get(
            "https://ark.cn-beijing.volces.com/api/v3/models",
            headers=headers,
            timeout=30
        )
        
        print(f"状态码: {resp.status_code}")
        print(f"响应头: {dict(resp.headers)}")
        
        if resp.status_code == 200:
            result = resp.json()
            print("✅ 成功获取模型列表:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result
        else:
            print(f"❌ 获取模型列表失败: {resp.status_code}")
            print(f"响应内容: {resp.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None


def test_known_models():
    """测试已知的模型名称"""
    api_key = os.getenv("ARK_API_KEY", "ecaa1600-6dab-4700-8655-63a260492b8c")
    base_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 基于文档和常见命名规则的模型名称
    test_models = [
        "doubao-1-5-thinking-vision-pro-250428",  # 当前使用的
        "doubao-pro-32k",
        "doubao-pro-4k", 
        "doubao-lite-32k",
        "doubao-lite-4k",
        "doubao-1-5-pro",
        "doubao-1-5-lite",
        "doubao-pro",
        "doubao-lite",
        "doubao-1.5-pro",
        "doubao-1.5-lite",
        "doubao-pro-32k-20241201",
        "doubao-lite-32k-20241201",
        "doubao-pro-4k-20241201",
        "doubao-lite-4k-20241201"
    ]
    
    print("=== 测试已知模型名称 ===")
    
    for model in test_models:
        print(f"\n测试模型: {model}")
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": "你好"}],
            "max_tokens": 10
        }
        
        try:
            resp = requests.post(base_url, headers=headers, json=data, timeout=30)
            
            if resp.status_code == 200:
                print(f"✅ {model} - 可用")
                result = resp.json()
                print(f"   响应: {result.get('choices', [{}])[0].get('message', {}).get('content', '')[:50]}...")
            elif resp.status_code == 404:
                print(f"❌ {model} - 模型不存在")
            elif resp.status_code == 429:
                print(f"⚠️  {model} - 限流，但模型可能可用")
            else:
                print(f"❌ {model} - 错误 {resp.status_code}: {resp.text[:100]}")
                
        except Exception as e:
            print(f"❌ {model} - 请求失败: {e}")


def main():
    """主函数"""
    print("=== 豆包API模型检测 ===")
    
    print("\n1. 尝试获取官方模型列表...")
    models = get_available_models()
    
    print("\n2. 测试已知模型名称...")
    test_known_models()
    
    print("\n=== 检测完成 ===")
    print("如果所有模型都返回404，可能需要:")
    print("1. 检查API密钥是否正确")
    print("2. 检查API端点是否正确")
    print("3. 联系豆包技术支持获取正确的模型名称")


if __name__ == "__main__":
    main()








