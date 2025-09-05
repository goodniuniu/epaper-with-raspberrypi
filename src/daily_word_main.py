#!/usr/bin/env python3
"""
每日单词墨水屏显示系统 - 主程序
Daily Word E-Paper Display System - Main Program

系统主入口，协调API客户端和显示控制器
"""

import argparse
import logging
import signal
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from daily_word_config import (
    PROJECT_NAME, PROJECT_VERSION, LOGGING_CONFIG, UPDATE_CONFIG,
    FEATURE_FLAGS, DEBUG_CONFIG, DATA_DIR, LOGS_DIR
)
from daily_word_api_client import DailyWordAPIClient

# 尝试导入新的显示控制器，如果失败则使用原来的
try:
    from daily_word_epaper_controller import DailyWordEPaperController as DisplayController
    DISPLAY_TYPE = "epaper"
except ImportError:
    try:
        from daily_word_display_epaper import DailyWordEPaperDisplay as DisplayController
        DISPLAY_TYPE = "epaper_old"
    except ImportError:
        from daily_word_display_controller import DailyWordDisplayController as DisplayController
        DISPLAY_TYPE = "original"

class DailyWordSystem:
    """每日单词系统主类"""
    
    def __init__(self):
        """初始化系统"""
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"初始化 {PROJECT_NAME} v{PROJECT_VERSION}")
        
        # 初始化组件
        self.api_client = None
        self.display_controller = None
        self.running = False
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            self.api_client = DailyWordAPIClient()
            self.display_controller = DisplayController()
            self.logger.info(f"系统组件初始化完成 (显示类型: {DISPLAY_TYPE})")
        except Exception as e:
            self.logger.error(f"系统初始化失败: {e}")
            raise
    
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
                    LOGS_DIR / LOGGING_CONFIG['log_files']['main'],
                    encoding=LOGGING_CONFIG['log_settings']['encoding']
                )
            ]
        )
        
        # 配置特定模块的日志
        api_logger = logging.getLogger('daily_word_api_client')
        api_handler = logging.FileHandler(
            LOGS_DIR / LOGGING_CONFIG['log_files']['api'],
            encoding=LOGGING_CONFIG['log_settings']['encoding']
        )
        api_handler.setFormatter(logging.Formatter(log_format, date_format))
        api_logger.addHandler(api_handler)
        
        display_logger = logging.getLogger('daily_word_display_controller')
        display_handler = logging.FileHandler(
            LOGS_DIR / LOGGING_CONFIG['log_files']['display'],
            encoding=LOGGING_CONFIG['log_settings']['encoding']
        )
        display_handler.setFormatter(logging.Formatter(log_format, date_format))
        display_logger.addHandler(display_handler)
        
        # 错误日志
        error_handler = logging.FileHandler(
            LOGS_DIR / LOGGING_CONFIG['log_files']['error'],
            encoding=LOGGING_CONFIG['log_settings']['encoding']
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(log_format, date_format))
        logging.getLogger().addHandler(error_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        self.logger.info(f"接收到信号 {signum}，准备退出...")
        self.running = False
    
    def update_display(self, force_new: bool = False) -> bool:
        """更新显示内容"""
        try:
            self.logger.info("开始更新显示内容...")
            
            # 获取内容
            content = self.api_client.get_daily_content(force_new=force_new)
            
            if not content or (not content.get('word') and not content.get('quote')):
                self.logger.warning("未获取到有效内容")
                return False
            
            # 显示内容
            if DISPLAY_TYPE in ["epaper", "epaper_old"]:
                self.display_controller.display_daily_content(content)
            else:
                self.display_controller.display_content(content)
            
            # 记录更新信息
            self._log_update_info(content)
            
            self.logger.info("显示内容更新完成")
            return True
            
        except Exception as e:
            self.logger.error(f"更新显示失败: {e}")
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
    
    def clear_display(self) -> bool:
        """清空显示"""
        try:
            self.logger.info("清空显示...")
            self.display_controller.clear_display()
            self.logger.info("显示已清空")
            return True
        except Exception as e:
            self.logger.error(f"清空显示失败: {e}")
            return False
    
    def test_system(self) -> bool:
        """测试系统功能"""
        self.logger.info("开始系统测试...")
        
        try:
            # 测试API客户端
            self.logger.info("测试API客户端...")
            test_content = self.api_client.get_daily_content(force_new=False)
            
            if not test_content:
                self.logger.error("API客户端测试失败")
                return False
            
            self.logger.info("API客户端测试通过")
            
            # 测试显示控制器
            self.logger.info("测试显示控制器...")
            if DISPLAY_TYPE in ["epaper", "epaper_old"]:
                self.display_controller.display_daily_content(test_content)
            else:
                self.display_controller.display_content(test_content)
            self.logger.info("显示控制器测试通过")
            
            self.logger.info("系统测试完成")
            return True
            
        except Exception as e:
            self.logger.error(f"系统测试失败: {e}")
            return False
    
    def run_scheduled_mode(self):
        """运行定时模式"""
        self.logger.info("启动定时更新模式...")
        self.running = True
        
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
                self.logger.error(f"定时模式运行错误: {e}")
                time.sleep(60)
        
        self.logger.info("定时更新模式已停止")
    
    def run_interval_mode(self):
        """运行间隔模式"""
        interval = UPDATE_CONFIG['interval']['update_interval']
        self.logger.info(f"启动间隔更新模式，间隔: {interval}秒")
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
                    self.logger.info("间隔更新触发")
                    self.update_display()
                
            except Exception as e:
                self.logger.error(f"间隔模式运行错误: {e}")
                time.sleep(60)
        
        self.logger.info("间隔更新模式已停止")
    
    def run_daemon_mode(self):
        """运行守护进程模式"""
        self.logger.info("启动守护进程模式...")
        
        # 根据配置选择运行模式
        mode = UPDATE_CONFIG['mode']
        
        if mode == 'scheduled':
            self.run_scheduled_mode()
        elif mode == 'interval':
            self.run_interval_mode()
        else:
            self.logger.error(f"未知的更新模式: {mode}")
            return False
        
        return True
    
    def get_system_status(self) -> Dict:
        """获取系统状态"""
        try:
            # 获取缓存统计
            cache_stats = self.api_client.get_cache_stats() if self.api_client else {}
            
            # 获取系统信息（包括IP地址）
            try:
                from word_config_rpi import get_system_info
                sys_info = get_system_info()
            except Exception as e:
                self.logger.warning(f"获取系统信息失败: {e}")
                sys_info = {}
            
            # 系统状态
            status = {
                'system': {
                    'name': PROJECT_NAME,
                    'version': PROJECT_VERSION,
                    'running': self.running,
                    'timestamp': datetime.now().isoformat(),
                    'ip_address': sys_info.get('ip_address'),
                    'cpu_temperature': sys_info.get('cpu_temperature'),
                },
                'components': {
                    'api_client': self.api_client is not None,
                    'display_controller': self.display_controller is not None,
                },
                'cache': cache_stats,
                'config': {
                    'update_mode': UPDATE_CONFIG['mode'],
                    'debug_mode': DEBUG_CONFIG['debug_mode'],
                    'features_enabled': sum(1 for v in FEATURE_FLAGS.values() if v),
                }
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"获取系统状态失败: {e}")
            return {'error': str(e)}
    
    def cleanup(self):
        """清理资源"""
        self.logger.info("清理系统资源...")
        
        try:
            if self.display_controller:
                self.display_controller.cleanup()
            
            if self.api_client:
                # API客户端清理旧缓存
                self.api_client.cleanup_old_cache()
            
            self.logger.info("系统资源清理完成")
            
        except Exception as e:
            self.logger.error(f"清理资源失败: {e}")

def create_argument_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description=f"{PROJECT_NAME} v{PROJECT_VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s                    # 更新一次显示内容
  %(prog)s --daemon           # 守护进程模式运行
  %(prog)s --clear            # 清空显示
  %(prog)s --test             # 测试系统功能
  %(prog)s --status           # 显示系统状态
  %(prog)s --force            # 强制获取新内容
        """
    )
    
    parser.add_argument(
        '--daemon', '-d',
        action='store_true',
        help='守护进程模式运行'
    )
    
    parser.add_argument(
        '--clear', '-c',
        action='store_true',
        help='清空显示'
    )
    
    parser.add_argument(
        '--test', '-t',
        action='store_true',
        help='测试系统功能'
    )
    
    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help='显示系统状态'
    )
    
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='强制获取新内容'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='详细输出'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'{PROJECT_NAME} v{PROJECT_VERSION}'
    )
    
    return parser

def main():
    """主函数"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # 设置详细输出
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # 创建系统实例
        system = DailyWordSystem()
        
        # 根据参数执行相应操作
        if args.clear:
            success = system.clear_display()
            sys.exit(0 if success else 1)
        
        elif args.test:
            success = system.test_system()
            sys.exit(0 if success else 1)
        
        elif args.status:
            status = system.get_system_status()
            print("系统状态:")
            print(f"  名称: {status['system']['name']}")
            print(f"  版本: {status['system']['version']}")
            print(f"  运行状态: {'运行中' if status['system']['running'] else '已停止'}")
            print(f"  时间戳: {status['system']['timestamp']}")
            print(f"  API客户端: {'正常' if status['components']['api_client'] else '异常'}")
            print(f"  显示控制器: {'正常' if status['components']['display_controller'] else '异常'}")
            print(f"  缓存统计: 单词 {status['cache'].get('word_cache_size', 0)} 条, 句子 {status['cache'].get('quote_cache_size', 0)} 条")
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
        print(f"程序执行失败: {e}")
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