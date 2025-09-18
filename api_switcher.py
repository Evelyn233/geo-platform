#!/usr/bin/env python3
"""
API切换器 - 支持多种大模型API
"""

import requests
import time
import json
import os


class APISwitcher:
    """支持多种API的切换器"""
    
    def __init__(self, api_type="doubao"):
        self.api_type = api_type
        self.setup_api()
    
    def setup_api(self):
        """设置API配置"""
        if self.api_type == "doubao":
            self.base_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
            self.api_key = os.getenv("ARK_API_KEY", "ecaa1600-6dab-4700-8655-63a260492b8c")
            self.model = "doubao-1-5-thinking-vision-pro-250428"
            self.delay = 10  # 豆包需要更长延迟
            
        elif self.api_type == "qwen":
            self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
            self.api_key = os.getenv("QWEN_API_KEY", "your_qwen_key")
            self.model = "qwen-plus"
            self.delay = 2
            
        elif self.api_type == "glm":
            self.base_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            self.api_key = os.getenv("GLM_API_KEY", "your_glm_key")
            self.model = "glm-4"
            self.delay = 1
            
        elif self.api_type == "kimi":
            self.base_url = "https://api.moonshot.cn/v1/chat/completions"
            self.api_key = os.getenv("KIMI_API_KEY", "your_kimi_key")
            self.model = "moonshot-v1-8k"
            self.delay = 1
    
    def complete(self, messages, temperature=0.1, max_tokens=4000):
        """调用API进行文本生成"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        if self.api_type == "doubao":
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        elif self.api_type == "qwen":
            data = {
                "model": self.model,
                "input": {
                    "messages": messages
                },
                "parameters": {
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            }
        else:  # glm, kimi
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        
        # 添加延迟
        time.sleep(self.delay)
        
        try:
            resp = requests.post(self.base_url, headers=headers, json=data, timeout=120)
            resp.raise_for_status()
            result = resp.json()
            
            if self.api_type == "qwen":
                return result["output"]["text"]
            else:
                return result["choices"][0]["message"]["content"]
                
        except Exception as e:
            print(f"API调用失败: {e}")
            raise e


def test_apis():
    """测试不同API"""
    test_message = [{"role": "user", "content": "你好，请简单介绍一下自己"}]
    
    apis = ["doubao", "qwen", "glm", "kimi"]
    
    for api_type in apis:
        print(f"\n=== 测试 {api_type.upper()} API ===")
        try:
            switcher = APISwitcher(api_type)
            result = switcher.complete(test_message)
            print(f"成功: {result[:100]}...")
        except Exception as e:
            print(f"失败: {e}")


if __name__ == "__main__":
    # 测试所有API
    test_apis()
    
    # 使用特定API
    print("\n=== 使用豆包API ===")
    switcher = APISwitcher("doubao")
    messages = [{"role": "user", "content": "请总结一下RAG技术的主要应用场景"}]
    result = switcher.complete(messages)
    print(f"结果: {result}")








