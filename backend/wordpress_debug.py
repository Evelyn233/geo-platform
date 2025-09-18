#!/usr/bin/env python3
"""
WordPress详细调试工具
"""

import requests
import re
from urllib.parse import urljoin

def debug_wordpress_login():
    """详细调试WordPress登录过程"""
    print("=" * 60)
    print("🔍 WordPress登录详细调试")
    print("=" * 60)
    
    wp_url = "https://www.shjingjun.com"
    username = "jingjun2020"
    password = "shjingjun20201919"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    try:
        # 1. 测试网站可访问性
        print("1. 测试网站可访问性...")
        response = session.get(wp_url, timeout=10)
        print(f"   状态码: {response.status_code}")
        print(f"   响应长度: {len(response.text)} 字符")
        
        if response.status_code != 200:
            print("❌ 网站无法访问")
            return
        
        # 2. 测试登录页面
        print("\n2. 测试登录页面...")
        login_url = f"{wp_url}/wp-login.php"
        login_response = session.get(login_url, timeout=10)
        print(f"   登录页面状态码: {login_response.status_code}")
        print(f"   登录页面URL: {login_response.url}")
        
        if login_response.status_code != 200:
            print("❌ 登录页面无法访问")
            return
        
        # 3. 分析登录页面内容
        print("\n3. 分析登录页面内容...")
        content = login_response.text
        
        # 检查是否有安全插件
        security_plugins = [
            'Wordfence', 'Sucuri', 'iThemes Security', 'All In One WP Security',
            'BulletProof Security', 'WP Security', 'Security Ninja'
        ]
        
        found_plugins = []
        for plugin in security_plugins:
            if plugin.lower() in content.lower():
                found_plugins.append(plugin)
        
        if found_plugins:
            print(f"   发现安全插件: {', '.join(found_plugins)}")
        else:
            print("   未发现常见安全插件")
        
        # 检查是否有验证码
        if 'captcha' in content.lower() or 'recaptcha' in content.lower():
            print("   ⚠️ 发现验证码，可能需要手动处理")
        
        # 检查是否有两步验证
        if 'two-factor' in content.lower() or '2fa' in content.lower():
            print("   ⚠️ 发现两步验证")
        
        # 4. 提取登录表单信息
        print("\n4. 提取登录表单信息...")
        
        # 查找表单action
        form_action_match = re.search(r'<form[^>]*action="([^"]+)"', content)
        if form_action_match:
            form_action = form_action_match.group(1)
            print(f"   表单action: {form_action}")
        else:
            print("   未找到表单action")
        
        # 查找隐藏字段
        hidden_fields = re.findall(r'<input[^>]*type="hidden"[^>]*name="([^"]+)"[^>]*value="([^"]+)"', content)
        print(f"   隐藏字段数量: {len(hidden_fields)}")
        for name, value in hidden_fields[:5]:  # 只显示前5个
            print(f"     {name}: {value[:50]}...")
        
        # 5. 尝试登录
        print("\n5. 尝试登录...")
        
        # 准备登录数据
        login_data = {
            'log': username,
            'pwd': password,
            'wp-submit': '登录',
            'redirect_to': f"{wp_url}/wp-admin/",
            'testcookie': '1'
        }
        
        # 添加隐藏字段
        for name, value in hidden_fields:
            login_data[name] = value
        
        print(f"   登录数据字段: {list(login_data.keys())}")
        
        # 执行登录
        login_result = session.post(login_url, data=login_data, allow_redirects=True, timeout=15)
        print(f"   登录后状态码: {login_result.status_code}")
        print(f"   登录后URL: {login_result.url}")
        
        # 6. 分析登录结果
        print("\n6. 分析登录结果...")
        
        if 'wp-admin' in login_result.url or 'dashboard' in login_result.url:
            print("   ✅ 登录成功！")
            
            # 测试API访问
            print("\n7. 测试API访问...")
            api_url = f"{wp_url}/wp-json/wp/v2/users/me"
            api_response = session.get(api_url, timeout=10)
            print(f"   API状态码: {api_response.status_code}")
            
            if api_response.status_code == 200:
                print("   ✅ API访问成功！")
                user_data = api_response.json()
                print(f"   用户: {user_data.get('name', '未知')}")
            else:
                print(f"   ❌ API访问失败: {api_response.text[:200]}...")
                
        else:
            print("   ❌ 登录失败")
            
            # 查找错误信息
            error_patterns = [
                r'<div class="login_error">([^<]+)</div>',
                r'<div class="error">([^<]+)</div>',
                r'<p class="error">([^<]+)</p>',
                r'class="error"[^>]*>([^<]+)<'
            ]
            
            for pattern in error_patterns:
                error_match = re.search(pattern, login_result.text)
                if error_match:
                    error_msg = error_match.group(1).strip()
                    print(f"   错误信息: {error_msg}")
                    break
            
            # 检查是否需要验证码
            if 'captcha' in login_result.text.lower():
                print("   ⚠️ 需要验证码验证")
            
            # 检查是否需要邮箱验证
            if 'email' in login_result.text.lower() and 'verify' in login_result.text.lower():
                print("   ⚠️ 可能需要邮箱验证")
        
        # 7. 检查WordPress版本和插件
        print("\n8. 检查WordPress信息...")
        
        # 检查WordPress版本
        version_match = re.search(r'<meta name="generator" content="WordPress ([^"]+)"', content)
        if version_match:
            wp_version = version_match.group(1)
            print(f"   WordPress版本: {wp_version}")
        
        # 检查是否有REST API
        rest_url = f"{wp_url}/wp-json/"
        rest_response = session.get(rest_url, timeout=10)
        print(f"   REST API状态: {rest_response.status_code}")
        
        if rest_response.status_code == 200:
            print("   ✅ REST API可用")
        else:
            print("   ❌ REST API不可用")
    
    except Exception as e:
        print(f"❌ 调试过程出错: {str(e)}")
        import traceback
        traceback.print_exc()

def suggest_solutions():
    """提供解决方案建议"""
    print("\n" + "=" * 60)
    print("💡 解决方案建议")
    print("=" * 60)
    
    print("1. 手动创建应用密码:")
    print("   - 登录 https://www.shjingjun.com/wp-admin/")
    print("   - 进入 用户 → 个人资料")
    print("   - 找到'应用密码'部分")
    print("   - 创建名为'GEO系统'的应用密码")
    print("   - 复制生成的密码")
    
    print("\n2. 检查安全插件设置:")
    print("   - 暂时禁用安全插件")
    print("   - 或配置插件允许API访问")
    
    print("\n3. 使用替代方案:")
    print("   - 手动复制生成的文章内容")
    print("   - 使用WordPress导入功能")
    print("   - 考虑使用其他发布方式")

if __name__ == "__main__":
    debug_wordpress_login()
    suggest_solutions()


