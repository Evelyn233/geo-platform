#!/usr/bin/env python3
"""
简单方式将WordPress数据导入到RAG数据库
使用与simple_query.py相同的方式，避免复杂的LightRAG导入问题
"""

import os
import sys
import json
from pathlib import Path

# 添加项目路径
PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def doubao_complete(messages, model="doubao-1-5-pro-32k-250115", temperature=0.1, max_tokens=4000):
    """调用豆包API进行文本生成"""
    import time
    import requests
    
    # 直接设置API密钥
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

def load_wordpress_content():
    """加载WordPress内容"""
    wp_file = "./rag_storage/wordpress_rag_content.json"
    
    if not os.path.exists(wp_file):
        print(f"错误: 找不到WordPress数据文件 {wp_file}")
        return None
    
    with open(wp_file, 'r', encoding='utf-8') as f:
        wp_data = json.load(f)
    
    # 提取所有文本内容
    text_contents = []
    for item in wp_data:
        if item.get('type') == 'text':
            text_contents.append(item['text'])
    
    print(f"加载了 {len(text_contents)} 个文本内容")
    return text_contents

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

def save_to_rag_storage(content_list):
    """保存到RAG存储格式"""
    try:
        # 合并所有内容
        combined_content = "\n\n".join(content_list)
        
        # 保存为RAG-Anything可识别的格式
        doc_status_file = "./rag_storage/kv_store_doc_status.json"
        
        # 创建文档状态
        doc_status = {
            "wordpress_content": {
                "content_summary": combined_content,
                "source": "wordpress",
                "count": len(content_list),
                "status": "processed"
            }
        }
        
        with open(doc_status_file, 'w', encoding='utf-8') as f:
            json.dump(doc_status, f, ensure_ascii=False, indent=2)
        
        print(f"WordPress内容已保存到RAG存储: {doc_status_file}")
        
        # 也保存到简单的文本文件
        text_file = "./rag_storage/wordpress_content.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(combined_content)
        
        print(f"WordPress内容也保存为文本文件: {text_file}")
        
        return True
        
    except Exception as e:
        print(f"保存失败: {e}")
        return False

def main():
    """主函数"""
    print("=== WordPress数据导入到RAG数据库 ===")
    
    # 加载WordPress内容
    content_list = load_wordpress_content()
    if not content_list:
        print("没有找到WordPress内容")
        return
    
    # 保存到RAG存储
    if save_to_rag_storage(content_list):
        print("WordPress内容导入成功！")
        
        # 测试查询
        print("\n测试查询...")
        combined_content = "\n\n".join(content_list)
        
        test_questions = [
            "静钧研磨的主要产品是什么？",
            "百洁布有什么特点？",
            "公司的联系方式是什么？"
        ]
        
        for question in test_questions:
            print(f"\n问题: {question}")
            answer = ask_question(question, combined_content)
            print(f"回答: {answer}")
    else:
        print("导入失败")

if __name__ == "__main__":
    main()
