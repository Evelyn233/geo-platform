#!/usr/bin/env python3
"""
检查网站百度统计代码安装情况
"""

import requests
from bs4 import BeautifulSoup
import re

def check_baidu_analytics_code(url):
    """检查网站是否安装了百度统计代码"""
    try:
        print(f"正在检查网站: {url}")
        
        # 获取网页内容
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        html_content = response.text
        print(f"网页状态码: {response.status_code}")
        print(f"网页大小: {len(html_content)} 字符")
        
        # 检查百度统计代码
        baidu_patterns = [
            r'hmt\.baidu\.com/hm\.js',
            r'tongji\.baidu\.com/hm-web',
            r'hm\.baidu\.com/hm\.js',
            r'hm\.baidu\.com/hm\.gif',
            r'hm\.baidu\.com/hm\.js\?',
            r'_hmt\.push',
            r'hm\.baidu\.com'
        ]
        
        found_codes = []
        for pattern in baidu_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                found_codes.extend(matches)
        
        if found_codes:
            print("✅ 找到百度统计代码:")
            for code in set(found_codes):
                print(f"  - {code}")
        else:
            print("❌ 未找到百度统计代码")
        
        # 检查其他统计代码
        other_stats = [
            'google-analytics.com',
            'gtag',
            'ga(',
            'googletagmanager.com',
            'cnzz.com',
            '51.la'
        ]
        
        found_other = []
        for stat in other_stats:
            if stat.lower() in html_content.lower():
                found_other.append(stat)
        
        if found_other:
            print("找到其他统计代码:")
            for stat in found_other:
                print(f"  - {stat}")
        
        # 检查网站基本信息
        soup = BeautifulSoup(html_content, 'html.parser')
        title = soup.find('title')
        if title:
            print(f"网站标题: {title.get_text().strip()}")
        
        # 检查meta信息
        description = soup.find('meta', attrs={'name': 'description'})
        if description:
            print(f"网站描述: {description.get('content', '')[:100]}...")
        
        return len(found_codes) > 0
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

def main():
    """主函数"""
    websites = [
        "https://www.shjingjun.com",
        "https://shjingjun.com"
    ]
    
    print("检查网站百度统计代码安装情况")
    print("=" * 50)
    
    for url in websites:
        print(f"\n检查: {url}")
        print("-" * 30)
        has_baidu = check_baidu_analytics_code(url)
        
        if has_baidu:
            print("✅ 该网站已安装百度统计代码")
        else:
            print("❌ 该网站未安装百度统计代码")
            print("建议:")
            print("1. 登录百度统计后台")
            print("2. 获取统计代码")
            print("3. 将代码添加到网站</head>标签前")

if __name__ == "__main__":
    main()

