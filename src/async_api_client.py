#!/usr/bin/env python3
"""
每日单词墨水屏显示系统 - 异步API客户端
Daily Word E-Paper Display System - Async API Client

实现异步并发API调用，提升响应速度
"""

import asyncio
import aiohttp
import logging
import json
import time
from typing import Dict, Optional, Any, List
from pathlib import Path
import urllib3
from datetime import datetime

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class AsyncAPIClient:
    """异步API客户端 - 支持并发请求和连接池"""
    
    def __init__(self, timeout: int = 15, max_connections: int = 10):
        self.timeout = timeout
        self.max_connections = max_connections
        self._session: Optional[aiohttp.ClientSession] = None
        self._connector: Optional[aiohttp.TCPConnector] = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self._create_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self._close_session()
    
    async def _create_session(self):
        """创建HTTP会话"""
        if self._session is None:
            # 配置连接池
            self._connector = aiohttp.TCPConnector(
                limit=self.max_connections,
                limit_per_host=5,
                ttl_dns_cache=300,
                use_dns_cache=True,
                keepalive_timeout=30
            )
            
            # 配置超时
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            # 创建会话
            self._session = aiohttp.ClientSession(
                connector=self._connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; Daily-Word-EPaper/1.0)',
                    'Accept': 'application/json',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive'
                }
            )
    
    async def _close_session(self):
        """关闭HTTP会话"""
        if self._session:
            await self._session.close()
            self._session = None
        if self._connector:
            await self._connector.close()
            self._connector = None
    
    async def _make_request(self, url: str, retry_count: int = 3) -> Optional[Dict]:
        """发起异步HTTP请求"""
        if not self._session:
            await self._create_session()
        
        for attempt in range(retry_count):
            try:
                logger.debug(f"异步请求URL: {url} (尝试 {attempt + 1}/{retry_count})")
                
                async with self._session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    logger.debug(f"异步请求成功: {url}")
                    return data
            
            except aiohttp.ClientSSLError as e:
                logger.warning(f"SSL验证失败: {e}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(2 ** attempt)
                continue
            
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.warning(f"异步请求失败 (尝试 {attempt + 1}/{retry_count}): {e}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(2 ** attempt)  # 指数退避
                continue
            
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}")
                break
            
            except Exception as e:
                logger.error(f"未知错误 (尝试 {attempt + 1}/{retry_count}): {e}")
                break
        
        logger.error(f"所有异步请求尝试失败: {url}")
        return None
    
    async def fetch_word_data(self, word: str) -> Optional[Dict]:
        """获取单词数据"""
        # 使用Free Dictionary API
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        return await self._make_request(url)
    
    async def fetch_quote_data(self) -> Optional[Dict]:
        """获取句子数据"""
        # 使用ZenQuotes API
        url = "https://zenquotes.io/api/random"
        data = await self._make_request(url)
        
        if data and isinstance(data, list) and len(data) > 0:
            quote = data[0]
            return {
                'text': quote.get('q', ''),
                'author': quote.get('a', ''),
                'category': 'inspiration',
                'source': 'ZenQuotes API'
            }
        
        return None
    
    async def fetch_daily_content(self, word: str = None) -> Dict[str, Any]:
        """并发获取每日内容（单词+句子）"""
        start_time = time.time()
        
        # 如果没有指定单词，使用默认单词
        if not word:
            word = "serendipity"  # 默认单词
        
        try:
            # 并发执行API调用
            word_task = self.fetch_word_data(word)
            quote_task = self.fetch_quote_data()
            
            word_data, quote_data = await asyncio.gather(
                word_task, 
                quote_task, 
                return_exceptions=True
            )
            
            # 处理结果
            content = {
                'word': self._process_word_data(word_data, word),
                'quote': self._process_quote_data(quote_data),
                'generated_at': datetime.now().isoformat(),
                'fetch_time': time.time() - start_time
            }
            
            logger.info(f"异步内容获取完成，耗时: {content['fetch_time']:.3f}s")
            return content
            
        except Exception as e:
            logger.error(f"异步获取内容失败: {e}")
            return {
                'word': None,
                'quote': None,
                'error': str(e),
                'generated_at': datetime.now().isoformat(),
                'fetch_time': time.time() - start_time
            }
    
    def _process_word_data(self, data: Any, fallback_word: str) -> Optional[Dict]:
        """处理单词API响应数据"""
        if not data or isinstance(data, Exception):
            return None
        
        try:
            if isinstance(data, list) and len(data) > 0:
                entry = data[0]
                
                # 提取音标
                phonetic = ""
                if 'phonetics' in entry:
                    for p in entry['phonetics']:
                        if p.get('text'):
                            phonetic = p['text']
                            break
                
                # 提取定义
                definition = ""
                if 'meanings' in entry and len(entry['meanings']) > 0:
                    meaning = entry['meanings'][0]
                    if 'definitions' in meaning and len(meaning['definitions']) > 0:
                        definition = meaning['definitions'][0].get('definition', '')
                
                # 提取例句
                example = ""
                if 'meanings' in entry and len(entry['meanings']) > 0:
                    meaning = entry['meanings'][0]
                    if 'definitions' in meaning and len(meaning['definitions']) > 0:
                        def_item = meaning['definitions'][0]
                        if 'example' in def_item:
                            example = def_item['example']
                
                return {
                    'word': entry.get('word', fallback_word),
                    'phonetic': phonetic,
                    'definition': definition,
                    'example': example,
                    'source': 'Free Dictionary API'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"处理单词数据失败: {e}")
            return None
    
    def _process_quote_data(self, data: Any) -> Optional[Dict]:
        """处理句子API响应数据"""
        if not data or isinstance(data, Exception):
            return None
        
        return data  # 已经在fetch_quote_data中处理了


class AsyncDailyWordAPIClient:
    """异步每日单词API客户端 - 与现有代码兼容的接口"""
    
    def __init__(self, cache_manager=None):
        from daily_word_config import DATA_DIR
        self.cache_dir = Path(DATA_DIR) / "cache"
        self.cache_manager = cache_manager
        self._async_client: Optional[AsyncAPIClient] = None
    
    async def __aenter__(self):
        self._async_client = AsyncAPIClient()
        await self._async_client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._async_client:
            await self._async_client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def get_daily_content(self, force_new: bool = False) -> Dict[str, Any]:
        """获取每日内容 - 异步版本"""
        today = datetime.now().strftime('%Y-%m-%d')
        cache_key = f"daily_content:{today}"
        
        # 尝试从缓存获取
        if not force_new and self.cache_manager:
            cached_content = self.cache_manager.get(cache_key, max_age=3600)
            if cached_content:
                logger.info("使用缓存的每日内容")
                return cached_content
        
        try:
            # 使用异步客户端获取内容
            if not self._async_client:
                async with AsyncAPIClient() as client:
                    content = await client.fetch_daily_content()
            else:
                content = await self._async_client.fetch_daily_content()
            
            # 缓存结果
            if self.cache_manager and content.get('word') and content.get('quote'):
                self.cache_manager.set(cache_key, content, ttl=3600)
            
            return content
            
        except Exception as e:
            logger.error(f"异步获取每日内容失败: {e}")
            # 回退到同步获取或返回错误
            return {
                'word': None,
                'quote': None,
                'error': str(e),
                'generated_at': datetime.now().isoformat()
            }


# 便捷函数 - 与现有代码兼容
async def async_get_daily_content(force_new: bool = False) -> Dict[str, Any]:
    """异步获取每日内容的便捷函数"""
    from cache_manager import get_cache_manager
    
    cache_manager = get_cache_manager()
    
    async with AsyncDailyWordAPIClient(cache_manager) as client:
        return await client.get_daily_content(force_new)


# 性能测试函数
async def benchmark_async_vs_sync():
    """对比异步和同步性能"""
    import time
    
    logger.info("开始性能对比测试...")
    
    # 测试异步版本
    start_time = time.time()
    async_content = await async_get_daily_content(force_new=True)
    async_time = time.time() - start_time
    
    # 测试同步版本（模拟）
    from daily_word_api_client import DailyWordAPIClient
    
    start_time = time.time()
    sync_client = DailyWordAPIClient()
    sync_content = sync_client.get_daily_content(force_new=True)
    sync_time = time.time() - start_time
    
    logger.info(f"异步版本耗时: {async_time:.3f}s")
    logger.info(f"同步版本耗时: {sync_time:.3f}s")
    logger.info(f"性能提升: {(sync_time - async_time) / sync_time * 100:.1f}%")
    
    return {
        'async_time': async_time,
        'sync_time': sync_time,
        'improvement': (sync_time - async_time) / sync_time * 100
    }


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 运行异步测试
    async def main():
        # 测试异步获取内容
        content = await async_get_daily_content(force_new=True)
        
        print("\n" + "="*50)
        print("异步获取的每日内容")
        print("="*50)
        
        if content['word']:
            word = content['word']
            print(f"📚 单词: {word['word']}")
            if word.get('phonetic'):
                print(f"🔊 音标: {word['phonetic']}")
            print(f"📖 定义: {word['definition'][:100]}...")
            print(f"⏱️  获取耗时: {content.get('fetch_time', 0):.3f}s")
        
        if content['quote']:
            quote = content['quote']
            print(f"💬 句子: \"{quote['text'][:50]}...\"")
            print(f"✍️  作者: {quote['author']}")
        
        # 运行性能对比
        print("\n📊 性能对比测试:")
        benchmark_result = await benchmark_async_vs_sync()
        
        print(f"异步版本: {benchmark_result['async_time']:.3f}s")
        print(f"同步版本: {benchmark_result['sync_time']:.3f}s")
        print(f"性能提升: {benchmark_result['improvement']:.1f}%")
    
    # 运行异步主函数
    asyncio.run(main())