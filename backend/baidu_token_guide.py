#!/usr/bin/env python3
"""
百度统计API Token获取指南
"""

def print_token_guide():
    """打印获取百度统计API Token的步骤"""
    
    print("=" * 60)
    print("百度统计API Token获取指南")
    print("=" * 60)
    
    print("\n1. 登录百度统计后台")
    print("   访问: https://tongji.baidu.com")
    print("   使用你的百度账号登录")
    
    print("\n2. 进入数据API页面")
    print("   路径: 数据管理 -> 数据API")
    print("   或者: 管理 -> 数据导出服务")
    
    print("\n3. 开通API权限")
    print("   - 只有主账号才能开通此服务")
    print("   - 子账号无法进行此操作")
    print("   - 如果提示需要开通，请点击开通")
    
    print("\n4. 获取Access Token")
    print("   - 在数据API页面找到'Access Token'")
    print("   - 点击'生成'或'获取'按钮")
    print("   - 复制生成的token（不是JWT格式）")
    
    print("\n5. Token格式说明")
    print("   正确的token格式类似: abc123def456ghi789")
    print("   你提供的token是JWT格式，需要重新获取")
    
    print("\n6. 注意事项")
    print("   - Access Token有效期为30天")
    print("   - 过期后需要重新获取")
    print("   - 确保网站已正确安装百度统计代码")
    
    print("\n7. 验证Token")
    print("   获取到正确token后，运行以下命令测试:")
    print("   python test_baidu_api.py")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    print_token_guide()

