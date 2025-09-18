#!/usr/bin/env python3
"""
RAG-Anything 前端界面
使用Flask创建Web界面，用户可以输入问题并与RAG系统交互
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session
import threading
import time

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

from raganything import RAGAnything, RAGAnythingConfig
from lightrag.utils import EmbeddingFunc
import requests


app = Flask(__name__)
app.secret_key = 'rag-anything-secret-key-2024'

# 全局变量存储RAG实例
rag_instance = None
rag_initialized = False


def doubao_complete(prompt, system_prompt=None, history_messages=[], messages=None, model="doubao-1-5-pro-32k-250115", temperature=0.1, max_tokens=4000, **kwargs):
    """调用豆包API进行文本生成"""
    api_key = os.getenv("ARK_API_KEY", "ecaa1600-6dab-4700-8655-63a260492b8c")
    base_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 构建消息列表
    if messages is not None:
        msg_list = messages
    else:
        msg_list = []
        if system_prompt:
            msg_list.append({"role": "system", "content": system_prompt})
        if history_messages:
            msg_list.extend(history_messages)
        if prompt:
            msg_list.append({"role": "user", "content": prompt})
    
    # 截断过长的提示
    if prompt and isinstance(prompt, str) and len(prompt) > 4000:
        prompt = prompt[:4000] + "..."
    
    data = {
        "model": model,
        "messages": msg_list,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    # 添加延迟避免429错误
    time.sleep(3)
    
    retry_delays = [0, 5, 15, 30]
    last_err = None
    
    for delay in retry_delays:
        if delay > 0:
            print(f"等待 {delay} 秒后重试...")
            time.sleep(delay)
        
        try:
            resp = requests.post(base_url, headers=headers, json=data, timeout=120)
            resp.raise_for_status()
            result = resp.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            last_err = e
            print(f"API调用失败: {e}")
            if "429" in str(e):
                continue
            else:
                break
    
    raise last_err if last_err else Exception("Doubao request failed after retries")


def doubao_embed(texts):
    """调用豆包API进行文本嵌入"""
    api_key = os.getenv("ARK_EMBEDDING_API_KEY", "6f1aa1a3-e483-42c9-a3a0-418eceeea598")
    base_url = "https://ark.cn-beijing.volces.com/api/v3/embeddings/multimodal"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 豆包API一次只能处理一个文本
    embeddings = []
    for text in texts:
        data = {
            "model": "doubao-embedding-vision-250615",
            "input": text
        }
        
        try:
            resp = requests.post(base_url, headers=headers, json=data, timeout=120)
            resp.raise_for_status()
            result = resp.json()
            embeddings.append(result["data"][0]["embedding"])
        except Exception as e:
            print(f"嵌入API调用失败: {e}")
            # 返回零向量作为fallback
            embeddings.append([0.0] * 2048)
    
    return embeddings


async def async_llm_model_func(*args, **kwargs):
    """异步包装的LLM函数"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: doubao_complete(*args, **kwargs))


async def async_doubao_embed(texts):
    """异步包装的嵌入函数"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: doubao_embed(texts))


async def async_initialize_rag():
    """异步初始化RAG系统"""
    global rag_instance, rag_initialized
    
    try:
        print("正在初始化RAG系统...")
        
        # 检查工作目录
        working_dir = "./rag_storage"
        if not os.path.exists(working_dir):
            print("错误: 找不到rag_storage目录")
            return False
        
        # 直接使用LightRAG，避免RAG-Anything的复杂性
        from lightrag import LightRAG
        from lightrag.kg.shared_storage import initialize_pipeline_status
        
        # 创建嵌入函数
        embedding_func = EmbeddingFunc(
            embedding_dim=2048,
            max_token_size=8192,
            func=async_doubao_embed,
        )
        
        # 创建简单tokenizer避免序列化问题
        class SimpleTokenizer:
            def encode(self, text):
                return text.split()
            def decode(self, tokens):
                return " ".join(tokens)
        
        # 初始化LightRAG
        rag_instance = LightRAG(
            working_dir=working_dir,
            llm_model_func=async_llm_model_func,
            embedding_func=embedding_func,
            tiktoken_model_name="gpt-3.5-turbo",
            tokenizer=SimpleTokenizer(),
        )
        
        # 异步初始化存储
        await rag_instance.initialize_storages()
        await initialize_pipeline_status()
        
        rag_initialized = True
        print("RAG系统初始化成功！")
        return True
        
    except Exception as e:
        print(f"RAG系统初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def initialize_rag():
    """同步包装的初始化函数"""
    global rag_initialized
    
    try:
        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(async_initialize_rag())
            return result
        finally:
            loop.close()
            
    except Exception as e:
        print(f"RAG系统初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """获取系统状态"""
    return jsonify({
        'rag_initialized': rag_initialized,
        'working_dir_exists': os.path.exists('./rag_storage')
    })


@app.route('/api/initialize', methods=['POST'])
def initialize():
    """初始化RAG系统"""
    def init_task():
        initialize_rag()
    
    # 在后台线程中初始化
    thread = threading.Thread(target=init_task)
    thread.start()
    
    return jsonify({'message': 'RAG系统正在初始化中...'})


@app.route('/api/ask', methods=['POST'])
def ask_question():
    """处理用户问题"""
    if not rag_initialized:
        return jsonify({'error': 'RAG系统未初始化'}), 400
    
    data = request.get_json()
    question = data.get('question', '').strip()
    mode = data.get('mode', 'naive')
    
    if not question:
        return jsonify({'error': '请输入问题'}), 400
    
    try:
        # 在新的事件循环中运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 使用LightRAG的正确调用方式
            from lightrag import QueryParam
            query_param = QueryParam(mode=mode)
            answer = loop.run_until_complete(rag_instance.aquery(question, param=query_param))
            return jsonify({
                'question': question,
                'answer': answer,
                'mode': mode
            })
        finally:
            loop.close()
            
    except Exception as e:
        print(f"问答错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'处理问题时出错: {str(e)}'}), 500


async def analyze_knowledge_base_content():
    """分析知识库内容类型"""
    try:
        # 使用简单的查询来检测内容类型
        test_queries = [
            "这个人的姓名是什么？",
            "文档中提到了哪些地理位置？",
            "有哪些技术相关的信息？",
            "文档中涉及哪些学术概念？"
        ]
        
        content_types = []
        for query in test_queries:
            try:
                # 使用naive模式快速查询
                from lightrag import QueryParam
                query_param = QueryParam(mode="naive")
                result = await rag_instance.aquery(query, param=query_param)
                
                # 简单判断是否有相关内容
                if result and len(result.strip()) > 10 and "没有找到相关信息" not in result:
                    if "姓名" in query:
                        content_types.append("resume")
                    elif "地理位置" in query:
                        content_types.append("geography")
                    elif "技术" in query:
                        content_types.append("technical")
                    elif "学术" in query:
                        content_types.append("academic")
            except:
                continue
        
        return content_types
    except:
        return []


async def generate_dynamic_suggestions():
    """根据知识库内容生成动态建议问题"""
    if not rag_initialized or not rag_instance:
        return []
    
    try:
        # 基础问题模板
        base_questions = [
            "这个文档的主要内容是什么？",
            "文档中提到了哪些重要概念？",
            "总结一下文档的要点",
            "文档中有什么重要信息？",
            "这个文档讨论了什么问题？"
        ]
        
        # 分析知识库内容类型
        content_types = await analyze_knowledge_base_content()
        
        # 根据检测到的内容类型生成特定问题
        content_questions = []
        
        if "resume" in content_types:
            content_questions.extend([
                "这个人的姓名是什么？",
                "他有什么工作经历？",
                "他掌握哪些技术技能？",
                "他的教育背景如何？",
                "总结一下这个人的主要特点",
                "文档中提到了哪些项目经验？",
                "这个人的联系方式是什么？",
                "他有什么专业证书或认证？",
                "文档中提到了哪些成就？",
                "这个人的职业目标是什么？"
            ])
        
        if "geography" in content_types:
            content_questions.extend([
                "文档中提到了哪些地理位置？",
                "有哪些地理相关的信息？",
                "文档中涉及哪些地区或城市？",
                "提到了哪些地理概念？",
                "有哪些地理数据或统计信息？",
                "文档中描述了哪些地理特征？",
                "涉及哪些地理分析方法？",
                "提到了哪些地理工具或技术？"
            ])
        
        if "technical" in content_types:
            content_questions.extend([
                "文档中提到了哪些技术？",
                "有哪些技术实现方案？",
                "涉及哪些编程语言或框架？",
                "提到了哪些技术架构？",
                "有哪些技术挑战和解决方案？"
            ])
        
        if "academic" in content_types:
            content_questions.extend([
                "文档中提到了哪些学术概念？",
                "有哪些研究方法？",
                "涉及哪些理论或模型？",
                "提到了哪些学术成果？",
                "有哪些研究结论？"
            ])
        
        # 如果没有检测到特定类型，使用通用问题
        if not content_questions:
            content_questions = [
                "这个人的姓名是什么？",
                "他有什么工作经历？",
                "他掌握哪些技术技能？",
                "他的教育背景如何？",
                "总结一下这个人的主要特点",
                "文档中提到了哪些地理位置？",
                "有哪些地理相关的信息？",
                "文档中涉及哪些地区或城市？",
                "提到了哪些地理概念？",
                "有哪些地理数据或统计信息？"
            ]
        
        # 合并所有问题
        all_suggestions = base_questions + content_questions
        
        # 去重并限制数量
        unique_suggestions = list(dict.fromkeys(all_suggestions))[:15]
        
        return unique_suggestions
        
    except Exception as e:
        print(f"生成动态建议失败: {e}")
        # 返回默认问题
        return [
            "这个文档的主要内容是什么？",
            "文档中提到了哪些重要概念？",
            "总结一下文档的要点",
            "文档中有什么重要信息？",
            "这个文档讨论了什么问题？"
        ]


@app.route('/api/suggestions')
def get_suggestions():
    """获取建议问题"""
    try:
        # 尝试生成动态建议
        if rag_initialized:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                suggestions = loop.run_until_complete(generate_dynamic_suggestions())
                return jsonify({'suggestions': suggestions})
            finally:
                loop.close()
        else:
            # 如果RAG未初始化，返回默认问题
            suggestions = [
                "这个文档的主要内容是什么？",
                "文档中提到了哪些重要概念？",
                "总结一下文档的要点",
                "文档中有什么重要信息？",
                "这个文档讨论了什么问题？"
            ]
            return jsonify({'suggestions': suggestions})
    except Exception as e:
        print(f"获取建议问题失败: {e}")
        # 返回默认问题
        suggestions = [
            "这个文档的主要内容是什么？",
            "文档中提到了哪些重要概念？",
            "总结一下文档的要点",
            "文档中有什么重要信息？",
            "这个文档讨论了什么问题？"
        ]
        return jsonify({'suggestions': suggestions})


if __name__ == '__main__':
    # 检查是否需要初始化RAG
    if os.path.exists('./rag_storage'):
        print("检测到rag_storage目录，尝试初始化RAG系统...")
        initialize_rag()
    
    print("启动RAG-Anything前端服务...")
    print("访问地址: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
