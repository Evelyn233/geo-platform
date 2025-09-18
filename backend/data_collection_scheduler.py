#!/usr/bin/env python3
"""
数据采集调度系统
支持定时采集、任务队列、错误重试等功能
"""

import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import aiofiles
from concurrent.futures import ThreadPoolExecutor
import signal
import sys

from real_data_platform import RealDataPlatform, SearchResult

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class CollectionTask:
    """采集任务"""
    task_id: str
    keywords: List[str]
    platforms: List[str]
    priority: int = 1  # 优先级，数字越小优先级越高
    max_retries: int = 3
    retry_delay: int = 60  # 重试延迟（秒）
    created_at: datetime = None
    started_at: datetime = None
    completed_at: datetime = None
    status: TaskStatus = TaskStatus.PENDING
    error_message: str = None
    results: List[SearchResult] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.results is None:
            self.results = []

class DataCollectionScheduler:
    """数据采集调度器"""
    
    def __init__(self, config_file: str = "scheduler_config.json"):
        self.config_file = config_file
        self.platform = RealDataPlatform()
        self.tasks = {}  # task_id -> CollectionTask
        self.task_queue = []  # 待执行任务队列
        self.running_tasks = {}  # 正在运行的任务
        self.completed_tasks = []  # 已完成的任务
        self.failed_tasks = []  # 失败的任务
        
        self.is_running = False
        self.worker_count = 3  # 并发工作线程数
        self.workers = []
        
        self.load_config()
        self.setup_signal_handlers()
    
    def load_config(self):
        """加载调度器配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.worker_count = config.get('worker_count', 3)
            self.max_queue_size = config.get('max_queue_size', 100)
            self.task_timeout = config.get('task_timeout', 300)  # 5分钟超时
            
            # 加载定时任务配置
            self.scheduled_tasks = config.get('scheduled_tasks', [])
            
        except FileNotFoundError:
            logger.warning(f"配置文件 {self.config_file} 不存在，使用默认配置")
            self.create_default_config()
    
    def create_default_config(self):
        """创建默认配置"""
        default_config = {
            "worker_count": 3,
            "max_queue_size": 100,
            "task_timeout": 300,
            "scheduled_tasks": [
                {
                    "name": "每日采集",
                    "keywords": ["静钧抛光", "抛光布轮", "尼龙打磨片"],
                    "platforms": ["豆包", "Deepseek", "通义"],
                    "cron": "0 9 * * *",  # 每天上午9点
                    "enabled": True
                },
                {
                    "name": "每周深度采集",
                    "keywords": ["静钧抛光", "抛光布轮", "尼龙打磨片", "静钧海绵轮", "静钧麻轮"],
                    "platforms": ["豆包", "Deepseek", "通义"],
                    "cron": "0 10 * * 1",  # 每周一上午10点
                    "enabled": True
                }
            ]
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已创建默认配置文件: {self.config_file}")
    
    def setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            logger.info(f"收到信号 {signum}，正在停止调度器...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def create_task(self, keywords: List[str], platforms: List[str] = None, 
                   priority: int = 1, max_retries: int = 3) -> str:
        """创建采集任务"""
        task_id = f"task_{int(time.time())}_{len(self.tasks)}"
        
        task = CollectionTask(
            task_id=task_id,
            keywords=keywords,
            platforms=platforms or list(self.platform.collectors.keys()),
            priority=priority,
            max_retries=max_retries
        )
        
        self.tasks[task_id] = task
        self.task_queue.append(task_id)
        
        # 按优先级排序
        self.task_queue.sort(key=lambda tid: self.tasks[tid].priority)
        
        logger.info(f"创建任务 {task_id}: {len(keywords)} 个关键词, {len(platforms or [])} 个平台")
        return task_id
    
    async def start(self):
        """启动调度器"""
        if self.is_running:
            logger.warning("调度器已在运行")
            return
        
        self.is_running = True
        logger.info("启动数据采集调度器...")
        
        # 启动工作线程
        for i in range(self.worker_count):
            worker = asyncio.create_task(self.worker(f"worker-{i}"))
            self.workers.append(worker)
        
        # 启动定时任务检查
        scheduler_task = asyncio.create_task(self.scheduler_loop())
        
        try:
            # 等待所有任务完成
            await asyncio.gather(*self.workers, scheduler_task)
        except asyncio.CancelledError:
            logger.info("调度器被取消")
        finally:
            self.is_running = False
    
    async def stop(self):
        """停止调度器"""
        logger.info("正在停止调度器...")
        self.is_running = False
        
        # 取消所有工作线程
        for worker in self.workers:
            worker.cancel()
        
        # 等待工作线程结束
        await asyncio.gather(*self.workers, return_exceptions=True)
        
        logger.info("调度器已停止")
    
    async def worker(self, worker_name: str):
        """工作线程"""
        logger.info(f"工作线程 {worker_name} 启动")
        
        while self.is_running:
            try:
                # 获取下一个任务
                task_id = await self.get_next_task()
                if not task_id:
                    await asyncio.sleep(1)
                    continue
                
                task = self.tasks[task_id]
                logger.info(f"{worker_name} 开始执行任务 {task_id}")
                
                # 执行任务
                await self.execute_task(task)
                
            except asyncio.CancelledError:
                logger.info(f"工作线程 {worker_name} 被取消")
                break
            except Exception as e:
                logger.error(f"工作线程 {worker_name} 出错: {e}")
                await asyncio.sleep(5)
        
        logger.info(f"工作线程 {worker_name} 结束")
    
    async def get_next_task(self) -> Optional[str]:
        """获取下一个任务"""
        if not self.task_queue:
            return None
        
        # 检查队列大小限制
        if len(self.task_queue) > self.max_queue_size:
            logger.warning(f"任务队列已满 ({len(self.task_queue)}/{self.max_queue_size})")
            return None
        
        # 获取优先级最高的任务
        task_id = self.task_queue.pop(0)
        task = self.tasks[task_id]
        
        # 检查任务是否应该执行
        if task.status != TaskStatus.PENDING:
            return None
        
        return task_id
    
    async def execute_task(self, task: CollectionTask):
        """执行采集任务"""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        self.running_tasks[task.task_id] = task
        
        try:
            logger.info(f"执行任务 {task.task_id}: {task.keywords}")
            
            # 执行数据采集
            results = await self.platform.collect_data(
                keywords=task.keywords,
                platforms=task.platforms
            )
            
            task.results = results
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            logger.info(f"任务 {task.task_id} 完成，采集到 {len(results)} 个结果")
            
            # 保存结果
            await self.save_task_results(task)
            
            # 移动到已完成列表
            self.completed_tasks.append(task)
            
        except Exception as e:
            logger.error(f"任务 {task.task_id} 执行失败: {e}")
            task.error_message = str(e)
            
            # 检查是否需要重试
            if task.max_retries > 0:
                task.max_retries -= 1
                task.status = TaskStatus.PENDING
                task.started_at = None
                
                # 延迟后重新加入队列
                asyncio.create_task(self.retry_task(task))
                logger.info(f"任务 {task.task_id} 将在 {task.retry_delay} 秒后重试")
            else:
                task.status = TaskStatus.FAILED
                self.failed_tasks.append(task)
                logger.error(f"任务 {task.task_id} 重试次数用尽，标记为失败")
        
        finally:
            # 从运行中任务列表移除
            self.running_tasks.pop(task.task_id, None)
    
    async def retry_task(self, task: CollectionTask):
        """重试任务"""
        await asyncio.sleep(task.retry_delay)
        self.task_queue.append(task.task_id)
        logger.info(f"任务 {task.task_id} 重新加入队列")
    
    async def save_task_results(self, task: CollectionTask):
        """保存任务结果"""
        try:
            # 保存到文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"task_results_{task.task_id}_{timestamp}.json"
            
            # 转换结果为可序列化格式
            results_data = []
            for result in task.results:
                result_dict = asdict(result)
                result_dict['timestamp'] = result.timestamp.isoformat()
                results_data.append(result_dict)
            
            task_data = {
                "task_id": task.task_id,
                "keywords": task.keywords,
                "platforms": task.platforms,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "results_count": len(task.results),
                "results": results_data
            }
            
            async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(task_data, ensure_ascii=False, indent=2))
            
            logger.info(f"任务结果已保存到: {filename}")
            
        except Exception as e:
            logger.error(f"保存任务结果失败: {e}")
    
    async def scheduler_loop(self):
        """定时任务调度循环"""
        logger.info("定时任务调度器启动")
        
        while self.is_running:
            try:
                # 检查定时任务
                await self.check_scheduled_tasks()
                
                # 每分钟检查一次
                await asyncio.sleep(60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"定时任务调度出错: {e}")
                await asyncio.sleep(60)
    
    async def check_scheduled_tasks(self):
        """检查定时任务"""
        now = datetime.now()
        
        for scheduled_task in self.scheduled_tasks:
            if not scheduled_task.get('enabled', True):
                continue
            
            # 简单的cron解析（这里简化处理）
            cron = scheduled_task.get('cron', '')
            if self.should_run_task(cron, now):
                logger.info(f"触发定时任务: {scheduled_task['name']}")
                
                # 创建采集任务
                task_id = self.create_task(
                    keywords=scheduled_task['keywords'],
                    platforms=scheduled_task['platforms'],
                    priority=1
                )
                
                logger.info(f"定时任务已创建: {task_id}")
    
    def should_run_task(self, cron: str, now: datetime) -> bool:
        """检查任务是否应该运行（简化的cron解析）"""
        if not cron:
            return False
        
        parts = cron.split()
        if len(parts) != 5:
            return False
        
        minute, hour, day, month, weekday = parts
        
        # 检查分钟
        if minute != '*' and int(minute) != now.minute:
            return False
        
        # 检查小时
        if hour != '*' and int(hour) != now.hour:
            return False
        
        # 检查星期
        if weekday != '*' and int(weekday) != now.weekday():
            return False
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        return {
            "is_running": self.is_running,
            "worker_count": self.worker_count,
            "queue_size": len(self.task_queue),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "total_tasks": len(self.tasks),
            "platforms": list(self.platform.collectors.keys())
        }
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        return {
            "task_id": task.task_id,
            "status": task.status.value,
            "keywords": task.keywords,
            "platforms": task.platforms,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "results_count": len(task.results) if task.results else 0,
            "error_message": task.error_message
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_results = sum(len(task.results) if task.results else 0 for task in self.completed_tasks)
        
        platform_stats = {}
        for task in self.completed_tasks:
            if task.results:
                for result in task.results:
                    platform = result.platform
                    if platform not in platform_stats:
                        platform_stats[platform] = 0
                    platform_stats[platform] += 1
        
        return {
            "total_tasks": len(self.tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "total_results": total_results,
            "platform_distribution": platform_stats,
            "average_results_per_task": total_results / len(self.completed_tasks) if self.completed_tasks else 0
        }

async def main():
    """主函数 - 测试调度器"""
    scheduler = DataCollectionScheduler()
    
    print("=== 数据采集调度器测试 ===")
    
    # 创建测试任务
    task_id = scheduler.create_task(
        keywords=["静钧抛光", "抛光布轮"],
        platforms=["豆包", "Deepseek"],
        priority=1
    )
    
    print(f"创建测试任务: {task_id}")
    
    # 启动调度器
    try:
        await scheduler.start()
    except KeyboardInterrupt:
        print("\n收到中断信号，正在停止...")
        await scheduler.stop()

if __name__ == "__main__":
    asyncio.run(main())
