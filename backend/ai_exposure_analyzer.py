#!/usr/bin/env python3
"""
AI大模型曝光率分析器
用于分析各种AI大模型对网站的曝光率和问题收录情况
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
from dataclasses import dataclass

@dataclass
class AIPlatformData:
    """AI平台数据结构"""
    platform_name: str
    total_questions: int
    included_questions: int
    desktop_questions: int
    mobile_questions: int
    exposure_rate: float
    brand_keywords: int
    last_updated: str

@dataclass
class QuestionData:
    """问题数据结构"""
    id: int
    training_word: str
    question: str
    platform: str
    source: str  # 移动端/电脑端
    launch_time: str
    category: str = ""

class AIExposureAnalyzer:
    """AI大模型曝光率分析器"""
    
    def __init__(self, data_file: str = "rag_storage/ai_exposure_data.json"):
        self.data_file = data_file
        self.platforms = [
            "Deepseek", "豆包", "通义", "元宝", "KIMI", 
            "文心一言", "ChatGPT", "Claude", "Gemini"
        ]
        self.ensure_data_file()
    
    def ensure_data_file(self):
        """确保数据文件存在"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            self.init_sample_data()
    
    def init_sample_data(self):
        """初始化示例数据（基于图片中的数据）"""
        sample_data = {
            "summary": {
                "total_questions": 20000,
                "included_questions": 8732,
                "brand_keywords": 25,
                "covered_platforms": 5,
                "last_updated": datetime.now().isoformat()
            },
            "platforms": {
                "Deepseek": {
                    "total_questions": 3609,
                    "included_questions": 3609,
                    "desktop_questions": 1802,
                    "mobile_questions": 1807,
                    "exposure_rate": 41.33,
                    "brand_keywords": 8,
                    "last_updated": datetime.now().isoformat()
                },
                "豆包": {
                    "total_questions": 245,
                    "included_questions": 245,
                    "desktop_questions": 124,
                    "mobile_questions": 121,
                    "exposure_rate": 2.81,
                    "brand_keywords": 3,
                    "last_updated": datetime.now().isoformat()
                },
                "通义": {
                    "total_questions": 250,
                    "included_questions": 250,
                    "desktop_questions": 126,
                    "mobile_questions": 124,
                    "exposure_rate": 2.86,
                    "brand_keywords": 2,
                    "last_updated": datetime.now().isoformat()
                },
                "元宝": {
                    "total_questions": 2247,
                    "included_questions": 2247,
                    "desktop_questions": 1125,
                    "mobile_questions": 1122,
                    "exposure_rate": 25.73,
                    "brand_keywords": 6,
                    "last_updated": datetime.now().isoformat()
                },
                "KIMI": {
                    "total_questions": 2381,
                    "included_questions": 2381,
                    "desktop_questions": 1191,
                    "mobile_questions": 1190,
                    "exposure_rate": 27.27,
                    "brand_keywords": 6,
                    "last_updated": datetime.now().isoformat()
                }
            },
            "questions": [
                {
                    "id": 1,
                    "training_word": "柚木柜",
                    "question": "柚木柜厂家推荐",
                    "platform": "元宝",
                    "source": "移动端",
                    "launch_time": "2025-01-18",
                    "category": "产品推荐"
                },
                {
                    "id": 2,
                    "training_word": "柚木柜",
                    "question": "柚木柜厂家排行",
                    "platform": "KIMI",
                    "source": "电脑端",
                    "launch_time": "2025-01-18",
                    "category": "厂家排行"
                },
                {
                    "id": 3,
                    "training_word": "抛光白膏",
                    "question": "抛光白膏使用方法",
                    "platform": "Deepseek",
                    "source": "移动端",
                    "launch_time": "2025-01-17",
                    "category": "使用方法"
                },
                {
                    "id": 4,
                    "training_word": "抛光布轮",
                    "question": "抛光布轮价格",
                    "platform": "豆包",
                    "source": "电脑端",
                    "launch_time": "2025-01-17",
                    "category": "价格咨询"
                },
                {
                    "id": 5,
                    "training_word": "尼龙打磨片",
                    "question": "尼龙打磨片规格",
                    "platform": "通义",
                    "source": "移动端",
                    "launch_time": "2025-01-16",
                    "category": "规格参数"
                }
            ],
            "brand_keywords": [
                "静钧抛光", "静钧布轮", "静钧打磨", "静钧抛光膏", "静钧尼龙片",
                "静钧海绵轮", "静钧麻轮", "静钧风布轮", "静钧抛光轮", "静钧打磨片",
                "静钧抛光白膏", "静钧抛光布轮", "静钧尼龙打磨片", "静钧海绵抛光轮",
                "静钧抛光风布轮", "静钧生产", "静钧厂家", "静钧推荐", "静钧排行",
                "静钧价格", "静钧规格", "静钧使用方法", "静钧技术", "静钧质量",
                "静钧服务"
            ]
        }
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    def load_data(self) -> Dict:
        """加载数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载数据失败: {e}")
            return {}
    
    def save_data(self, data: Dict):
        """保存数据"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存数据失败: {e}")
            return False
    
    def get_summary_stats(self) -> Dict:
        """获取汇总统计信息"""
        data = self.load_data()
        return data.get("summary", {})
    
    def get_platform_stats(self) -> List[Dict]:
        """获取各平台统计信息"""
        data = self.load_data()
        platforms = data.get("platforms", {})
        
        result = []
        for platform_name, platform_data in platforms.items():
            result.append({
                "platform": platform_name,
                "total_questions": platform_data.get("total_questions", 0),
                "included_questions": platform_data.get("included_questions", 0),
                "desktop_questions": platform_data.get("desktop_questions", 0),
                "mobile_questions": platform_data.get("mobile_questions", 0),
                "exposure_rate": platform_data.get("exposure_rate", 0.0),
                "brand_keywords": platform_data.get("brand_keywords", 0),
                "last_updated": platform_data.get("last_updated", "")
            })
        
        # 按曝光率排序
        result.sort(key=lambda x: x["exposure_rate"], reverse=True)
        return result
    
    def get_questions_data(self, platform: str = None, source: str = None, 
                          search_term: str = None) -> List[Dict]:
        """获取问题数据"""
        data = self.load_data()
        questions = data.get("questions", [])
        
        # 过滤条件
        if platform:
            questions = [q for q in questions if q.get("platform") == platform]
        
        if source:
            questions = [q for q in questions if q.get("source") == source]
        
        if search_term:
            questions = [q for q in questions if 
                        search_term.lower() in q.get("question", "").lower() or
                        search_term.lower() in q.get("training_word", "").lower()]
        
        return questions
    
    def get_brand_keywords(self) -> List[str]:
        """获取品牌关键词列表"""
        data = self.load_data()
        return data.get("brand_keywords", [])
    
    def add_question(self, training_word: str, question: str, platform: str, 
                    source: str, category: str = "") -> bool:
        """添加新问题"""
        data = self.load_data()
        questions = data.get("questions", [])
        
        # 生成新ID
        new_id = max([q.get("id", 0) for q in questions], default=0) + 1
        
        new_question = {
            "id": new_id,
            "training_word": training_word,
            "question": question,
            "platform": platform,
            "source": source,
            "launch_time": datetime.now().strftime("%Y-%m-%d"),
            "category": category
        }
        
        questions.append(new_question)
        data["questions"] = questions
        
        # 更新平台统计
        if platform in data.get("platforms", {}):
            platform_data = data["platforms"][platform]
            platform_data["total_questions"] += 1
            platform_data["included_questions"] += 1
            if source == "电脑端":
                platform_data["desktop_questions"] += 1
            else:
                platform_data["mobile_questions"] += 1
            platform_data["last_updated"] = datetime.now().isoformat()
        
        # 更新汇总统计
        data["summary"]["total_questions"] += 1
        data["summary"]["included_questions"] += 1
        data["summary"]["last_updated"] = datetime.now().isoformat()
        
        return self.save_data(data)
    
    def update_platform_stats(self, platform: str, stats: Dict) -> bool:
        """更新平台统计信息"""
        data = self.load_data()
        if "platforms" not in data:
            data["platforms"] = {}
        
        data["platforms"][platform] = {
            "total_questions": stats.get("total_questions", 0),
            "included_questions": stats.get("included_questions", 0),
            "desktop_questions": stats.get("desktop_questions", 0),
            "mobile_questions": stats.get("mobile_questions", 0),
            "exposure_rate": stats.get("exposure_rate", 0.0),
            "brand_keywords": stats.get("brand_keywords", 0),
            "last_updated": datetime.now().isoformat()
        }
        
        return self.save_data(data)
    
    def calculate_exposure_rates(self) -> Dict[str, float]:
        """计算各平台曝光率"""
        data = self.load_data()
        platforms = data.get("platforms", {})
        total_included = data.get("summary", {}).get("included_questions", 0)
        
        if total_included == 0:
            return {}
        
        exposure_rates = {}
        for platform, platform_data in platforms.items():
            included = platform_data.get("included_questions", 0)
            rate = (included / total_included) * 100
            exposure_rates[platform] = round(rate, 2)
        
        return exposure_rates
    
    def get_platform_contribution_chart_data(self) -> Dict:
        """获取平台贡献图表数据"""
        platforms = self.get_platform_stats()
        
        chart_data = {
            "labels": [p["platform"] for p in platforms],
            "datasets": [{
                "label": "问题数量",
                "data": [p["included_questions"] for p in platforms],
                "backgroundColor": [
                    "#3498db", "#e74c3c", "#f39c12", "#9b59b6", "#1abc9c",
                    "#34495e", "#e67e22", "#2ecc71", "#8e44ad"
                ]
            }]
        }
        
        return chart_data
    
    def get_device_distribution_data(self) -> Dict:
        """获取设备分布数据"""
        platforms = self.get_platform_stats()
        
        desktop_data = []
        mobile_data = []
        labels = []
        
        for platform in platforms:
            labels.append(platform["platform"])
            desktop_data.append(platform["desktop_questions"])
            mobile_data.append(platform["mobile_questions"])
        
        return {
            "labels": labels,
            "datasets": [
                {
                    "label": "电脑端",
                    "data": desktop_data,
                    "backgroundColor": "#3498db"
                },
                {
                    "label": "移动端", 
                    "data": mobile_data,
                    "backgroundColor": "#e74c3c"
                }
            ]
        }
    
    def search_questions(self, keyword: str, platform: str = None) -> List[Dict]:
        """搜索问题"""
        questions = self.get_questions_data(platform=platform)
        
        if not keyword:
            return questions
        
        # 模糊搜索
        results = []
        keyword_lower = keyword.lower()
        
        for question in questions:
            if (keyword_lower in question.get("question", "").lower() or
                keyword_lower in question.get("training_word", "").lower() or
                keyword_lower in question.get("category", "").lower()):
                results.append(question)
        
        return results
    
    def export_data(self, format: str = "json") -> str:
        """导出数据"""
        data = self.load_data()
        
        if format == "json":
            return json.dumps(data, ensure_ascii=False, indent=2)
        elif format == "csv":
            # 简单的CSV导出
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 写入问题数据
            writer.writerow(["ID", "训练词", "问题", "平台", "来源", "上线时间", "分类"])
            for question in data.get("questions", []):
                writer.writerow([
                    question.get("id", ""),
                    question.get("training_word", ""),
                    question.get("question", ""),
                    question.get("platform", ""),
                    question.get("source", ""),
                    question.get("launch_time", ""),
                    question.get("category", "")
                ])
            
            return output.getvalue()
        
        return ""

def main():
    """主函数 - 测试功能"""
    analyzer = AIExposureAnalyzer()
    
    # 获取汇总统计
    summary = analyzer.get_summary_stats()
    print("汇总统计:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    
    # 获取平台统计
    platforms = analyzer.get_platform_stats()
    print("\n平台统计:")
    for platform in platforms:
        print(f"{platform['platform']}: {platform['exposure_rate']}% ({platform['included_questions']}条)")
    
    # 获取问题数据
    questions = analyzer.get_questions_data()
    print(f"\n问题数据: {len(questions)}条")
    
    # 搜索测试
    search_results = analyzer.search_questions("柚木柜")
    print(f"\n搜索'柚木柜'结果: {len(search_results)}条")

if __name__ == "__main__":
    main()
