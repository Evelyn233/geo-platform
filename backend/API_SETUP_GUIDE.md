# GEO平台API配置指南

## 豆包API配置

### 1. 获取API密钥

1. **登录字节跳动控制台**
   - 访问：https://console.volcengine.com/
   - 使用您的账号登录

2. **进入豆包大模型服务**
   - 在控制台中找到"豆包大模型服务"
   - 点击进入服务页面

3. **创建API密钥**
   - 点击"API密钥管理"
   - 点击"创建API密钥"
   - 复制生成的API密钥（格式：`sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`）

### 2. 配置API密钥

#### 方法一：环境变量（推荐）
```bash
# Windows PowerShell
$env:ARK_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Windows CMD
set ARK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Linux/Mac
export ARK_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

#### 方法二：配置文件
1. 复制 `api_keys_template.txt` 为 `api_keys.txt`
2. 将您的API密钥填入：
```
ARK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. 资源包管理

#### 当前状态
- 总余量：48156 token
- 建议：立即续购资源包

#### 续购步骤
1. 在豆包控制台点击"资源包管理"
2. 选择适合的资源包
3. 建议购买：Doubao1.5-pro-32k 资源包

#### 优化建议
- 使用基础模式生成文章（不调用大模型）
- 减少文章生成数量
- 优化提示词长度

### 4. 使用说明

#### 基础模式（不消耗豆包token）
- 取消勾选"增强模式"
- 使用预设模板生成文章
- 适合快速生成大量文章

#### 增强模式（消耗豆包token）
- 勾选"增强模式"
- 联网搜索相关内容
- 使用大模型优化内容
- 适合高质量文章生成

### 5. 故障排除

#### API密钥错误
```
错误：The API key format is incorrect
解决：检查API密钥格式是否正确，确保以"sk-"开头
```

#### 资源不足
```
错误：资源包余量不足
解决：续购资源包或使用基础模式
```

#### 网络连接问题
```
错误：搜索API返回错误: 202
解决：检查网络连接，或使用基础模式
```

### 6. 联系支持

如遇到问题，请联系：
- 字节跳动技术支持
- 或使用基础模式继续使用系统


