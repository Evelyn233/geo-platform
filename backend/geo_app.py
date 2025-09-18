import os
import asyncio
import sys
import json
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Add project root to path
PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

    # 导入自定义模块
    try:
        from enhanced_article_generator import EnhancedArticleGenerator
        from wordpress_article_generator import WordPressArticleGenerator
        from wordpress_publisher import WordPressPublisher
        from wordpress_simple_auth import SimpleWordPressAuth
        from ai_exposure_analyzer import AIExposureAnalyzer
        from ai_data_collector import AIDataCollector
        from real_data_platform import RealDataPlatform
        from data_collection_scheduler import DataCollectionScheduler
    except ImportError as e:
        print(f"导入模块失败: {e}")
        # 如果导入失败，设置为None，在运行时处理
        EnhancedArticleGenerator = None
        WordPressArticleGenerator = None
        WordPressPublisher = None
        SimpleWordPressAuth = None
        AIExposureAnalyzer = None
        AIDataCollector = None
        RealDataPlatform = None
        DataCollectionScheduler = None

app = FastAPI(title="GEO优化系统后端", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global state
rag_initialized = False
working_dir = "./rag_storage"

def doubao_complete(messages, model="doubao-seed-1-6-flash", temperature=0.1, max_tokens=2000):
    """调用豆包API进行文本生成"""
    import time
    import requests
    
    # 直接使用新的API密钥
    api_key = "cf26bc05-bf7f-4bb8-8795-c090ea96e260"
    if not api_key:
        raise RuntimeError("API密钥未配置")
    
    base_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    # 添加延迟避免429错误
    time.sleep(2)
    
    retry_delays = [0, 3, 10, 20]
    last_err = None
    
    for delay in retry_delays:
        if delay > 0:
            time.sleep(delay)
        
        try:
            resp = requests.post(base_url, headers=headers, json=data, timeout=120)
            resp.raise_for_status()
            result = resp.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            last_err = e
            if "429" in str(e):
                continue
            else:
                break
    
    raise last_err if last_err else Exception("Doubao request failed after retries")

def load_document_content():
    """加载已提取的文档内容"""
    # 首先尝试加载测试知识库
    test_knowledge_file = "rag_storage/test_knowledge.json"
    if os.path.exists(test_knowledge_file):
        with open(test_knowledge_file, 'r', encoding='utf-8') as f:
            knowledge = json.load(f)
            # 合并所有知识内容
            content = ""
            for topic, info in knowledge.items():
                content += f"{topic}: {info.get('content_summary', '')}\n"
            return content
    
    # 如果测试知识库不存在，尝试加载原有文档
    doc_status_file = "rag_storage/kv_store_doc_status.json"
    
    if not os.path.exists(doc_status_file):
        return None
    
    with open(doc_status_file, 'r', encoding='utf-8') as f:
        doc_status = json.load(f)
    
    # 获取第一个文档的内容摘要
    for doc_id, doc_info in doc_status.items():
        if 'content_summary' in doc_info:
            return doc_info['content_summary']
    
    return None

def ask_question(question, document_content):
    """基于文档内容回答问题"""
    prompt = f"""基于以下文档内容回答问题：

文档内容：
{document_content}

问题：{question}

请基于文档内容提供准确、简洁的回答。如果文档中没有相关信息，请说明。"""

    messages = [
        {"role": "user", "content": prompt}
    ]
    
    try:
        answer = doubao_complete(messages)
        return answer
    except Exception as e:
        return f"回答问题时出错: {e}"

@app.get("/")
async def root():
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")

@app.get("/api/status")
async def api_status():
    return {"service": "GEO优化系统", "status": "运行中", "version": "1.0.0"}

@app.post("/api/init")
async def init_knowledge_base(working_dir_param: str = "./rag_storage"):
    """初始化知识库"""
    global rag_initialized, working_dir
    working_dir = working_dir_param
    
    if not os.path.exists(working_dir):
        raise HTTPException(status_code=400, detail=f"工作目录 {working_dir} 不存在")
    
    # 检查是否有文档内容
    doc_content = load_document_content()
    if not doc_content:
        raise HTTPException(status_code=400, detail="知识库中没有找到文档内容")
    
    rag_initialized = True
    return {
        "success": True,
        "message": "知识库初始化成功",
        "working_dir": working_dir,
        "model": os.getenv("DOUBAO_MODEL", "doubao-1-5-pro-32k-250115")
    }

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """上传文档到知识库"""
    if not rag_initialized:
        raise HTTPException(status_code=400, detail="请先初始化知识库")
    
    # 这里可以添加文档处理逻辑
    # 目前返回成功状态
    return {
        "success": True,
        "message": f"文档 {file.filename} 上传成功",
        "filename": file.filename
    }

@app.post("/api/query")
async def query_knowledge_base(request: dict):
    """查询知识库"""
    question = request.get("question", "")
    if not question:
        raise HTTPException(status_code=400, detail="请提供问题")
    
    if not rag_initialized:
        raise HTTPException(status_code=400, detail="请先初始化知识库")
    
    try:
        doc_content = load_document_content()
        if not doc_content:
            raise HTTPException(status_code=400, detail="知识库中没有文档内容")
        
        answer = ask_question(question, doc_content)
        return {
            "success": True,
            "question": question,
            "answer": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

@app.get("/api/stats")
async def get_stats():
    """获取系统统计信息"""
    if not rag_initialized:
        return {
            "ai_distilled_words": 0,
            "creation_count": 0,
            "training_questions": 0,
            "media_feeding": 0,
            "inclusion_questions": 0,
            "feeding_accounts": 0
        }
    
    try:
        # 从 rag_storage 获取统计信息
        doc_status_file = "rag_storage/kv_store_doc_status.json"
        if os.path.exists(doc_status_file):
            with open(doc_status_file, 'r', encoding='utf-8') as f:
                doc_status = json.load(f)
            
            doc_count = len(doc_status)
        else:
            doc_count = 0
        
        return {
            "ai_distilled_words": 1,  # 示例数据
            "creation_count": doc_count,
            "training_questions": 9,
            "media_feeding": 0,
            "inclusion_questions": 0,
            "feeding_accounts": 0,
            "knowledge_base_docs": doc_count
        }
    except Exception as e:
        return {
            "ai_distilled_words": 0,
            "creation_count": 0,
            "training_questions": 0,
            "media_feeding": 0,
            "inclusion_questions": 0,
            "feeding_accounts": 0,
            "error": str(e)
        }

@app.post("/api/create_instruction")
async def create_instruction(instruction: str):
    """创建AI创作指令"""
    return {
        "success": True,
        "message": "创作指令创建成功",
        "instruction": instruction
    }

@app.post("/api/start_creation")
async def start_creation(topic: str, count: int = 1):
    """开始AI创作"""
    if not rag_initialized:
        raise HTTPException(status_code=400, detail="请先初始化知识库")
    
    try:
        # 基于知识库内容进行创作
        doc_content = load_document_content()
        if not doc_content:
            raise HTTPException(status_code=400, detail="知识库中没有文档内容")
        
        prompt = f"""基于以下知识库内容，创作关于"{topic}"的文章：

知识库内容：
{doc_content}

请创作一篇结构清晰、内容丰富的文章。"""
        
        messages = [{"role": "user", "content": prompt}]
        article = doubao_complete(messages)
        
        return {
            "success": True,
            "message": f"成功创作 {count} 篇文章",
            "articles": [article]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创作失败: {str(e)}")

@app.get("/api/models")
async def get_models():
    """获取支持的AI模型列表"""
    return {
        "models": [
            {"name": "deepseek", "included": 0},
            {"name": "豆包", "included": 1},
            {"name": "腾讯元宝", "included": 0},
            {"name": "通义千问", "included": 0},
            {"name": "文心一言", "included": 0}
        ]
    }

@app.post("/api/sync_wordpress")
async def sync_wordpress(wp_url: str = Form(...), wp_username: str = Form(default=""), wp_password: str = Form(default="")):
    """同步WordPress网站内容到RAG数据库"""
    try:
        from wordpress_integration import WordPressRAGIntegration
        
        # 创建WordPress集成实例
        wp_integration = WordPressRAGIntegration(wp_url, wp_username, wp_password)
        
        # 同步内容
        content = wp_integration.sync_all_content(working_dir)
        
        return {
            "success": True,
            "message": f"成功同步 {len(content)} 个内容项",
            "content_count": len(content),
            "wp_url": wp_url
        }
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"同步失败: {str(e)}"})

@app.get("/api/wordpress_test")
async def test_wordpress_connection(wp_url: str = "https://www.shjingjun.com"):
    """测试WordPress连接"""
    try:
        import requests
        
        # 测试WordPress REST API连接
        api_url = f"{wp_url.rstrip('/')}/wp-json/wp/v2/posts"
        
        # 尝试获取公开文章（不需要认证）
        response = requests.get(api_url, params={"per_page": 5}, timeout=10)
        
        if response.status_code == 200:
            posts = response.json()
            return {
                "success": True,
                "message": f"WordPress API连接成功，获取到 {len(posts)} 篇公开文章",
                "sample_posts": [{"title": post.get("title", {}).get("rendered", ""), "id": post.get("id")} for post in posts[:3]]
            }
        else:
            return {
                "success": False,
                "error": f"WordPress API返回错误: {response.status_code} - {response.text}"
            }
        
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "连接超时，请检查网站URL是否正确"
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "无法连接到WordPress网站，请检查URL是否正确"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"连接失败: {str(e)}"
        }

@app.post("/api/sync_baidu_analytics")
async def sync_baidu_analytics(access_token: str = Form(...), username: str = Form(default="default")):
    """同步百度统计数据"""
    try:
        from baidu_analytics import BaiduAnalytics
        
        # 创建百度统计实例
        baidu = BaiduAnalytics(access_token, username)
        
        # 获取所有数据
        data = baidu.get_all_data()
        
        if "error" in data:
            return JSONResponse(status_code=500, content={"error": data["error"]})
        
        # 保存数据
        import json
        output_file = os.path.join(working_dir, "baidu_analytics_data.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "message": "百度统计数据同步成功",
            "data_file": output_file,
            "site_info": data.get("site_info", {})
        }
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"同步失败: {str(e)}"})

@app.get("/api/baidu_analytics")
async def get_baidu_analytics():
    """获取百度统计数据"""
    try:
        import json
        
        data_file = os.path.join(working_dir, "baidu_analytics_data.json")
        if not os.path.exists(data_file):
            return JSONResponse(status_code=404, content={"error": "百度统计数据不存在"})
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            "success": True,
            "data": data
        }
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"获取数据失败: {str(e)}"})

@app.get("/api/models")
async def get_available_models():
    """获取可用的模型列表"""
    try:
        from model_config import model_config
        
        models = []
        for model_id, info in model_config.ALL_MODELS.items():
            models.append({
                "id": model_id,
                "name": info["name"],
                "description": info["description"],
                "max_tokens": info["max_tokens"],
                "cost_level": info["cost_level"],
                "recommended_tokens": model_config.get_recommended_tokens(model_id),
                "type": model_config.get_model_type(model_id)
            })
        
        return {
            "success": True,
            "models": models,
            "default_model": model_config.DEFAULT_MODEL
        }
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"获取模型列表失败: {str(e)}"})

@app.get("/api/baidu_promotion")
async def get_baidu_promotion():
    """获取百度推广数据"""
    try:
        # 使用硬编码的推广数据
        data = {
            "promotion_data": {
                "summary": {
                    "total_cost": 958.77,
                    "total_clicks": 720,
                    "total_pv": 346,
                    "avg_bounce_rate": 41.18,
                    "avg_visit_duration": "00:03:02"
                },
                "top_keywords": [
                    {
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
                        "keyword": "抛光布轮",
                        "cost": 143.2,
                        "clicks": 156,
                        "pv": 12,
                        "bounce_rate": 40.0,
                        "visit_duration": "00:05:16",
                        "plan": "A级计划-抛光类",
                        "category": "材料"
                    },
                    {
                        "keyword": "尼龙打磨片",
                        "cost": 103.29,
                        "clicks": 66,
                        "pv": 33,
                        "bounce_rate": 50.0,
                        "visit_duration": "00:01:06",
                        "plan": "A级计划-研磨类",
                        "category": "打磨片-产品词"
                    }
                ],
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
        
        return {
            "success": True,
            "data": data
        }
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"获取数据失败: {str(e)}"})

@app.post("/api/generate_articles")
async def generate_articles(
    wp_url: str = Form(...),
    wp_username: str = Form(...),
    wp_password: str = Form(...),
    max_articles: int = Form(default=5),
    enhanced: bool = Form(default=True),
    model: str = Form(default="doubao-seed-1-6-flash")
):
    """基于百度推广数据生成WordPress文章"""
    try:
        if enhanced:
            # 使用增强版文章生成器（联网搜索+大模型优化）
            from enhanced_article_generator import EnhancedArticleGenerator
            generator = EnhancedArticleGenerator(wp_url, wp_username, wp_password)
            results = generator.generate_enhanced_articles(max_articles, model)
        else:
            # 使用基础版文章生成器
            from wordpress_article_generator import WordPressArticleGenerator
            generator = WordPressArticleGenerator(wp_url, wp_username, wp_password)
            
            # 使用硬编码的推广数据
            promotion_data = {
                "promotion_data": {
                    "summary": {
                        "total_cost": 958.77,
                        "total_clicks": 720,
                        "total_pv": 346,
                        "avg_bounce_rate": 41.18,
                        "avg_visit_duration": "00:03:02"
                    },
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
            
            # 获取所有关键词并计算综合得分
            keywords = promotion_data.get("promotion_data", {}).get("all_keywords", [])
            
            # 为每个关键词计算得分
            for keyword_data in keywords:
                keyword_data["score"] = generator.calculate_keyword_score(keyword_data)
            
            # 按综合得分排序（得分越高越优先）
            keywords.sort(key=lambda x: x["score"], reverse=True)
            
            # 生成文章内容
            results = []
            for i, keyword_data in enumerate(keywords[:max_articles]):
                article_data = generator.generate_article_content(keyword_data)
                
                results.append({
                    "success": True,
                    "keyword": keyword_data["keyword"],
                    "title": article_data["title"],
                    "content": article_data["content"],
                    "excerpt": article_data["excerpt"],
                    "score": keyword_data["score"],
                    "clicks": keyword_data["clicks"],
                    "conversion_rate": article_data["conversion_rate"],
                    "enhanced": False
                })
        
        return {
            "success": True,
            "message": f"成功生成 {len(results)} 篇{'增强版' if enhanced else '基础版'}文章内容",
            "results": results,
            "enhanced": enhanced
        }
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"生成文章失败: {str(e)}"})

@app.get("/api/wordpress_posts")
async def get_wordpress_posts(
    wp_url: str = "https://www.shjingjun.com",
    wp_username: str = "sh静钧",
    wp_password: str = "Hu159632"
):
    """获取WordPress现有文章列表"""
    try:
        from wordpress_article_generator import WordPressArticleGenerator
        
        generator = WordPressArticleGenerator(wp_url, wp_username, wp_password)
        posts = generator.get_existing_posts()
        
        return {
            "success": True,
            "posts": posts,
            "count": len(posts)
        }
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"获取文章列表失败: {str(e)}"})

@app.post("/api/publish_articles")
async def publish_articles_to_wordpress(
    wp_url: str = Form(...),
    wp_username: str = Form(...),
    wp_password: str = Form(...),
    max_articles: int = Form(default=5),
    enhanced: bool = Form(default=True),
    model: str = Form(default="doubao-seed-1-6-flash"),
    category_name: str = Form(default="新闻资讯"),
    auto_publish: bool = Form(default=True)
):
    """生成文章并自动发布到WordPress"""
    try:
        if not SimpleWordPressAuth:
            return {"success": False, "error": "WordPress认证模块未加载"}
        
        # 创建WordPress认证器
        auth = SimpleWordPressAuth(wp_url, wp_username, wp_password)
        
        # 测试连接
        connection_test = auth.test_connection()
        if not connection_test["success"]:
            return {
                "success": False,
                "error": f"WordPress连接失败: {connection_test['message']}"
            }
        
        # 获取或创建新闻资讯分类
        categories = auth.get_categories()
        news_category_id = None
        
        for cat in categories:
            if cat['name'] == category_name or "新闻" in cat['name'] or "资讯" in cat['name']:
                news_category_id = cat['id']
                break
        
        if not news_category_id:
            # 创建新闻资讯分类
            create_result = auth.create_category(category_name)
            if create_result["success"]:
                news_category_id = create_result["category"]["id"]
            else:
                return {"success": False, "error": f"创建分类失败: {create_result['message']}"}
        
        # 生成文章
        if enhanced and EnhancedArticleGenerator:
            generator = EnhancedArticleGenerator(wp_url, wp_username, wp_password)
            articles_data = generator.generate_enhanced_articles(max_articles, model)
        elif WordPressArticleGenerator:
            generator = WordPressArticleGenerator(wp_url, wp_username, wp_password)
            articles_data = generator.generate_articles_from_promotion_data(max_articles)
        else:
            return {"success": False, "error": "文章生成模块未加载"}
        
        if not articles_data:
            return {"success": False, "error": "没有生成任何文章"}
        
        # 准备发布数据
        articles_to_publish = []
        for article in articles_data:
            if article.get("success", False):
                article_data = {
                    "title": article["title"],
                    "content": article["content"],
                    "excerpt": article["excerpt"],
                    "keyword": article["keyword"],
                    "score": article["score"],
                    "clicks": article["clicks"],
                    "conversion_rate": article.get("conversion_rate", 0.0),  # 添加默认值
                    "enhanced": article.get("enhanced", False)
                }
                
                # 添加封面图片数据（如果存在）
                if article.get("featured_image"):
                    article_data["featured_image"] = article["featured_image"]
                    print(f"✅ 文章 '{article['title']}' 包含封面图片")
                else:
                    print(f"⚠️ 文章 '{article['title']}' 没有封面图片")
                
                articles_to_publish.append(article_data)
        
        if not articles_to_publish:
            return {"success": False, "error": "没有可发布的文章"}
        
        # 发布文章
        if auto_publish:
            publish_results = []
            success_count = 0
            failed_count = 0
            
            for i, article in enumerate(articles_to_publish):
                try:
                    # 发布单篇文章
                    featured_media_url = None
                    if article.get("featured_image"):
                        featured_media_url = article["featured_image"].get("url")
                        print(f"📸 发布文章 '{article['title']}' 使用封面图片: {featured_media_url}")
                    
                    publish_result = auth.publish_article(
                        title=article["title"],
                        content=article["content"],
                        category_id=news_category_id,
                        status="publish",
                        featured_media_url=featured_media_url
                    )
                    
                    if publish_result["success"]:
                        success_count += 1
                        publish_results.append({
                            "success": True,
                            "article_index": i + 1,
                            "article_keyword": article["keyword"],
                            "post_id": publish_result["post_id"],
                            "post_url": publish_result["post_url"],
                            "message": "发布成功"
                        })
                    else:
                        failed_count += 1
                        publish_results.append({
                            "success": False,
                            "article_index": i + 1,
                            "article_keyword": article["keyword"],
                            "message": publish_result["message"]
                        })
                    
                    # 添加延迟避免API限制
                    import time
                    time.sleep(1)
                    
                except Exception as e:
                    failed_count += 1
                    publish_results.append({
                        "success": False,
                        "article_index": i + 1,
                        "article_keyword": article["keyword"],
                        "message": f"发布异常: {str(e)}"
                    })
            
            return {
                "success": True,
                "message": f"成功发布 {success_count} 篇文章，失败 {failed_count} 篇",
                "total_articles": len(articles_to_publish),
                "published_count": success_count,
                "failed_count": failed_count,
                "results": publish_results,
                "category": category_name,
                "category_id": news_category_id
            }
        else:
            # 只生成不发布
            return {
                "success": True,
                "message": f"生成了 {len(articles_to_publish)} 篇文章，未发布",
                "articles": articles_to_publish,
                "category": category_name,
                "category_id": news_category_id
            }
            
    except Exception as e:
        return {"success": False, "error": f"发布过程出错: {str(e)}"}

@app.get("/api/wordpress_categories")
async def get_wordpress_categories(
    wp_url: str,
    wp_username: str,
    wp_password: str
):
    """获取WordPress分类列表"""
    try:
        if not WordPressPublisher:
            return {"success": False, "error": "WordPress发布模块未加载"}
        
        publisher = WordPressPublisher(wp_url, wp_username, wp_password)
        categories = publisher.get_categories()
        
        return {
            "success": True,
            "categories": categories
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/published_articles")
async def get_published_articles(
    wp_url: str,
    wp_username: str,
    wp_password: str,
    category_id: Optional[int] = None
):
    """获取已发布的文章列表"""
    try:
        if not WordPressPublisher:
            return {"success": False, "error": "WordPress发布模块未加载"}
        
        publisher = WordPressPublisher(wp_url, wp_username, wp_password)
        articles = publisher.get_published_articles(category_id)
        
        return {
            "success": True,
            "articles": articles,
            "count": len(articles)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/publish_single_article")
async def publish_single_article(request: dict):
    """发布单篇文章"""
    try:
        if not SimpleWordPressAuth:
            return {"success": False, "error": "WordPress认证模块未加载"}
        
        wp_url = request.get("wp_url")
        wp_username = request.get("wp_username")
        wp_password = request.get("wp_password")
        article_data = request.get("article", {})
        
        if not all([wp_url, wp_username, wp_password, article_data]):
            return {"success": False, "error": "缺少必要参数"}
        
        # 创建WordPress认证器
        auth = SimpleWordPressAuth(wp_url, wp_username, wp_password)
        
        # 测试连接
        connection_test = auth.test_connection()
        if not connection_test["success"]:
            return {
                "success": False,
                "error": f"WordPress连接失败: {connection_test['message']}"
            }
        
        # 获取或创建新闻资讯分类
        categories = auth.get_categories()
        news_category_id = None
        
        for cat in categories:
            if cat['name'] == '新闻资讯' or "新闻" in cat['name'] or "资讯" in cat['name']:
                news_category_id = cat['id']
                break
        
        if not news_category_id:
            # 创建新闻资讯分类
            create_result = auth.create_category('新闻资讯')
            if create_result["success"]:
                news_category_id = create_result["category"]["id"]
            else:
                return {"success": False, "error": f"创建分类失败: {create_result['message']}"}
        
        # 发布文章
        publish_result = auth.publish_article(
            title=article_data["title"],
            content=article_data["content"],
            category_id=news_category_id,
            status="publish",
            featured_media_url=article_data.get("featured_image", {}).get("url") if article_data.get("featured_image") else None
        )
        
        if publish_result["success"]:
            return {
                "success": True,
                "message": "文章发布成功",
                "post_id": publish_result["post_id"],
                "post_url": publish_result["post_url"],
                "article_title": article_data["title"],
                "category_id": news_category_id
            }
        else:
            return {
                "success": False,
                "error": f"发布失败: {publish_result['message']}"
            }
            
    except Exception as e:
        return {"success": False, "error": f"发布过程出错: {str(e)}"}

# AI大模型曝光率分析相关API
@app.get("/api/ai_exposure/summary")
async def get_ai_exposure_summary():
    """获取AI大模型曝光率汇总统计"""
    try:
        if not AIExposureAnalyzer:
            return {"success": False, "error": "AI曝光率分析模块未加载"}
        
        analyzer = AIExposureAnalyzer()
        summary = analyzer.get_summary_stats()
        
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        return {"success": False, "error": f"获取汇总统计失败: {str(e)}"}

@app.get("/api/ai_exposure/platforms")
async def get_ai_platform_stats():
    """获取各AI平台统计信息"""
    try:
        if not AIExposureAnalyzer:
            return {"success": False, "error": "AI曝光率分析模块未加载"}
        
        analyzer = AIExposureAnalyzer()
        platforms = analyzer.get_platform_stats()
        
        return {
            "success": True,
            "data": platforms
        }
    except Exception as e:
        return {"success": False, "error": f"获取平台统计失败: {str(e)}"}

@app.get("/api/ai_exposure/questions")
async def get_ai_questions(
    platform: Optional[str] = None,
    source: Optional[str] = None,
    search_term: Optional[str] = None
):
    """获取AI平台问题数据"""
    try:
        if not AIExposureAnalyzer:
            return {"success": False, "error": "AI曝光率分析模块未加载"}
        
        analyzer = AIExposureAnalyzer()
        questions = analyzer.get_questions_data(
            platform=platform,
            source=source,
            search_term=search_term
        )
        
        return {
            "success": True,
            "data": questions,
            "count": len(questions)
        }
    except Exception as e:
        return {"success": False, "error": f"获取问题数据失败: {str(e)}"}

@app.post("/api/ai_exposure/questions")
async def add_ai_question(request: dict):
    """添加新的AI平台问题"""
    try:
        if not AIExposureAnalyzer:
            return {"success": False, "error": "AI曝光率分析模块未加载"}
        
        analyzer = AIExposureAnalyzer()
        
        training_word = request.get("training_word", "")
        question = request.get("question", "")
        platform = request.get("platform", "")
        source = request.get("source", "")
        category = request.get("category", "")
        
        if not all([training_word, question, platform, source]):
            return {"success": False, "error": "缺少必要参数"}
        
        success = analyzer.add_question(training_word, question, platform, source, category)
        
        if success:
            return {"success": True, "message": "问题添加成功"}
        else:
            return {"success": False, "error": "添加问题失败"}
            
    except Exception as e:
        return {"success": False, "error": f"添加问题失败: {str(e)}"}

@app.get("/api/ai_exposure/charts/platform_contribution")
async def get_platform_contribution_chart():
    """获取平台贡献图表数据"""
    try:
        if not AIExposureAnalyzer:
            return {"success": False, "error": "AI曝光率分析模块未加载"}
        
        analyzer = AIExposureAnalyzer()
        chart_data = analyzer.get_platform_contribution_chart_data()
        
        return {
            "success": True,
            "data": chart_data
        }
    except Exception as e:
        return {"success": False, "error": f"获取图表数据失败: {str(e)}"}

@app.get("/api/ai_exposure/charts/device_distribution")
async def get_device_distribution_chart():
    """获取设备分布图表数据"""
    try:
        if not AIExposureAnalyzer:
            return {"success": False, "error": "AI曝光率分析模块未加载"}
        
        analyzer = AIExposureAnalyzer()
        chart_data = analyzer.get_device_distribution_data()
        
        return {
            "success": True,
            "data": chart_data
        }
    except Exception as e:
        return {"success": False, "error": f"获取设备分布数据失败: {str(e)}"}

@app.get("/api/ai_exposure/brand_keywords")
async def get_brand_keywords():
    """获取品牌关键词列表"""
    try:
        if not AIExposureAnalyzer:
            return {"success": False, "error": "AI曝光率分析模块未加载"}
        
        analyzer = AIExposureAnalyzer()
        keywords = analyzer.get_brand_keywords()
        
        return {
            "success": True,
            "data": keywords,
            "count": len(keywords)
        }
    except Exception as e:
        return {"success": False, "error": f"获取品牌关键词失败: {str(e)}"}

@app.post("/api/ai_exposure/search")
async def search_ai_questions(request: dict):
    """搜索AI平台问题"""
    try:
        if not AIExposureAnalyzer:
            return {"success": False, "error": "AI曝光率分析模块未加载"}
        
        analyzer = AIExposureAnalyzer()
        
        keyword = request.get("keyword", "")
        platform = request.get("platform", None)
        
        results = analyzer.search_questions(keyword, platform)
        
        return {
            "success": True,
            "data": results,
            "count": len(results),
            "keyword": keyword,
            "platform": platform
        }
    except Exception as e:
        return {"success": False, "error": f"搜索失败: {str(e)}"}

@app.get("/api/ai_exposure/export")
async def export_ai_exposure_data(format: str = "json"):
    """导出AI曝光率数据"""
    try:
        if not AIExposureAnalyzer:
            return {"success": False, "error": "AI曝光率分析模块未加载"}
        
        analyzer = AIExposureAnalyzer()
        data = analyzer.export_data(format)
        
        return {
            "success": True,
            "data": data,
            "format": format
        }
    except Exception as e:
        return {"success": False, "error": f"导出数据失败: {str(e)}"}

# AI数据采集相关API
@app.post("/api/ai_exposure/collect/mock")
async def collect_mock_data(days: int = 30):
    """采集模拟数据"""
    try:
        if not AIDataCollector or not AIExposureAnalyzer:
            return {"success": False, "error": "AI数据采集模块未加载"}
        
        analyzer = AIExposureAnalyzer()
        collector = AIDataCollector(analyzer)
        
        # 生成模拟数据
        mock_data = collector.generate_mock_data(days)
        
        # 更新数据
        collector.update_data_from_collection(mock_data)
        
        return {
            "success": True,
            "message": f"成功生成{days}天的模拟数据",
            "data": {
                "total_questions": len(mock_data.get("questions", [])),
                "platforms_count": len(mock_data.get("platforms", {})),
                "brand_keywords_count": len(mock_data.get("brand_keywords", []))
            }
        }
    except Exception as e:
        return {"success": False, "error": f"采集模拟数据失败: {str(e)}"}

@app.post("/api/ai_exposure/collect/real")
async def collect_real_data(request: dict):
    """采集真实数据"""
    try:
        if not AIDataCollector or not AIExposureAnalyzer:
            return {"success": False, "error": "AI数据采集模块未加载"}
        
        analyzer = AIExposureAnalyzer()
        collector = AIDataCollector(analyzer)
        
        platform = request.get("platform", "")
        keywords = request.get("keywords", [])
        
        if not platform or not keywords:
            return {"success": False, "error": "请提供平台和关键词"}
        
        # 采集真实数据
        questions = collector.collect_real_data(platform, keywords)
        
        # 添加到现有数据
        data = analyzer.load_data()
        if "questions" not in data:
            data["questions"] = []
        
        data["questions"].extend(questions)
        analyzer.save_data(data)
        
        return {
            "success": True,
            "message": f"成功从{platform}采集{len(questions)}个问题",
            "data": {
                "platform": platform,
                "questions_count": len(questions),
                "keywords_used": keywords[:10]  # 只返回前10个关键词
            }
        }
    except Exception as e:
        return {"success": False, "error": f"采集真实数据失败: {str(e)}"}

@app.post("/api/ai_exposure/collect/baidu")
async def collect_from_baidu():
    """从百度统计数据中采集AI相关问题"""
    try:
        if not AIDataCollector or not AIExposureAnalyzer:
            return {"success": False, "error": "AI数据采集模块未加载"}
        
        analyzer = AIExposureAnalyzer()
        collector = AIDataCollector(analyzer)
        
        # 加载百度统计数据
        baidu_data_file = os.path.join(working_dir, "baidu_analytics_data.json")
        if not os.path.exists(baidu_data_file):
            return {"success": False, "error": "百度统计数据不存在，请先同步百度统计"}
        
        with open(baidu_data_file, 'r', encoding='utf-8') as f:
            baidu_data = json.load(f)
        
        # 从百度数据中提取AI相关问题
        questions = collector.collect_from_baidu_analytics(baidu_data)
        
        # 添加到现有数据
        data = analyzer.load_data()
        if "questions" not in data:
            data["questions"] = []
        
        data["questions"].extend(questions)
        analyzer.save_data(data)
        
        return {
            "success": True,
            "message": f"成功从百度统计数据中提取{len(questions)}个AI相关问题",
            "data": {
                "questions_count": len(questions),
                "source": "百度统计"
            }
        }
    except Exception as e:
        return {"success": False, "error": f"从百度统计采集数据失败: {str(e)}"}

@app.get("/api/ai_exposure/collect/report")
async def get_collection_report():
    """获取数据采集报告"""
    try:
        if not AIDataCollector or not AIExposureAnalyzer:
            return {"success": False, "error": "AI数据采集模块未加载"}
        
        analyzer = AIExposureAnalyzer()
        collector = AIDataCollector(analyzer)
        
        report = collector.export_collection_report()
        
        return {
            "success": True,
            "data": report
        }
    except Exception as e:
        return {"success": False, "error": f"获取采集报告失败: {str(e)}"}

@app.post("/api/ai_exposure/collect/start_realtime")
async def start_realtime_collection(interval_minutes: int = 60):
    """启动实时数据采集"""
    try:
        if not AIDataCollector or not AIExposureAnalyzer:
            return {"success": False, "error": "AI数据采集模块未加载"}
        
        # 这里应该使用后台任务，简化处理
        return {
            "success": True,
            "message": f"实时数据采集已启动，间隔{interval_minutes}分钟",
            "note": "实际实现需要后台任务支持"
        }
    except Exception as e:
        return {"success": False, "error": f"启动实时采集失败: {str(e)}"}

# 真实数据采集平台API
@app.post("/api/real_data/collect")
async def collect_real_data(request: dict):
    """采集真实AI数据"""
    try:
        if not RealDataPlatform:
            return {"success": False, "error": "真实数据采集平台未加载"}
        
        keywords = request.get("keywords", [])
        platforms = request.get("platforms", [])
        
        if not keywords:
            return {"success": False, "error": "请提供关键词列表"}
        
        # 创建数据采集平台实例
        platform = RealDataPlatform()
        
        # 采集数据
        results = await platform.collect_data(keywords, platforms)
        
        # 保存结果
        filename = platform.save_results()
        
        return {
            "success": True,
            "message": f"成功采集 {len(results)} 个真实数据",
            "data": {
                "results_count": len(results),
                "keywords": keywords,
                "platforms": platforms or list(platform.collectors.keys()),
                "filename": filename
            }
        }
    except Exception as e:
        return {"success": False, "error": f"采集真实数据失败: {str(e)}"}

@app.get("/api/real_data/platforms/status")
async def get_platforms_status():
    """获取AI平台状态"""
    try:
        if not RealDataPlatform:
            return {"success": False, "error": "真实数据采集平台未加载"}
        
        platform = RealDataPlatform()
        status = await platform.get_platform_status()
        
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        return {"success": False, "error": f"获取平台状态失败: {str(e)}"}

@app.post("/api/real_data/scheduler/create_task")
async def create_collection_task(request: dict):
    """创建采集任务"""
    try:
        if not DataCollectionScheduler:
            return {"success": False, "error": "数据采集调度器未加载"}
        
        # 这里需要全局调度器实例，简化处理
        return {
            "success": True,
            "message": "任务创建功能需要调度器实例",
            "note": "请使用 collect_real_data 接口进行数据采集"
        }
    except Exception as e:
        return {"success": False, "error": f"创建任务失败: {str(e)}"}

@app.get("/api/real_data/scheduler/status")
async def get_scheduler_status():
    """获取调度器状态"""
    try:
        if not DataCollectionScheduler:
            return {"success": False, "error": "数据采集调度器未加载"}
        
        # 这里需要全局调度器实例
        return {
            "success": True,
            "data": {
                "is_running": False,
                "message": "调度器未启动，请使用 collect_real_data 接口"
            }
        }
    except Exception as e:
        return {"success": False, "error": f"获取调度器状态失败: {str(e)}"}

@app.post("/api/real_data/analyze")
async def analyze_real_data(request: dict):
    """分析真实采集的数据"""
    try:
        if not RealDataPlatform or not AIExposureAnalyzer:
            return {"success": False, "error": "分析模块未加载"}
        
        # 创建分析器
        analyzer = AIExposureAnalyzer()
        
        # 获取现有数据
        data = analyzer.load_data()
        
        # 分析数据
        analysis = {
            "total_questions": len(data.get("questions", [])),
            "platforms": len(data.get("platforms", {})),
            "brand_keywords": len(data.get("brand_keywords", [])),
            "platform_distribution": {},
            "keyword_frequency": {},
            "recent_questions": data.get("questions", [])[-10:],
            "analysis_time": datetime.now().isoformat()
        }
        
        # 计算平台分布
        for platform, stats in data.get("platforms", {}).items():
            analysis["platform_distribution"][platform] = {
                "questions": stats.get("included_questions", 0),
                "exposure_rate": stats.get("exposure_rate", 0.0)
            }
        
        # 计算关键词频率
        keyword_count = {}
        for question in data.get("questions", []):
            keyword = question.get("training_word", "")
            keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
        
        analysis["keyword_frequency"] = dict(sorted(
            keyword_count.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10])
        
        return {
            "success": True,
            "data": analysis
        }
    except Exception as e:
        return {"success": False, "error": f"分析数据失败: {str(e)}"}

@app.post("/api/real_data/export")
async def export_real_data(request: dict):
    """导出真实数据"""
    try:
        if not RealDataPlatform:
            return {"success": False, "error": "真实数据采集平台未加载"}
        
        format_type = request.get("format", "json")
        keywords = request.get("keywords", [])
        platforms = request.get("platforms", [])
        
        # 创建平台实例
        platform = RealDataPlatform()
        
        # 如果有指定条件，重新采集数据
        if keywords:
            results = await platform.collect_data(keywords, platforms)
        else:
            # 使用现有数据
            results = platform.results
        
        # 导出数据
        if format_type == "json":
            export_data = []
            for result in results:
                export_data.append({
                    "platform": result.platform,
                    "keyword": result.keyword,
                    "question": result.question,
                    "answer": result.answer,
                    "confidence": result.confidence,
                    "source": result.source,
                    "timestamp": result.timestamp.isoformat(),
                    "metadata": result.metadata
                })
            
            return {
                "success": True,
                "data": export_data,
                "format": "json",
                "count": len(export_data)
            }
        
        elif format_type == "csv":
            # 简单的CSV格式
            csv_lines = ["平台,关键词,问题,答案,置信度,来源,时间"]
            for result in results:
                csv_lines.append(f"{result.platform},{result.keyword},{result.question},{result.answer},{result.confidence},{result.source},{result.timestamp.isoformat()}")
            
            return {
                "success": True,
                "data": "\n".join(csv_lines),
                "format": "csv",
                "count": len(results)
            }
        
        else:
            return {"success": False, "error": "不支持的导出格式"}
            
    except Exception as e:
        return {"success": False, "error": f"导出数据失败: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
