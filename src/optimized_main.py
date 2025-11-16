#!/usr/bin/env python3
"""
每日单词墨水屏显示系统 - 优化主程序
Daily Word E-Paper Display System - Optimized Main Program

集成所有优化组件的高性能版本
"""

import argparse
import asyncio
import logging
import signal
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入优化组件
from cache_manager import get_cache_manager, cache_result
from async_api_client import AsyncDailyWordAPIClient, async_get_daily_content
from optimized_display_controller import OptimizedDailyWordDisplayController
from performance_monitor import (
    get_performance_metrics, get_performance_monitor, 
    api_performance, display_performance
)
from daily_word_file_manager import DailyWordFileManager
from daily_word_config import (
    PROJECT_NAME, PROJECT_VERSION, LOGGING_CONFIG, UPDATE_CONFIG,
    FEATURE_FLAGS, DEBUG_CONFIG, DATA_DIR, LOGS_DIR
)

logger = logging.getLogger(__name__)


class OptimizedDailyWordSystem:
    """优化的每日单词系统主类"""
    
    def __init__(self):
        """初始化优化系统"""
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"初始化优化版 {PROJECT_NAME} v{PROJECT_VERSION}")
        
        # 初始化优化组件
        self.cache_manager = get_cache_manager()
        self.file_manager = DailyWordFileManager()
        self.display_controller = OptimizedDailyWordDisplayController()
        self.performance_monitor = get_performance_monitor()
        
        # 异步客户端
        self.async_client = None
        
        self.running = False
        self._stats = {
            'total_updates': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'async_requests': 0,
            'sync_fallbacks': 0
        }
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # 启动性能监控
        if FEATURE_FLAGS['enable_monitoring']:
            self.performance_monitor.start_monitoring()
    
    def setup_logging(self):
        """设置日志系统"""
        # 确保日志目录存在
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        # 配置日志格式
        log_format = LOGGING_CONFIG['log_settings']['log_format']
        date_format = LOGGING_CONFIG['log_settings']['date_format']
        log_level = getattr(logging, LOGGING_CONFIG['log_level'].upper())
        
        # 配置根日志记录器
        logging.basicConfig(
            level=log_level,
            format=log_format,
            datefmt=date_format,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(
                    LOGS_DIR / f"optimized_{LOGGING_CONFIG['log_files']['main']}",
                    encoding=LOGGING_CONFIG['log_settings']['encoding']
                )
            ]
        )
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        self.logger.info(f"接收到信号 {signum}，准备退出...")
        self.running = False
    
    @api_performance
    async def get_daily_content_async(self, force_new: bool = False) -> Dict:
        """异步获取每日内容（优化版本）"""
        try:
            # 使用异步客户端
            if not self.async_client:
                self.async_client = AsyncDailyWordAPIClient(self.cache_manager)
            
            async with self.async_client as client:
                content = await client.get_daily_content(force_new=force_new)
                self._stats['async_requests'] += 1
                return content
                
        except Exception as e:
            self.logger.error(f"异步获取内容失败: {e}")
            # 回退到同步获取
            self._stats['sync_fallbacks'] += 1
            return self._get_content_sync_fallback(force_new)
    
    def _get_content_sync_fallback(self, force_new: bool = False) -> Dict:
        """同步获取内容的回退方法"""
        try:
            from daily_word_api_client import DailyWordAPIClient
            
            sync_client = DailyWordAPIClient()
            content = sync_client.get_daily_content(force_new=force_new)
            
            # 保存到缓存
            if content and self.cache_manager:
                today = datetime.now().strftime('%Y-%m-%d')
                cache_key = f"daily_content:{today}"
                self.cache_manager.set(cache_key, content, ttl=3600)
            
            return content
            
        except Exception as e:
            self.logger.error(f"同步回退获取内容失败: {e}")
            return {
                'word': None,
                'quote': None,
                'error': str(e),
                'generated_at': datetime.now().isoformat()
            }
    
    @display_performance
    def update_display(self, force_new: bool = False) -> bool:
        """更新显示内容（优化版本）"""
        try:
            self.logger.info("开始优化更新显示内容...")
            
            # 检查缓存
            today = datetime.now().strftime('%Y-%m-%d')
            cache_key = f"daily_content:{today}"
            
            if not force_new:
                cached_content = self.cache_manager.get(cache_key, max_age=3600)
                if cached_content:
                    self._stats['cache_hits'] += 1
                    self.logger.info("使用缓存的每日内容")
                    content = cached_content
                else:
                    self._stats['cache_misses'] += 1
                    # 异步获取新内容
                    content = asyncio.run(self.get_daily_content_async(force_new))
            else:
                # 强制获取新内容
                content = asyncio.run(self.get_daily_content_async(force_new=True))
            
            if not content or (not content.get('word') and not content.get('quote')):
                self.logger.warning("未获取到有效内容，尝试使用文件缓存")
                # 尝试使用文件中的内容
                cached_content = self.file_manager.load_current_content()
                if cached_content:
                    content = cached_content
                    self.logger.info("使用文件缓存内容")
                else:
                    self.logger.error("无法获取任何有效内容")
                    return False
            
            # 保存内容到文件
            if content.get('word') or content.get('quote'):
                word_data = content.get('word', {})
                quote_data = content.get('quote', {})
                self.file_manager.save_current_content(word_data, quote_data)
            
            # 显示内容
            success = self.display_controller.display_content(content)
            
            if success:
                self._stats['total_updates'] += 1
                self._log_update_info(content)
                self.logger.info("优化显示内容更新完成")
            
            return success
            
        except Exception as e:
            self.logger.error(f"优化更新显示失败: {e}")
            return False
    
    def _log_update_info(self, content: Dict):
        """记录更新信息"""
        word_info = "无"
        quote_info = "无"
        
        if content.get('word'):
            word = content['word']
            word_info = f"{word.get('word', 'Unknown')} ({word.get('source', 'Unknown')})"
        
        if content.get('quote'):
            quote = content['quote']
            quote_text = quote.get('text', '')[:30] + "..." if len(quote.get('text', '')) > 30 else quote.get('text', '')
            quote_info = f"{quote_text} - {quote.get('author', 'Unknown')} ({quote.get('source', 'Unknown')})"
        
        self.logger.info(f"更新内容 - 单词: {word_info}, 句子: {quote_info}")
    
    def get_system_status(self) -> Dict:
        """获取系统状态（优化版本）"""
        try:
            # 获取性能指标
            perf_metrics = self.performance_monitor.get_performance_report()
            
            # 获取缓存统计
            cache_stats = self.cache_manager.get_stats() if hasattr(self.cache_manager, 'get_stats') else {}
            
            # 获取显示控制器统计
            display_stats = self.display_controller.get_stats() if hasattr(self.display_controller, 'get_stats') else {}
            
            # 获取文件管理器统计
            file_stats = self.file_manager.get_file_stats() if hasattr(self.file_manager, 'get_file_stats') else {}
            
            # 系统状态
            status = {
                'system': {
                    'name': f"Optimized {PROJECT_NAME}",
                    'version': PROJECT_VERSION,
                    'running': self.running,
                    'timestamp': datetime.now().isoformat(),
                    'uptime': perf_metrics.get('uptime', 0),
                    'performance_status': perf_metrics.get('status', 'unknown'),
                    'total_updates': self._stats['total_updates']
                },
                'performance': {
                    'cache_hit_rate': cache_stats.get('hit_rate', 0),
                    'async_requests': self._stats['async_requests'],
                    'sync_fallbacks': self._stats['sync_fallbacks'],
                    'system_metrics': perf_metrics.get('system_status', {}),
                    'averages': perf_metrics.get('performance_averages', {})
                },
                'components': {
                    'cache_manager': cache_stats,
                    'display_controller': display_stats,
                    'file_manager': file_stats,
                    'performance_monitor': {
                        'alerts': len(perf_metrics.get('recent_alerts', [])),
                        'status': perf_metrics.get('status', 'normal')
                    }
                },
                'optimization': {
                    'features_enabled': {
                        'caching': True,
                        'async_requests': True,
                        'image_pooling': True,
                        'font_caching': True,
                        'performance_monitoring': FEATURE_FLAGS['enable_monitoring']
                    },
                    'efficiency_gains': self._calculate_efficiency_gains()
                }
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"获取优化系统状态失败: {e}")
            return {'error': str(e)}
    
    def _calculate_efficiency_gains(self) -> Dict[str, Any]:
        """计算效率提升"""
        total_requests = self._stats['cache_hits'] + self._stats['cache_misses']
        
        if total_requests > 0:
            cache_efficiency = self._stats['cache_hits'] / total_requests
        else:
            cache_efficiency = 0
        
        return {
            'cache_efficiency': cache_efficiency,
            'async_usage_ratio': self._stats['async_requests'] / max(1, self._stats['total_updates']),
            'estimated_time_saved': self._stats['cache_hits'] * 0.5  # 估算每次缓存命中节省0.5秒
        }
    
    def run_daemon_mode(self):
        """运行守护进程模式（优化版本）"""
        self.logger.info("启动优化守护进程模式...")
        self.running = True
        
        # 根据配置选择运行模式
        mode = UPDATE_CONFIG['mode']
        
        if mode == 'scheduled':
            self.run_optimized_scheduled_mode()
        elif mode == 'interval':
            self.run_optimized_interval_mode()
        else:
            self.logger.error(f"未知的更新模式: {mode}")
            return False
        
        return True
    
    def run_optimized_scheduled_mode(self):
        """优化的定时模式"""
        self.logger.info("启动优化定时更新模式...")
        
        # 获取更新时间配置
        update_times = UPDATE_CONFIG['scheduled']['update_times']
        self.logger.info(f"定时更新时间: {', '.join(update_times)}")
        
        # 立即执行一次更新
        self.update_display()
        
        while self.running:
            try:
                current_time = datetime.now().strftime('%H:%M')
                
                # 检查是否到了更新时间
                if current_time in update_times:
                    self.logger.info(f"定时更新触发: {current_time}")
                    self.update_display()
                    
                    # 等待一分钟，避免重复触发
                    time.sleep(60)
                
                # 每分钟检查一次
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"优化定时模式运行错误: {e}")
                time.sleep(60)
        
        self.logger.info("优化定时更新模式已停止")
    
    def run_optimized_interval_mode(self):
        """优化的间隔模式"""
        interval = UPDATE_CONFIG['interval']['update_interval']
        self.logger.info(f"启动优化间隔更新模式，间隔: {interval}秒")
        self.running = True
        
        # 立即执行一次更新
        self.update_display()
        
        while self.running:
            try:
                self.logger.debug(f"等待 {interval} 秒后进行下次更新...")
                
                # 分段等待，以便响应退出信号
                wait_time = 0
                while wait_time < interval and self.running:
                    time.sleep(min(60, interval - wait_time))
                    wait_time += 60
                
                if self.running:
                    self.logger.info("优化间隔更新触发")
                    self.update_display()
                
            except Exception as e:
                self.logger.error(f"优化间隔模式运行错误: {e}")
                time.sleep(60)
        
        self.logger.info("优化间隔更新模式已停止")
    
    def cleanup(self):
        """清理优化系统资源"""
        self.logger.info("清理优化系统资源...")
        
        try:
            # 停止性能监控
            if FEATURE_FLAGS['enable_monitoring']:
                self.performance_monitor.stop_monitoring()
            
            # 清理显示控制器
            if self.display_controller:
                self.display_controller.cleanup()
            
            # 导出性能指标
            if self.performance_monitor:
                metrics_file = LOGS_DIR / "performance_metrics.json"
                get_performance_metrics().export_metrics(metrics_file)
                self.logger.info(f"性能指标已导出到: {metrics_file}")
            
            # 显示最终统计
            final_stats = self.get_system_status()
            self.logger.info("最终系统统计:")
            self.logger.info(f"  总更新次数: {final_stats['system']['total_updates']}")
            self.logger.info(f"  缓存效率: {final_stats['optimization']['efficiency_gains']['cache_efficiency']:.2%}")
            self.logger.info(f"  异步使用率: {final_stats['optimization']['efficiency_gains']['async_usage_ratio']:.2%}")
            
            self.logger.info("优化系统资源清理完成")
            
        except Exception as e:
            self.logger.error(f"清理优化资源失败: {e}")


def create_argument_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description=f"优化版 {PROJECT_NAME} v{PROJECT_VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s                    # 更新一次显示内容
  %(prog)s --daemon           # 优化守护进程模式运行
  %(prog)s --clear            # 清空显示
  %(prog)s --test             # 测试优化系统功能
  %(prog)s --status           # 显示优化系统状态
  %(prog)s --force            # 强制获取新内容
  %(prog)s --benchmark        # 运行性能对比测试
        """
    )
    
    parser.add_argument(
        '--daemon', '-d',
        action='store_true',
        help='优化守护进程模式运行'
    )
    
    parser.add_argument(
        '--clear', '-c',
        action='store_true',
        help='清空显示'
    )
    
    parser.add_argument(
        '--test', '-t',
        action='store_true',
        help='测试优化系统功能'
    )
    
    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help='显示优化系统状态'
    )
    
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='强制获取新内容'
    )
    
    parser.add_argument(
        '--benchmark', '-b',
        action='store_true',
        help='运行性能对比测试'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='详细输出'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'优化版 {PROJECT_NAME} v{PROJECT_VERSION}'
    )
    
    return parser


async def run_benchmark():
    """运行性能对比测试"""
    print("🚀 开始性能对比测试...")
    
    # 测试异步内容获取
    print("\n1. 测试异步内容获取:")
    start_time = time.time()
    
    content = await async_get_daily_content(force_new=True)
    async_time = time.time() - start_time
    
    print(f"   异步获取耗时: {async_time:.3f}s")
    if content.get('word'):
        print(f"   获取单词: {content['word']['word']}")
    if content.get('quote'):
        print(f"   获取句子: {content['quote']['text'][:30]}...")
    
    # 测试同步内容获取（作为对比）
    print("\n2. 测试同步内容获取:")
    from daily_word_api_client import DailyWordAPIClient
    
    start_time = time.time()
    sync_client = DailyWordAPIClient()
    sync_content = sync_client.get_daily_content(force_new=True)
    sync_time = time.time() - start_time
    
    print(f"   同步获取耗时: {sync_time:.3f}s")
    
    # 性能对比
    improvement = (sync_time - async_time) / sync_time * 100 if sync_time > 0 else 0
    print(f"\n📊 性能对比结果:")
    print(f"   异步版本: {async_time:.3f}s")
    print(f"   同步版本: {sync_time:.3f}s")
    print(f"   性能提升: {improvement:.1f}%")
    
    return {
        'async_time': async_time,
        'sync_time': sync_time,
        'improvement': improvement
    }


def main():
    """主函数"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # 设置详细输出
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # 创建优化系统实例
        system = OptimizedDailyWordSystem()
        
        # 性能对比测试
        if args.benchmark:
            print("运行性能对比测试...")
            benchmark_result = asyncio.run(run_benchmark())
            print(f"\n✅ 性能测试完成！提升: {benchmark_result['improvement']:.1f}%")
            return
        
        # 根据参数执行相应操作
        if args.clear:
            success = system.display_controller.clear_display()
            sys.exit(0 if success else 1)
        
        elif args.test:
            success = system.update_display(force_new=True)
            sys.exit(0 if success else 1)
        
        elif args.status:
            status = system.get_system_status()
            print("优化系统状态:")
            print(f"  名称: {status['system']['name']}")
            print(f"  版本: {status['system']['version']}")
            print(f"  运行状态: {'运行中' if status['system']['running'] else '已停止'}")
            print(f"  性能状态: {status['system']['performance_status']}")
            print(f"  总更新次数: {status['system']['total_updates']}")
            print(f"  缓存效率: {status['performance']['cache_hit_rate']:.2%}")
            print(f"  异步使用率: {status['performance']['async_usage_ratio']:.2%}")
            print(f"  内存使用率: {status['performance']['system_metrics'].get('memory_usage', 0):.1f}%")
            print(f"  CPU使用率: {status['performance']['system_metrics'].get('cpu_usage', 0):.1f}%")
            sys.exit(0)
        
        elif args.daemon:
            system.run_daemon_mode()
        
        else:
            # 默认：更新一次显示
            success = system.update_display(force_new=args.force)
            sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(130)
    
    except Exception as e:
        print(f"优化程序执行失败: {e}")
        sys.exit(1)
    
    finally:
        # 清理资源
        try:
            if 'system' in locals():
                system.cleanup()
        except:
            pass


if __name__ == "__main__":
    main()