 #!/usr/bin/env python3
"""
简单的问答测试脚本
用于测试已处理的文档的问答功能
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from raganything import RAGAnything, RAGAnythingConfig
from lightrag.utils import EmbeddingFunc
import requests
import time
import json


def doubao_complete(messages, model="doubao-1-5-thinking-vision-pro-250428", temperature=0.1, max_tokens=4000):
    """调用豆包API进行文本生成"""
    api_key = os.getenv("ARK_API_KEY", "ecaa1600-6dab-4700-8655-63a260492b8c")
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
            "model": "doubao-embedding-v1",
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


async def test_queries():
    """测试问答功能"""
    print("=== RAG-Anything 问答测试 ===")
    
    # 设置工作目录
    working_dir = "./rag_storage"
    
    # 检查是否有已处理的知识库
    if not os.path.exists(working_dir):
        print(f"错误: 工作目录 {working_dir} 不存在")
        print("请先运行文档处理脚本")
        return
    
    # 创建配置
    config = RAGAnythingConfig(
        working_dir=working_dir,
        enable_image_processing=False,  # 禁用图像处理减少API调用
        enable_table_processing=False,  # 禁用表格处理
        enable_equation_processing=False,  # 禁用公式处理
    )
    
    # 创建嵌入函数
    embedding_func = EmbeddingFunc(
        embedding_dim=2048,  # 豆包嵌入维度
        max_token_size=8192,
        func=async_doubao_embed,
    )
    
    # 初始化RAGAnything
    rag = RAGAnything(
        config=config,
        llm_model_func=async_llm_model_func,
        embedding_func=embedding_func,
        lightrag_kwargs={
            "tiktoken_model_name": "gpt-3.5-turbo",
        },
    )
    
    # 测试查询
    test_queries = [
        "这个文档的主要内容是什么？",
        "文档中提到了哪些技术？",
        "总结一下这个文档的要点",
        "文档中有什么重要信息？"
    ]
    
    print(f"\n开始测试 {len(test_queries)} 个查询...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- 查询 {i}/{len(test_queries)} ---")
        print(f"问题: {query}")
        
        try:
            # 使用naive模式，避免复杂的实体关系查询
            result = await rag.aquery(query, mode="naive")
            print(f"回答: {result}")
        except Exception as e:
            print(f"查询失败: {e}")
        
        # 添加延迟避免API限制
        if i < len(test_queries):
            print("等待5秒...")
            await asyncio.sleep(5)
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    asyncio.run(test_queries())
