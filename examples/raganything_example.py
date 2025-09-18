#!/usr/bin/env python
"""
Example script demonstrating the integration of MinerU parser with RAGAnything

This example shows how to:
1. Process documents with RAGAnything using MinerU parser
2. Perform pure text queries using aquery() method
3. Perform multimodal queries with specific multimodal content using aquery_with_multimodal() method
4. Handle different types of multimodal content (tables, equations) in queries
"""

import os
import argparse
import asyncio
import logging
import logging.config
from pathlib import Path

# Add project root directory to Python path
import sys

sys.path.append(str(Path(__file__).parent.parent))

import requests
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc, logger, set_verbose_debug
from raganything import RAGAnything, RAGAnythingConfig

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", override=False)


def configure_logging():
    """Configure logging for the application"""
    # Get log directory path from environment variable or use current directory
    log_dir = os.getenv("LOG_DIR", os.getcwd())
    log_file_path = os.path.abspath(os.path.join(log_dir, "raganything_example.log"))

    print(f"\nRAGAnything example log file: {log_file_path}\n")
    os.makedirs(os.path.dirname(log_dir), exist_ok=True)

    # Get log file max size and backup count from environment variables
    log_max_bytes = int(os.getenv("LOG_MAX_BYTES", 10485760))  # Default 10MB
    log_backup_count = int(os.getenv("LOG_BACKUP_COUNT", 5))  # Default 5 backups

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(levelname)s: %(message)s",
                },
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
                "file": {
                    "formatter": "detailed",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": log_file_path,
                    "maxBytes": log_max_bytes,
                    "backupCount": log_backup_count,
                    "encoding": "utf-8",
                },
            },
            "loggers": {
                "lightrag": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }
    )

    # Set the logger level to INFO
    logger.setLevel(logging.INFO)
    # Enable verbose debug if needed
    set_verbose_debug(os.getenv("VERBOSE", "false").lower() == "true")


async def process_with_rag(
    file_path: str,
    output_dir: str,
    api_key: str,
    base_url: str = None,
    working_dir: str = "./rag_storage",
    parser: str = "mineru",
    max_chars: int = None,  # 新增：限制处理的字符数
):
    """
    Process document with RAGAnything

    Args:
        file_path: Path to the document
        output_dir: Output directory for RAG results
        api_key: OpenAI API key
        base_url: Optional base URL for API
        working_dir: Working directory for RAG storage
    """
    try:
        # Create RAGAnything configuration
        config = RAGAnythingConfig(
            working_dir=working_dir or "./rag_storage",
            parser=parser,  # Parser selection: mineru or docling
            parse_method="auto",  # Parse method: auto, ocr, or txt
            enable_image_processing=False,
            enable_table_processing=False,
            enable_equation_processing=False,
        )

        # Define Doubao LLM adapter function
        def doubao_complete(prompt, system_prompt=None, history_messages=[], messages=None, api_key=None, **kwargs):
            url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
            api_key = api_key or os.getenv("ARK_API_KEY")
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            # Truncate overly long prompt to reduce timeouts
            if prompt and isinstance(prompt, str) and len(prompt) > 4000:
                prompt = prompt[:4000] + "..."
            if messages is not None:
                msg_list = messages
            else:
                msg_list = []
                if system_prompt:
                    msg_list.append({"role": "system", "content": system_prompt})
                if history_messages:
                    msg_list.extend(history_messages)
                msg_list.append({"role": "user", "content": prompt})
            # 支持模型切换
            model_name = os.getenv("DOUBAO_MODEL", "doubao-1-5-pro-32k-250115")
            data = {
                "model": model_name,
                "messages": msg_list
            }
            # Add simple throttle and robust retry on 429
            import time
            backoffs = [0, 5, 15, 30]  # initial + progressive backoffs
            last_err = None
            for delay in backoffs:
                if delay:
                    time.sleep(delay)
                # always apply a small per-request throttle
                time.sleep(3)
                try:
                    resp = requests.post(url, headers=headers, json=data, timeout=120)
                    resp.raise_for_status()
                    result = resp.json()
                    return result["choices"][0]["message"]["content"]
                except requests.exceptions.HTTPError as e:
                    last_err = e
                    if getattr(e.response, "status_code", None) == 429:
                        # try next backoff
                        continue
                    raise
            # exhausted retries
            raise last_err if last_err else Exception("Doubao request failed after retries")

        # Define LLM model function (use Doubao)
        def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
            return doubao_complete(
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                api_key=api_key,
                **kwargs,
            )

        # 包装 llm_model_func 为 async 版本，兼容 lightrag await 调用
        import asyncio
        async def async_llm_model_func(*args, **kwargs):
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: llm_model_func(*args, **kwargs))

        # Define a simple tokenizer class with encode method for Doubao/LLM
        class SimpleTokenizer:
            def encode(self, text):
                # 简单分词，每个词一个token（适配lightrag要求）
                return text.split()
            def decode(self, tokens):
                # 简单拼接token为字符串
                return " ".join(tokens)
        tokenizer = SimpleTokenizer()

        # Define vision model function for image processing (use Doubao)
        def vision_model_func(
            prompt,
            system_prompt=None,
            history_messages=[],
            image_data=None,
            messages=None,
            **kwargs,
        ):
            # If messages format is provided (for multimodal VLM enhanced query), use it directly
            if messages:
                return doubao_complete(
                    prompt,
                    system_prompt=system_prompt,
                    history_messages=history_messages,
                    messages=messages,
                    api_key=api_key,
                    **kwargs,
                )
            # Traditional single image format
            elif image_data:
                # Assemble messages for image+text
                msg_list = []
                if system_prompt:
                    msg_list.append({"role": "system", "content": system_prompt})
                msg_list.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                    ]
                })
                return doubao_complete(
                    prompt,
                    system_prompt=system_prompt,
                    history_messages=history_messages,
                    messages=msg_list,
                    api_key=api_key,
                    **kwargs,
                )
            # Pure text format
            else:
                return llm_model_func(prompt, system_prompt, history_messages, **kwargs)

        # Wrap vision model as async for LightRAG
        async def async_vision_model_func(*args, **kwargs):
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: vision_model_func(*args, **kwargs))

        # Define Doubao embedding adapter function
        import numpy as np
        import base64
        import json
        import inspect
        import asyncio
        def doubao_embed(texts, model=None, api_key=None, **kwargs):
            url = "https://ark.cn-beijing.volces.com/api/v3/embeddings/multimodal"
            # 优先用传入的 api_key，否则用 ARK_EMBEDDING_API_KEY，否则用 ARK_API_KEY
            api_key = api_key or os.getenv("ARK_EMBEDDING_API_KEY") or os.getenv("ARK_API_KEY")
            if api_key:
                print(f"Using embedding API key: {api_key[:10]}...")  # 调试输出
            else:
                print("Warning: No embedding API key found!")
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            # 豆包API一次只能处理一个文本，需要逐个处理
            embeddings = []
            for i, text in enumerate(texts):
                # 限制文本长度
                max_length = 4000
                if len(text) > max_length:
                    print(f"Warning: Text too long ({len(text)} chars), truncating to {max_length} chars")
                    text = text[:max_length] + "..."
                
                input_list = [{"type": "text", "text": text}]
                data = {
                    "model": "doubao-embedding-vision-250615",
                    "encoding_format": "float",
                    "input": input_list
                }
                
                # 添加请求间隔，避免频率限制
                if i > 0:
                    import time
                    time.sleep(1)  # 等待1秒
                
                try:
                    # 增加超时时间到120秒
                    resp = requests.post(url, headers=headers, json=data, timeout=120)
                    resp.raise_for_status()
                    result = resp.json()
                    
                    # 调试输出
                    print(f"Processing text {i+1}/{len(texts)}: {text[:50]}...")
                    print(f"API response keys: {list(result.keys())}")
                    
                    # 解析embedding - 处理不同的返回格式
                    if "data" in result:
                        if isinstance(result["data"], dict) and "embedding" in result["data"]:
                            # 格式: {"data": {"embedding": [...]}}
                            embeddings.append(result["data"]["embedding"])
                        elif isinstance(result["data"], list) and len(result["data"]) > 0:
                            if isinstance(result["data"][0], dict) and "embedding" in result["data"][0]:
                                # 格式: {"data": [{"embedding": [...]}]}
                                embeddings.append(result["data"][0]["embedding"])
                            else:
                                # 格式: {"data": [[...]]}
                                embeddings.append(result["data"][0])
                        else:
                            print(f"Unexpected data format: {result['data']}")
                            # 生成随机向量作为fallback
                            import numpy as np
                            embeddings.append(np.random.rand(2048).tolist())
                    else:
                        print(f"No 'data' field in response: {result}")
                        # 生成随机向量作为fallback
                        import numpy as np
                        embeddings.append(np.random.rand(2048).tolist())
                        
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:
                        print(f"Rate limit hit, waiting 5 seconds...")
                        import time
                        time.sleep(5)
                        # 重试一次
                        resp = requests.post(url, headers=headers, json=data, timeout=120)
                        resp.raise_for_status()
                        result = resp.json()
                        # 解析结果...
                        if "data" in result and isinstance(result["data"], dict) and "embedding" in result["data"]:
                            embeddings.append(result["data"]["embedding"])
                        else:
                            import numpy as np
                            embeddings.append(np.random.rand(2048).tolist())
                    else:
                        print(f"HTTP Error: {e}")
                        import numpy as np
                        embeddings.append(np.random.rand(2048).tolist())
                except Exception as e:
                    print(f"Error processing text {i+1}: {e}")
                    print(f"Response: {result if 'result' in locals() else 'No response'}")
                    # 生成随机向量作为fallback
                    import numpy as np
                    embeddings.append(np.random.rand(2048).tolist())
            
            return embeddings
        # 包装为 async 版本
        async def async_doubao_embed(texts, model=None, api_key=None, **kwargs):
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: doubao_embed(texts, model=model, api_key=api_key, **kwargs))
        embedding_func = EmbeddingFunc(
            embedding_dim=2048,  # match Doubao embedding dimension
            max_token_size=8192,
            func=async_doubao_embed,
        )

        # Initialize RAGAnything with new dataclass structure
        rag = RAGAnything(
            config=config,
            llm_model_func=async_llm_model_func,
            vision_model_func=async_vision_model_func,
            embedding_func=embedding_func,
            lightrag_kwargs={
                "tiktoken_model_name": "gpt-3.5-turbo",
                "tokenizer": tokenizer,
            },
        )

        # Process document
        await rag.process_document_complete(
            file_path=file_path, output_dir=output_dir, parse_method="auto"
        )

        # 直接进行问答测试
        logger.info("\n=== 开始问答测试 ===")
        
        # 简历相关问题
        resume_questions = [
            "这个人的姓名是什么？",
            "他有什么工作经历？", 
            "他掌握哪些技术技能？",
            "他的教育背景如何？",
            "总结一下这个人的主要特点"
        ]
        
        logger.info(f"开始测试 {len(resume_questions)} 个简历相关问题...")
        
        for i, question in enumerate(resume_questions, 1):
            logger.info(f"\n--- 问题 {i}/{len(resume_questions)} ---")
            logger.info(f"问题: {question}")
            
            try:
                # 使用naive模式，避免复杂的实体关系查询
                result = await rag.aquery(question, mode="naive")
                logger.info(f"回答: {result}")
            except Exception as e:
                logger.error(f"查询失败: {e}")
            
            # 添加延迟避免API限制
            if i < len(resume_questions):
                logger.info("等待5秒...")
                import time
                time.sleep(5)
        
        logger.info("\n=== 问答测试完成 ===")
        
        # 交互式问答
        logger.info("\n=== 交互式问答模式 ===")
        logger.info("输入 'quit' 或 'exit' 退出")
        logger.info("输入 'mode:naive' 或 'mode:hybrid' 切换查询模式")
        
        current_mode = "naive"
        
        while True:
            try:
                user_input = input(f"\n[{current_mode}] 请输入您的问题: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '退出']:
                    logger.info("再见！")
                    break
                
                if user_input.startswith('mode:'):
                    new_mode = user_input.split(':')[1]
                    if new_mode in ['naive', 'hybrid', 'local', 'global']:
                        current_mode = new_mode
                        logger.info(f"已切换到 {current_mode} 模式")
                    else:
                        logger.info("无效模式，支持: naive, hybrid, local, global")
                    continue
                
                if not user_input:
                    continue
                
                logger.info("正在思考...")
                answer = await rag.aquery(user_input, mode=current_mode)
                logger.info(f"回答: {answer}")
                
            except KeyboardInterrupt:
                logger.info("\n\n再见！")
                break
            except Exception as e:
                logger.error(f"发生错误: {e}")

    except Exception as e:
        logger.error(f"Error processing with RAG: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())


def main():
    """Main function to run the example"""
    parser = argparse.ArgumentParser(description="MinerU RAG Example")
    parser.add_argument("file_path", help="Path to the document to process")
    parser.add_argument(
        "--working_dir", "-w", default="./rag_storage", help="Working directory path"
    )
    parser.add_argument(
        "--output", "-o", default="./output", help="Output directory path"
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("LLM_BINDING_API_KEY"),
        help="OpenAI API key (defaults to LLM_BINDING_API_KEY env var)",
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("LLM_BINDING_HOST"),
        help="Optional base URL for API",
    )
    parser.add_argument(
        "--parser",
        default=os.getenv("PARSER", "mineru"),
        help="Optional base URL for API",
    )

    args = parser.parse_args()

    # Check if API key is provided
    if not args.api_key:
        logger.error("Error: OpenAI API key is required")
        logger.error("Set api key environment variable or use --api-key option")
        return

    # Create output directory if specified
    if args.output:
        os.makedirs(args.output, exist_ok=True)

    # Process with RAG
    asyncio.run(
        process_with_rag(
            args.file_path,
            args.output,
            args.api_key,
            args.base_url,
            args.working_dir,
            args.parser,
        )
    )


if __name__ == "__main__":
    # Configure logging first
    configure_logging()

    print("RAGAnything Example")
    print("=" * 30)
    print("Processing document with multimodal RAG pipeline")
    print("=" * 30)

    main()
