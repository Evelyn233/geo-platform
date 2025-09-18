#!/usr/bin/env python3
"""
WordPress文章自动生成系统
基于百度推广排名数据生成SEO优化文章
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class WordPressArticleGenerator:
    def __init__(self, wp_url: str, username: str, password: str):
        """
        初始化WordPress文章生成器
        
        Args:
            wp_url: WordPress网站URL
            username: WordPress用户名
            password: WordPress密码或应用密码
        """
        self.wp_url = wp_url.rstrip('/')
        self.username = username
        self.password = password
        self.api_url = f"{self.wp_url}/wp-json/wp/v2"
        
    def test_connection(self) -> bool:
        """测试WordPress连接"""
        try:
            response = requests.get(f"{self.api_url}/posts", auth=(self.username, self.password))
            return response.status_code == 200
        except Exception as e:
            print(f"连接测试失败: {e}")
            return False
    
    def load_promotion_data(self) -> Dict:
        """加载百度推广数据"""
        try:
            # 尝试多个可能的路径
            possible_paths = [
                "baidu_promotion_data.json",
                "rag_storage/baidu_promotion_data.json",
                "../baidu_promotion_data.json"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        return json.load(f)
            
            print(f"未找到推广数据文件，尝试的路径: {possible_paths}")
            return {}
        except Exception as e:
            print(f"加载推广数据失败: {e}")
            return {}
    
    def generate_article_content(self, keyword_data: Dict) -> Dict:
        """基于关键词数据生成文章内容，根据点击量和转化率优化内容策略"""
        
        keyword = keyword_data['keyword']
        cost = keyword_data['cost']
        clicks = keyword_data['clicks']
        pv = keyword_data['pv']
        bounce_rate = keyword_data['bounce_rate']
        visit_duration = keyword_data['visit_duration']
        category = keyword_data['category']
        score = keyword_data.get('score', 0)
        
        # 计算转化率
        conversion_rate = (pv / clicks) if clicks > 0 else 0
        
        # 根据数据表现调整内容策略
        if score > 50:  # 高得分关键词
            title_style = "热门"
            content_focus = "专业性和权威性"
            call_to_action = "立即咨询"
        elif score > 30:  # 中等得分关键词
            title_style = "专业"
            content_focus = "产品特性和应用"
            call_to_action = "了解更多"
        else:  # 低得分关键词
            title_style = "优质"
            content_focus = "基础介绍和优势"
            call_to_action = "联系我们"
        
        # 根据跳出率调整内容结构
        if bounce_rate > 60:  # 高跳出率，需要更吸引人的开头
            opening_strategy = "问题导向"
            content_structure = "问题-解决方案-产品-案例"
        else:  # 低跳出率，用户已经感兴趣
            opening_strategy = "价值导向"
            content_structure = "价值-产品-技术-服务"
        
        # 生成文章标题
        if "厂家" in keyword or "供应商" in keyword:
            title = f"{keyword} - 上海静钧研磨{title_style}供应商"
        elif "生产" in keyword:
            title = f"{keyword} - 上海静钧研磨专业制造商"
        else:
            title = f"{keyword} - 上海静钧研磨{title_style}产品"
        
        # 根据内容策略生成文章
        if opening_strategy == "问题导向":
            opening = f"""
<p>在寻找优质的{keyword}时，您是否遇到过以下问题？</p>
<ul>
<li>产品质量不稳定，影响加工效果？</li>
<li>供应商响应慢，影响生产进度？</li>
<li>价格不透明，难以控制成本？</li>
<li>技术支持不到位，使用效果不佳？</li>
</ul>
<p>上海静钧研磨20年专业经验，为您提供一站式{keyword}解决方案！</p>
"""
        else:
            opening = f"""
<p>作为{keyword}领域的专业供应商，上海静钧研磨凭借20年的行业经验，为全球客户提供高品质的研磨抛光材料。我们的产品广泛应用于金属加工、汽车制造、航空航天等各个领域。</p>
<p>选择上海静钧研磨，就是选择专业、可靠、高效的{keyword}解决方案！</p>
"""
        
        # 根据转化率调整产品介绍
        if conversion_rate > 0.5:  # 高转化率，用户对产品很感兴趣
            product_intro = f"""
<h3>为什么选择我们的{keyword}？</h3>
<p>基于{clicks}次点击和{pv}次浏览的数据分析，我们的{keyword}在以下方面表现优异：</p>
<ul>
<li><strong>高转化率</strong>：转化率达到{conversion_rate:.1%}，远超行业平均水平</li>
<li><strong>低跳出率</strong>：跳出率仅{bounce_rate}%，用户粘性强</li>
<li><strong>长停留时间</strong>：平均访问时长{visit_duration}，用户深度了解产品</li>
<li><strong>高点击量</strong>：{clicks}次点击证明市场需求旺盛</li>
</ul>
"""
        else:
            product_intro = f"""
<h3>产品优势</h3>
<ul>
<li><strong>品质保证</strong>：采用优质原材料，确保产品质量稳定</li>
<li><strong>规格齐全</strong>：提供多种规格和型号，满足不同需求</li>
<li><strong>定制服务</strong>：可根据客户要求定制特殊规格产品</li>
<li><strong>快速交付</strong>：完善的供应链体系，确保及时交付</li>
</ul>
"""
        
        # 根据分类调整技术参数
        if "抛光" in category:
            tech_params = """
<h3>技术参数</h3>
<p>抛光产品规格参数：</p>
<ul>
<li>直径：2-14寸可选</li>
<li>厚度：0.5-5mm</li>
<li>硬度：软、中、硬三种等级</li>
<li>基材：棉布、麻布、尼龙等</li>
<li>粒度：60#-3000#</li>
</ul>
"""
        elif "打磨" in category:
            tech_params = """
<h3>技术参数</h3>
<p>打磨产品规格参数：</p>
<ul>
<li>直径：50-200mm</li>
<li>厚度：1-10mm</li>
<li>材质：尼龙、聚酯、碳化硅等</li>
<li>粒度：80#-2000#</li>
<li>形状：圆形、方形、异形定制</li>
</ul>
"""
        else:
            tech_params = """
<h3>技术参数</h3>
<p>产品规格可根据客户需求定制，包括：</p>
<ul>
<li>尺寸：多种规格可选</li>
<li>材质：优质原材料</li>
<li>硬度：多种硬度等级</li>
<li>表面处理：根据应用需求定制</li>
</ul>
"""
        
        # 生成完整文章内容
        content = f"""
{opening}

{product_intro}

<h3>应用领域</h3>
<p>我们的{keyword}广泛应用于：</p>
<ul>
<li>金属加工行业 - 不锈钢、铝合金、铜材等</li>
<li>汽车制造 - 车身抛光、零部件加工</li>
<li>航空航天 - 精密零件表面处理</li>
<li>电子设备制造 - 精密仪器加工</li>
<li>模具制造 - 模具表面精加工</li>
</ul>

{tech_params}

<h3>成功案例</h3>
<p>我们为众多知名企业提供{keyword}解决方案：</p>
<ul>
<li>某汽车零部件企业：使用我们的抛光产品，表面光洁度提升30%</li>
<li>某精密仪器厂：采用定制打磨方案，加工效率提高25%</li>
<li>某航空航天企业：通过我们的技术支持，产品合格率达到99.5%</li>
</ul>

<h3>服务承诺</h3>
<p>上海静钧研磨承诺：</p>
<ul>
<li>产品质量保证 - 提供质量检测报告</li>
<li>技术支持服务 - 专业工程师现场指导</li>
<li>快速响应客户需求 - 24小时内回复</li>
<li>完善的售后服务 - 终身技术支持</li>
</ul>

<h3>立即{call_to_action}</h3>
<p>如需了解更多{keyword}相关信息，欢迎联系我们：</p>
<ul>
                <li>电话：13331805825</li>
<li>邮箱：info@shjingjun.com</li>
<li>地址：上海市xxx区xxx路xxx号</li>
<li>微信：shjingjun2024</li>
</ul>

<p><strong>选择上海静钧研磨，选择专业品质！让数据说话，让效果证明！</strong></p>

<!-- SEO优化标签 -->
<div style="display:none;">
关键词：{keyword}, 研磨材料, 抛光材料, 上海静钧, 工业磨料
分类：{category}
推广数据：消费{cost}元，点击{clicks}次，浏览{pv}次，跳出率{bounce_rate}%，访问时长{visit_duration}，综合得分{score:.2f}
转化率：{conversion_rate:.1%}
内容策略：{content_focus}
</div>
"""
        
        return {
            "title": title,
            "content": content,
            "excerpt": f"专业{keyword}供应商，上海静钧研磨提供高品质研磨抛光材料，20年行业经验，转化率{conversion_rate:.1%}，{call_to_action}！",
            "keywords": [keyword, "研磨材料", "抛光材料", "上海静钧", "工业磨料"],
            "category": category,
            "score": score,
            "conversion_rate": conversion_rate
        }
    
    def create_wordpress_post(self, article_data: Dict) -> Dict:
        """创建WordPress文章"""
        try:
            post_data = {
                "title": article_data["title"],
                "content": article_data["content"],
                "excerpt": article_data["excerpt"],
                "status": "publish",
                "format": "standard",
                "meta": {
                    "keywords": ", ".join(article_data["keywords"])
                }
            }
            
            response = requests.post(
                f"{self.api_url}/posts",
                auth=(self.username, self.password),
                json=post_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                result = response.json()
                return {
                    "success": True,
                    "post_id": result["id"],
                    "post_url": result["link"],
                    "message": "文章创建成功"
                }
            else:
                return {
                    "success": False,
                    "error": f"创建失败: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"创建文章异常: {str(e)}"
            }
    
    def calculate_keyword_score(self, keyword_data: Dict) -> float:
        """计算关键词综合得分，用于排序"""
        clicks = keyword_data.get("clicks", 0)
        pv = keyword_data.get("pv", 0)
        cost = keyword_data.get("cost", 0)
        bounce_rate = keyword_data.get("bounce_rate", 100)
        visit_duration = keyword_data.get("visit_duration", "00:00:00")
        
        # 计算访问时长（秒）
        duration_parts = visit_duration.split(":")
        duration_seconds = int(duration_parts[0]) * 3600 + int(duration_parts[1]) * 60 + int(duration_parts[2])
        
        # 计算转化率（PV/点击）
        conversion_rate = (pv / clicks) if clicks > 0 else 0
        
        # 计算跳出率得分（跳出率越低越好）
        bounce_score = max(0, 100 - bounce_rate)
        
        # 计算时长得分（访问时长越长越好）
        duration_score = min(100, duration_seconds * 2)  # 每30秒得1分，最高100分
        
        # 综合得分 = 点击量权重 + 转化率权重 + 跳出率权重 + 时长权重
        score = (
            clicks * 0.3 +           # 点击量权重30%
            conversion_rate * 20 +    # 转化率权重20%
            bounce_score * 0.2 +      # 跳出率权重20%
            duration_score * 0.3      # 访问时长权重30%
        )
        
        return score
    
    def generate_articles_from_promotion_data(self, max_articles: int = 5) -> List[Dict]:
        """基于推广数据批量生成文章，按点击量和转化率智能排序"""
        promotion_data = self.load_promotion_data()
        if not promotion_data:
            return []
        
        # 获取所有关键词并计算综合得分
        keywords = promotion_data.get("promotion_data", {}).get("all_keywords", [])
        
        # 为每个关键词计算得分
        for keyword_data in keywords:
            keyword_data["score"] = self.calculate_keyword_score(keyword_data)
        
        # 按综合得分排序（得分越高越优先）
        keywords.sort(key=lambda x: x["score"], reverse=True)
        
        print(f"关键词排序结果（按综合得分）:")
        for i, kw in enumerate(keywords[:10]):
            print(f"{i+1}. {kw['keyword']} - 得分: {kw['score']:.2f} (点击:{kw['clicks']}, 转化:{kw['pv']/kw['clicks']:.2f}, 跳出率:{kw['bounce_rate']}%)")
        
        results = []
        for i, keyword_data in enumerate(keywords[:max_articles]):
            print(f"正在生成第{i+1}篇文章: {keyword_data['keyword']} (得分: {keyword_data['score']:.2f})")
            
            # 生成文章内容
            article_data = self.generate_article_content(keyword_data)
            
            # 创建WordPress文章
            result = self.create_wordpress_post(article_data)
            result["keyword"] = keyword_data["keyword"]
            result["cost"] = keyword_data["cost"]
            result["clicks"] = keyword_data["clicks"]
            result["score"] = keyword_data["score"]
            
            results.append(result)
            
            # 避免请求过于频繁
            time.sleep(2)
        
        return results
    
    def get_existing_posts(self) -> List[Dict]:
        """获取现有文章列表"""
        try:
            response = requests.get(
                f"{self.api_url}/posts",
                auth=(self.username, self.password),
                params={"per_page": 100}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
                
        except Exception as e:
            print(f"获取文章列表失败: {e}")
            return []

def main():
    """主函数"""
    # WordPress配置
    wp_url = "https://www.shjingjun.com"
    username = "sh静钧"  # 你的WordPress用户名
    password = "Hu159632"  # 你的WordPress密码
    
    # 创建文章生成器
    generator = WordPressArticleGenerator(wp_url, username, password)
    
    # 测试连接
    if not generator.test_connection():
        print("❌ WordPress连接失败，请检查URL和认证信息")
        return
    
    print("✅ WordPress连接成功")
    
    # 生成文章
    print("开始基于推广数据生成文章...")
    results = generator.generate_articles_from_promotion_data(max_articles=3)
    
    # 输出结果
    print("\n文章生成结果:")
    print("=" * 50)
    for result in results:
        if result["success"]:
            print(f"✅ {result['keyword']} - 文章ID: {result['post_id']}")
            print(f"   链接: {result['post_url']}")
        else:
            print(f"❌ {result['keyword']} - 失败: {result['error']}")

if __name__ == "__main__":
    main()

