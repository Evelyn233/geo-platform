#!/usr/bin/env python3
"""
豆包模型切换器 - 测试不同的豆包模型
"""

import requests
import time
import json
import os


class DoubaoModelSwitcher:
    """豆包模型切换器"""
    
    def __init__(self):
        self.api_key = os.getenv("ARK_API_KEY", "ecaa1600-6dab-4700-8655-63a260492b8c")
        self.base_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        
        # 豆包可用模型列表
        self.available_models = {
            "doubao-1-5-thinking-vision-pro-250428": "当前使用的模型 - 多模态思维模型",
            "doubao-pro-32k": "豆包Pro 32K上下文模型",
            "doubao-pro-4k": "豆包Pro 4K上下文模型", 
            "doubao-lite-4k": "豆包Lite 4K上下文模型",
            "doubao-lite-32k": "豆包Lite 32K上下文模型",
            "doubao-1-5-pro": "豆包1.5 Pro模型",
            "doubao-1-5-lite": "豆包1.5 Lite模型"
        }
    
    def list_models(self):
        """列出可用模型"""
        print("=== 豆包可用模型列表 ===")
        for model, description in self.available_models.items():
            print(f"模型: {model}")
            print(f"描述: {description}")
            print("-" * 50)
    
    def test_model(self, model_name, test_message="你好，请简单介绍一下自己"):
        """测试指定模型"""
        print(f"\n=== 测试模型: {model_name} ===")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": model_name,
            "messages": [{"role": "user", "content": test_message}],
            "temperature": 0.1,
            "max_tokens": 1000
        }
        
        # 增加延迟避免429
        time.sleep(5)
        
        try:
            resp = requests.post(self.base_url, headers=headers, json=data, timeout=120)
            resp.raise_for_status()
            result = resp.json()
            
            response_text = result["choices"][0]["message"]["content"]
            print(f"✅ 模型 {model_name} 测试成功")
            print(f"响应: {response_text[:200]}...")
            return True, response_text
            
        except Exception as e:
            print(f"❌ 模型 {model_name} 测试失败: {e}")
            return False, str(e)
    
    def test_all_models(self):
        """测试所有可用模型"""
        print("=== 开始测试所有豆包模型 ===")
        
        results = {}
        for model_name in self.available_models.keys():
            success, result = self.test_model(model_name)
            results[model_name] = {"success": success, "result": result}
            
            # 测试间隔
            time.sleep(10)
        
        # 汇总结果
        print("\n=== 测试结果汇总 ===")
        for model, result in results.items():
            status = "✅ 成功" if result["success"] else "❌ 失败"
            print(f"{model}: {status}")
        
        return results
    
    def get_available_models_from_api(self):
        """从API获取可用模型列表"""
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            resp = requests.get(
                "https://ark.cn-beijing.volces.com/api/v3/models",
                headers=headers,
                timeout=30
            )
            resp.raise_for_status()
            result = resp.json()
            
            print("=== 从API获取的可用模型 ===")
            for model in result.get("data", []):
                print(f"模型ID: {model.get('id')}")
                print(f"模型名称: {model.get('name', 'N/A')}")
                print(f"创建时间: {model.get('created', 'N/A')}")
                print("-" * 30)
            
            return result.get("data", [])
            
        except Exception as e:
            print(f"获取模型列表失败: {e}")
            return []


def main():
    """主函数"""
    switcher = DoubaoModelSwitcher()
    
    print("豆包模型切换器")
    print("1. 列出可用模型")
    print("2. 测试所有模型")
    print("3. 测试指定模型")
    print("4. 从API获取模型列表")
    print("5. 退出")
    
    while True:
        try:
            choice = input("\n请选择操作 (1-5): ").strip()
            
            if choice == "1":
                switcher.list_models()
                
            elif choice == "2":
                switcher.test_all_models()
                
            elif choice == "3":
                model_name = input("请输入要测试的模型名称: ").strip()
                if model_name in switcher.available_models:
                    test_msg = input("请输入测试消息 (回车使用默认): ").strip()
                    if not test_msg:
                        test_msg = "你好，请简单介绍一下自己"
                    switcher.test_model(model_name, test_msg)
                else:
                    print("模型不存在，请从列表中选择")
                    
            elif choice == "4":
                switcher.get_available_models_from_api()
                
            elif choice == "5":
                print("再见！")
                break
                
            else:
                print("无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"发生错误: {e}")


if __name__ == "__main__":
    main()








