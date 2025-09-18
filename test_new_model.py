#!/usr/bin/env python3
"""
测试新的豆包模型 doubao-1-5-pro-32k-250115
"""

import requests
import time
import os


def test_new_model():
    """测试新模型"""
    api_key = os.getenv("ARK_API_KEY", "ecaa1600-6dab-4700-8655-63a260492b8c")
    base_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "doubao-1-5-pro-32k-250115",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Hello! Please introduce yourself briefly."
            }
        ],
        "temperature": 0.1,
        "max_tokens": 500
    }
    
    print("=== 测试新模型: doubao-1-5-pro-32k-250115 ===")
    print("等待5秒...")
    time.sleep(5)
    
    try:
        resp = requests.post(base_url, headers=headers, json=data, timeout=120)
        
        print(f"状态码: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            response_text = result["choices"][0]["message"]["content"]
            print("✅ 模型测试成功!")
            print(f"响应: {response_text}")
            return True
        else:
            print(f"❌ 模型测试失败: {resp.status_code}")
            print(f"错误信息: {resp.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False


def test_rag_task():
    """测试RAG相关任务"""
    api_key = os.getenv("ARK_API_KEY", "ecaa1600-6dab-4700-8655-63a260492b8c")
    base_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 测试实体提取任务（RAG-Anything的核心任务）
    rag_test_data = {
        "model": "doubao-1-5-pro-32k-250115",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert at extracting entities and relationships from text. Extract key entities and their relationships from the given text."
            },
            {
                "role": "user",
                "content": """Please extract entities and relationships from this text:

"John Smith is a software engineer at Google. He works on machine learning projects and has expertise in Python and TensorFlow. His colleague Sarah Johnson is a data scientist who specializes in natural language processing."

Format your response as:
Entities: [list of entities]
Relationships: [list of relationships]"""
            }
        ],
        "temperature": 0.1,
        "max_tokens": 1000
    }
    
    print("\n=== 测试RAG任务: 实体提取 ===")
    print("等待5秒...")
    time.sleep(5)
    
    try:
        resp = requests.post(base_url, headers=headers, json=rag_test_data, timeout=120)
        
        if resp.status_code == 200:
            result = resp.json()
            response_text = result["choices"][0]["message"]["content"]
            print("✅ RAG任务测试成功!")
            print(f"实体提取结果: {response_text}")
            return True
        else:
            print(f"❌ RAG任务测试失败: {resp.status_code}")
            print(f"错误信息: {resp.text}")
            return False
            
    except Exception as e:
        print(f"❌ RAG任务请求失败: {e}")
        return False


def main():
    """主函数"""
    print("豆包新模型测试")
    print("=" * 50)
    
    # 基础测试
    basic_success = test_new_model()
    
    if basic_success:
        # RAG任务测试
        rag_success = test_rag_task()
        
        if rag_success:
            print("\n🎉 所有测试通过!")
            print("新模型 doubao-1-5-pro-32k-250115 可以用于RAG-Anything项目")
            print("\n现在可以运行RAG-Anything:")
            print("python examples/raganything_example.py your_document.pdf --api-key your_key")
        else:
            print("\n⚠️  基础测试通过，但RAG任务测试失败")
    else:
        print("\n❌ 基础测试失败，请检查API配置")


if __name__ == "__main__":
    main()








