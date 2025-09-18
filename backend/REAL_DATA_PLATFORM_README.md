# 真实AI大模型数据采集平台

## 功能概述

这是一个完整的真实AI大模型数据采集平台，可以采集各种AI大模型对您网站的真实曝光数据，提供类似图片中仪表板的专业分析功能。

## 核心特性

### 🎯 真实数据采集
- **多平台支持**: 豆包、Deepseek、通义、元宝、KIMI等主流AI平台
- **智能问题生成**: 基于关键词自动生成相关问题
- **API集成**: 直接调用各AI平台的官方API
- **速率限制**: 智能控制API调用频率，避免超限

### 📊 数据分析
- **曝光率统计**: 各AI平台的问题分布和曝光率
- **关键词分析**: 热门关键词频率统计
- **设备分布**: 电脑端vs移动端数据对比
- **时间趋势**: 数据采集时间线分析

### 🔄 任务调度
- **定时采集**: 支持cron表达式定时任务
- **任务队列**: 多任务并发处理
- **错误重试**: 自动重试失败的任务
- **状态监控**: 实时任务状态跟踪

### 📈 可视化界面
- **专业仪表板**: 类似图片中的统计界面
- **实时图表**: 饼图、柱状图等数据可视化
- **交互搜索**: 支持关键词和平台筛选
- **数据导出**: JSON/CSV格式数据导出

## 快速开始

### 1. 安装依赖

```bash
pip install aiohttp aiofiles asyncio
```

### 2. 配置API密钥

编辑 `ai_platform_config.json` 文件，填入您的API密钥：

```json
{
  "platforms": [
    {
      "name": "豆包",
      "api_key": "your_actual_doubao_api_key",
      "enabled": true
    },
    {
      "name": "Deepseek", 
      "api_key": "your_actual_deepseek_api_key",
      "enabled": true
    }
  ]
}
```

### 3. 启动系统

```bash
python geo_app.py
```

访问 `http://localhost:8000` 查看界面。

### 4. 开始采集

1. 点击侧边栏 **"AI曝光率分析"**
2. 在真实数据采集区域输入关键词
3. 选择要采集的AI平台
4. 点击 **"🚀 开始真实采集"**

## 详细使用指南

### 配置AI平台

#### 豆包 (Doubao)
1. 访问 [豆包开放平台](https://www.volcengine.com/product/doubao)
2. 注册账号并创建应用
3. 获取API Key
4. 在配置文件中填入密钥

#### Deepseek
1. 访问 [Deepseek开放平台](https://platform.deepseek.com/)
2. 注册账号并获取API Key
3. 在配置文件中填入密钥

#### 通义千问
1. 访问 [阿里云DashScope](https://dashscope.aliyun.com/)
2. 开通服务并获取API Key
3. 在配置文件中填入密钥

### 数据采集流程

1. **准备关键词**: 输入您要分析的关键词，每行一个
2. **选择平台**: 勾选要采集的AI平台
3. **开始采集**: 系统会自动调用各平台API生成相关问题
4. **查看结果**: 在仪表板中查看采集的数据和分析结果

### 数据分析功能

#### 汇总统计
- 总问题量
- 收录问题数
- 品牌词量
- 覆盖平台数

#### 平台分析
- 各平台问题分布
- 曝光率计算
- 设备类型分析
- 平台状态监控

#### 关键词分析
- 热门关键词排行
- 关键词频率统计
- 问题类型分布

## API接口文档

### 数据采集

#### 采集真实数据
```http
POST /api/real_data/collect
Content-Type: application/json

{
  "keywords": ["静钧抛光", "抛光布轮"],
  "platforms": ["豆包", "Deepseek"]
}
```

#### 检查平台状态
```http
GET /api/real_data/platforms/status
```

#### 分析数据
```http
POST /api/real_data/analyze
Content-Type: application/json

{}
```

#### 导出数据
```http
POST /api/real_data/export
Content-Type: application/json

{
  "format": "json",
  "keywords": ["静钧抛光"],
  "platforms": ["豆包"]
}
```

### 任务调度

#### 创建采集任务
```http
POST /api/real_data/scheduler/create_task
Content-Type: application/json

{
  "keywords": ["静钧抛光"],
  "platforms": ["豆包", "Deepseek"],
  "priority": 1,
  "max_retries": 3
}
```

#### 获取调度器状态
```http
GET /api/real_data/scheduler/status
```

## 高级功能

### 定时任务配置

编辑 `scheduler_config.json` 文件：

```json
{
  "worker_count": 3,
  "max_queue_size": 100,
  "task_timeout": 300,
  "scheduled_tasks": [
    {
      "name": "每日采集",
      "keywords": ["静钧抛光", "抛光布轮"],
      "platforms": ["豆包", "Deepseek"],
      "cron": "0 9 * * *",
      "enabled": true
    }
  ]
}
```

### 自定义采集器

您可以扩展 `AIPlatformCollector` 类来支持更多AI平台：

```python
class CustomPlatformCollector(AIPlatformCollector):
    async def search_questions(self, keyword: str) -> List[SearchResult]:
        # 实现自定义平台的搜索逻辑
        pass
    
    async def get_platform_info(self) -> Dict[str, Any]:
        # 返回平台信息
        pass
```

### 数据清洗和验证

系统自动进行以下数据处理：

1. **问题去重**: 自动去除重复问题
2. **质量过滤**: 过滤低质量或过短的问题
3. **格式标准化**: 统一问题格式
4. **置信度评估**: 为每个结果分配置信度分数

## 监控和报警

### 平台状态监控
- 实时检查各AI平台API状态
- 自动检测API限制和错误
- 提供平台健康度报告

### 任务监控
- 任务执行状态跟踪
- 失败任务自动重试
- 执行时间统计

### 数据质量监控
- 采集数据质量评估
- 异常数据检测
- 数据完整性检查

## 性能优化

### 并发控制
- 多线程并发采集
- 智能速率限制
- 资源使用优化

### 缓存机制
- 结果缓存
- 配置缓存
- 状态缓存

### 错误处理
- 自动重试机制
- 错误日志记录
- 优雅降级

## 故障排除

### 常见问题

1. **API密钥错误**
   - 检查配置文件中的API密钥是否正确
   - 确认API密钥是否有效且有足够权限

2. **网络连接问题**
   - 检查网络连接
   - 确认防火墙设置
   - 检查代理配置

3. **API限制**
   - 调整速率限制设置
   - 增加重试间隔
   - 检查API配额

4. **数据质量问题**
   - 检查关键词设置
   - 调整问题生成模板
   - 验证平台配置

### 日志查看

查看详细日志：

```bash
tail -f data_collection.log
```

### 调试模式

启用调试模式：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 扩展开发

### 添加新平台

1. 创建新的采集器类
2. 实现 `search_questions` 和 `get_platform_info` 方法
3. 在配置文件中添加平台配置
4. 注册到平台管理器

### 自定义分析

1. 扩展 `AIExposureAnalyzer` 类
2. 添加新的分析方法
3. 更新前端界面
4. 添加新的API端点

### 数据存储

当前使用JSON文件存储，可以扩展为：

1. **数据库存储**: MySQL、PostgreSQL等
2. **NoSQL存储**: MongoDB、Redis等
3. **云存储**: AWS S3、阿里云OSS等

## 安全考虑

### API密钥安全
- 不要在代码中硬编码API密钥
- 使用环境变量或配置文件
- 定期轮换API密钥

### 数据隐私
- 遵守各平台的数据使用政策
- 不要采集敏感信息
- 定期清理历史数据

### 访问控制
- 限制API访问权限
- 使用HTTPS传输
- 实施用户认证

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献指南

欢迎提交Issue和Pull Request来改进项目。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交GitHub Issue
- 发送邮件到项目维护者
- 加入项目讨论群

---

**注意**: 使用本平台前请确保遵守各AI平台的服务条款和使用政策。
