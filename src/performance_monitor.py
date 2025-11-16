#!/usr/bin/env python3
"""
每日单词墨水屏显示系统 - 性能监控器
Daily Word E-Paper Display System - Performance Monitor

实现性能指标收集、监控和装饰器功能
"""

import time
import logging
import functools
import threading
import psutil
from typing import Dict, Any, Callable, Optional
from datetime import datetime
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """性能指标收集器"""
    
    def __init__(self):
        self.metrics: Dict[str, list] = {
            'api_response_time': [],
            'display_update_time': [],
            'cache_hit_rate': [],
            'memory_usage': [],
            'cpu_usage': [],
            'disk_usage': []
        }
        self._lock = threading.Lock()
        self._start_time = time.time()
    
    def record_metric(self, metric_name: str, value: float):
        """记录性能指标"""
        with self._lock:
            if metric_name in self.metrics:
                self.metrics[metric_name].append({
                    'value': value,
                    'timestamp': time.time(),
                    'datetime': datetime.now().isoformat()
                })
                
                # 限制历史数据数量
                if len(self.metrics[metric_name]) > 1000:
                    self.metrics[metric_name] = self.metrics[metric_name][-500:]
    
    def get_system_metrics(self) -> Dict[str, float]:
        """获取系统资源使用情况"""
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            disk = psutil.disk_usage('/')
            
            return {
                'memory_usage': memory.percent,
                'memory_available_mb': memory.available / 1024 / 1024,
                'cpu_usage': cpu_percent,
                'disk_usage': disk.percent,
                'disk_free_gb': disk.free / 1024 / 1024 / 1024
            }
        except Exception as e:
            logger.error(f"获取系统指标失败: {e}")
            return {
                'memory_usage': 0.0,
                'memory_available_mb': 0.0,
                'cpu_usage': 0.0,
                'disk_usage': 0.0,
                'disk_free_gb': 0.0
            }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        with self._lock:
            summary = {
                'uptime': time.time() - self._start_time,
                'system': self.get_system_metrics(),
                'averages': {}
            }
            
            # 计算平均值
            for metric_name, values in self.metrics.items():
                if values:
                    recent_values = [v['value'] for v in values[-10:]]  # 最近10次
                    summary['averages'][f'{metric_name}_avg'] = sum(recent_values) / len(recent_values)
                    summary['averages'][f'{metric_name}_max'] = max(recent_values)
                    summary['averages'][f'{metric_name}_min'] = min(recent_values)
            
            return summary
    
    def export_metrics(self, file_path: Path) -> bool:
        """导出指标到文件"""
        try:
            with self._lock:
                export_data = {
                    'export_time': datetime.now().isoformat(),
                    'uptime': time.time() - self._start_time,
                    'metrics': self.metrics,
                    'summary': self.get_metrics_summary()
                }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return True
        
        except Exception as e:
            logger.error(f"导出指标失败: {e}")
            return False


# 全局性能指标实例
_performance_metrics = PerformanceMetrics()


def get_performance_metrics() -> PerformanceMetrics:
    """获取全局性能指标实例"""
    return _performance_metrics


def measure_time(metric_name: str, log_result: bool = True):
    """性能测量装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # 记录开始时的系统资源
            start_metrics = _performance_metrics.get_system_metrics()
            
            try:
                result = func(*args, **kwargs)
                
                # 计算执行时间
                elapsed_time = time.time() - start_time
                
                # 记录指标
                _performance_metrics.record_metric(metric_name, elapsed_time)
                
                # 记录系统资源变化
                end_metrics = _performance_metrics.get_system_metrics()
                _performance_metrics.record_metric('memory_usage', end_metrics['memory_usage'])
                _performance_metrics.record_metric('cpu_usage', end_metrics['cpu_usage'])
                
                if log_result:
                    logger.info(f"{func.__name__} 执行完成，耗时: {elapsed_time:.3f}s")
                
                return result
            
            except Exception as e:
                elapsed_time = time.time() - start_time
                logger.error(f"{func.__name__} 执行失败，耗时: {elapsed_time:.3f}s, 错误: {e}")
                raise
        
        return wrapper
    return decorator


def measure_async_time(metric_name: str, log_result: bool = True):
    """异步性能测量装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                elapsed_time = time.time() - start_time
                _performance_metrics.record_metric(metric_name, elapsed_time)
                
                if log_result:
                    logger.info(f"{func.__name__} 异步执行完成，耗时: {elapsed_time:.3f}s")
                
                return result
            
            except Exception as e:
                elapsed_time = time.time() - start_time
                logger.error(f"{func.__name__} 异步执行失败，耗时: {elapsed_time:.3f}s, 错误: {e}")
                raise
        
        return wrapper
    return decorator


class PerformanceMonitor:
    """性能监控器 - 实时监控和告警"""
    
    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.thresholds = {
            'memory_usage': 85.0,  # 内存使用率阈值
            'cpu_usage': 80.0,     # CPU使用率阈值
            'disk_usage': 90.0,    # 磁盘使用率阈值
            'api_response_time': 10.0,  # API响应时间阈值
            'display_update_time': 5.0  # 显示更新时间阈值
        }
        self.alerts = []
        self.monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
    
    def set_threshold(self, metric: str, threshold: float):
        """设置告警阈值"""
        if metric in self.thresholds:
            self.thresholds[metric] = threshold
    
    def start_monitoring(self):
        """开始性能监控"""
        if not self.monitoring:
            self.monitoring = True
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()
            logger.info("性能监控已启动")
    
    def stop_monitoring(self):
        """停止性能监控"""
        self.monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("性能监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                # 检查系统资源
                system_metrics = _performance_metrics.get_system_metrics()
                
                # 检查内存使用率
                if system_metrics['memory_usage'] > self.thresholds['memory_usage']:
                    self._add_alert('memory_usage', system_metrics['memory_usage'], 
                                  f"内存使用率过高: {system_metrics['memory_usage']:.1f}%")
                
                # 检查CPU使用率
                if system_metrics['cpu_usage'] > self.thresholds['cpu_usage']:
                    self._add_alert('cpu_usage', system_metrics['cpu_usage'],
                                  f"CPU使用率过高: {system_metrics['cpu_usage']:.1f}%")
                
                # 检查磁盘使用率
                if system_metrics['disk_usage'] > self.thresholds['disk_usage']:
                    self._add_alert('disk_usage', system_metrics['disk_usage'],
                                  f"磁盘使用率过高: {system_metrics['disk_usage']:.1f}%")
                
                # 检查API响应时间
                recent_api_times = _performance_metrics.metrics.get('api_response_time', [])[-5:]
                if recent_api_times:
                    avg_api_time = sum(v['value'] for v in recent_api_times) / len(recent_api_times)
                    if avg_api_time > self.thresholds['api_response_time']:
                        self._add_alert('api_response_time', avg_api_time,
                                      f"API响应时间过慢: {avg_api_time:.1f}s")
                
                # 检查显示更新时间
                recent_display_times = _performance_metrics.metrics.get('display_update_time', [])[-5:]
                if recent_display_times:
                    avg_display_time = sum(v['value'] for v in recent_display_times) / len(recent_display_times)
                    if avg_display_time > self.thresholds['display_update_time']:
                        self._add_alert('display_update_time', avg_display_time,
                                      f"显示更新时间过慢: {avg_display_time:.1f}s")
            
            except Exception as e:
                logger.error(f"监控循环出错: {e}")
            
            # 等待下次检查
            time.sleep(self.check_interval)
    
    def _add_alert(self, metric: str, value: float, message: str):
        """添加告警"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'metric': metric,
            'value': value,
            'message': message,
            'threshold': self.thresholds[metric]
        }
        
        self.alerts.append(alert)
        logger.warning(f"性能告警: {message}")
        
        # 限制告警数量
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-50:]
    
    def get_alerts(self, limit: int = 10) -> list:
        """获取最近的告警"""
        return self.alerts[-limit:] if self.alerts else []
    
    def get_performance_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        summary = _performance_metrics.get_metrics_summary()
        alerts = self.get_alerts(limit=5)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'uptime': summary['uptime'],
            'system_status': summary['system'],
            'performance_averages': summary['averages'],
            'recent_alerts': alerts,
            'alert_count': len(alerts),
            'status': self._get_overall_status(summary['system'])
        }
    
    def _get_overall_status(self, system_metrics: Dict[str, float]) -> str:
        """获取整体状态"""
        if system_metrics['memory_usage'] > 90 or system_metrics['cpu_usage'] > 85:
            return 'critical'
        elif system_metrics['memory_usage'] > 80 or system_metrics['cpu_usage'] > 70:
            return 'warning'
        else:
            return 'normal'


# 全局性能监控器实例
_performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """获取全局性能监控器实例"""
    return _performance_monitor


# 便捷装饰器
api_performance = measure_time('api_response_time')
display_performance = measure_time('display_update_time')
cache_performance = measure_time('cache_operation_time')


# 使用示例
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 示例函数
    @api_performance
    def simulate_api_call():
        """模拟API调用"""
        time.sleep(0.5)  # 模拟网络延迟
        return {"data": "test"}
    
    @display_performance
    def simulate_display_update():
        """模拟显示更新"""
        time.sleep(0.3)  # 模拟处理时间
        return True
    
    # 测试性能监控
    monitor = get_performance_monitor()
    monitor.start_monitoring()
    
    print("开始性能监控测试...")
    
    # 模拟一些操作
    for i in range(3):
        simulate_api_call()
        simulate_display_update()
        time.sleep(1)
    
    # 获取性能报告
    report = monitor.get_performance_report()
    
    print("\n" + "="*50)
    print("性能监控报告")
    print("="*50)
    print(f"系统状态: {report['status']}")
    print(f"运行时间: {report['uptime']:.1f}秒")
    print(f"内存使用率: {report['system_status']['memory_usage']:.1f}%")
    print(f"CPU使用率: {report['system_status']['cpu_usage']:.1f}%")
    print(f"告警数量: {report['alert_count']}")
    
    if report['performance_averages']:
        print("\n性能指标:")
        for key, value in report['performance_averages'].items():
            print(f"  {key}: {value:.3f}")
    
    # 停止监控
    monitor.stop_monitoring()
    
    print("\n✅ 性能监控测试完成!")