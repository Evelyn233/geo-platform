#!/usr/bin/env python3
"""
离线问答脚本 - 基于已提取的文档内容进行本地问答
避免频繁API调用导致的429错误
"""

import json
import os
import re


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


def simple_search(content, keywords):
    """简单的关键词搜索"""
    content_lower = content.lower()
    keywords_lower = [kw.lower() for kw in keywords]
    
    found_sentences = []
    sentences = re.split(r'[.!?。！？\n]', content)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if any(keyword in sentence.lower() for keyword in keywords_lower):
            found_sentences.append(sentence)
    
    return found_sentences


def answer_question(question, document_content):
    """基于文档内容回答问题（本地处理）"""
    question_lower = question.lower()
    
    # 根据问题类型提取相关信息
    if "主要内容" in question or "内容" in question:
        # 返回前几段作为主要内容
        paragraphs = document_content.split('\n\n')
        main_content = '\n'.join(paragraphs[:3])
        return f"文档主要内容：\n{main_content}"
    
    elif "技术" in question or "技能" in question:
        # 搜索技术相关词汇
        tech_keywords = ["技术", "技能", "experience", "ai", "python", "machine learning", "deep learning", "programming", "development"]
        tech_sentences = simple_search(document_content, tech_keywords)
        if tech_sentences:
            return f"技术技能相关信息：\n" + "\n".join(tech_sentences[:5])
        else:
            return "文档中未找到明确的技术技能信息"
    
    elif "工作经历" in question or "经验" in question:
        # 搜索工作经历相关词汇
        work_keywords = ["工作", "experience", "工作经历", "career", "position", "role", "company", "公司"]
        work_sentences = simple_search(document_content, work_keywords)
        if work_sentences:
            return f"工作经历相关信息：\n" + "\n".join(work_sentences[:5])
        else:
            return "文档中未找到明确的工作经历信息"
    
    elif "总结" in question or "要点" in question:
        # 提取关键信息
        lines = document_content.split('\n')
        key_lines = [line.strip() for line in lines if line.strip() and len(line.strip()) > 10]
        summary = '\n'.join(key_lines[:8])
        return f"文档要点总结：\n{summary}"
    
    else:
        # 通用搜索
        words = question.split()
        relevant_sentences = simple_search(document_content, words)
        if relevant_sentences:
            return f"相关信息：\n" + "\n".join(relevant_sentences[:3])
        else:
            return "在文档中未找到相关信息"


def main():
    """主函数"""
    print("=== 离线文档问答系统 ===")
    print("基于已提取的文档内容进行本地问答，无需API调用")
    
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
        
        answer = answer_question(question, document_content)
        print(f"回答: {answer}")
    
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
            
            answer = answer_question(user_question, document_content)
            print(f"回答: {answer}")
            
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"发生错误: {e}")


if __name__ == "__main__":
    main()








