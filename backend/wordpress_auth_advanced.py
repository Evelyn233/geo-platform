#!/usr/bin/env python3
"""
高级WordPress认证模块
支持多种认证方式和安全插件绕过
"""

import requests
import base64
import json
import re
from typing import Dict, Optional
from urllib.parse import urljoin

class AdvancedWordPressAuth:
    """高级WordPress认证类"""
    
    def __init__(self, wp_url: str, username: str, password: str):
        self.wp_url = wp_url.rstrip('/')
        self.username = username
        self.password = password
        self.api_url = f"{self.wp_url}/wp-json/wp/v2"
        self.session = requests.Session()
        
        # 设置用户代理，模拟真实浏览器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_login_page(self) -> Dict:
        """获取登录页面并提取必要信息"""
        try:
            # 清理所有现有cookie，避免重复cookie问题
            self.session.cookies.clear()
            
            login_url = f"{self.wp_url}/wp-login.php"
            response = self.session.get(login_url, timeout=10)
            
            if response.status_code == 200:
                # 提取nonce等隐藏字段
                content = response.text
                
                # 查找WordPress的nonce
                nonce_match = re.search(r'name="wp_nonce" value="([^"]+)"', content)
                nonce = nonce_match.group(1) if nonce_match else ""
                
                # 查找其他隐藏字段
                redirect_to_match = re.search(r'name="redirect_to" value="([^"]+)"', content)
                redirect_to = redirect_to_match.group(1) if redirect_to_match else f"{self.wp_url}/wp-admin/"
                
                return {
                    "success": True,
                    "nonce": nonce,
                    "redirect_to": redirect_to,
                    "cookies": dict(response.cookies)
                }
            else:
                return {
                    "success": False,
                    "message": f"无法访问登录页面: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"获取登录页面失败: {str(e)}"
            }
    
    def login_with_session(self) -> Dict:
        """使用会话登录"""
        try:
            # 创建全新的会话，避免cookie冲突
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            # 获取登录页面
            login_info = self.get_login_page()
            if not login_info["success"]:
                return login_info
            
            # 准备登录数据
            login_data = {
                'log': self.username,
                'pwd': self.password,
                'wp-submit': '登录',
                'redirect_to': login_info["redirect_to"],
                'testcookie': '1',
                'wp_nonce': login_info["nonce"]
            }
            
            # 添加Cookie
            for name, value in login_info["cookies"].items():
                self.session.cookies.set(name, value)
            
            # 执行登录
            login_url = f"{self.wp_url}/wp-login.php"
            response = self.session.post(login_url, data=login_data, allow_redirects=True, timeout=15)
            
            # 检查登录是否成功
            if 'wp-admin' in response.url or 'dashboard' in response.url:
                return {
                    "success": True,
                    "message": "登录成功",
                    "cookies": dict(self.session.cookies)
                }
            else:
                # 检查是否有错误信息
                error_match = re.search(r'<div class="login_error">([^<]+)</div>', response.text)
                error_msg = error_match.group(1) if error_match else "未知错误"
                
                return {
                    "success": False,
                    "message": f"登录失败: {error_msg}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"登录异常: {str(e)}"
            }
    
    def test_api_access(self) -> Dict:
        """测试API访问"""
        try:
            # 先尝试登录
            login_result = self.login_with_session()
            if not login_result["success"]:
                return login_result
            
            # 测试API访问
            response = self.session.get(f"{self.api_url}/users/me", timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "success": True,
                    "message": "API访问成功",
                    "user": user_data.get("name", "未知用户")
                }
            else:
                return {
                    "success": False,
                    "message": f"API访问失败: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"API测试异常: {str(e)}"
            }
    
    def create_application_password(self) -> Dict:
        """尝试创建应用密码"""
        try:
            # 先登录
            login_result = self.login_with_session()
            if not login_result["success"]:
                return login_result
            
            # 访问用户资料页面
            profile_url = f"{self.wp_url}/wp-admin/profile.php"
            response = self.session.get(profile_url, timeout=10)
            
            if response.status_code == 200:
                # 查找应用密码表单
                if 'application-passwords' in response.text:
                    # 尝试创建应用密码
                    app_password_data = {
                        'new_application_password_name': 'GEO系统',
                        'action': 'create_application_password',
                        'wp_nonce': self.extract_nonce(response.text)
                    }
                    
                    create_response = self.session.post(profile_url, data=app_password_data, timeout=10)
                    
                    if create_response.status_code == 200:
                        # 查找生成的密码
                        password_match = re.search(r'<input[^>]*value="([^"]+)"[^>]*class="application-password-input"', create_response.text)
                        if password_match:
                            return {
                                "success": True,
                                "message": "应用密码创建成功",
                                "password": password_match.group(1)
                            }
                        else:
                            return {
                                "success": False,
                                "message": "应用密码创建失败，无法提取密码"
                            }
                    else:
                        return {
                            "success": False,
                            "message": f"创建应用密码失败: {create_response.status_code}"
                        }
                else:
                    return {
                        "success": False,
                        "message": "WordPress版本不支持应用密码功能"
                    }
            else:
                return {
                    "success": False,
                    "message": f"无法访问用户资料页面: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"创建应用密码异常: {str(e)}"
            }
    
    def extract_nonce(self, content: str) -> str:
        """从HTML内容中提取nonce"""
        nonce_match = re.search(r'name="wp_nonce" value="([^"]+)"', content)
        return nonce_match.group(1) if nonce_match else ""
    
    def get_alternative_auth_methods(self) -> Dict:
        """获取替代认证方法"""
        try:
            # 检查是否有JWT插件
            jwt_url = f"{self.wp_url}/wp-json/jwt-auth/v1/token"
            jwt_response = self.session.post(jwt_url, json={
                'username': self.username,
                'password': self.password
            }, timeout=10)
            
            if jwt_response.status_code == 200:
                jwt_data = jwt_response.json()
                return {
                    "success": True,
                    "method": "jwt",
                    "token": jwt_data.get("token"),
                    "message": "JWT认证可用"
                }
            
            # 检查是否有其他认证插件
            return {
                "success": False,
                "message": "未找到替代认证方法"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"检查替代方法异常: {str(e)}"
            }

def test_advanced_auth():
    """测试高级认证"""
    print("=" * 60)
    print("🔐 高级WordPress认证测试")
    print("=" * 60)
    
    wp_url = "https://www.shjingjun.com"
    username = "jingjun2020"
    password = "shjingjun20201919."
    
    auth = AdvancedWordPressAuth(wp_url, username, password)
    
    # 测试登录
    print("1. 测试会话登录...")
    login_result = auth.login_with_session()
    print(f"   结果: {login_result['message']}")
    
    if login_result["success"]:
        # 测试API访问
        print("2. 测试API访问...")
        api_result = auth.test_api_access()
        print(f"   结果: {api_result['message']}")
        
        if api_result["success"]:
            print("✅ 认证成功！可以使用会话方式发布文章")
        else:
            # 尝试创建应用密码
            print("3. 尝试创建应用密码...")
            app_password_result = auth.create_application_password()
            print(f"   结果: {app_password_result['message']}")
            
            if app_password_result["success"]:
                print(f"✅ 应用密码创建成功: {app_password_result['password']}")
                print("请在GEO系统中使用这个应用密码")
    
    # 检查替代方法
    print("4. 检查替代认证方法...")
    alt_result = auth.get_alternative_auth_methods()
    print(f"   结果: {alt_result['message']}")

if __name__ == "__main__":
    test_advanced_auth()
