#!/usr/bin/env python3
"""
测试所有可用模型
"""

from model_config import model_config

def test_models():
    """测试所有模型配置"""
    # 使用新的摘要方法
    model_config.print_model_summary()
    
    print("\n" + "=" * 60)
    print("📋 详细模型信息")
    print("=" * 60)
    
    for category, models in model_config.MODEL_CATEGORIES.items():
        print(f"\n📂 {category}:")
        for model_id in models:
            info = model_config.get_model_info(model_id)
            model_type = model_config.get_model_type(model_id)
            recommended_tokens = model_config.get_recommended_tokens(model_id)
            
            print(f"  🔹 {info['name']}")
            print(f"     ID: {model_id}")
            print(f"     描述: {info['description']}")
            print(f"     类型: {model_type}")
            print(f"     最大Token: {info['max_tokens']:,}")
            print(f"     推荐Token: {recommended_tokens:,}")
            print(f"     成本等级: {info['cost_level']}")
            print(f"     推荐用途: {info.get('recommended_for', '通用')}")
            print()

def test_api_call():
    """测试API调用"""
    import requests
    
    # 测试豆包API
    api_key = "cf26bc05-bf7f-4bb8-8795-c090ea96e260"
    base_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 测试快速模型
    data = {
        "model": "doubao-seed-1-6-flash",
        "messages": [
            {"role": "system", "content": "你是人工智能助手."},
            {"role": "user", "content": "你好，请简单介绍一下自己"}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    try:
        print("\n=== 测试API调用 ===")
        print(f"使用模型: {data['model']}")
        
        response = requests.post(base_url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"✅ API调用成功")
            print(f"回复: {content}")
            
            if "usage" in result:
                usage = result["usage"]
                print(f"Token使用: 输入{usage.get('prompt_tokens', 0)}, 输出{usage.get('completion_tokens', 0)}, 总计{usage.get('total_tokens', 0)}")
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ API调用异常: {e}")

if __name__ == "__main__":
    test_models()
    test_api_call()
