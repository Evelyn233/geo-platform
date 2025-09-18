#!/usr/bin/env python3
"""
基于已提取内容的简单问答脚本
"""

import json
import os
import requests
import time


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


def load_document_content():
    """加载已提取的文档内容"""
    doc_status_file = "rag_storage/kv_store_doc_status.json"
    
    if not os.path.exists(doc_status_file):
        print("错误: 找不到文档状态文件")
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


def main():
    """主函数"""
    print("=== 基于文档内容的问答系统 ===")
    
    # 加载文档内容
    document_content = load_document_content()
    if not document_content:
        print("无法加载文档内容")
        return
    
    print(f"已加载文档内容 ({len(document_content)} 字符)")
    print(f"内容预览: {document_content[:200]}...")
    
    # 预定义的问题
    questions = [
        "这个文档的主要内容是什么？",
        "文档中提到了哪些技术或技能？",
        "这个人的工作经历如何？",
        "总结一下这个文档的要点",
        "文档中有什么重要信息？"
    ]
    
    print(f"\n开始回答 {len(questions)} 个问题...")
    
    for i, question in enumerate(questions, 1):
        print(f"\n--- 问题 {i}/{len(questions)} ---")
        print(f"问题: {question}")
        
        answer = ask_question(question, document_content)
        print(f"回答: {answer}")
        
        # 添加延迟避免API限制
        if i < len(questions):
            print("等待5秒...")
            time.sleep(5)
    
    # 交互式问答
    print(f"\n=== 交互式问答模式 ===")
    print("输入 'quit' 或 'exit' 退出")
    
    while True:
        try:
            user_question = input("\n请输入您的问题: ").strip()
            
            if user_question.lower() in ['quit', 'exit', '退出']:
                print("再见！")
                break
            
            if not user_question:
                continue
            
            print("正在思考...")
            answer = ask_question(user_question, document_content)
            print(f"回答: {answer}")
            
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"发生错误: {e}")


if __name__ == "__main__":
    main()








