#!/usr/bin/env python3
"""
优化的豆包API调用策略
"""

import requests
import time
import random
import json


def doubao_complete_optimized(messages, model="doubao-1-5-thinking-vision-pro-250428", temperature=0.1, max_tokens=4000):
    """优化的豆包API调用，增加更长的延迟和随机化"""
    api_key = os.getenv("ARK_API_KEY", "ecaa1600-6dab-4700-8655-63a260492b8c")
    base_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    # 增加基础延迟到10秒，并添加随机延迟
    base_delay = 10
    random_delay = random.uniform(0, 5)
    total_delay = base_delay + random_delay
    print(f"等待 {total_delay:.1f} 秒...")
    time.sleep(total_delay)
    
    # 更长的重试延迟
    retry_delays = [0, 30, 60, 120, 300]  # 最长等待5分钟
    last_err = None
    
    for delay in retry_delays:
        if delay > 0:
            print(f"重试等待 {delay} 秒...")
            time.sleep(delay)
        
        try:
            resp = requests.post(base_url, headers=headers, json=data, timeout=180)
            resp.raise_for_status()
            result = resp.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            last_err = e
            print(f"API调用失败: {e}")
            if "429" in str(e):
                continue
            else:
                break
    
    raise last_err if last_err else Exception("Doubao request failed after retries")








