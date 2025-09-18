#!/usr/bin/env python3
"""
测试不同豆包模型的简单脚本
"""

import os
import requests
import time


def test_doubao_model(model_name, test_message="你好，请简单介绍一下自己"):
    """测试指定的豆包模型"""
    api_key = os.getenv("ARK_API_KEY", "ecaa1600-6dab-4700-8655-63a260492b8c")
    base_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model_name,
        "messages": [{"role": "user", "content": test_message}],
        "temperature": 0.1,
        "max_tokens": 500
    }
    
    print(f"测试模型: {model_name}")
    print(f"测试消息: {test_message}")
    print("等待5秒...")
    time.sleep(5)
    
    try:
        resp = requests.post(base_url, headers=headers, json=data, timeout=120)
        resp.raise_for_status()
        result = resp.json()
        
        response_text = result["choices"][0]["message"]["content"]
        print(f"✅ 成功!")
        print(f"响应: {response_text}")
        print("-" * 50)
        return True
        
    except Exception as e:
        print(f"❌ 失败: {e}")
        print("-" * 50)
        return False


def main():
    """主函数"""
    print("=== 豆包模型测试 ===")
    
    # 要测试的模型列表
    models_to_test = [
        "doubao-1-5-thinking-vision-pro-250428",  # 当前使用的
        "doubao-pro-32k",  # Pro版本
        "doubao-pro-4k",   # Pro版本
        "doubao-lite-4k",  # Lite版本
        "doubao-lite-32k", # Lite版本
        "doubao-1-5-pro",  # 1.5 Pro
        "doubao-1-5-lite"  # 1.5 Lite
    ]
    
    test_message = "请用一句话介绍什么是人工智能"
    
    print(f"测试消息: {test_message}")
    print(f"将测试 {len(models_to_test)} 个模型")
    print("=" * 50)
    
    successful_models = []
    
    for i, model in enumerate(models_to_test, 1):
        print(f"\n[{i}/{len(models_to_test)}] 测试模型: {model}")
        
        success = test_doubao_model(model, test_message)
        if success:
            successful_models.append(model)
        
        # 模型间延迟
        if i < len(models_to_test):
            print("等待10秒后测试下一个模型...")
            time.sleep(10)
    
    # 汇总结果
    print(f"\n=== 测试完成 ===")
    print(f"成功模型数量: {len(successful_models)}/{len(models_to_test)}")
    print("成功的模型:")
    for model in successful_models:
        print(f"  ✅ {model}")
    
    if successful_models:
        print(f"\n推荐使用: {successful_models[0]}")
        print(f"设置环境变量: $env:DOUBAO_MODEL=\"{successful_models[0]}\"")


if __name__ == "__main__":
    main()








