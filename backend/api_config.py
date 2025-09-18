#!/usr/bin/env python3
"""
API配置管理
"""

import os
from typing import Optional

class APIConfig:
    """API配置管理类"""
    
    def __init__(self):
        self.doubao_api_key = self.get_doubao_api_key()
        self.doubao_base_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        self.doubao_model = "doubao-1-5-pro-32k-250115"
    
    def get_doubao_api_key(self) -> Optional[str]:
        """获取豆包API密钥"""
        # 优先级：环境变量 > 配置文件 > 默认值
        api_key = os.getenv("ARK_API_KEY")
        
        if not api_key:
            # 尝试从配置文件读取
            try:
                with open("api_keys.txt", "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("ARK_API_KEY="):
                            api_key = line.split("=", 1)[1].strip()
                            break
            except FileNotFoundError:
                pass
        
        if not api_key:
            print("⚠️  警告：未找到豆包API密钥")
            print("请设置环境变量 ARK_API_KEY 或创建 api_keys.txt 文件")
            print("格式：ARK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        
        return api_key
    
    def is_api_key_valid(self) -> bool:
        """检查API密钥是否有效"""
        return self.doubao_api_key and self.doubao_api_key.startswith("sk-")
    
    def get_headers(self) -> dict:
        """获取API请求头"""
        if not self.is_api_key_valid():
            raise ValueError("API密钥无效或未设置")
        
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.doubao_api_key}"
        }

# 全局配置实例
api_config = APIConfig()


