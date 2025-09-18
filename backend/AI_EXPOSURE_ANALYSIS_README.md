# AI大模型曝光率分析系统

## 功能概述

这个系统可以帮助您分析各种AI大模型对您网站的曝光率，类似于图片中显示的仪表板。系统提供了完整的数据采集、分析和可视化功能。

## 主要功能

### 1. 数据采集
- **模拟数据生成**: 快速生成测试数据，包含多个AI平台的问题分布
- **百度统计集成**: 从百度统计数据中提取AI相关问题
- **实时数据采集**: 支持定期采集新数据（需要后台任务支持）

### 2. 数据分析
- **汇总统计**: 总问题量、收录问题、品牌词量、覆盖平台数
- **平台分析**: 各AI平台的曝光率、问题数量、设备分布
- **问题搜索**: 支持按关键词、平台筛选问题
- **品牌关键词管理**: 管理和分析品牌相关关键词

### 3. 数据可视化
- **饼图**: 显示各平台问题占比
- **柱状图**: 显示设备分布（电脑端vs移动端）
- **数据表格**: 详细的问题列表和平台统计

## 文件结构

```
backend/
├── ai_exposure_analyzer.py      # 核心分析器
├── ai_data_collector.py         # 数据采集器
├── geo_app.py                   # 主应用（包含API端点）
├── static/index.html            # 前端界面
├── test_ai_exposure.py          # 测试脚本
└── AI_EXPOSURE_ANALYSIS_README.md  # 说明文档
```

## 使用方法

### 1. 启动系统

```bash
cd backend
python geo_app.py
```

访问 `http://localhost:8000` 查看前端界面。

### 2. 查看AI曝光率分析

1. 点击侧边栏的 **"AI曝光率分析"**
2. 系统会显示类似图片中的仪表板界面

### 3. 生成测试数据

1. 点击 **"📊 生成模拟数据"** 按钮
2. 系统会生成30天的模拟数据
3. 数据包括多个AI平台的问题分布

### 4. 从百度统计采集数据

1. 确保已同步百度统计数据
2. 点击 **"🔍 从百度统计采集"** 按钮
3. 系统会从百度推广数据中提取AI相关问题

### 5. 查看采集报告

1. 点击 **"📋 查看采集报告"** 按钮
2. 查看详细的数据采集统计和分析

## API端点

### 数据获取
- `GET /api/ai_exposure/summary` - 获取汇总统计
- `GET /api/ai_exposure/platforms` - 获取平台统计
- `GET /api/ai_exposure/questions` - 获取问题数据
- `GET /api/ai_exposure/brand_keywords` - 获取品牌关键词

### 数据采集
- `POST /api/ai_exposure/collect/mock` - 生成模拟数据
- `POST /api/ai_exposure/collect/baidu` - 从百度统计采集
- `GET /api/ai_exposure/collect/report` - 获取采集报告

### 数据搜索
- `POST /api/ai_exposure/search` - 搜索问题
- `POST /api/ai_exposure/questions` - 添加新问题

### 数据导出
- `GET /api/ai_exposure/export` - 导出数据（JSON/CSV格式）

## 数据结构

### 汇总统计
```json
{
  "total_questions": 20000,
  "included_questions": 8732,
  "brand_keywords": 25,
  "covered_platforms": 5,
  "last_updated": "2025-01-18T10:00:00"
}
```

### 平台统计
```json
{
  "platform": "Deepseek",
  "total_questions": 3609,
  "included_questions": 3609,
  "desktop_questions": 1802,
  "mobile_questions": 1807,
  "exposure_rate": 41.33,
  "brand_keywords": 8
}
```

### 问题数据
```json
{
  "id": 1,
  "training_word": "柚木柜",
  "question": "柚木柜厂家推荐",
  "platform": "元宝",
  "source": "移动端",
  "launch_time": "2025-01-18",
  "category": "产品推荐"
}
```

## 支持的AI平台

- Deepseek
- 豆包 (Doubao)
- 通义 (Tongyi)
- 元宝 (Yuanbao)
- KIMI
- 文心一言
- ChatGPT
- Claude
- Gemini

## 测试

运行测试脚本验证功能：

```bash
python test_ai_exposure.py
```

## 自定义配置

### 修改品牌关键词

在 `ai_data_collector.py` 中修改 `brand_keywords` 列表：

```python
self.brand_keywords = [
    "您的品牌词1",
    "您的品牌词2",
    # ... 添加更多品牌关键词
]
```

### 修改问题模板

在 `ai_data_collector.py` 中修改 `question_templates` 列表：

```python
self.question_templates = [
    "{keyword}厂家推荐",
    "{keyword}价格",
    # ... 添加更多问题模板
]
```

### 添加新的AI平台

在 `ai_exposure_analyzer.py` 中修改 `platforms` 列表：

```python
self.platforms = [
    "Deepseek", "豆包", "通义", "元宝", "KIMI",
    "文心一言", "ChatGPT", "Claude", "Gemini",
    "新平台名称"  # 添加新平台
]
```

## 注意事项

1. **数据存储**: 数据存储在 `rag_storage/ai_exposure_data.json` 文件中
2. **API限制**: 真实数据采集需要各平台的API密钥和权限
3. **性能优化**: 大量数据时建议使用数据库存储
4. **实时采集**: 当前版本需要手动触发，生产环境建议使用后台任务

## 扩展功能

### 集成真实API

要集成真实的AI平台API，需要：

1. 获取各平台的API密钥
2. 在 `ai_data_collector.py` 中实现具体的API调用
3. 处理API限制和错误重试

### 添加更多图表

可以在前端添加更多可视化图表：

1. 时间趋势图
2. 关键词热力图
3. 平台对比图
4. 设备类型分析

### 数据导出

支持更多导出格式：

1. Excel文件
2. PDF报告
3. 邮件推送
4. 定时报告

## 故障排除

### 常见问题

1. **数据不显示**: 检查是否生成了模拟数据
2. **图表不渲染**: 确保浏览器支持Canvas
3. **API错误**: 检查服务器是否正常运行
4. **数据采集失败**: 检查网络连接和API权限

### 日志查看

查看控制台输出获取详细错误信息：

```bash
python geo_app.py
```

## 联系支持

如有问题或建议，请查看项目文档或提交Issue。
