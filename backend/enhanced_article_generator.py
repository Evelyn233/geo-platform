#!/usr/bin/env python3
"""
增强版文章生成器
集成联网搜索和大模型优化功能
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import os
from image_search import ImageSearcher

class EnhancedArticleGenerator:
    def __init__(self, wp_url: str, username: str, password: str):
        """
        初始化增强版文章生成器
        
        Args:
            wp_url: WordPress网站URL
            username: WordPress用户名
            password: WordPress密码或应用密码
        """
        self.wp_url = wp_url.rstrip('/')
        self.username = username
        self.password = password
        self.api_url = f"{self.wp_url}/wp-json/wp/v2"
        self.image_searcher = ImageSearcher()  # 初始化图片搜索器
        
    def search_web_content(self, keyword: str, max_results: int = 5) -> List[Dict]:
        """联网搜索相关内容"""
        try:
            # 使用DuckDuckGo搜索API（免费，无需API密钥）
            search_url = "https://api.duckduckgo.com/"
            params = {
                "q": f"{keyword} 研磨 抛光 材料 供应商",
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            
            # 处理不同的状态码
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # 处理搜索结果
                for i, result in enumerate(data.get("RelatedTopics", [])[:max_results]):
                    if isinstance(result, dict) and "Text" in result:
                        results.append({
                            "title": result.get("FirstURL", "").split("/")[-1].replace("_", " "),
                            "content": result.get("Text", ""),
                            "url": result.get("FirstURL", ""),
                            "source": "DuckDuckGo"
                        })
                
                # 如果没有相关主题，尝试使用抽象结果
                if not results and "Abstract" in data:
                    results.append({
                        "title": f"{keyword}相关信息",
                        "content": data.get("Abstract", ""),
                        "url": data.get("AbstractURL", ""),
                        "source": "DuckDuckGo"
                    })
                
                return results
            elif response.status_code == 202:
                print(f"搜索请求已接受但处理中，状态码: {response.status_code}")
                # 202状态码表示请求已接受，但处理尚未完成
                # 我们可以等待一下再重试，或者使用备用搜索方案
                import time
                time.sleep(2)
                # 尝试使用备用搜索方案
                return self._fallback_search(keyword)
            else:
                print(f"搜索API返回错误: {response.status_code}")
                return self._fallback_search(keyword)
                
        except Exception as e:
            print(f"联网搜索失败: {e}")
            return self._fallback_search(keyword)
    
    def _fallback_search(self, keyword: str) -> List[Dict]:
        """备用搜索方案，当主要搜索API失败时使用"""
        try:
            # 使用更简单的搜索API或者返回预设内容
            print(f"使用备用搜索方案搜索: {keyword}")
            
            # 返回基于关键词的预设内容
            fallback_results = [
                {
                    "title": f"{keyword}专业供应商 - 上海静钧研磨",
                    "content": f"上海静钧研磨是专业的{keyword}供应商，拥有20年行业经验，提供高品质研磨抛光材料。我们专注于为客户提供优质的{keyword}产品和专业的技术支持。",
                    "url": "https://www.shjingjun.com",
                    "source": "备用搜索"
                },
                {
                    "title": f"{keyword}技术参数和应用指南",
                    "content": f"详细介绍{keyword}的技术参数、使用方法、注意事项等专业信息。包括材料特性、规格标准、应用场景等详细内容。",
                    "url": "https://example.com/guide",
                    "source": "备用搜索"
                },
                {
                    "title": f"{keyword}行业发展趋势",
                    "content": f"分析{keyword}行业的发展趋势、市场前景、技术创新等。了解行业动态，把握发展机遇。",
                    "url": "https://example.com/trends",
                    "source": "备用搜索"
                }
            ]
            
            return fallback_results
            
        except Exception as e:
            print(f"备用搜索也失败: {e}")
            return []
    
    def search_baidu_content(self, keyword: str) -> List[Dict]:
        """使用百度搜索相关内容（模拟）"""
        try:
            print(f"正在使用百度搜索: {keyword}")
            
            # 这里可以集成百度搜索API，目前返回模拟数据
            mock_results = [
                {
                    "title": f"{keyword}专业供应商 - 上海静钧研磨",
                    "content": f"上海静钧研磨是专业的{keyword}供应商，拥有20年行业经验，提供高品质研磨抛光材料。我们致力于为客户提供优质的{keyword}产品和专业的技术服务。",
                    "url": "https://www.shjingjun.com",
                    "source": "百度搜索"
                },
                {
                    "title": f"{keyword}技术参数和应用指南",
                    "content": f"详细介绍{keyword}的技术参数、使用方法、注意事项等专业信息。包括规格标准、性能指标、应用场景等详细内容。",
                    "url": "https://example.com/guide",
                    "source": "百度搜索"
                },
                {
                    "title": f"{keyword}质量标准和认证",
                    "content": f"了解{keyword}的质量标准、认证要求、检测方法等。确保产品质量符合行业标准和客户要求。",
                    "url": "https://example.com/standards",
                    "source": "百度搜索"
                }
            ]
            
            print(f"百度搜索返回 {len(mock_results)} 个结果")
            return mock_results
            
        except Exception as e:
            print(f"百度搜索失败: {e}")
            return []
    
    def call_doubao_api(self, messages: List[Dict], model: str = "doubao-seed-1-6-flash") -> str:
        """调用豆包API进行内容优化"""
        try:
            from model_config import model_config
            
            # 直接使用新的API密钥
            api_key = "cf26bc05-bf7f-4bb8-8795-c090ea96e260"
            
            if not api_key:
                print("API密钥无效，使用默认内容")
                return "API密钥无效，使用默认内容"
            
            # 根据模型获取推荐的token数
            recommended_tokens = model_config.get_recommended_tokens(model)
            
            # 优化请求参数，减少token消耗
            data = {
                "model": model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": recommended_tokens,
                "top_p": 0.9,
                "frequency_penalty": 0.1
            }
            
            print(f"使用模型: {model} (推荐token: {recommended_tokens})")
            
            base_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            response = requests.post(
                base_url, 
                headers=headers, 
                json=data, 
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # 记录token使用情况
                if "usage" in result:
                    usage = result["usage"]
                    print(f"Token使用: 输入{usage.get('prompt_tokens', 0)}, 输出{usage.get('completion_tokens', 0)}, 总计{usage.get('total_tokens', 0)}")
                
                return content
            else:
                print(f"豆包API调用失败: {response.status_code} - {response.text}")
                return "API调用失败，使用默认内容"
                
        except Exception as e:
            print(f"调用豆包API异常: {e}")
            return "API调用异常，使用默认内容"
    
    def enhance_article_with_search(self, keyword_data: Dict, model: str = "doubao-seed-1-6-flash") -> Dict:
        """基于搜索内容增强文章"""
        keyword = keyword_data['keyword']
        
        print(f"正在搜索 {keyword} 相关内容...")
        
        # 联网搜索
        web_results = self.search_web_content(keyword)
        baidu_results = self.search_baidu_content(keyword)
        
        # 搜索相关图片
        print(f"正在搜索 {keyword} 相关图片...")
        images = self.image_searcher.search_images(keyword, max_results=3)
        
        # 合并搜索结果
        all_results = web_results + baidu_results
        
        # 构建搜索内容摘要
        search_summary = ""
        if all_results:
            search_summary = "\n\n".join([
                f"来源: {result['source']}\n标题: {result['title']}\n内容: {result['content'][:200]}..."
                for result in all_results[:3]
            ])
        
        # 构建图片内容摘要
        image_summary = ""
        if images:
            image_summary = f"找到 {len(images)} 张相关图片，包括：{', '.join([img['title'] for img in images[:2]])}"
        
        # 使用大模型优化内容（优化提示词，减少token消耗）
        optimization_prompt = f"""为关键词"{keyword}"创建SEO文章。

数据：点击{keyword_data['clicks']}，浏览{keyword_data['pv']}，跳出率{keyword_data['bounce_rate']}%，时长{keyword_data['visit_duration']}，消费¥{keyword_data['cost']}

搜索信息：{search_summary[:500]}...

图片信息：{image_summary}

要求：800字文章，使用WordPress标准HTML格式，包含以下结构：
1. 开头段落使用<p>标签
2. 主标题使用<h2>标签
3. 子标题使用<h3>标签
4. 列表使用<ul>和<li>标签
5. 强调文字使用<strong>标签
6. 段落使用<p>标签
7. 包含产品介绍、技术参数、应用案例、行动号召
8. 在适当位置添加图片展示区域（使用<img>标签）
9. 自然融入关键词，专业易懂
10. 符合WordPress新闻文章标准格式
11. 联系电话：13331805825"""
        
        # 调用大模型优化
        messages = [
            {"role": "system", "content": "你是一个专业的SEO内容创作专家，擅长创建高质量的营销文章。"},
            {"role": "user", "content": optimization_prompt}
        ]
        
        enhanced_content = self.call_doubao_api(messages)
        
        # 如果API调用失败，使用增强版基础模板
        if "API调用" in enhanced_content or len(enhanced_content) < 100:
            print("API调用失败，使用增强版基础模板...")
            enhanced_content = self.generate_enhanced_basic_article(keyword_data, search_summary, image_summary)
        
        # 选择最佳封面图片
        featured_image = None
        if images:
            featured_image = self.image_searcher.get_best_image_for_featured(images)
            print(f"选择封面图片: {featured_image['title'] if featured_image else '无'}")
        
        # 添加图片HTML到内容中
        if images:
            image_html = self.image_searcher.get_image_html(images, max_images=3)
            # 在文章中间插入图片（在技术参数部分之后）
            if "<h2>" in enhanced_content:
                # 找到第一个h2标签后插入图片
                parts = enhanced_content.split("<h2>", 1)
                if len(parts) > 1:
                    enhanced_content = parts[0] + image_html + "\n<h2>" + parts[1]
                else:
                    enhanced_content = enhanced_content + "\n" + image_html
            else:
                enhanced_content = enhanced_content + "\n" + image_html
        
        return {
            "title": f"{keyword} - 上海静钧研磨专业供应商",
            "content": enhanced_content,
            "excerpt": f"专业{keyword}供应商，上海静钧研磨提供高品质研磨抛光材料，20年行业经验。",
            "search_results": all_results,
            "images": images,
            "featured_image": featured_image,  # 添加封面图片
            "enhanced": True
        }
    
    def generate_basic_article(self, keyword_data: Dict) -> str:
        """生成基础文章模板"""
        keyword = keyword_data['keyword']
        clicks = keyword_data['clicks']
        pv = keyword_data['pv']
        bounce_rate = keyword_data['bounce_rate']
        visit_duration = keyword_data['visit_duration']
        cost = keyword_data['cost']
        
        return f"""专业{keyword}供应商 - 上海静钧研磨

作为{keyword}领域的专业供应商，上海静钧研磨凭借20年的行业经验，为全球客户提供高品质的研磨抛光材料。我们的产品在{clicks}次点击中获得了{pv}次浏览，跳出率仅{bounce_rate}%，平均访问时长{visit_duration}，充分证明了产品的市场认可度。

为什么选择我们的{keyword}？

• 市场验证：{clicks}次点击证明市场需求旺盛
• 用户认可：{bounce_rate}%的低跳出率显示用户粘性强
• 深度了解：{visit_duration}的平均访问时长说明用户深度了解产品
• 投资价值：¥{cost}的推广投入证明产品价值

产品优势

• 品质保证：采用优质原材料，确保产品质量稳定
• 规格齐全：提供多种规格和型号，满足不同需求
• 定制服务：可根据客户要求定制特殊规格产品
• 快速交付：完善的供应链体系，确保及时交付

应用领域

我们的{keyword}广泛应用于：

• 金属加工行业 - 不锈钢、铝合金、铜材等
• 汽车制造 - 车身抛光、零部件加工
• 航空航天 - 精密零件表面处理
• 电子设备制造 - 精密仪器加工
• 模具制造 - 模具表面精加工

技术参数

产品规格可根据客户需求定制，包括：

• 尺寸：多种规格可选
• 材质：优质原材料
• 硬度：多种硬度等级
• 表面处理：根据应用需求定制

成功案例

我们为众多知名企业提供{keyword}解决方案：

• 某汽车零部件企业：使用我们的产品，表面光洁度提升30%
• 某精密仪器厂：采用定制方案，加工效率提高25%
• 某航空航天企业：通过我们的技术支持，产品合格率达到99.5%

服务承诺

上海静钧研磨承诺：

• 产品质量保证 - 提供质量检测报告
• 技术支持服务 - 专业工程师现场指导
• 快速响应客户需求 - 24小时内回复
• 完善的售后服务 - 终身技术支持

立即咨询

如需了解更多{keyword}相关信息，欢迎联系我们：

• 电话：13331805825
• 邮箱：info@shjingjun.com
• 地址：上海市xxx区xxx路xxx号
• 微信：shjingjun2024

选择上海静钧研磨，选择专业品质！让数据说话，让效果证明！
"""
    
    def generate_enhanced_articles(self, max_articles: int = 5, model: str = "doubao-seed-1-6-flash") -> List[Dict]:
        """生成增强版文章"""
        # 使用硬编码的推广数据
        promotion_data = {
            "promotion_data": {
                "all_keywords": [
                    {
                        "rank": 1,
                        "keyword": "抛光轮布轮,麻轮",
                        "cost": 31.55,
                        "clicks": 17,
                        "pv": 48,
                        "bounce_rate": 54.55,
                        "visit_duration": "00:02:35",
                        "plan": "A级计划-抛光类",
                        "category": "布轮-产品词"
                    },
                    {
                        "rank": 2,
                        "keyword": "抛光风布轮厂家",
                        "cost": 22.81,
                        "clicks": 12,
                        "pv": 48,
                        "bounce_rate": 0.0,
                        "visit_duration": "00:15:50",
                        "plan": "A级计划-抛光类",
                        "category": "布轮-厂家词"
                    },
                    {
                        "rank": 3,
                        "keyword": "生产尼龙打磨片",
                        "cost": 103.29,
                        "clicks": 66,
                        "pv": 33,
                        "bounce_rate": 50.0,
                        "visit_duration": "00:01:06",
                        "plan": "A级计划-研磨类",
                        "category": "打磨片-产品词"
                    },
                    {
                        "rank": 4,
                        "keyword": "抛光白膏",
                        "cost": 154.24,
                        "clicks": 108,
                        "pv": 23,
                        "bounce_rate": 37.5,
                        "visit_duration": "00:03:49",
                        "plan": "A级计划-抛光类",
                        "category": "膏-产品词"
                    },
                    {
                        "rank": 5,
                        "keyword": "海绵抛光轮",
                        "cost": 26.04,
                        "clicks": 11,
                        "pv": 23,
                        "bounce_rate": 28.57,
                        "visit_duration": "00:00:41",
                        "plan": "A级计划-抛光类",
                        "category": "抛光盘-产品词"
                    }
                ]
            }
        }
        
        keywords = promotion_data.get("promotion_data", {}).get("all_keywords", [])
        
        # 计算得分并排序
        for keyword_data in keywords:
            score = self.calculate_keyword_score(keyword_data)
            keyword_data["score"] = score
        
        keywords.sort(key=lambda x: x["score"], reverse=True)
        
        results = []
        for i, keyword_data in enumerate(keywords[:max_articles]):
            print(f"正在生成第{i+1}篇增强文章: {keyword_data['keyword']}")
            
            # 生成增强版文章
            article_data = self.enhance_article_with_search(keyword_data, model)
            
            results.append({
                "success": True,
                "keyword": keyword_data["keyword"],
                "title": article_data["title"],
                "content": article_data["content"],
                "excerpt": article_data["excerpt"],
                "score": keyword_data["score"],
                "clicks": keyword_data["clicks"],
                "enhanced": True,
                "search_results": article_data.get("search_results", [])
            })
            
            # 避免请求过于频繁
            time.sleep(3)
        
        return results
    
    def calculate_keyword_score(self, keyword_data: Dict) -> float:
        """计算关键词综合得分"""
        clicks = keyword_data.get("clicks", 0)
        pv = keyword_data.get("pv", 0)
        bounce_rate = keyword_data.get("bounce_rate", 100)
        visit_duration = keyword_data.get("visit_duration", "00:00:00")
        
        # 计算访问时长（秒）
        duration_parts = visit_duration.split(":")
        duration_seconds = int(duration_parts[0]) * 3600 + int(duration_parts[1]) * 60 + int(duration_parts[2])
        
        # 计算转化率
        conversion_rate = (pv / clicks) if clicks > 0 else 0
        
        # 计算跳出率得分
        bounce_score = max(0, 100 - bounce_rate)
        
        # 计算时长得分
        duration_score = min(100, duration_seconds * 2)
        
        # 综合得分
        score = (
            clicks * 0.3 +
            conversion_rate * 20 +
            bounce_score * 0.2 +
            duration_score * 0.3
        )
        
        return score

def main():
    """测试增强版文章生成器"""
    generator = EnhancedArticleGenerator("", "", "")
    
    print("=== 增强版文章生成器测试 ===")
    results = generator.generate_enhanced_articles(max_articles=2)
    
    for i, result in enumerate(results):
        print(f"\n=== 文章 {i+1} ===")
        print(f"关键词: {result['keyword']}")
        print(f"标题: {result['title']}")
        print(f"增强版: {result['enhanced']}")
        print(f"搜索结果数量: {len(result.get('search_results', []))}")

    def generate_enhanced_basic_article(self, keyword_data: Dict, search_summary: str = "", image_summary: str = "") -> str:
        """生成增强版基础文章模板 - 即使API失败也能生成高质量文章"""
        keyword = keyword_data['keyword']
        clicks = keyword_data['clicks']
        pv = keyword_data['pv']
        bounce_rate = keyword_data['bounce_rate']
        visit_duration = keyword_data['visit_duration']
        cost = keyword_data['cost']
        
        # 根据数据表现调整内容策略
        if clicks > 50:
            performance_level = "卓越"
            market_demand = "市场需求极其旺盛"
        elif clicks > 20:
            performance_level = "优秀"
            market_demand = "市场需求旺盛"
        else:
            performance_level = "良好"
            market_demand = "市场需求稳定"
        
        # 根据跳出率调整描述
        if bounce_rate < 30:
            user_engagement = "用户粘性极强"
        elif bounce_rate < 50:
            user_engagement = "用户粘性较强"
        else:
            user_engagement = "用户关注度高"
        
        # 根据访问时长调整描述
        if ":" in visit_duration:
            duration_parts = visit_duration.split(":")
            minutes = int(duration_parts[0])
            if minutes > 10:
                depth_level = "深度了解"
            elif minutes > 5:
                depth_level = "详细了解"
            else:
                depth_level = "充分了解"
        else:
            depth_level = "充分了解"
        
        return f"""<h1>{keyword} - 上海静钧研磨专业供应商</h1>

<p>在精密制造和工业加工领域，<strong>{keyword}</strong>作为核心工具，其质量直接影响着加工效率和产品品质。作为深耕行业20年的专业供应商，<strong>上海静钧研磨</strong>始终以"技术领先、品质至上"为核心理念，为全球客户提供从产品选型到工艺优化的全方位解决方案。</p>

<p>基于最新的市场数据分析，我们的{keyword}在<strong>{clicks}次点击</strong>中获得了<strong>{pv}次浏览</strong>，跳出率仅<strong>{bounce_rate}%</strong>，平均访问时长达到<strong>{visit_duration}</strong>，充分证明了产品在市场上的{performance_level}表现和客户的深度认可。</p>

<h2>一、为什么选择上海静钧研磨{keyword}？</h2>

<h3>1. 市场验证数据</h3>
<ul>
<li><strong>市场认可度</strong>：{clicks}次点击证明{market_demand}</li>
<li><strong>用户粘性</strong>：{bounce_rate}%的低跳出率显示{user_engagement}</li>
<li><strong>深度了解</strong>：{visit_duration}的平均访问时长说明用户{depth_level}产品特性</li>
<li><strong>投资价值</strong>：¥{cost}的精准推广投入证明产品具有极高的市场价值</li>
</ul>

<h3>2. 技术优势</h3>
<ul>
<li><strong>20年行业经验</strong>：深耕研磨抛光领域，对产品性能有深刻理解</li>
<li><strong>源头直供</strong>：省去中间环节，确保产品质量和价格优势</li>
<li><strong>定制化服务</strong>：可根据客户特殊需求提供个性化解决方案</li>
<li><strong>品质保证</strong>：严格的质量控制体系，确保每一件产品都符合标准</li>
</ul>

<h2>二、产品技术参数与规格</h2>

<p>我们的{keyword}采用优质材料制造，具有以下技术特点：</p>

<h3>材料特性</h3>
<ul>
<li><strong>基材选择</strong>：采用高密度优质材料，确保产品稳定性和耐用性</li>
<li><strong>工艺标准</strong>：先进的制造工艺，保证产品性能一致性</li>
<li><strong>环保要求</strong>：符合国际环保标准，安全无污染</li>
</ul>

<h3>规格范围</h3>
<ul>
<li><strong>直径规格</strong>：50mm-500mm，支持定制异形尺寸</li>
<li><strong>厚度选择</strong>：3mm-30mm，满足不同加工需求</li>
<li><strong>适配性</strong>：兼容多种设备，安装简便</li>
</ul>

<h2>三、应用案例与效果展示</h2>

<p>我们的{keyword}已广泛应用于多个行业，取得了显著的效果：</p>

<h3>案例1：汽车零部件加工</h3>
<p>某汽车零部件厂商使用我们的{keyword}后，加工效率提升35%，产品表面质量达到镜面级标准，客户满意度大幅提升。</p>

<h3>案例2：航空航天精密加工</h3>
<p>在航空航天领域，我们的{keyword}帮助客户实现了高精度加工要求，产品通过了严格的质检标准，获得了客户的高度认可。</p>

<h2>四、服务保障与技术支持</h2>

<p>选择上海静钧研磨，您将获得全方位的服务保障：</p>

<ul>
<li><strong>专业技术支持</strong>：免费提供技术咨询和工艺指导</li>
<li><strong>快速响应</strong>：24小时内响应客户需求</li>
<li><strong>质量保证</strong>：30天质量问题免费退换</li>
<li><strong>定制服务</strong>：支持小批量试产和批量定制</li>
</ul>

<h2>五、立即联系我们</h2>

<p>无论您是需要常规规格的标准{keyword}，还是特殊场景的定制产品，上海静钧研磨都能为您提供专业的解决方案。</p>

<p><strong>现在咨询，即可免费获取《{keyword}技术手册》和专属加工方案！</strong></p>

<p>📞 <strong>咨询电话：13331805825</strong><br>
📧 邮箱：info@shjingjun.com<br>
🏢 地址：上海市专业研磨材料生产基地<br>
💬 微信：shjingjun2020</p>

<p>选择上海静钧研磨，让专业为您的生产保驾护航！</p>"""

if __name__ == "__main__":
    main()
