#!/usr/bin/env python3
"""
测试智能文章生成系统
演示如何根据点击量和转化率生成优化内容
"""

import json
from wordpress_article_generator import WordPressArticleGenerator

def test_keyword_scoring():
    """测试关键词评分算法"""
    print("=== 关键词智能评分测试 ===\n")
    
    # 加载推广数据
    with open("baidu_promotion_data.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    keywords = data["promotion_data"]["all_keywords"]
    
    # 创建生成器实例
    generator = WordPressArticleGenerator("", "", "")
    
    # 计算每个关键词的得分
    print("关键词评分结果（按综合得分排序）：")
    print("-" * 80)
    
    for keyword_data in keywords:
        score = generator.calculate_keyword_score(keyword_data)
        keyword_data["score"] = score
        
        # 计算转化率
        conversion_rate = (keyword_data["pv"] / keyword_data["clicks"]) if keyword_data["clicks"] > 0 else 0
        
        print(f"关键词: {keyword_data['keyword']}")
        print(f"  得分: {score:.2f}")
        print(f"  点击: {keyword_data['clicks']} | 浏览: {keyword_data['pv']} | 转化率: {conversion_rate:.1%}")
        print(f"  跳出率: {keyword_data['bounce_rate']}% | 访问时长: {keyword_data['visit_duration']}")
        print(f"  消费: ¥{keyword_data['cost']} | 分类: {keyword_data['category']}")
        print()
    
    # 按得分排序
    keywords.sort(key=lambda x: x["score"], reverse=True)
    
    print("排序后的关键词（前5名）：")
    print("-" * 50)
    for i, kw in enumerate(keywords[:5]):
        print(f"{i+1}. {kw['keyword']} - 得分: {kw['score']:.2f}")

def test_content_generation():
    """测试内容生成策略"""
    print("\n=== 智能内容生成测试 ===\n")
    
    # 测试数据
    test_keywords = [
        {
            "keyword": "抛光白膏",
            "cost": 154.24,
            "clicks": 108,
            "pv": 23,
            "bounce_rate": 37.5,
            "visit_duration": "00:03:49",
            "category": "膏-产品词"
        },
        {
            "keyword": "抛光风布轮厂家",
            "cost": 22.81,
            "clicks": 12,
            "pv": 48,
            "bounce_rate": 0.0,
            "visit_duration": "00:15:50",
            "category": "布轮-厂家词"
        }
    ]
    
    generator = WordPressArticleGenerator("", "", "")
    
    for i, keyword_data in enumerate(test_keywords):
        print(f"=== 测试案例 {i+1}: {keyword_data['keyword']} ===")
        
        # 计算得分
        score = generator.calculate_keyword_score(keyword_data)
        keyword_data["score"] = score
        
        # 生成文章内容
        article_data = generator.generate_article_content(keyword_data)
        
        print(f"标题: {article_data['title']}")
        print(f"得分: {score:.2f}")
        print(f"转化率: {article_data['conversion_rate']:.1%}")
        print(f"内容策略: {'高转化率优化' if article_data['conversion_rate'] > 0.5 else '标准内容'}")
        print(f"摘要: {article_data['excerpt']}")
        print()

def main():
    """主函数"""
    print("GEO平台智能文章生成系统测试")
    print("=" * 50)
    
    # 测试关键词评分
    test_keyword_scoring()
    
    # 测试内容生成
    test_content_generation()
    
    print("\n=== 测试完成 ===")
    print("系统已准备好根据点击量和转化率智能生成WordPress文章！")

if __name__ == "__main__":
    main()
