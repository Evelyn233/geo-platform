#!/usr/bin/env python3
"""
WordPress应用密码创建指导
"""

def print_instructions():
    """打印详细的创建应用密码指导"""
    print("=" * 80)
    print("🔐 WordPress应用密码创建详细指导")
    print("=" * 80)
    
    print("\n📋 步骤1：登录WordPress后台")
    print("   1. 打开浏览器，访问：https://www.shjingjun.com/wp-admin/")
    print("   2. 使用以下信息登录：")
    print("      - 用户名：jingjun2020")
    print("      - 密码：shjingjun20201919.")
    print("   3. 点击'登录'按钮")
    
    print("\n📋 步骤2：进入用户资料页面")
    print("   1. 登录成功后，在左侧菜单中找到'用户'")
    print("   2. 点击'用户' → '个人资料'")
    print("   3. 或者直接访问：https://www.shjingjun.com/wp-admin/profile.php")
    
    print("\n📋 步骤3：创建应用密码")
    print("   1. 在个人资料页面中，向下滚动")
    print("   2. 找到'应用密码'部分（通常在页面底部）")
    print("   3. 在'新应用密码名称'输入框中输入：GEO系统")
    print("   4. 点击'添加新应用密码'按钮")
    print("   5. WordPress会生成一个应用密码，类似：")
    print("      xxxx xxxx xxxx xxxx xxxx xxxx")
    print("   6. 复制这个密码（包含空格）")
    
    print("\n📋 步骤4：测试应用密码")
    print("   1. 复制生成的应用密码")
    print("   2. 运行测试脚本：python test_app_password.py")
    print("   3. 输入应用密码进行测试")
    
    print("\n⚠️  重要提示：")
    print("   - 应用密码只能看到一次，请立即复制保存")
    print("   - 应用密码格式：xxxx xxxx xxxx xxxx xxxx xxxx")
    print("   - 不要使用登录密码，必须使用应用密码")
    print("   - 如果忘记应用密码，需要重新创建")
    
    print("\n🔧 如果找不到'应用密码'部分：")
    print("   1. 检查WordPress版本（需要5.6+）")
    print("   2. 检查是否有安全插件阻止了此功能")
    print("   3. 尝试更新WordPress到最新版本")
    print("   4. 检查用户权限（需要管理员权限）")
    
    print("\n" + "=" * 80)

def create_test_script():
    """创建测试应用密码的脚本"""
    test_script = '''#!/usr/bin/env python3
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
        print("\\n1. 测试连接...")
        response = requests.get(f"{wp_url}/wp-json/wp/v2/users/me", headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ 应用密码测试成功！")
            print(f"   用户: {user_data.get('name', '未知')}")
            print(f"   用户ID: {user_data.get('id', 0)}")
            print(f"   邮箱: {user_data.get('email', '未知')}")
            
            # 测试获取分类
            print("\\n2. 测试获取分类...")
            cat_response = requests.get(f"{wp_url}/wp-json/wp/v2/categories", headers=headers, timeout=10)
            if cat_response.status_code == 200:
                categories = cat_response.json()
                print(f"✅ 成功获取 {len(categories)} 个分类")
                for cat in categories[:3]:
                    print(f"   - {cat['name']} (ID: {cat['id']})")
            else:
                print(f"❌ 获取分类失败: {cat_response.status_code}")
            
            print("\\n🎉 应用密码配置成功！可以在GEO系统中使用这个密码了。")
            
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
'''
    
    with open("test_app_password.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print(f"\n📄 已创建测试脚本：test_app_password.py")
    print("   运行命令：python test_app_password.py")

if __name__ == "__main__":
    print_instructions()
    create_test_script()

