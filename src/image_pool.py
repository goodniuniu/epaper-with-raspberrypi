#!/usr/bin/env python3
"""
每日单词墨水屏显示系统 - 图像对象池
Daily Word E-Paper Display System - Image Pool

实现图像对象的池化管理，减少内存分配和GC压力
"""

import logging
import queue
import threading
from typing import Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

logger = logging.getLogger(__name__)


class ImagePool:
    """图像对象池 - 重用Image对象以减少内存分配"""
    
    def __init__(self, width: int, height: int, pool_size: int = 5, color_mode: str = '1'):
        self.width = width
        self.height = height
        self.pool_size = pool_size
        self.color_mode = color_mode
        self._pool: queue.Queue = queue.Queue(maxsize=pool_size)
        self._in_use: Dict[int, Image.Image] = {}
        self._lock = threading.Lock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'created': 0,
            'returned': 0,
            'cleaned': 0
        }
        
        # 预创建图像对象
        self._prepopulate_pool()
    
    def _prepopulate_pool(self):
        """预填充对象池"""
        for _ in range(self.pool_size // 2):  # 预创建一半
            try:
                image = self._create_image()
                self._pool.put_nowait(image)
                self._stats['created'] += 1
            except queue.Full:
                break
    
    def _create_image(self) -> Image.Image:
        """创建新的图像对象"""
        # 创建白色背景图像
        image = Image.new(self.color_mode, (self.width, self.height), 255)
        return image
    
    def get_image(self, timeout: float = 0.1) -> Optional[Image.Image]:
        """从池中获取图像对象"""
        try:
            # 尝试从池中获取
            image = self._pool.get(timeout=timeout)
            
            with self._lock:
                self._stats['hits'] += 1
                self._in_use[id(image)] = image
            
            # 清理图像内容
            self._clear_image(image)
            logger.debug(f"从对象池获取图像，ID: {id(image)}")
            return image
            
        except queue.Empty:
            # 池为空，创建新对象
            with self._lock:
                self._stats['misses'] += 1
                
                if self._stats['created'] < self.pool_size * 2:  # 允许临时超出池大小
                    image = self._create_image()
                    self._in_use[id(image)] = image
                    self._stats['created'] += 1
                    logger.debug(f"创建新图像对象，ID: {id(image)}")
                    return image
                else:
                    logger.warning("图像对象池已满，无法创建新对象")
                    return None
    
    def return_image(self, image: Image.Image, force: bool = False) -> bool:
        """将图像对象返回池中"""
        if image is None:
            return False
        
        image_id = id(image)
        
        with self._lock:
            if image_id not in self._in_use:
                logger.warning(f"尝试返回未借出的图像对象，ID: {image_id}")
                return False
            
            del self._in_use[image_id]
            self._stats['returned'] += 1
        
        # 清理图像内容
        self._clear_image(image)
        
        # 尝试返回池中
        try:
            self._pool.put_nowait(image)
            logger.debug(f"图像对象返回池中，ID: {image_id}")
            return True
        except queue.Full:
            # 池已满，丢弃对象
            logger.debug(f"对象池已满，丢弃图像对象，ID: {image_id}")
            return False
    
    def _clear_image(self, image: Image.Image):
        """清理图像内容"""
        try:
            # 用白色填充整个图像
            if image.mode == '1':  # 1位图像
                image.paste(255, (0, 0, self.width, self.height))
            else:  # 其他模式
                draw = ImageDraw.Draw(image)
                draw.rectangle([0, 0, self.width, self.height], fill=255)
            
            self._stats['cleaned'] += 1
        except Exception as e:
            logger.error(f"清理图像失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取对象池统计"""
        with self._lock:
            return {
                'pool_size': self.pool_size,
                'available': self._pool.qsize(),
                'in_use': len(self._in_use),
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'created': self._stats['created'],
                'returned': self._stats['returned'],
                'cleaned': self._stats['cleaned'],
                'hit_rate': self._stats['hits'] / max(1, self._stats['hits'] + self._stats['misses'])
            }
    
    def cleanup(self):
        """清理对象池"""
        with self._lock:
            # 清空池中对象
            while not self._pool.empty():
                try:
                    self._pool.get_nowait()
                except queue.Empty:
                    break
            
            # 清理使用中的对象
            self._in_use.clear()
            
            logger.info(f"图像对象池已清理，共清理 {self._stats['created']} 个对象")


class FontCache:
    """字体缓存 - 避免重复加载字体文件"""
    
    def __init__(self, max_size: int = 20):
        self._cache: Dict[str, ImageFont.FreeTypeFont] = {}
        self.max_size = max_size
        self._lock = threading.Lock()
        self._access_count: Dict[str, int] = {}
    
    def get_font(self, font_path: str, size: int) -> Optional[ImageFont.FreeTypeFont]:
        """获取字体对象"""
        cache_key = f"{font_path}:{size}"
        
        with self._lock:
            if cache_key in self._cache:
                # 更新访问计数
                self._access_count[cache_key] = self._access_count.get(cache_key, 0) + 1
                logger.debug(f"字体缓存命中: {cache_key}")
                return self._cache[cache_key]
        
        # 缓存未命中，加载字体
        try:
            font = ImageFont.truetype(font_path, size)
            
            with self._lock:
                # 检查缓存大小
                if len(self._cache) >= self.max_size:
                    # 清理最少使用的字体
                    self._evict_lru_font()
                
                self._cache[cache_key] = font
                self._access_count[cache_key] = 1
                logger.debug(f"字体已缓存: {cache_key}")
            
            return font
            
        except Exception as e:
            logger.error(f"加载字体失败 {font_path} ({size}pt): {e}")
            return None
    
    def _evict_lru_font(self):
        """清理最少使用的字体"""
        if not self._access_count:
            return
        
        # 找到最少使用的字体
        lru_key = min(self._access_count.items(), key=lambda x: x[1])[0]
        
        if lru_key in self._cache:
            del self._cache[lru_key]
            del self._access_count[lru_key]
            logger.debug(f"清理最少使用字体: {lru_key}")
    
    def clear(self):
        """清空字体缓存"""
        with self._lock:
            self._cache.clear()
            self._access_count.clear()
            logger.info("字体缓存已清空")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取字体缓存统计"""
        with self._lock:
            return {
                'cached_fonts': len(self._cache),
                'max_size': self.max_size,
                'total_access': sum(self._access_count.values()),
                'font_keys': list(self._cache.keys())
            }


class OptimizedDisplayContext:
    """优化的显示上下文 - 集成对象池和缓存"""
    
    def __init__(self, width: int, height: int, font_paths: Dict[str, str], font_sizes: Dict[str, int]):
        self.width = width
        self.height = height
        
        # 图像对象池
        self.image_pool = ImagePool(width, height)
        
        # 字体缓存
        self.font_cache = FontCache()
        self.font_paths = font_paths
        self.font_sizes = font_sizes
        
        # 绘图上下文缓存
        self._draw_context: Optional[ImageDraw.Draw] = None
        self._current_image: Optional[Image.Image] = None
    
    def __enter__(self):
        """上下文管理器入口"""
        # 从对象池获取图像
        self._current_image = self.image_pool.get_image()
        if self._current_image:
            self._draw_context = ImageDraw.Draw(self._current_image)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if self._current_image:
            # 将图像返回对象池
            self.image_pool.return_image(self._current_image)
            self._current_image = None
            self._draw_context = None
    
    def get_font(self, font_type: str) -> Optional[ImageFont.FreeTypeFont]:
        """获取字体对象"""
        if font_type not in self.font_sizes:
            return None
        
        font_path = self.font_paths.get(font_type, self.font_paths.get('default', ''))
        font_size = self.font_sizes[font_type]
        
        return self.font_cache.get_font(font_path, font_size)
    
    def draw_text(self, position: tuple, text: str, font: Optional[ImageFont.FreeTypeFont] = None, fill: int = 0):
        """绘制文本"""
        if self._draw_context:
            self._draw_context.text(position, text, font=font, fill=fill)
    
    def draw_rectangle(self, bbox: tuple, fill: int = 255, outline: int = 0, width: int = 1):
        """绘制矩形"""
        if self._draw_context:
            self._draw_context.rectangle(bbox, fill=fill, outline=outline, width=width)
    
    def draw_line(self, xy: tuple, fill: int = 0, width: int = 1):
        """绘制线条"""
        if self._draw_context:
            self._draw_context.line(xy, fill=fill, width=width)
    
    @property
    def image(self) -> Optional[Image.Image]:
        """获取当前图像对象"""
        return self._current_image
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'image_pool': self.image_pool.get_stats(),
            'font_cache': self.font_cache.get_stats()
        }


# 全局对象池管理器
_image_pools: Dict[str, ImagePool] = {}
_font_cache = FontCache()


def get_image_pool(width: int, height: int, pool_size: int = 5) -> ImagePool:
    """获取图像对象池"""
    pool_key = f"{width}x{height}"
    
    if pool_key not in _image_pools:
        _image_pools[pool_key] = ImagePool(width, height, pool_size)
    
    return _image_pools[pool_key]


def get_font_cache() -> FontCache:
    """获取全局字体缓存"""
    return _font_cache


def cleanup_all_pools():
    """清理所有对象池"""
    global _image_pools, _font_cache
    
    # 清理图像对象池
    for pool in _image_pools.values():
        pool.cleanup()
    
    _image_pools.clear()
    
    # 清理字体缓存
    _font_cache.clear()
    
    logger.info("所有对象池已清理")


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("图像对象池测试开始...")
    
    # 测试图像对象池
    pool = get_image_pool(250, 122, pool_size=3)
    
    print("\n1. 测试对象池基本功能:")
    images = []
    for i in range(5):
        img = pool.get_image()
        if img:
            images.append(img)
            print(f"  获取图像对象 {i+1}, ID: {id(img)}")
        else:
            print(f"  获取图像对象 {i+1} 失败")
    
    print(f"\n对象池统计: {pool.get_stats()}")
    
    # 返回部分对象
    print("\n2. 测试返回对象:")
    for i, img in enumerate(images[:3]):
        success = pool.return_image(img)
        print(f"  返回图像对象 {i+1}: {'成功' if success else '失败'}")
    
    print(f"\n对象池统计: {pool.get_stats()}")
    
    # 测试字体缓存
    print("\n3. 测试字体缓存:")
    font_cache = get_font_cache()
    
    # 模拟加载字体
    test_fonts = [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16),  # 重复
    ]
    
    for font_path, size in test_fonts:
        font = font_cache.get_font(font_path, size)
        if font:
            print(f"  加载字体成功: {font_path} ({size}pt)")
        else:
            print(f"  加载字体失败: {font_path} ({size}pt)")
    
    print(f"\n字体缓存统计: {font_cache.get_stats()}")
    
    # 测试优化的显示上下文
    print("\n4. 测试优化的显示上下文:")
    font_paths = {
        'default': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        'title': '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    }
    font_sizes = {
        'default': 12,
        'title': 16
    }
    
    with OptimizedDisplayContext(250, 122, font_paths, font_sizes) as context:
        if context.image:
            print(f"  获取显示上下文成功")
            print(f"  图像尺寸: {context.image.size}")
            
            # 测试绘制
            title_font = context.get_font('title')
            if title_font:
                context.draw_text((10, 10), "测试标题", font=title_font)
                print("  绘制标题成功")
            
            # 显示统计
            stats = context.get_stats()
            print(f"  上下文统计: {stats}")
        else:
            print("  获取显示上下文失败")
    
    # 清理
    cleanup_all_pools()
    print("\n✅ 图像对象池测试完成!")