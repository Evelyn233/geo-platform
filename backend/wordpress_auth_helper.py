#!/usr/bin/env python3
"""
WordPress认证辅助工具
提供多种认证方式支持
"""

import requests
import base64
import json
from typing import Dict, Optional

class WordPressAuthHelper:
    """WordPress认证辅助类"""
    
    def __init__(self, wp_url: str, username: str, password: str):
        self.wp_url = wp_url.rstrip('/')
        self.username = username
        self.password = password
        self.api_url = f"{self.wp_url}/wp-json/wp/v2"
    
    def test_basic_auth(self) -> Dict:
        """测试基础认证（用户名+密码）"""
        try:
            # 使用基础认证
            auth = (self.username, self.password)
            response = requests.get(
                f"{self.api_url}/users/me",
                auth=auth,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "method": "basic_auth",
                    "message": "基础认证成功"
                }
            else:
                return {
                    "success": False,
                    "method": "basic_auth",
                    "message": f"基础认证失败: {response.status_code} - {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "method": "basic_auth",
                "message": f"基础认证异常: {str(e)}"
            }
    
    def test_cookie_auth(self) -> Dict:
        """测试Cookie认证"""
        try:
            # 先登录获取Cookie
            login_url = f"{self.wp_url}/wp-login.php"
            session = requests.Session()
            
            # 获取登录页面
            login_page = session.get(login_url)
            
            # 提取nonce等必要参数
            # 这里需要解析HTML获取隐藏字段，简化处理
            
            login_data = {
                'log': self.username,
                'pwd': self.password,
                'wp-submit': '登录',
                'redirect_to': f"{self.wp_url}/wp-admin/",
                'testcookie': '1'
            }
            
            # 尝试登录
            login_response = session.post(login_url, data=login_data)
            
            if 'wp-admin' in login_response.url:
                # 登录成功，测试API
                api_response = session.get(f"{self.api_url}/users/me")
                
                if api_response.status_code == 200:
                    return {
                        "success": True,
                        "method": "cookie_auth",
                        "message": "Cookie认证成功"
                    }
                else:
                    return {
                        "success": False,
                        "method": "cookie_auth",
                        "message": f"API调用失败: {api_response.status_code}"
                    }
            else:
                return {
                    "success": False,
                    "method": "cookie_auth",
                    "message": "登录失败，可能用户名或密码错误"
                }
                
        except Exception as e:
            return {
                "success": False,
                "method": "cookie_auth",
                "message": f"Cookie认证异常: {str(e)}"
            }
    
    def test_all_methods(self) -> Dict:
        """测试所有认证方法"""
        print("🔍 测试WordPress认证方法...")
        
        results = {}
        
        # 测试基础认证
        print("1. 测试基础认证...")
        basic_result = self.test_basic_auth()
        results["basic_auth"] = basic_result
        print(f"   结果: {basic_result['message']}")
        
        # 测试Cookie认证
        print("2. 测试Cookie认证...")
        cookie_result = self.test_cookie_auth()
        results["cookie_auth"] = cookie_result
        print(f"   结果: {cookie_result['message']}")
        
        # 找出成功的认证方法
        successful_methods = [method for method, result in results.items() if result["success"]]
        
        if successful_methods:
            return {
                "success": True,
                "message": f"找到可用的认证方法: {', '.join(successful_methods)}",
                "methods": results,
                "recommended": successful_methods[0]
            }
        else:
            return {
                "success": False,
                "message": "所有认证方法都失败了",
                "methods": results
            }

def test_wordpress_auth():
    """测试WordPress认证"""
    print("=" * 60)
    print("🔐 WordPress认证测试")
    print("=" * 60)
    
    # 你的WordPress信息
    wp_url = "https://www.shjingjun.com"
    username = "jingjun2020"
    password = "shjingjun20201919"
    
    helper = WordPressAuthHelper(wp_url, username, password)
    result = helper.test_all_methods()
    
    print(f"\n📊 测试结果: {result['message']}")
    
    if result["success"]:
        print(f"✅ 推荐使用: {result['recommended']}")
    else:
        print("❌ 所有认证方法都失败了")
        print("\n💡 建议:")
        print("1. 检查用户名和密码是否正确")
        print("2. 确认WordPress网站可以正常访问")
        print("3. 检查是否有安全插件阻止API访问")
        print("4. 尝试创建应用密码")

if __name__ == "__main__":
    test_wordpress_auth()


