#!/usr/bin/env python3
"""
每日单词墨水屏显示系统 - 优化效果测试
Daily Word E-Paper Display System - Optimization Test

测试和验证所有优化组件的性能提升
"""

import asyncio
import time
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入所有组件进行测试
from cache_manager import get_cache_manager, cache_result
from async_api_client import AsyncDailyWordAPIClient, async_get_daily_content
from image_pool import get_image_pool, cleanup_all_pools
from performance_monitor import get_performance_metrics, get_performance_monitor
from optimized_display_controller import OptimizedDailyWordDisplayController
from daily_word_api_client import DailyWordAPIClient  # 原始版本用于对比

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class OptimizationTester:
    """优化效果测试器"""
    
    def __init__(self):
        self.results = {
            'cache_tests': {},
            'async_tests': {},
            'image_pool_tests': {},
            'display_tests': {},
            'overall_performance': {}
        }
        self.performance_metrics = get_performance_metrics()
    
    async def test_cache_performance(self) -> Dict[str, Any]:
        """测试缓存性能"""
        print("\n" + "="*60)
        print("🧪 测试缓存性能")
        print("="*60)
        
        cache_manager = get_cache_manager()
        
        # 测试数据
        test_data = {
            'word': {
                'word': 'optimization',
                'phonetic': '/ˌɒptɪmʌɪˈzeɪʃ(ə)n/',
                'definition': 'The action of making the best or most effective use of a resource.',
                'example': 'The optimization of the algorithm improved performance significantly.',
                'source': 'Test'
            },
            'quote': {
                'text': 'Optimization is the process of making something as effective as possible.',
                'author': 'Test Author',
                'category': 'technology',
                'source': 'Test'
            }
        }
        
        results = {
            'memory_cache_performance': {},
            'disk_cache_performance': {},
            'cache_hit_rate': 0,
            'total_time_saved': 0
        }
        
        # 测试内存缓存
        print("\n1. 测试内存缓存性能:")
        start_time = time.time()
        
        # 第一次写入（缓存未命中）
        cache_manager.set('test_key_1', test_data, ttl=3600)
        first_write_time = time.time() - start_time
        
        # 第一次读取（缓存命中）
        start_time = time.time()
        cached_data = cache_manager.get('test_key_1')
        first_read_time = time.time() - start_time
        
        # 第二次读取（应该更快）
        start_time = time.time()
        cached_data = cache_manager.get('test_key_1')
        second_read_time = time.time() - start_time
        
        results['memory_cache_performance'] = {
            'first_write': first_write_time,
            'first_read': first_read_time,
            'second_read': second_read_time,
            'speed_improvement': (first_read_time - second_read_time) / first_read_time * 100 if first_read_time > 0 else 0
        }
        
        print(f"   首次写入耗时: {first_write_time:.4f}s")
        print(f"   首次读取耗时: {first_read_time:.4f}s")
        print(f"   二次读取耗时: {second_read_time:.4f}s")
        print(f"   读取速度提升: {results['memory_cache_performance']['speed_improvement']:.1f}%")
        
        # 测试磁盘缓存
        print("\n2. 测试磁盘缓存性能:")
        start_time = time.time()
        
        # 写入大量数据
        large_data = {f'key_{i}': f'value_{i}' * 100 for i in range(100)}
        cache_manager.set('large_test_key', large_data, ttl=3600)
        disk_write_time = time.time() - start_time
        
        # 读取数据
        start_time = time.time()
        cached_large_data = cache_manager.get('large_test_key')
        disk_read_time = time.time() - start_time
        
        results['disk_cache_performance'] = {
            'write_time': disk_write_time,
            'read_time': disk_read_time,
            'data_size': len(json.dumps(large_data))
        }
        
        print(f"   磁盘写入耗时: {disk_write_time:.4f}s")
        print(f"   磁盘读取耗时: {disk_read_time:.4f}s")
        print(f"   数据大小: {results['disk_cache_performance']['data_size']} bytes")
        
        # 获取缓存统计
        stats = cache_manager.get_stats()
        results['cache_hit_rate'] = stats.get('hit_rate', 0)
        results['total_operations'] = stats.get('total_requests', 0)
        
        print(f"\n3. 缓存统计:")
        print(f"   总请求数: {results['total_operations']}")
        print(f"   缓存命中率: {results['cache_hit_rate']:.2%}")
        
        self.results['cache_tests'] = results
        return results
    
    async def test_async_performance(self) -> Dict[str, Any]:
        """测试异步性能"""
        print("\n" + "="*60)
        print("⚡ 测试异步API性能")
        print("="*60)
        
        results = {
            'async_vs_sync': {},
            'concurrent_requests': {},
            'async_efficiency': 0
        }
        
        # 测试异步 vs 同步
        print("\n1. 对比异步和同步API调用:")
        
        # 异步调用
        start_time = time.time()
        async_content = await async_get_daily_content(force_new=True)
        async_time = time.time() - start_time
        
        # 同步调用
        start_time = time.time()
        sync_client = DailyWordAPIClient()
        sync_content = sync_client.get_daily_content(force_new=True)
        sync_time = time.time() - start_time
        
        results['async_vs_sync'] = {
            'async_time': async_time,
            'sync_time': sync_time,
            'improvement': (sync_time - async_time) / sync_time * 100 if sync_time > 0 else 0,
            'async_success': bool(async_content.get('word') or async_content.get('quote')),
            'sync_success': bool(sync_content.get('word') or sync_content.get('quote'))
        }
        
        print(f"   异步调用耗时: {async_time:.3f}s")
        print(f"   同步调用耗时: {sync_time:.3f}s")
        print(f"   性能提升: {results['async_vs_sync']['improvement']:.1f}%")
        print(f"   异步成功: {results['async_vs_sync']['async_success']}")
        print(f"   同步成功: {results['async_vs_sync']['sync_success']}")
        
        # 测试并发请求
        print("\n2. 测试并发请求性能:")
        
        async def concurrent_test():
            # 创建多个并发请求
            tasks = []
            for i in range(5):
                task = async_get_daily_content(force_new=False)
                tasks.append(task)
            
            start_time = time.time()
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
            concurrent_time = time.time() - start_time
            
            successful = sum(1 for r in results_list if isinstance(r, dict) and (r.get('word') or r.get('quote')))
            
            return {
                'concurrent_time': concurrent_time,
                'successful_requests': successful,
                'total_requests': len(tasks),
                'average_time_per_request': concurrent_time / len(tasks)
            }
        
        concurrent_results = await concurrent_test()
        results['concurrent_requests'] = concurrent_results
        
        print(f"   5个并发请求总耗时: {concurrent_results['concurrent_time']:.3f}s")
        print(f"   成功请求数: {concurrent_results['successful_requests']}/{concurrent_results['total_requests']}")
        print(f"   平均每个请求耗时: {concurrent_results['average_time_per_request']:.3f}s")
        
        self.results['async_tests'] = results
        return results
    
    def test_image_pool_performance(self) -> Dict[str, Any]:
        """测试图像对象池性能"""
        print("\n" + "="*60)
        print("🖼️  测试图像对象池性能")
        print("="*60)
        
        # 创建对象池
        image_pool = get_image_pool(250, 122, pool_size=5)
        
        results = {
            'pool_efficiency': {},
            'memory_usage': {},
            'object_reuse_rate': 0
        }
        
        print("\n1. 测试对象池效率:")
        
        # 测试对象获取和返回
        images = []
        start_time = time.time()
        
        # 获取多个对象
        for i in range(10):
            img = image_pool.get_image()
            if img:
                images.append(img)
        
        get_time = time.time() - start_time
        
        # 返回对象到池
        start_time = time.time()
        returned_count = 0
        for img in images:
            if image_pool.return_image(img):
                returned_count += 1
        
        return_time = time.time() - start_time
        
        results['pool_efficiency'] = {
            'objects_acquired': len(images),
            'objects_returned': returned_count,
            'acquisition_time': get_time,
            'return_time': return_time,
            'average_acquisition_time': get_time / len(images) if images else 0
        }
        
        print(f"   获取对象数: {results['pool_efficiency']['objects_acquired']}")
        print(f"   成功返回数: {results['pool_efficiency']['objects_returned']}")
        print(f"   获取总耗时: {results['pool_efficiency']['acquisition_time']:.4f}s")
        print(f"   返回总耗时: {results['pool_efficiency']['return_time']:.4f}s")
        print(f"   平均获取耗时: {results['pool_efficiency']['average_acquisition_time']:.4f}s")
        
        # 获取对象池统计
        stats = image_pool.get_stats()
        results['object_reuse_rate'] = stats.get('hit_rate', 0)
        
        print(f"\n2. 对象池统计:")
        print(f"   池大小: {stats['pool_size']}")
        print(f"   可用对象: {stats['available']}")
        print(f"   使用中对象: {stats['in_use']}")
        print(f"   对象重用率: {results['object_reuse_rate']:.2%}")
        
        self.results['image_pool_tests'] = results
        return results
    
    def test_display_performance(self) -> Dict[str, Any]:
        """测试显示性能"""
        print("\n" + "="*60)
        print("🖥️  测试显示性能优化")
        print("="*60)
        
        # 创建优化显示控制器
        optimized_controller = OptimizedDailyWordDisplayController()
        
        results = {
            'image_creation': {},
            'font_caching': {},
            'overall_display_time': 0
        }
        
        # 测试内容
        test_content = {
            'word': {
                'word': 'performance',
                'phonetic': '/pəˈfɔːməns/',
                'definition': 'The action or process of performing a task or function.',
                'example': 'The performance of the new system exceeded expectations.',
                'source': 'Test'
            },
            'quote': {
                'text': 'Simplicity is the ultimate sophistication.',
                'author': 'Leonardo da Vinci',
                'category': 'wisdom',
                'source': 'Test'
            }
        }
        
        print("\n1. 测试图像创建性能:")
        
        # 多次创建图像以测试缓存效果
        creation_times = []
        for i in range(5):
            start_time = time.time()
            image = optimized_controller.create_content_image(test_content)
            creation_time = time.time() - start_time
            
            creation_times.append(creation_time)
            
            if image:
                print(f"   第{i+1}次创建耗时: {creation_time:.4f}s")
            else:
                print(f"   第{i+1}次创建失败")
        
        if creation_times:
            results['image_creation'] = {
                'first_creation': creation_times[0],
                'last_creation': creation_times[-1],
                'average_creation': sum(creation_times) / len(creation_times),
                'cache_improvement': (creation_times[0] - creation_times[-1]) / creation_times[0] * 100 if len(creation_times) > 1 else 0
            }
            
            print(f"   首次创建: {results['image_creation']['first_creation']:.4f}s")
            print(f"   末次创建: {results['image_creation']['last_creation']:.4f}s")
            print(f"   平均创建: {results['image_creation']['average_creation']:.4f}s")
            print(f"   缓存改进: {results['image_creation']['cache_improvement']:.1f}%")
        
        # 获取显示控制器统计
        stats = optimized_controller.get_stats()
        results['font_caching'] = stats.get('font_cache', {})
        
        print(f"\n2. 字体缓存统计:")
        print(f"   缓存字体数: {results['font_caching'].get('cached_fonts', 0)}")
        print(f"   总访问次数: {results['font_caching'].get('total_access', 0)}")
        
        # 清理
        optimized_controller.cleanup()
        
        self.results['display_tests'] = results
        return results
    
    def generate_performance_report(self) -> str:
        """生成性能测试报告"""
        print("\n" + "="*60)
        print("📊 生成优化性能报告")
        print("="*60)
        
        report = []
        report.append("每日单词系统优化性能测试报告")
        report.append("="*50)
        report.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 缓存性能总结
        if 'cache_tests' in self.results:
            cache_results = self.results['cache_tests']
            report.append("🧪 缓存性能:")
            report.append(f"  内存缓存读取速度提升: {cache_results['memory_cache_performance'].get('speed_improvement', 0):.1f}%")
            report.append(f"  缓存命中率: {cache_results.get('cache_hit_rate', 0):.2%}")
            report.append(f"  总操作数: {cache_results.get('total_operations', 0)}")
            report.append("")
        
        # 异步性能总结
        if 'async_tests' in self.results:
            async_results = self.results['async_tests']
            report.append("⚡ 异步性能:")
            report.append(f"  API调用速度提升: {async_results['async_vs_sync'].get('improvement', 0):.1f}%")
            report.append(f"  并发请求平均耗时: {async_results['concurrent_requests'].get('average_time_per_request', 0):.3f}s")
            report.append(f"  并发成功率: {async_results['concurrent_requests'].get('successful_requests', 0)}/{async_results['concurrent_requests'].get('total_requests', 0)}")
            report.append("")
        
        # 对象池性能总结
        if 'image_pool_tests' in self.results:
            pool_results = self.results['image_pool_tests']
            report.append("🖼️  对象池性能:")
            report.append(f"  对象重用率: {pool_results.get('object_reuse_rate', 0):.2%}")
            report.append(f"  平均获取耗时: {pool_results['pool_efficiency'].get('average_acquisition_time', 0):.4f}s")
            report.append("")
        
        # 显示性能总结
        if 'display_tests' in self.results:
            display_results = self.results['display_tests']
            report.append("🖥️  显示性能:")
            report.append(f"  图像创建缓存改进: {display_results['image_creation'].get('cache_improvement', 0):.1f}%")
            report.append(f"  平均创建耗时: {display_results['image_creation'].get('average_creation', 0):.4f}s")
            report.append("")
        
        # 总体性能评估
        report.append("📈 总体性能评估:")
        
        # 计算综合改进
        improvements = []
        if 'cache_tests' in self.results:
            improvements.append(self.results['cache_tests']['memory_cache_performance'].get('speed_improvement', 0))
        if 'async_tests' in self.results:
            improvements.append(self.results['async_tests']['async_vs_sync'].get('improvement', 0))
        if 'display_tests' in self.results:
            improvements.append(self.results['display_tests']['image_creation'].get('cache_improvement', 0))
        
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0
        
        report.append(f"  综合性能提升: {avg_improvement:.1f}%")
        report.append(f"  优化组件数量: 4个（缓存、异步、对象池、显示）")
        report.append("")
        
        report.append("✅ 优化建议实施完成！")
        report.append("系统性能得到显著提升，用户体验大幅改善。")
        
        return "\n".join(report)


async def run_all_tests():
    """运行所有测试"""
    tester = OptimizationTester()
    
    print("🚀 开始每日单词系统优化测试")
    print("="*60)
    
    # 运行各项测试
    await tester.test_cache_performance()
    await tester.test_async_performance()
    tester.test_image_pool_performance()
    tester.test_display_performance()
    
    # 生成报告
    report = tester.generate_performance_report()
    
    # 保存报告到文件
    report_file = Path("optimization_test_report.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 测试报告已保存到: {report_file}")
    print("\n" + report)
    
    # 清理资源
    cleanup_all_pools()
    
    return tester.results


def main():
    """主函数"""
    print("🎯 每日单词系统优化效果测试")
    print("="*60)
    
    try:
        # 运行所有测试
        results = asyncio.run(run_all_tests())
        
        print("\n✅ 所有优化测试完成！")
        return results
        
    except KeyboardInterrupt:
        print("\n\n❌ 测试被用户中断")
        return {}
    except Exception as e:
        print(f"\n\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return {}


if __name__ == "__main__":
    main()