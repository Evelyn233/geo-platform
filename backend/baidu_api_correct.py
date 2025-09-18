#!/usr/bin/env python3
"""
正确的百度统计API调用方式
"""

import requests
import json

def test_baidu_api_correct():
    """测试正确的百度统计API调用"""
    
    access_token = "eyJhbGciOiJIUzM4NCJ9.eyJzdWIiOiJhY2MiLCJhdWQiOiLnmb7luqbnu5_orqEiLCJ1aWQiOjI0NTk4OTkzLCJhcHBJZCI6IjEzYmQ1MDQ5YTY3NmQxMDczNzk1OTkzMjEwMmVjNTU3IiwiaXNzIjoi5ZWG5Lia5byA5Y-R6ICF5Lit5b-DIiwicGxhdGZvcm1JZCI6IjQ5NjAzNDU5NjU5NTg1NjE3OTQiLCJleHAiOjE3NjA0NDcyNzAsImp0aSI6Ii04Mzk3MzE5MjkzMTc2MjU4NTA0In0.oOkSqxODhCqNUKpTtpwjwVBFyReTkUFXTww7RuklaeIwazIRHHWu9CdDXJR1FtfR"
    
    # 根据百度统计API文档，正确的调用方式
    api_url = "https://api.baidu.com/json/tongji/v1/ReportService/getSiteList"
    
    # 正确的请求格式
    data = {
        "header": {
            "userName": "sh静钧",  # 你的实际用户名
            "accessToken": access_token
        },
        "body": {}
    }
    
    print("测试百度统计API调用:")
    print("=" * 50)
    print(f"API地址: {api_url}")
    print(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=30
        )
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            header = result.get("header", {})
            
            if header.get("desc") == "success":
                print("✅ API调用成功！")
                sites = result.get("body", {}).get("data", [])
                print(f"获取到 {len(sites)} 个站点")
                for site in sites:
                    print(f"  - 站点ID: {site.get('site_id')}, 名称: {site.get('site_name')}")
                return True
            else:
                print(f"❌ API返回错误: {header.get('message', 'Unknown error')}")
                failures = header.get("failures", [])
                for failure in failures:
                    print(f"  错误代码: {failure.get('code')}")
                    print(f"  错误信息: {failure.get('message')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_with_different_username():
    """尝试不同的用户名"""
    access_token = "eyJhbGciOiJIUzM4NCJ9.eyJzdWIiOiJhY2MiLCJhdWQiOiLnmb7luqbnu5_orqEiLCJ1aWQiOjI0NTk4OTkzLCJhcHBJZCI6IjEzYmQ1MDQ5YTY3NmQxMDczNzk1OTkzMjEwMmVjNTU3IiwiaXNzIjoi5ZWG5Lia5byA5Y-R6ICF5Lit5b-DIiwicGxhdGZvcm1JZCI6IjQ5NjAzNDU5NjU5NTg1NjE3OTQiLCJleHAiOjE3NjA0NDcyNzAsImp0aSI6Ii04Mzk3MzE5MjkzMTc2MjU4NTA0In0.oOkSqxODhCqNUKpTtpwjwVBFyReTkUFXTww7RuklaeIwazIRHHWu9CdDXJR1FtfR"
    
    # 尝试不同的用户名
    usernames = ["default", "admin", "root", "tongji", "baidu"]
    
    for username in usernames:
        print(f"\n尝试用户名: {username}")
        print("-" * 30)
        
        data = {
            "header": {
                "userName": username,
                "accessToken": access_token
            },
            "body": {}
        }
        
        try:
            response = requests.post(
                "https://api.baidu.com/json/tongji/v1/ReportService/getSiteList",
                headers={"Content-Type": "application/json"},
                json=data,
                timeout=30
            )
            
            result = response.json()
            header = result.get("header", {})
            
            if header.get("desc") == "success":
                print(f"✅ 用户名 {username} 成功！")
                return username
            else:
                print(f"❌ 用户名 {username} 失败: {header.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ 用户名 {username} 异常: {e}")
    
    return None

if __name__ == "__main__":
    print("测试1: 使用默认用户名")
    success = test_baidu_api_correct()
    
    if not success:
        print("\n测试2: 尝试不同用户名")
        correct_username = test_with_different_username()
        if correct_username:
            print(f"\n找到正确的用户名: {correct_username}")
        else:
            print("\n所有用户名都失败了，可能需要检查token或API权限")
