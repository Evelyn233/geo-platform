#!/usr/bin/env python3
"""
测试WordPress应用密码
"""

import requests
import base64

def test_app_password():
    """测试应用密码"""
    print("=" * 60)
    print("🧪 测试WordPress应用密码")
    print("=" * 60)
    
    # 获取用户输入
    wp_url = "https://www.shjingjun.com"
    username = "jingjun2020"
    app_password = input("请输入应用密码（格式：xxxx xxxx xxxx xxxx xxxx xxxx）: ").strip()
    
    if not app_password:
        print("❌ 应用密码不能为空")
        return
    
    # 设置认证头
    credentials = f"{username}:{app_password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/json',
        'User-Agent': 'GEO-System/1.0'
    }
    
    try:
        # 测试连接
        print("\n1. 测试连接...")
        response = requests.get(f"{wp_url}/wp-json/wp/v2/users/me", headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ 应用密码测试成功！")
            print(f"   用户: {user_data.get('name', '未知')}")
            print(f"   用户ID: {user_data.get('id', 0)}")
            print(f"   邮箱: {user_data.get('email', '未知')}")
            
            # 测试获取分类
            print("\n2. 测试获取分类...")
            cat_response = requests.get(f"{wp_url}/wp-json/wp/v2/categories", headers=headers, timeout=10)
            if cat_response.status_code == 200:
                categories = cat_response.json()
                print(f"✅ 成功获取 {len(categories)} 个分类")
                for cat in categories[:3]:
                    print(f"   - {cat['name']} (ID: {cat['id']})")
            else:
                print(f"❌ 获取分类失败: {cat_response.status_code}")
            
            print("\n🎉 应用密码配置成功！可以在GEO系统中使用这个密码了。")
            
        elif response.status_code == 401:
            print("❌ 认证失败：应用密码错误")
            print("   请检查：")
            print("   1. 应用密码是否正确复制（包含空格）")
            print("   2. 用户名是否正确")
            print("   3. 应用密码是否已创建")
        else:
            print(f"❌ 连接失败：HTTP {response.status_code}")
            print(f"   响应: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")

if __name__ == "__main__":
    test_app_password()
