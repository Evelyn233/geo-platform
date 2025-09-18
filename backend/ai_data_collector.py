#!/usr/bin/env python3
"""
AI大模型数据采集器
用于采集各种AI大模型平台的问题和曝光数据
"""

import json
import time
import random
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from ai_exposure_analyzer import AIExposureAnalyzer

class AIDataCollector:
    """AI大模型数据采集器"""
    
    def __init__(self, analyzer: AIExposureAnalyzer):
        self.analyzer = analyzer
        self.platforms = [
            "Deepseek", "豆包", "通义", "元宝", "KIMI", 
            "文心一言", "ChatGPT", "Claude", "Gemini"
        ]
        
        # 模拟的品牌关键词
        self.brand_keywords = [
            "静钧抛光", "静钧布轮", "静钧打磨", "静钧抛光膏", "静钧尼龙片",
            "静钧海绵轮", "静钧麻轮", "静钧风布轮", "静钧抛光轮", "静钧打磨片",
            "静钧抛光白膏", "静钧抛光布轮", "静钧尼龙打磨片", "静钧海绵抛光轮",
            "静钧抛光风布轮", "静钧生产", "静钧厂家", "静钧推荐", "静钧排行",
            "静钧价格", "静钧规格", "静钧使用方法", "静钧技术", "静钧质量",
            "静钧服务"
        ]
        
        # 模拟的问题模板
        self.question_templates = [
            "{keyword}厂家推荐",
            "{keyword}厂家排行", 
            "{keyword}价格",
            "{keyword}规格",
            "{keyword}使用方法",
            "{keyword}质量怎么样",
            "{keyword}哪里买",
            "{keyword}批发",
            "{keyword}定制",
            "{keyword}技术参数",
            "{keyword}生产工艺",
            "{keyword}应用领域",
            "{keyword}优势特点",
            "{keyword}售后服务",
            "{keyword}联系方式"
        ]
    
    def generate_mock_data(self, days: int = 30) -> Dict:
        """生成模拟数据"""
        print(f"开始生成过去{days}天的模拟数据...")
        
        # 生成问题数据
        questions = []
        question_id = 1
        
        # 为每个平台生成不同数量的问题
        platform_weights = {
            "Deepseek": 0.35,    # 35%
            "元宝": 0.25,        # 25%
            "KIMI": 0.25,        # 25%
            "豆包": 0.08,        # 8%
            "通义": 0.07         # 7%
        }
        
        total_questions = random.randint(15000, 25000)
        
        for platform, weight in platform_weights.items():
            platform_questions = int(total_questions * weight)
            
            for i in range(platform_questions):
                # 随机选择品牌关键词
                keyword = random.choice(self.brand_keywords)
                
                # 随机选择问题模板
                template = random.choice(self.question_templates)
                question = template.format(keyword=keyword)
                
                # 随机选择设备类型
                source = random.choice(["电脑端", "移动端"])
                
                # 随机生成日期（过去30天内）
                days_ago = random.randint(0, days)
                launch_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
                
                # 随机分类
                category = random.choice([
                    "产品推荐", "厂家排行", "价格咨询", "规格参数", 
                    "使用方法", "质量评价", "购买渠道", "技术咨询"
                ])
                
                questions.append({
                    "id": question_id,
                    "training_word": keyword,
                    "question": question,
                    "platform": platform,
                    "source": source,
                    "launch_time": launch_date,
                    "category": category
                })
                
                question_id += 1
        
        # 计算平台统计
        platform_stats = {}
        for platform in self.platforms:
            platform_questions = [q for q in questions if q["platform"] == platform]
            desktop_questions = len([q for q in platform_questions if q["source"] == "电脑端"])
            mobile_questions = len([q for q in platform_questions if q["source"] == "移动端"])
            
            platform_stats[platform] = {
                "total_questions": len(platform_questions),
                "included_questions": len(platform_questions),
                "desktop_questions": desktop_questions,
                "mobile_questions": mobile_questions,
                "exposure_rate": 0.0,  # 稍后计算
                "brand_keywords": len(set([q["training_word"] for q in platform_questions])),
                "last_updated": datetime.now().isoformat()
            }
        
        # 计算曝光率
        total_included = sum(stats["included_questions"] for stats in platform_stats.values())
        for platform, stats in platform_stats.items():
            if total_included > 0:
                stats["exposure_rate"] = round((stats["included_questions"] / total_included) * 100, 2)
        
        # 生成汇总数据
        summary = {
            "total_questions": total_questions,
            "included_questions": total_included,
            "brand_keywords": len(self.brand_keywords),
            "covered_platforms": len([p for p in platform_stats.values() if p["included_questions"] > 0]),
            "last_updated": datetime.now().isoformat()
        }
        
        return {
            "summary": summary,
            "platforms": platform_stats,
            "questions": questions,
            "brand_keywords": self.brand_keywords
        }
    
    def collect_real_data(self, platform: str, keywords: List[str]) -> List[Dict]:
        """采集真实数据（需要各平台的API）"""
        print(f"开始从{platform}采集真实数据...")
        
        # 这里需要根据各平台的实际API来实现
        # 目前返回模拟数据
        questions = []
        
        for i, keyword in enumerate(keywords[:10]):  # 限制采集数量
            template = random.choice(self.question_templates)
            question = template.format(keyword=keyword)
            
            questions.append({
                "id": i + 1,
                "training_word": keyword,
                "question": question,
                "platform": platform,
                "source": random.choice(["电脑端", "移动端"]),
                "launch_time": datetime.now().strftime("%Y-%m-%d"),
                "category": random.choice(["产品推荐", "厂家排行", "价格咨询"])
            })
            
            # 添加延迟避免API限制
            time.sleep(0.5)
        
        return questions
    
    def update_data_from_collection(self, new_data: Dict):
        """更新数据"""
        print("更新AI曝光率数据...")
        
        # 保存新数据
        with open(self.analyzer.data_file, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        
        print(f"数据更新完成，共{len(new_data.get('questions', []))}个问题")
    
    def simulate_real_time_collection(self, interval_minutes: int = 60):
        """模拟实时数据采集"""
        print(f"开始模拟实时数据采集，间隔{interval_minutes}分钟...")
        
        while True:
            try:
                # 生成少量新数据
                new_questions = []
                for platform in random.sample(self.platforms, 3):  # 随机选择3个平台
                    keyword = random.choice(self.brand_keywords)
                    template = random.choice(self.question_templates)
                    question = template.format(keyword=keyword)
                    
                    new_questions.append({
                        "id": int(time.time()),  # 使用时间戳作为ID
                        "training_word": keyword,
                        "question": question,
                        "platform": platform,
                        "source": random.choice(["电脑端", "移动端"]),
                        "launch_time": datetime.now().strftime("%Y-%m-%d"),
                        "category": random.choice(["产品推荐", "厂家排行", "价格咨询"])
                    })
                
                # 添加到现有数据
                data = self.analyzer.load_data()
                if "questions" not in data:
                    data["questions"] = []
                
                data["questions"].extend(new_questions)
                
                # 更新平台统计
                for question in new_questions:
                    platform = question["platform"]
                    if platform not in data["platforms"]:
                        data["platforms"][platform] = {
                            "total_questions": 0,
                            "included_questions": 0,
                            "desktop_questions": 0,
                            "mobile_questions": 0,
                            "exposure_rate": 0.0,
                            "brand_keywords": 0,
                            "last_updated": datetime.now().isoformat()
                        }
                    
                    data["platforms"][platform]["total_questions"] += 1
                    data["platforms"][platform]["included_questions"] += 1
                    
                    if question["source"] == "电脑端":
                        data["platforms"][platform]["desktop_questions"] += 1
                    else:
                        data["platforms"][platform]["mobile_questions"] += 1
                
                # 重新计算曝光率
                total_included = sum(p["included_questions"] for p in data["platforms"].values())
                for platform_data in data["platforms"].values():
                    if total_included > 0:
                        platform_data["exposure_rate"] = round(
                            (platform_data["included_questions"] / total_included) * 100, 2
                        )
                
                # 更新汇总统计
                data["summary"]["total_questions"] = len(data["questions"])
                data["summary"]["included_questions"] = total_included
                data["summary"]["last_updated"] = datetime.now().isoformat()
                
                # 保存数据
                self.analyzer.save_data(data)
                
                print(f"实时采集完成，新增{len(new_questions)}个问题")
                
                # 等待下次采集
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("停止实时数据采集")
                break
            except Exception as e:
                print(f"实时采集出错: {e}")
                time.sleep(60)  # 出错后等待1分钟再试
    
    def collect_from_baidu_analytics(self, baidu_data: Dict) -> List[Dict]:
        """从百度统计数据中提取AI相关问题"""
        print("从百度统计数据中提取AI相关问题...")
        
        questions = []
        question_id = 1
        
        # 从百度推广数据中提取关键词
        keywords = []
        if "promotion_data" in baidu_data:
            for keyword_data in baidu_data["promotion_data"].get("all_keywords", []):
                keyword = keyword_data.get("keyword", "")
                if keyword and "静钧" in keyword:
                    keywords.append(keyword)
        
        # 为每个关键词生成问题
        for keyword in keywords:
            for platform in self.platforms[:5]:  # 只在前5个平台生成
                template = random.choice(self.question_templates)
                question = template.format(keyword=keyword)
                
                questions.append({
                    "id": question_id,
                    "training_word": keyword,
                    "question": question,
                    "platform": platform,
                    "source": random.choice(["电脑端", "移动端"]),
                    "launch_time": datetime.now().strftime("%Y-%m-%d"),
                    "category": "百度推广"
                })
                
                question_id += 1
        
        return questions
    
    def export_collection_report(self) -> Dict:
        """导出采集报告"""
        data = self.analyzer.load_data()
        
        report = {
            "collection_time": datetime.now().isoformat(),
            "total_questions": len(data.get("questions", [])),
            "platforms_count": len(data.get("platforms", {})),
            "brand_keywords_count": len(data.get("brand_keywords", [])),
            "platform_breakdown": {},
            "recent_questions": data.get("questions", [])[-10:],  # 最近10个问题
            "top_keywords": []
        }
        
        # 统计各平台问题数
        for platform, stats in data.get("platforms", {}).items():
            report["platform_breakdown"][platform] = {
                "questions": stats.get("included_questions", 0),
                "exposure_rate": stats.get("exposure_rate", 0.0)
            }
        
        # 统计热门关键词
        keyword_count = {}
        for question in data.get("questions", []):
            keyword = question.get("training_word", "")
            keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
        
        report["top_keywords"] = sorted(
            keyword_count.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        return report

def main():
    """主函数 - 测试数据采集"""
    analyzer = AIExposureAnalyzer()
    collector = AIDataCollector(analyzer)
    
    print("=== AI大模型数据采集器测试 ===")
    
    # 生成模拟数据
    mock_data = collector.generate_mock_data(days=30)
    
    # 更新数据
    collector.update_data_from_collection(mock_data)
    
    # 生成采集报告
    report = collector.export_collection_report()
    
    print(f"\n采集报告:")
    print(f"总问题数: {report['total_questions']}")
    print(f"平台数量: {report['platforms_count']}")
    print(f"品牌关键词数: {report['brand_keywords_count']}")
    
    print(f"\n平台分布:")
    for platform, stats in report['platform_breakdown'].items():
        print(f"  {platform}: {stats['questions']}个问题 ({stats['exposure_rate']}%)")
    
    print(f"\n热门关键词TOP5:")
    for keyword, count in report['top_keywords'][:5]:
        print(f"  {keyword}: {count}次")

if __name__ == "__main__":
    main()
