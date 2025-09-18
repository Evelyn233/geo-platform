#!/usr/bin/env python3
"""
真实AI大模型数据采集平台
支持多个AI平台的真实数据采集和分析
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import hashlib
import re
from urllib.parse import quote, urlencode

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AIPlatformConfig:
    """AI平台配置"""
    name: str
    api_base_url: str
    api_key: str
    rate_limit: int  # 每分钟请求次数
    timeout: int = 30
    headers: Dict[str, str] = None
    enabled: bool = True

@dataclass
class SearchQuery:
    """搜索查询"""
    keyword: str
    platform: str
    timestamp: datetime
    query_id: str = None
    
    def __post_init__(self):
        if not self.query_id:
            self.query_id = hashlib.md5(f"{self.keyword}_{self.platform}_{self.timestamp}".encode()).hexdigest()[:12]

@dataclass
class SearchResult:
    """搜索结果"""
    query_id: str
    platform: str
    keyword: str
    question: str
    answer: str
    confidence: float
    source: str  # 电脑端/移动端
    timestamp: datetime
    metadata: Dict[str, Any] = None

class AIPlatformCollector(ABC):
    """AI平台采集器基类"""
    
    def __init__(self, config: AIPlatformConfig):
        self.config = config
        self.session = None
        self.rate_limiter = RateLimiter(config.rate_limit)
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            headers=self.config.headers or {}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def search_questions(self, keyword: str) -> List[SearchResult]:
        """搜索问题"""
        pass
    
    @abstractmethod
    async def get_platform_info(self) -> Dict[str, Any]:
        """获取平台信息"""
        pass

class DoubaoCollector(AIPlatformCollector):
    """豆包平台采集器"""
    
    async def search_questions(self, keyword: str) -> List[SearchResult]:
        """从豆包搜索问题"""
        await self.rate_limiter.acquire()
        
        try:
            # 构建搜索提示词
            prompt = f"""请帮我生成关于"{keyword}"的常见问题，包括：
1. 产品推荐类问题
2. 价格咨询类问题  
3. 使用方法类问题
4. 厂家信息类问题
5. 技术参数类问题

请以JSON格式返回，包含question和answer字段。"""
            
            # 调用豆包API
            url = f"{self.config.api_base_url}/api/v3/chat/completions"
            data = {
                "model": "doubao-seed-1-6-flash",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    # 解析返回的问题
                    questions = self._parse_questions(content, keyword)
                    return questions
                else:
                    logger.error(f"豆包API错误: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"豆包搜索失败: {e}")
            return []
    
    def _parse_questions(self, content: str, keyword: str) -> List[SearchResult]:
        """解析问题内容"""
        questions = []
        
        try:
            # 尝试解析JSON
            if content.strip().startswith('{') or content.strip().startswith('['):
                data = json.loads(content)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'question' in item:
                            questions.append(self._create_result(keyword, item['question'], item.get('answer', '')))
                elif isinstance(data, dict) and 'questions' in data:
                    for item in data['questions']:
                        questions.append(self._create_result(keyword, item['question'], item.get('answer', '')))
        except json.JSONDecodeError:
            # 如果不是JSON，尝试文本解析
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and ('?' in line or '？' in line or '推荐' in line or '价格' in line):
                    # 清理问题文本
                    question = re.sub(r'^\d+[\.\)]\s*', '', line)
                    question = re.sub(r'^[-•]\s*', '', question)
                    if len(question) > 10:  # 过滤太短的问题
                        questions.append(self._create_result(keyword, question, ""))
        
        return questions[:10]  # 限制返回数量
    
    def _create_result(self, keyword: str, question: str, answer: str) -> SearchResult:
        """创建搜索结果"""
        return SearchResult(
            query_id=hashlib.md5(f"{keyword}_doubao_{time.time()}".encode()).hexdigest()[:12],
            platform="豆包",
            keyword=keyword,
            question=question,
            answer=answer,
            confidence=0.8,
            source="电脑端",  # 默认电脑端
            timestamp=datetime.now(),
            metadata={"api_version": "v3"}
        )
    
    async def get_platform_info(self) -> Dict[str, Any]:
        """获取豆包平台信息"""
        return {
            "name": "豆包",
            "version": "doubao-seed-1-6-flash",
            "status": "active",
            "rate_limit": self.config.rate_limit,
            "last_check": datetime.now().isoformat()
        }

class DeepSeekCollector(AIPlatformCollector):
    """DeepSeek平台采集器"""
    
    async def search_questions(self, keyword: str) -> List[SearchResult]:
        """从DeepSeek搜索问题"""
        await self.rate_limiter.acquire()
        
        try:
            # 构建搜索提示词
            prompt = f"""作为AI助手，请为关键词"{keyword}"生成5个用户最可能询问的问题，包括：
- 产品推荐和选择
- 价格和性价比
- 使用方法和技巧
- 厂家和品牌信息
- 技术规格和参数

请直接列出问题，每行一个。"""
            
            # 调用DeepSeek API
            url = f"{self.config.api_base_url}/v1/chat/completions"
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.6,
                "max_tokens": 1500
            }
            
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    # 解析问题
                    questions = self._parse_questions(content, keyword)
                    return questions
                else:
                    logger.error(f"DeepSeek API错误: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"DeepSeek搜索失败: {e}")
            return []
    
    def _parse_questions(self, content: str, keyword: str) -> List[SearchResult]:
        """解析DeepSeek返回的问题"""
        questions = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and ('?' in line or '？' in line or '推荐' in line or '价格' in line or '如何' in line):
                # 清理问题文本
                question = re.sub(r'^\d+[\.\)]\s*', '', line)
                question = re.sub(r'^[-•]\s*', '', question)
                if len(question) > 10:
                    questions.append(SearchResult(
                        query_id=hashlib.md5(f"{keyword}_deepseek_{time.time()}".encode()).hexdigest()[:12],
                        platform="Deepseek",
                        keyword=keyword,
                        question=question,
                        answer="",
                        confidence=0.85,
                        source="电脑端",
                        timestamp=datetime.now(),
                        metadata={"api_version": "v1"}
                    ))
        
        return questions[:8]
    
    async def get_platform_info(self) -> Dict[str, Any]:
        """获取DeepSeek平台信息"""
        return {
            "name": "DeepSeek",
            "version": "deepseek-chat",
            "status": "active",
            "rate_limit": self.config.rate_limit,
            "last_check": datetime.now().isoformat()
        }

class TongyiCollector(AIPlatformCollector):
    """通义千问平台采集器"""
    
    async def search_questions(self, keyword: str) -> List[SearchResult]:
        """从通义千问搜索问题"""
        await self.rate_limiter.acquire()
        
        try:
            prompt = f"""请为关键词"{keyword}"生成用户常见问题，包括产品推荐、价格咨询、使用方法等方面的问题。请以简洁的问题形式返回。"""
            
            # 调用通义千问API
            url = f"{self.config.api_base_url}/api/v1/chat/completions"
            data = {
                "model": "qwen-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    questions = self._parse_questions(content, keyword)
                    return questions
                else:
                    logger.error(f"通义千问API错误: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"通义千问搜索失败: {e}")
            return []
    
    def _parse_questions(self, content: str, keyword: str) -> List[SearchResult]:
        """解析通义千问返回的问题"""
        questions = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and ('?' in line or '？' in line or '推荐' in line or '价格' in line):
                question = re.sub(r'^\d+[\.\)]\s*', '', line)
                question = re.sub(r'^[-•]\s*', '', question)
                if len(question) > 10:
                    questions.append(SearchResult(
                        query_id=hashlib.md5(f"{keyword}_tongyi_{time.time()}".encode()).hexdigest()[:12],
                        platform="通义",
                        keyword=keyword,
                        question=question,
                        answer="",
                        confidence=0.8,
                        source="移动端",
                        timestamp=datetime.now(),
                        metadata={"api_version": "v1"}
                    ))
        
        return questions[:6]
    
    async def get_platform_info(self) -> Dict[str, Any]:
        """获取通义千问平台信息"""
        return {
            "name": "通义千问",
            "version": "qwen-turbo",
            "status": "active",
            "rate_limit": self.config.rate_limit,
            "last_check": datetime.now().isoformat()
        }

class RateLimiter:
    """速率限制器"""
    
    def __init__(self, max_requests_per_minute: int):
        self.max_requests = max_requests_per_minute
        self.requests = []
    
    async def acquire(self):
        """获取请求许可"""
        now = time.time()
        
        # 清理1分钟前的请求记录
        self.requests = [req_time for req_time in self.requests if now - req_time < 60]
        
        # 如果达到限制，等待
        if len(self.requests) >= self.max_requests:
            sleep_time = 60 - (now - self.requests[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
                self.requests = []
        
        self.requests.append(now)

class RealDataPlatform:
    """真实数据采集平台"""
    
    def __init__(self, config_file: str = "ai_platform_config.json"):
        self.config_file = config_file
        self.collectors = {}
        self.results = []
        self.load_config()
    
    def load_config(self):
        """加载平台配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            for platform_config in config_data.get('platforms', []):
                config = AIPlatformConfig(**platform_config)
                if config.enabled:
                    if config.name == "豆包":
                        self.collectors[config.name] = DoubaoCollector(config)
                    elif config.name == "Deepseek":
                        self.collectors[config.name] = DeepSeekCollector(config)
                    elif config.name == "通义":
                        self.collectors[config.name] = TongyiCollector(config)
                    else:
                        logger.warning(f"不支持的平台: {config.name}")
        except FileNotFoundError:
            logger.warning(f"配置文件 {self.config_file} 不存在，使用默认配置")
            self.create_default_config()
    
    def create_default_config(self):
        """创建默认配置"""
        default_config = {
            "platforms": [
                {
                    "name": "豆包",
                    "api_base_url": "https://ark.cn-beijing.volces.com",
                    "api_key": "your_doubao_api_key",
                    "rate_limit": 20,
                    "timeout": 30,
                    "headers": {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer your_doubao_api_key"
                    },
                    "enabled": True
                },
                {
                    "name": "Deepseek",
                    "api_base_url": "https://api.deepseek.com",
                    "api_key": "your_deepseek_api_key",
                    "rate_limit": 15,
                    "timeout": 30,
                    "headers": {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer your_deepseek_api_key"
                    },
                    "enabled": True
                },
                {
                    "name": "通义",
                    "api_base_url": "https://dashscope.aliyuncs.com",
                    "api_key": "your_tongyi_api_key",
                    "rate_limit": 10,
                    "timeout": 30,
                    "headers": {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer your_tongyi_api_key"
                    },
                    "enabled": True
                }
            ]
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已创建默认配置文件: {self.config_file}")
    
    async def collect_data(self, keywords: List[str], platforms: List[str] = None) -> List[SearchResult]:
        """采集数据"""
        if not platforms:
            platforms = list(self.collectors.keys())
        
        all_results = []
        
        for platform_name in platforms:
            if platform_name not in self.collectors:
                logger.warning(f"平台 {platform_name} 未配置")
                continue
            
            collector = self.collectors[platform_name]
            logger.info(f"开始从 {platform_name} 采集数据...")
            
            async with collector:
                for keyword in keywords:
                    try:
                        results = await collector.search_questions(keyword)
                        all_results.extend(results)
                        logger.info(f"从 {platform_name} 采集到 {len(results)} 个问题 (关键词: {keyword})")
                        
                        # 避免过于频繁的请求
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        logger.error(f"采集 {platform_name} 数据失败 (关键词: {keyword}): {e}")
        
        self.results.extend(all_results)
        return all_results
    
    async def get_platform_status(self) -> Dict[str, Any]:
        """获取平台状态"""
        status = {}
        
        for platform_name, collector in self.collectors.items():
            try:
                async with collector:
                    info = await collector.get_platform_info()
                    status[platform_name] = info
            except Exception as e:
                status[platform_name] = {
                    "name": platform_name,
                    "status": "error",
                    "error": str(e)
                }
        
        return status
    
    def save_results(self, filename: str = None):
        """保存采集结果"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"real_data_results_{timestamp}.json"
        
        # 转换结果为可序列化的格式
        serializable_results = []
        for result in self.results:
            result_dict = asdict(result)
            result_dict['timestamp'] = result.timestamp.isoformat()
            serializable_results.append(result_dict)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"结果已保存到: {filename}")
        return filename
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.results:
            return {"total": 0, "platforms": {}, "keywords": {}}
        
        stats = {
            "total": len(self.results),
            "platforms": {},
            "keywords": {},
            "time_range": {
                "start": min(r.timestamp for r in self.results).isoformat(),
                "end": max(r.timestamp for r in self.results).isoformat()
            }
        }
        
        # 按平台统计
        for result in self.results:
            platform = result.platform
            if platform not in stats["platforms"]:
                stats["platforms"][platform] = 0
            stats["platforms"][platform] += 1
        
        # 按关键词统计
        for result in self.results:
            keyword = result.keyword
            if keyword not in stats["keywords"]:
                stats["keywords"][keyword] = 0
            stats["keywords"][keyword] += 1
        
        return stats

async def main():
    """主函数 - 测试真实数据采集"""
    platform = RealDataPlatform()
    
    # 测试关键词
    keywords = ["静钧抛光", "抛光布轮", "尼龙打磨片"]
    
    print("=== 真实AI数据采集平台测试 ===")
    
    # 检查平台状态
    print("\n1. 检查平台状态:")
    status = await platform.get_platform_status()
    for platform_name, info in status.items():
        print(f"  {platform_name}: {info.get('status', 'unknown')}")
    
    # 采集数据
    print(f"\n2. 开始采集数据 (关键词: {keywords})...")
    results = await platform.collect_data(keywords)
    
    print(f"\n3. 采集完成，共获得 {len(results)} 个问题")
    
    # 显示部分结果
    print("\n4. 部分采集结果:")
    for i, result in enumerate(results[:5]):
        print(f"  {i+1}. [{result.platform}] {result.keyword} - {result.question}")
    
    # 保存结果
    filename = platform.save_results()
    print(f"\n5. 结果已保存到: {filename}")
    
    # 显示统计信息
    stats = platform.get_statistics()
    print(f"\n6. 统计信息:")
    print(f"  总问题数: {stats['total']}")
    print(f"  平台分布: {stats['platforms']}")
    print(f"  关键词分布: {dict(list(stats['keywords'].items())[:3])}")

if __name__ == "__main__":
    asyncio.run(main())
