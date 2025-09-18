#!/usr/bin/env python3
"""
测试百度统计API调用
"""

import requests
import json

def test_baidu_api():
    """测试百度统计API"""
    
    # 你的访问令牌（从百度统计后台获取的正确token）
    access_token = "eyJhbGciOiJIUzM4NCJ9.eyJzdWIiOiJhY2MiLCJhdWQiOiLnmb7luqbnu5_orqEiLCJ1aWQiOjI0NTk4OTkzLCJhcHBJZCI6IjEzYmQ1MDQ5YTY3NmQxMDczNzk1OTkzMjEwMmVjNTU3IiwiaXNzIjoi5ZWG5Lia5byA5Y-R6ICF5Lit5b-DIiwicGxhdGZvcm1JZCI6IjQ5NjAzNDU5NjU5NTg1NjE3OTQiLCJleHAiOjE3NjA0NDcyNzAsImp0aSI6Ii04Mzk3MzE5MjkzMTc2MjU4NTA0In0.oOkSqxODhCqNUKpTtpwjwVBFyReTkUFXTww7RuklaeIwazIRHHWu9CdDXJR1FtfR"
    
    # 测试不同的API地址
    api_urls = [
        "https://api.baidu.com/json/tongji/v1/ReportService/getSiteList",
        "https://tongji.baidu.com/api/tongji/v1/ReportService/getSiteList",
        "https://api.baidu.com/json/tongji/v1/getSiteList"
    ]
    
    for api_url in api_urls:
        print(f"\n测试API地址: {api_url}")
        
        data = {
            "header": {
                "userName": "default",
                "accessToken": access_token
            },
            "body": {}
        }
        
        try:
            response = requests.post(
                api_url,
                headers={"Content-Type": "application/json"},
                json=data,
                timeout=30
            )
            
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("header", {}).get("desc") == "success":
                    print("✅ API调用成功！")
                    return api_url
                else:
                    print(f"❌ API返回错误: {result.get('header', {}).get('message', 'Unknown error')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
    
    return None

if __name__ == "__main__":
    test_baidu_api()
