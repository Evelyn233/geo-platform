#!/usr/bin/env python3
"""
测试搜索功能
"""

from enhanced_article_generator import EnhancedArticleGenerator

def test_search_functionality():
    """测试搜索功能"""
    print("=" * 60)
    print("🔍 测试搜索功能")
    print("=" * 60)
    
    # 创建增强版文章生成器实例
    generator = EnhancedArticleGenerator("", "", "")
    
    # 测试关键词
    test_keywords = ["抛光轮", "抛光布轮", "抛光麻轮"]
    
    for keyword in test_keywords:
        print(f"\n📝 测试关键词: {keyword}")
        print("-" * 40)
        
        # 测试联网搜索
        print("1. 测试联网搜索...")
        web_results = generator.search_web_content(keyword)
        print(f"   联网搜索结果: {len(web_results)} 个")
        for i, result in enumerate(web_results[:2]):  # 只显示前2个结果
            print(f"   {i+1}. {result['title']} ({result['source']})")
        
        # 测试百度搜索
        print("2. 测试百度搜索...")
        baidu_results = generator.search_baidu_content(keyword)
        print(f"   百度搜索结果: {len(baidu_results)} 个")
        for i, result in enumerate(baidu_results[:2]):  # 只显示前2个结果
            print(f"   {i+1}. {result['title']} ({result['source']})")
        
        # 测试备用搜索
        print("3. 测试备用搜索...")
        fallback_results = generator._fallback_search(keyword)
        print(f"   备用搜索结果: {len(fallback_results)} 个")
        for i, result in enumerate(fallback_results[:2]):  # 只显示前2个结果
            print(f"   {i+1}. {result['title']} ({result['source']})")
        
        print()

def test_enhanced_article_generation():
    """测试增强版文章生成"""
    print("=" * 60)
    print("📝 测试增强版文章生成")
    print("=" * 60)
    
    # 创建增强版文章生成器实例
    generator = EnhancedArticleGenerator("", "", "")
    
    # 模拟关键词数据
    keyword_data = {
        "keyword": "抛光轮",
        "clicks": 17,
        "pv": 45,
        "bounce_rate": 0.15,
        "visit_duration": 180,
        "cost": 25.5,
        "conversion_rate": 0.85
    }
    
    print(f"测试关键词: {keyword_data['keyword']}")
    print(f"数据: 点击{keyword_data['clicks']}, 浏览{keyword_data['pv']}, 跳出率{keyword_data['bounce_rate']*100}%")
    
    try:
        # 测试增强版文章生成
        result = generator.enhance_article_with_search(keyword_data)
        
        print("\n✅ 增强版文章生成成功!")
        print(f"标题: {result['title']}")
        print(f"摘要: {result['excerpt'][:100]}...")
        print(f"内容长度: {len(result['content'])} 字符")
        
        if result.get('search_results'):
            print(f"搜索来源: {len(result['search_results'])} 个")
            for i, search_result in enumerate(result['search_results'][:2]):
                print(f"  {i+1}. {search_result['source']}: {search_result['title']}")
        
    except Exception as e:
        print(f"❌ 增强版文章生成失败: {e}")

if __name__ == "__main__":
    test_search_functionality()
    test_enhanced_article_generation()


