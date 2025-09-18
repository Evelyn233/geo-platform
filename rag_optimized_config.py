#!/usr/bin/env python3
"""
RAG-Anything 优化的模型配置
"""

import os

class RAGModelConfig:
    """RAG-Anything 模型配置优化"""
    
    # 推荐的模型配置
    RECOMMENDED_MODELS = {
        "doubao-pro-32k": {
            "description": "推荐：32K上下文，适合长文档处理",
            "context_length": 32768,
            "cost": "medium",
            "stability": "high",
            "best_for": ["实体提取", "长文档分析", "关系构建"]
        },
        "doubao-1-5-pro": {
            "description": "平衡选择：性能好，成本适中",
            "context_length": 8192,
            "cost": "low",
            "stability": "high", 
            "best_for": ["日常问答", "文档摘要", "多模态处理"]
        },
        "doubao-lite-32k": {
            "description": "经济选择：32K上下文，低成本",
            "context_length": 32768,
            "cost": "lowest",
            "stability": "medium",
            "best_for": ["预算有限", "长文档", "批量处理"]
        }
    }
    
    # 不推荐的模型
    NOT_RECOMMENDED = {
        "doubao-1-5-thinking-vision-pro-250428": "当前使用，但429错误频繁，稳定性差"
    }
    
    @classmethod
    def get_best_model_for_task(cls, task_type="general"):
        """根据任务类型推荐最佳模型"""
        if task_type == "long_document":
            return "doubao-pro-32k"
        elif task_type == "cost_effective":
            return "doubao-lite-32k"
        else:  # general
            return "doubao-1-5-pro"
    
    @classmethod
    def setup_environment(cls, model_name):
        """设置环境变量"""
        os.environ["DOUBAO_MODEL"] = model_name
        print(f"已设置模型: {model_name}")
        print(f"模型信息: {cls.RECOMMENDED_MODELS.get(model_name, {}).get('description', '未知模型')}")
    
    @classmethod
    def show_recommendations(cls):
        """显示推荐信息"""
        print("=== RAG-Anything 模型推荐 ===")
        print()
        
        print("🥇 推荐模型:")
        for model, info in cls.RECOMMENDED_MODELS.items():
            print(f"  {model}")
            print(f"    描述: {info['description']}")
            print(f"    上下文: {info['context_length']} tokens")
            print(f"    成本: {info['cost']}")
            print(f"    稳定性: {info['stability']}")
            print(f"    适用: {', '.join(info['best_for'])}")
            print()
        
        print("❌ 不推荐:")
        for model, reason in cls.NOT_RECOMMENDED.items():
            print(f"  {model}: {reason}")
        print()
        
        print("💡 使用建议:")
        print("  1. 长文档处理 → doubao-pro-32k")
        print("  2. 日常使用 → doubao-1-5-pro") 
        print("  3. 预算有限 → doubao-lite-32k")
        print("  4. 避免使用当前模型（429错误频繁）")


def main():
    """主函数"""
    config = RAGModelConfig()
    config.show_recommendations()
    
    print("\n=== 快速设置 ===")
    print("选择要使用的模型:")
    print("1. doubao-pro-32k (推荐)")
    print("2. doubao-1-5-pro (平衡)")
    print("3. doubao-lite-32k (经济)")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    model_map = {
        "1": "doubao-pro-32k",
        "2": "doubao-1-5-pro", 
        "3": "doubao-lite-32k"
    }
    
    if choice in model_map:
        model = model_map[choice]
        config.setup_environment(model)
        print(f"\n✅ 已设置模型: {model}")
        print("现在可以运行RAG-Anything了:")
        print(f"$env:DOUBAO_MODEL=\"{model}\"")
        print("python examples/raganything_example.py your_document.pdf --api-key your_key")
    else:
        print("无效选择")


if __name__ == "__main__":
    main()








