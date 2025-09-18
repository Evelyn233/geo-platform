#!/usr/bin/env python3
"""
百度统计API集成
获取网站SEO数据和统计信息
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

class BaiduAnalytics:
    def __init__(self, access_token: str, username: str = "default"):
        """
        初始化百度统计API
        
        Args:
            access_token: 百度统计API的访问令牌
            username: 用户名
        """
        self.access_token = access_token
        self.username = username
        # 使用百度商业账号API地址
        self.base_url = "https://api.baidu.com/json/tongji/v1/ReportService"
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, body: Dict = None) -> Dict:
        """发送API请求"""
        data = {
            "header": {
                "userName": self.username,
                "accessToken": self.access_token
            },
            "body": body or {}
        }
        
        try:
            print(f"发送请求到: {self.base_url}/{method}")
            print(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            response = requests.post(
                f"{self.base_url}/{method}",
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API请求失败: {e}")
            return {"error": str(e)}
    
    def get_site_list(self) -> List[Dict]:
        """获取站点列表"""
        result = self._make_request("getSiteList")
        
        if "error" in result:
            return []
        
        # 解析站点数据
        data = result.get("body", {}).get("data", [])
        sites = []
        if data and len(data) > 0:
            site_list = data[0].get("list", [])
            for site in site_list:
                sites.append({
                    "site_id": site.get("site_id"),
                    "domain": site.get("domain"),
                    "status": site.get("status"),
                    "create_time": site.get("create_time")
                })
        
        print(f"获取到 {len(sites)} 个站点")
        for site in sites:
            print(f"  - 站点ID: {site['site_id']}, 域名: {site['domain']}")
        return sites
    
    def get_site_info(self, site_id: str) -> Dict:
        """获取站点详细信息"""
        body = {"siteId": site_id}
        result = self._make_request("getSiteInfo", body)
        
        if "error" in result:
            return {}
        
        return result.get("body", {}).get("data", {})
    
    def get_trend_data(self, site_id: str, start_date: str = None, end_date: str = None) -> Dict:
        """获取趋势数据"""
        if not start_date:
            start_date = (datetime.now() - timedelta(days=180)).strftime("%Y%m%d")  # 改为180天（半年）
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        
        body = {
            "siteId": site_id,
            "startDate": start_date,
            "endDate": end_date,
            "metrics": "pv_count,visitor_count,ip_count,bounce_ratio,avg_visit_time",
            "gran": "day",
            "method": "trend/time/a"  # 添加method参数
        }
        
        result = self._make_request("getData", body)
        
        if "error" in result:
            return {}
        
        return result.get("body", {}).get("data", {})
    
    def get_source_data(self, site_id: str, start_date: str = None, end_date: str = None) -> Dict:
        """获取来源数据"""
        if not start_date:
            start_date = (datetime.now() - timedelta(days=180)).strftime("%Y%m%d")  # 改为180天（半年）
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        
        body = {
            "siteId": site_id,
            "startDate": start_date,
            "endDate": end_date,
            "metrics": "pv_count,visitor_count",
            "gran": "day",
            "source": "all",
            "method": "source/all/a"  # 添加method参数
        }
        
        result = self._make_request("getData", body)
        
        if "error" in result:
            return {}
        
        return result.get("body", {}).get("data", {})
    
    def get_keyword_data(self, site_id: str, start_date: str = None, end_date: str = None) -> Dict:
        """获取关键词数据"""
        if not start_date:
            start_date = (datetime.now() - timedelta(days=180)).strftime("%Y%m%d")  # 改为180天（半年）
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        
        body = {
            "siteId": site_id,
            "startDate": start_date,
            "endDate": end_date,
            "metrics": "pv_count,visitor_count",
            "gran": "day",
            "source": "search_engine",
            "method": "source/search_engine/a"  # 添加method参数
        }
        
        result = self._make_request("getData", body)
        
        if "error" in result:
            return {}
        
        return result.get("body", {}).get("data", {})
    
    def get_all_data(self, site_id: str = None) -> Dict:
        """获取所有数据"""
        # 如果没有指定站点ID，先获取站点列表
        if not site_id:
            sites = self.get_site_list()
            if not sites:
                return {"error": "无法获取站点列表"}
            site_id = sites[0]["site_id"]  # 使用第一个站点
        
        print(f"正在获取站点 {site_id} 的数据...")
        
        # 获取各种数据
        data = {
            "site_id": site_id,
            "site_info": self.get_site_info(site_id),
            "trend_data": self.get_trend_data(site_id),
            "source_data": self.get_source_data(site_id),
            "keyword_data": self.get_keyword_data(site_id),
            "fetch_time": datetime.now().isoformat()
        }
        
        return data

def main():
    """主函数"""
    # 你的百度统计API令牌
    access_token = "eyJhbGciOiJIUzM4NCJ9.eyJzdWIiOiJhY2MiLCJhdWQiOiLnmb7luqbnu5_orqEiLCJ1aWQiOjI0NTk4OTkzLCJhcHBJZCI6IjEzYmQ1MDQ5YTY3NmQxMDczNzk1OTkzMjEwMmVjNTU3IiwiaXNzIjoi5ZWG5Lia5byA5Y-R6ICF5Lit5b-DIiwicGxhdGZvcm1JZCI6IjQ5NjAzNDU5NjU5NTg1NjE3OTQiLCJleHAiOjE3NjA0NDcyNzAsImp0aSI6Ii04Mzk3MzE5MjkzMTc2MjU4NTA0In0.oOkSqxODhCqNUKpTtpwjwVBFyReTkUFXTww7RuklaeIwazIRHHWu9CdDXJR1FtfR"
    
    # 创建百度统计实例，使用正确的用户名
    baidu = BaiduAnalytics(access_token, "sh静钧")
    
    # 获取所有数据
    data = baidu.get_all_data()
    
    if "error" in data:
        print(f"获取数据失败: {data['error']}")
        return
    
    # 保存数据
    output_file = "./rag_storage/baidu_analytics_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"百度统计数据已保存到: {output_file}")
    
    # 打印摘要信息
    site_info = data.get("site_info", {})
    trend_data = data.get("trend_data", {})
    
    print(f"\n站点信息:")
    if isinstance(site_info, dict):
        print(f"站点名称: {site_info.get('site_name', 'N/A')}")
        print(f"站点URL: {site_info.get('domain', 'N/A')}")
    else:
        print(f"站点信息: {site_info}")
    
    if trend_data and isinstance(trend_data, dict):
        print(f"\n最近30天数据:")
        sum_data = trend_data.get('sum', {})
        if isinstance(sum_data, dict):
            print(f"总PV: {sum_data.get('pv_count', 'N/A')}")
            print(f"总访客: {sum_data.get('visitor_count', 'N/A')}")
            print(f"总IP: {sum_data.get('ip_count', 'N/A')}")
        else:
            print(f"趋势数据: {trend_data}")
    else:
        print(f"\n趋势数据: {trend_data}")

if __name__ == "__main__":
    main()
