#!/usr/bin/env python3
"""
模型配置管理 - 清晰分类展示
"""

class ModelConfig:
    """模型配置类 - 按功能分类整理"""
    
    # ==================== 豆包模型配置 ====================
    # 基于你的资源包，每个模型都有50万token额度
    
    # 🚀 快速响应类模型
    FAST_MODELS = {
        "doubao-seed-1-6-flash": {
            "name": "豆包Seed 1.6 Flash",
            "description": "⚡ 快速响应模型，适合实时对话和简单任务",
            "max_tokens": 8000,
            "cost_level": "低",
            "recommended_for": "日常对话、快速问答"
        },
        "doubao-1-5-lite-32k": {
            "name": "豆包1.5 Lite 32K", 
            "description": "💡 轻量级模型，经济实用，长上下文支持",
            "max_tokens": 32000,
            "cost_level": "低",
            "recommended_for": "长文档处理、成本敏感任务"
        }
    }
    
    # 🎯 专业功能类模型
    PROFESSIONAL_MODELS = {
        "doubao-seed-1-6": {
            "name": "豆包Seed 1.6",
            "description": "🌟 最新种子模型，性能优异，通用性强",
            "max_tokens": 8000,
            "cost_level": "中等",
            "recommended_for": "复杂任务、高质量内容生成"
        },
        "doubao-1-5-pro-32k": {
            "name": "豆包1.5 Pro 32K",
            "description": "💪 专业模型，适合复杂任务和长文档",
            "max_tokens": 32000,
            "cost_level": "高",
            "recommended_for": "专业写作、技术文档"
        },
        "doubao-1-5-pro-256k": {
            "name": "豆包1.5 Pro 256K",
            "description": "📚 超长上下文模型，适合超长文档处理",
            "max_tokens": 256000,
            "cost_level": "高",
            "recommended_for": "书籍、长篇小说、大型文档"
        }
    }
    
    # 👁️ 视觉理解类模型
    VISION_MODELS = {
        "doubao-1-5-vision-pro": {
            "name": "豆包1.5 Vision Pro",
            "description": "👁️ 视觉理解模型，支持图像分析和描述",
            "max_tokens": 8000,
            "cost_level": "中等",
            "recommended_for": "图像分析、视觉内容生成"
        },
        "doubao-seed-1-6-vision": {
            "name": "豆包Seed 1.6 Vision",
            "description": "👁️ 最新视觉种子模型，图像理解能力强",
            "max_tokens": 8000,
            "cost_level": "中等",
            "recommended_for": "高级图像分析、视觉创作"
        },
        "doubao-1-5-vision-pro-32k": {
            "name": "豆包1.5 Vision Pro 32K",
            "description": "👁️ 视觉理解+长上下文，适合复杂视觉任务",
            "max_tokens": 32000,
            "cost_level": "中等",
            "recommended_for": "长文档+图像分析"
        }
    }
    
    # 🎨 专业应用类模型
    SPECIALIZED_MODELS = {
        "doubao-1-5-ui-tars": {
            "name": "豆包1.5 UI TARS",
            "description": "🎨 UI交互模型，专门用于界面设计和交互",
            "max_tokens": 8000,
            "cost_level": "中等",
            "recommended_for": "UI设计、界面开发、交互设计"
        }
    }
    
    # 合并所有豆包模型
    DOUBAO_MODELS = {**FAST_MODELS, **PROFESSIONAL_MODELS, **VISION_MODELS, **SPECIALIZED_MODELS}
    
    # ==================== Kimi模型配置 ====================
    KIMI_MODELS = {
        "kimi-k2-250905": {
            "name": "Kimi K2",
            "description": "🤖 智能助手模型，适合对话和问答",
            "max_tokens": 8000,
            "cost_level": "中等",
            "recommended_for": "智能对话、问答系统"
        }
    }
    
    # ==================== 模型汇总 ====================
    # 合并所有模型
    ALL_MODELS = {**DOUBAO_MODELS, **KIMI_MODELS}
    
    # 默认配置
    DEFAULT_MODEL = "doubao-seed-1-6-flash"  # 使用快速响应模型作为默认
    DEFAULT_MAX_TOKENS = 2000
    DEFAULT_TEMPERATURE = 0.7
    
    # ==================== 模型分类统计 ====================
    MODEL_CATEGORIES = {
        "快速响应": list(FAST_MODELS.keys()),
        "专业功能": list(PROFESSIONAL_MODELS.keys()),
        "视觉理解": list(VISION_MODELS.keys()),
        "专业应用": list(SPECIALIZED_MODELS.keys()),
        "Kimi模型": list(KIMI_MODELS.keys())
    }
    
    @classmethod
    def get_model_info(cls, model_name: str) -> dict:
        """获取模型信息"""
        return cls.ALL_MODELS.get(model_name, {
            "name": model_name,
            "description": "未知模型",
            "max_tokens": 4000,
            "cost_level": "未知"
        })
    
    @classmethod
    def get_available_models(cls) -> list:
        """获取可用模型列表"""
        return list(cls.ALL_MODELS.keys())
    
    @classmethod
    def get_model_type(cls, model_name: str) -> str:
        """获取模型类型"""
        if model_name in cls.DOUBAO_MODELS:
            return "doubao"
        elif model_name in cls.KIMI_MODELS:
            return "kimi"
        else:
            return "unknown"
    
    @classmethod
    def get_recommended_tokens(cls, model_name: str) -> int:
        """获取推荐的最大token数"""
        model_info = cls.get_model_info(model_name)
        max_tokens = model_info["max_tokens"]
        
        # 根据模型类型推荐token数
        if "flash" in model_name or "lite" in model_name:
            return min(2000, max_tokens // 4)  # 快速模型，较少token
        elif "32k" in model_name:
            return min(4000, max_tokens // 8)
        elif "256k" in model_name:
            return min(8000, max_tokens // 32)
        elif "vision" in model_name:
            return min(3000, max_tokens // 3)  # 视觉模型
        else:
            return min(2000, max_tokens // 4)
    
    @classmethod
    def get_models_by_category(cls, category: str) -> dict:
        """根据分类获取模型"""
        return cls.MODEL_CATEGORIES.get(category, {})
    
    @classmethod
    def print_model_summary(cls):
        """打印模型配置摘要"""
        print("=" * 60)
        print("🤖 可用模型配置摘要")
        print("=" * 60)
        
        for category, models in cls.MODEL_CATEGORIES.items():
            print(f"\n📂 {category} ({len(models)}个模型):")
            for model_id in models:
                info = cls.get_model_info(model_id)
                print(f"  • {info['name']} - {info['description']}")
                print(f"    Token: {info['max_tokens']:,} | 成本: {info['cost_level']} | 推荐: {info.get('recommended_for', '通用')}")
        
        print(f"\n🎯 默认模型: {cls.DEFAULT_MODEL}")
        print(f"📊 总模型数: {len(cls.ALL_MODELS)}")
        print("=" * 60)

# 全局配置实例
model_config = ModelConfig()
