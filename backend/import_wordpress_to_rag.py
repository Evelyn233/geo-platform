#!/usr/bin/env python3
"""
将WordPress数据导入到RAG-Anything向量数据库
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# 添加项目路径
PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def doubao_complete(prompt=None, system_prompt=None, history_messages=None, messages=None, model=None, temperature=0.1, max_tokens=4000, **kwargs):
    """调用豆包API进行文本生成"""
    import time
    import requests
    
    api_key = os.getenv("ARK_API_KEY")
    if not api_key:
        raise RuntimeError("ARK_API_KEY is not set in environment")
    
    base_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    model = model or os.getenv("DOUBAO_MODEL", "doubao-1-5-pro-32k-250115")
    
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
    
    data = {"model": model, "messages": msg_list, "temperature": temperature, "max_tokens": max_tokens}
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    
    backoffs = [0, 2, 5, 10]
    last_err = None
    
    for delay in backoffs:
        if delay:
            time.sleep(delay)
        try:
            resp = requests.post(base_url, json=data, headers=headers, timeout=120)
            resp.raise_for_status()
            j = resp.json()
            return j["choices"][0]["message"]["content"]
        except Exception as e:
            last_err = e
            if "429" in str(e):
                continue
            break
    raise last_err if last_err else RuntimeError("Doubao request failed")

def doubao_embed(texts):
    """调用豆包API进行文本嵌入"""
    import time
    import requests
    
    api_key = os.getenv("ARK_API_KEY")
    if not api_key:
        raise RuntimeError("ARK_API_KEY is not set in environment")
    
    url = "https://ark.cn-beijing.volces.com/api/v3/embeddings"
    model = os.getenv("DOUBAO_EMBED_MODEL", "ep-20240613094406-3v7ht")
    
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    
    backoffs = [0, 2, 5]
    last_err = None
    
    for delay in backoffs:
        if delay:
            time.sleep(delay)
        try:
            resp = requests.post(url, json={"model": model, "input": texts}, headers=headers, timeout=120)
            resp.raise_for_status()
            j = resp.json()
            return [d["embedding"] for d in j.get("data", [])]
        except Exception as e:
            last_err = e
            if "429" in str(e):
                continue
            break
    raise last_err if last_err else RuntimeError("Doubao embedding failed")

async def async_doubao_embed(texts):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: doubao_embed(texts))

async def import_wordpress_to_rag():
    """将WordPress数据导入到RAG数据库"""
    try:
        from raganything import RAGAnything, RAGAnythingConfig
        from lightrag.utils import EmbeddingFunc
        
        print("正在初始化RAG-Anything...")
        
        # 配置
        config = RAGAnythingConfig(working_dir="./rag_storage")
        
        # 创建嵌入函数
        embedding_func = EmbeddingFunc(
            embedding_dim=2048,
            max_token_size=8192,
            func=async_doubao_embed,
        )
        
        # 初始化RAGAnything
        rag = RAGAnything(
            config=config,
            llm_model_func=doubao_complete,
            embedding_func=embedding_func,
            lightrag_kwargs={"tiktoken_model_name": "gpt-3.5-turbo"},
        )
        
        # 确保LightRAG初始化
        await rag._ensure_lightrag_initialized()
        print("RAG-Anything初始化完成")
        
        # 读取WordPress数据
        wp_file = "./rag_storage/wordpress_rag_content.json"
        if not os.path.exists(wp_file):
            print(f"错误: 找不到WordPress数据文件 {wp_file}")
            return
        
        with open(wp_file, 'r', encoding='utf-8') as f:
            wp_data = json.load(f)
        
        print(f"读取到 {len(wp_data)} 个WordPress内容项")
        
        # 处理文本内容
        text_contents = []
        for item in wp_data:
            if item.get('type') == 'text':
                text_contents.append(item['text'])
        
        print(f"准备处理 {len(text_contents)} 个文本内容")
        
        # 使用RAG-Anything的文本插入功能
        if text_contents:
            print("正在将文本内容插入到RAG数据库...")
            await rag.insert_text_content(text_contents)
            print("文本内容插入完成")
        
        # 处理图片内容
        image_contents = []
        for item in wp_data:
            if item.get('type') == 'image':
                image_contents.append({
                    'type': 'image',
                    'img_path': item['img_path'],
                    'text': item['text']
                })
        
        if image_contents:
            print(f"准备处理 {len(image_contents)} 个图片内容")
            # 使用RAG-Anything的多模态处理
            for img_item in image_contents:
                try:
                    await rag.process_multimodal_content([img_item])
                    print(f"处理图片: {img_item['img_path']}")
                except Exception as e:
                    print(f"处理图片失败 {img_item['img_path']}: {e}")
        
        print("WordPress数据导入完成！")
        
        # 测试查询
        print("\n测试查询...")
        test_query = "静钧研磨的主要产品是什么？"
        result = await rag.aquery(test_query)
        print(f"查询: {test_query}")
        print(f"回答: {result}")
        
    except Exception as e:
        print(f"导入失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("开始将WordPress数据导入到RAG数据库...")
    asyncio.run(import_wordpress_to_rag())

if __name__ == "__main__":
    main()
