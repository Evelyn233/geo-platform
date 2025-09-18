#!/usr/bin/env python3
"""
RAG-Anything 前端启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """检查依赖是否安装"""
    try:
        import flask
        import requests
        print("✅ 依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("正在安装依赖...")
        
        # 安装依赖
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "Flask==2.3.3", "requests==2.31.0"
            ])
            print("✅ 依赖安装完成")
            return True
        except subprocess.CalledProcessError:
            print("❌ 依赖安装失败")
            return False

def check_rag_storage():
    """检查RAG存储目录"""
    rag_storage = Path("./rag_storage")
    if rag_storage.exists():
        print("✅ 找到RAG存储目录")
        return True
    else:
        print("❌ 未找到RAG存储目录")
        print("请先运行文档处理脚本创建知识库")
        return False

def main():
    """主函数"""
    print("🚀 启动RAG-Anything前端服务")
    print("=" * 50)
    
    # 检查依赖
    if not check_requirements():
        return
    
    # 检查RAG存储
    if not check_rag_storage():
        print("\n💡 提示:")
        print("请先运行以下命令处理文档:")
        print("python examples/raganything_example.py your_document.pdf --api-key your_key")
        return
    
    # 启动前端服务
    print("\n🌐 启动Web服务...")
    print("访问地址: http://localhost:5000")
    print("按 Ctrl+C 停止服务")
    print("=" * 50)
    
    try:
        # 切换到frontend目录并启动Flask应用
        frontend_dir = Path(__file__).parent / "frontend"
        os.chdir(frontend_dir)
        
        # 添加当前目录到Python路径
        sys.path.insert(0, str(frontend_dir))
        
        # 启动Flask应用
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()
