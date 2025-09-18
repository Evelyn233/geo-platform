#!/usr/bin/env python3
"""
RAG-Anything 问答系统开发
基于已处理的简历文档进行问答测试
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


def doubao_complete(messages, model="doubao-1-5-pro-32k-250115", temperature=0.1, max_tokens=4000):
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


class QASystem:
    """问答系统类"""
    
    def __init__(self, working_dir="./rag_storage"):
        self.working_dir = working_dir
        self.rag = None
        self.setup_rag()
    
    def setup_rag(self):
        """设置RAG系统"""
        # 创建配置
        config = RAGAnythingConfig(
            working_dir=self.working_dir,
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
        self.rag = RAGAnything(
            config=config,
            llm_model_func=async_llm_model_func,
            embedding_func=embedding_func,
            lightrag_kwargs={
                "tiktoken_model_name": "gpt-3.5-turbo",
            },
        )
        
        # 手动初始化LightRAG实例
        from lightrag import LightRAG
        self.rag.lightrag = LightRAG(
            working_dir=self.working_dir,
            llm_model_func=async_llm_model_func,
            embedding_func=embedding_func,
            tiktoken_model_name="gpt-3.5-turbo",
        )
    
    async def ask_question(self, question, mode="hybrid"):
        """提问"""
        try:
            result = await self.rag.aquery(question, mode=mode)
            return result
        except Exception as e:
            return f"回答问题时出错: {e}"
    
    async def batch_questions(self, questions, mode="hybrid"):
        """批量提问"""
        results = []
        for i, question in enumerate(questions, 1):
            print(f"\n--- 问题 {i}/{len(questions)} ---")
            print(f"问题: {question}")
            
            answer = await self.ask_question(question, mode)
            print(f"回答: {answer}")
            
            results.append({
                "question": question,
                "answer": answer
            })
            
            # 添加延迟避免API限制
            if i < len(questions):
                print("等待5秒...")
                await asyncio.sleep(5)
        
        return results


async def test_resume_qa():
    """测试简历问答"""
    print("=== RAG-Anything 简历问答系统 ===")
    
    # 检查工作目录
    if not os.path.exists("./rag_storage"):
        print("错误: 找不到rag_storage目录")
        print("请先运行文档处理脚本")
        return
    
    # 创建问答系统
    qa_system = QASystem()
    
    # 简历相关问题
    resume_questions = [
        "这个人的姓名是什么？",
        "他有什么工作经历？",
        "他掌握哪些技术技能？",
        "他的教育背景如何？",
        "总结一下这个人的主要特点",
        "他有什么项目经验？",
        "他的联系方式是什么？",
        "他有什么特殊技能或证书？"
    ]
    
    print(f"开始测试 {len(resume_questions)} 个简历相关问题...")
    
    # 批量提问
    results = await qa_system.batch_questions(resume_questions)
    
    # 保存结果
    with open("qa_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 问答测试完成 ===")
    print(f"结果已保存到 qa_results.json")
    
    return results


async def interactive_qa():
    """交互式问答"""
    print("=== 交互式问答模式 ===")
    
    qa_system = QASystem()
    
    print("输入 'quit' 或 'exit' 退出")
    print("输入 'mode:naive' 或 'mode:hybrid' 切换查询模式")
    
    current_mode = "hybrid"
    
    while True:
        try:
            user_input = input(f"\n[{current_mode}] 请输入您的问题: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("再见！")
                break
            
            if user_input.startswith('mode:'):
                new_mode = user_input.split(':')[1]
                if new_mode in ['naive', 'hybrid', 'local', 'global']:
                    current_mode = new_mode
                    print(f"已切换到 {current_mode} 模式")
                else:
                    print("无效模式，支持: naive, hybrid, local, global")
                continue
            
            if not user_input:
                continue
            
            print("正在思考...")
            answer = await qa_system.ask_question(user_input, mode=current_mode)
            print(f"回答: {answer}")
            
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"发生错误: {e}")


def main():
    """主函数"""
    print("RAG-Anything 问答系统")
    print("1. 测试简历问答")
    print("2. 交互式问答")
    print("3. 退出")
    
    choice = input("请选择 (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(test_resume_qa())
    elif choice == "2":
        asyncio.run(interactive_qa())
    elif choice == "3":
        print("再见！")
    else:
        print("无效选择")


if __name__ == "__main__":
    main()
