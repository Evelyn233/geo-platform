#!/usr/bin/env python3
"""
测试改进后的图片搜索功能
"""

from image_search import ImageSearcher
from local_image_library import LocalImageLibrary

def test_improved_image_search():
    """测试改进后的图片搜索"""
    print("=" * 80)
    print("🖼️ 测试改进后的图片搜索功能")
    print("=" * 80)
    
    # 创建图片搜索器
    searcher = ImageSearcher()
    
    # 测试关键词
    test_keywords = [
        "抛光风布轮厂家",
        "研磨材料供应商", 
        "工业抛光设备",
        "精密制造工具"
    ]
    
    for keyword in test_keywords:
        print(f"\n{'='*60}")
        print(f"🔍 测试关键词: {keyword}")
        print(f"{'='*60}")
        
        # 搜索图片
        images = searcher.search_images(keyword, max_results=3)
        
        if images:
            print(f"✅ 找到 {len(images)} 张图片:")
            for i, img in enumerate(images):
                print(f"\n  📸 图片 {i+1}:")
                print(f"     标题: {img['title']}")
                print(f"     URL: {img['url']}")
                print(f"     来源: {img['source']}")
                print(f"     质量评分: {img.get('quality_score', 0):.1f}/1.0")
                print(f"     标签: {', '.join(img.get('tags', []))}")
                
                # 检查图片质量
                quality_score = img.get('quality_score', 0)
                if quality_score > 0.8:
                    print(f"     ✅ 高质量图片")
                elif quality_score > 0.6:
                    print(f"     ⚠️ 中等质量图片")
                else:
                    print(f"     ❌ 低质量图片")
        else:
            print("❌ 未找到任何图片")
    
    print(f"\n{'='*80}")
    print("🎯 图片搜索功能测试完成！")
    print("=" * 80)

def test_local_library():
    """测试本地图片库"""
    print("\n" + "=" * 80)
    print("📚 测试本地图片库功能")
    print("=" * 80)
    
    # 创建本地图片库
    library = LocalImageLibrary()
    
    # 初始化库
    print("正在初始化本地图片库...")
    library.initialize_library()
    
    # 测试搜索
    test_keywords = ['抛光', '研磨', '厂家', '工业']
    
    for keyword in test_keywords:
        print(f"\n搜索关键词: {keyword}")
        images = library.get_industrial_images(keyword, 2)
        
        print(f"找到 {len(images)} 张图片:")
        for i, img in enumerate(images):
            print(f"  {i+1}. {img['title']}")
            print(f"     标签: {', '.join(img.get('tags', []))}")
            print(f"     质量评分: {img.get('quality_score', 0):.1f}")

def test_image_quality():
    """测试图片质量评分"""
    print("\n" + "=" * 80)
    print("⭐ 测试图片质量评分")
    print("=" * 80)
    
    searcher = ImageSearcher()
    
    # 测试不同来源的图片质量
    test_images = [
        {
            'url': 'https://example.com/image1.jpg',
            'title': 'Pixabay专业图片',
            'source': 'Pixabay',
            'alt': '专业工业图片'
        },
        {
            'url': 'https://example.com/image2.jpg',
            'title': '本地库图片',
            'source': 'Local Library',
            'alt': '本地工业图片'
        },
        {
            'url': 'https://placeholder.com/image3.jpg',
            'title': '占位符图片',
            'source': 'Placeholder',
            'alt': '占位符图片'
        }
    ]
    
    for img in test_images:
        quality_score = searcher._calculate_image_quality(img)
        print(f"图片: {img['title']}")
        print(f"来源: {img['source']}")
        print(f"质量评分: {quality_score:.2f}/1.0")
        
        if quality_score > 0.8:
            print("评级: ⭐⭐⭐⭐⭐ 优秀")
        elif quality_score > 0.6:
            print("评级: ⭐⭐⭐⭐ 良好")
        elif quality_score > 0.4:
            print("评级: ⭐⭐⭐ 一般")
        else:
            print("评级: ⭐⭐ 较差")
        print()

if __name__ == "__main__":
    print("选择测试模式:")
    print("1. 完整图片搜索测试")
    print("2. 本地图片库测试")
    print("3. 图片质量评分测试")
    print("4. 全部测试")
    
    choice = input("请输入选择 (1/2/3/4): ").strip()
    
    if choice == "1":
        test_improved_image_search()
    elif choice == "2":
        test_local_library()
    elif choice == "3":
        test_image_quality()
    elif choice == "4":
        test_improved_image_search()
        test_local_library()
        test_image_quality()
    else:
        print("无效选择，运行完整测试...")
        test_improved_image_search()
        test_local_library()
        test_image_quality()

