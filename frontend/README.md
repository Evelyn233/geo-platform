# RAG-Anything 前端界面

这是一个基于Flask的Web前端界面，让用户可以通过浏览器与RAG-Anything系统交互。

## 功能特性

- 🌐 **Web界面** - 友好的浏览器界面
- 💬 **实时问答** - 支持多种查询模式
- 💡 **建议问题** - 提供常用问题模板
- 📱 **响应式设计** - 支持手机和桌面设备
- 🔄 **实时状态** - 显示RAG系统连接状态

## 使用方法

### 1. 准备知识库

首先需要处理文档并创建知识库：

```bash
cd RAG-Anything
python examples/raganything_example.py "test_output/geo.pdf" --api-key your_api_key
```

### 2. 启动前端服务

```bash
# 方法1: 使用启动脚本（推荐）
python start_frontend.py

# 方法2: 直接启动
cd frontend
python app.py
```

### 3. 访问界面

打开浏览器访问: http://localhost:5000

## 界面说明

### 状态栏
- 显示RAG系统连接状态
- 提供初始化按钮

### 问答区域
- **查询模式选择**:
  - `naive` - 简单模式，直接基于文档内容
  - `hybrid` - 混合模式，结合实体关系图
  - `local` - 局部模式，基于相关实体
  - `global` - 全局模式，基于整个知识图谱

- **输入框** - 输入问题
- **发送按钮** - 提交问题
- **聊天记录** - 显示问答历史

### 建议问题
- 点击建议问题可以快速提问
- 问题会自动填入输入框并发送

## API接口

### GET /api/status
获取系统状态

### POST /api/initialize
初始化RAG系统

### POST /api/ask
发送问题
```json
{
  "question": "你的问题",
  "mode": "naive"
}
```

### GET /api/suggestions
获取建议问题列表

## 技术栈

- **后端**: Flask + Python
- **前端**: HTML + CSS + JavaScript
- **RAG**: RAG-Anything + LightRAG
- **LLM**: 豆包API

## 注意事项

1. 确保已安装Flask依赖
2. 确保RAG存储目录存在
3. 确保API密钥配置正确
4. 首次使用需要初始化RAG系统

## 故障排除

### 依赖问题
```bash
pip install Flask==2.3.3 requests==2.31.0
```

### RAG系统未初始化
- 检查rag_storage目录是否存在
- 点击"初始化RAG系统"按钮
- 查看控制台错误信息

### API调用失败
- 检查网络连接
- 验证API密钥是否正确
- 查看浏览器控制台错误信息








