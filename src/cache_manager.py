#!/usr/bin/env python3
"""
每日单词墨水屏显示系统 - 缓存管理器
Daily Word E-Paper Display System - Cache Manager

实现多层缓存策略：内存缓存(L1) + 磁盘缓存(L2) + API缓存(L3)
"""

import json
import logging
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any, Union
from collections import OrderedDict
import hashlib

logger = logging.getLogger(__name__)

class MemoryCache:
    """内存缓存(L1) - 线程安全的高速缓存"""
    
    def __init__(self, max_size: int = 100, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_time: Dict[str, float] = {}
        self._lock = threading.RLock()
        self._cleanup_interval = 300  # 5分钟清理一次
        self._last_cleanup = time.time()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存项"""
        with self._lock:
            self._cleanup_if_needed()
            
            if key not in self._cache:
                return None
            
            item = self._cache[key]
            
            # 检查过期时间
            if item['expire_at'] < time.time():
                del self._cache[key]
                del self._access_time[key]
                return None
            
            # 更新访问时间
            self._access_time[key] = time.time()
            return item['data']
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存项"""
        with self._lock:
            ttl = ttl or self.default_ttl
            expire_at = time.time() + ttl
            
            # 如果缓存已满，清理最久未使用的项
            if len(self._cache) >= self.max_size:
                self._evict_lru()
            
            self._cache[key] = {
                'data': data,
                'expire_at': expire_at,
                'created_at': time.time()
            }
            self._access_time[key] = time.time()
            return True
    
    def delete(self, key: str) -> bool:
        """删除缓存项"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                del self._access_time[key]
                return True
            return False
    
    def clear(self) -> bool:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._access_time.clear()
            return True
    
    def _evict_lru(self):
        """清理最久未使用的项"""
        if not self._access_time:
            return
        
        # 找到最久未使用的key
        lru_key = min(self._access_time.items(), key=lambda x: x[1])[0]
        del self._cache[lru_key]
        del self._access_time[lru_key]
    
    def _cleanup_if_needed(self):
        """定期清理过期项"""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        
        expired_keys = [
            key for key, item in self._cache.items()
            if item['expire_at'] < now
        ]
        
        for key in expired_keys:
            del self._cache[key]
            if key in self._access_time:
                del self._access_time[key]
        
        self._last_cleanup = now
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self._lock:
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hit_rate': self._calculate_hit_rate(),
                'items': list(self._cache.keys())
            }
    
    def _calculate_hit_rate(self) -> float:
        """计算命中率（简化版）"""
        return 0.0


class DiskCache:
    """磁盘缓存(L2) - 持久化存储"""
    
    def __init__(self, cache_dir: Path, default_ttl: int = 86400):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        self._lock = threading.RLock()
    
    def _get_cache_file(self, key: str) -> Path:
        """获取缓存文件路径"""
        # 使用哈希避免文件名问题
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存项"""
        with self._lock:
            cache_file = self._get_cache_file(key)
            
            if not cache_file.exists():
                return None
            
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    item = json.load(f)
                
                # 检查过期时间
                if item['expire_at'] < time.time():
                    cache_file.unlink()  # 删除过期文件
                    return None
                
                return item['data']
            
            except (json.JSONDecodeError, KeyError, IOError) as e:
                logger.warning(f"读取磁盘缓存失败 {key}: {e}")
                if cache_file.exists():
                    cache_file.unlink()
                return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存项"""
        with self._lock:
            try:
                ttl = ttl or self.default_ttl
                expire_at = time.time() + ttl
                
                item = {
                    'data': data,
                    'expire_at': expire_at,
                    'created_at': time.time(),
                    'key': key
                }
                
                cache_file = self._get_cache_file(key)
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(item, f, ensure_ascii=False, indent=2)
                
                return True
            
            except IOError as e:
                logger.error(f"写入磁盘缓存失败 {key}: {e}")
                return False
    
    def delete(self, key: str) -> bool:
        """删除缓存项"""
        with self._lock:
            cache_file = self._get_cache_file(key)
            if cache_file.exists():
                try:
                    cache_file.unlink()
                    return True
                except IOError as e:
                    logger.error(f"删除磁盘缓存失败 {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """清空缓存"""
        with self._lock:
            try:
                for cache_file in self.cache_dir.glob("*.json"):
                    cache_file.unlink()
                return True
            except IOError as e:
                logger.error(f"清空磁盘缓存失败: {e}")
                return False


class CacheManager:
    """缓存管理器 - 统一的多层缓存接口"""
    
    def __init__(self, cache_dir: Path, memory_max_size: int = 100):
        self.memory_cache = MemoryCache(max_size=memory_max_size)
        self.disk_cache = DiskCache(cache_dir)
        self._lock = threading.RLock()
        self._stats = {
            'memory_hits': 0,
            'disk_hits': 0,
            'misses': 0,
            'total_requests': 0
        }
    
    def get(self, key: str, max_age: int = 3600) -> Optional[Any]:
        """多层缓存获取"""
        with self._lock:
            self._stats['total_requests'] += 1
            
            # L1: 内存缓存
            data = self.memory_cache.get(key)
            if data is not None:
                self._stats['memory_hits'] += 1
                logger.debug(f"内存缓存命中: {key}")
                return data
            
            # L2: 磁盘缓存
            data = self.disk_cache.get(key)
            if data is not None:
                self._stats['disk_hits'] += 1
                logger.debug(f"磁盘缓存命中: {key}")
                
                # 回填到内存缓存
                self.memory_cache.set(key, data, ttl=min(max_age, 3600))
                return data
            
            # 缓存未命中
            self._stats['misses'] += 1
            logger.debug(f"缓存未命中: {key}")
            return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """多层缓存设置"""
        with self._lock:
            # 同时写入内存和磁盘缓存
            memory_success = self.memory_cache.set(key, data, ttl)
            disk_success = self.disk_cache.set(key, data, ttl)
            return memory_success and disk_success
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self._lock:
            total = self._stats['total_requests']
            if total > 0:
                hit_rate = (self._stats['memory_hits'] + self._stats['disk_hits']) / total
            else:
                hit_rate = 0.0
            
            return {
                'total_requests': total,
                'memory_hits': self._stats['memory_hits'],
                'disk_hits': self._stats['disk_hits'],
                'misses': self._stats['misses'],
                'hit_rate': hit_rate,
                'memory_cache': self.memory_cache.get_stats()
            }


# 全局缓存管理器实例
_cache_manager: Optional[CacheManager] = None

def get_cache_manager(cache_dir: Optional[Path] = None) -> CacheManager:
    """获取全局缓存管理器实例"""
    global _cache_manager
    
    if _cache_manager is None:
        if cache_dir is None:
            from daily_word_config import DATA_DIR
            cache_dir = Path(DATA_DIR) / "cache"
        
        _cache_manager = CacheManager(cache_dir)
    
    return _cache_manager


def cache_result(key_prefix: str, ttl: int = 3600):
    """缓存装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 生成缓存key
            cache_key = f"{key_prefix}:{hash(str(args) + str(kwargs))}"
            
            # 获取缓存管理器
            cache_manager = get_cache_manager()
            
            # 尝试从缓存获取
            cached_result = cache_manager.get(cache_key, max_age=ttl)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator