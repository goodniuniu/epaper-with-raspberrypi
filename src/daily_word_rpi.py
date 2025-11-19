#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
树莓派每日单词显示主程序
"""

import sys
import time
import logging
import signal
import json
from pathlib import Path
from datetime import datetime, time as dt_time

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from class_word_api import WordAPI
from epaper_display_rpi import EPaperDisplay
from word_config_rpi import (
    WORD_API_CONFIG, DISPLAY_CONFIG, DATA_CONFIG, 
    SYSTEM_CONFIG, check_environment, get_system_info
)

class DailyWordRPi:
    """树莓派每日单词显示控制器"""
    
    def __init__(self):
        """初始化控制器"""
        self.setup_logging()
        self.word_api = WordAPI()
        self.display = None
        self.running = True
        
        # 检查环境
        self._check_environment()
        
        # 初始化显示器
        self._init_display()
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def setup_logging(self):
        """设置日志"""
        log_file = DATA_CONFIG['data_dir'] / DATA_CONFIG['log_file']
        
        # 创建日志目录
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 配置日志
        logging.basicConfig(
            level=getattr(logging, DATA_CONFIG['log_level']),
            format=DATA_CONFIG['log_format'],
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        logging.info("=== 每日单词系统启动 ===")
    
    def _check_environment(self):
        """检查运行环境"""
        issues = check_environment()
        for issue in issues:
            if issue.startswith("Error"):
                logging.error(issue)
            else:
                logging.warning(issue)
        
        # 显示系统信息
        sys_info = get_system_info()
        if sys_info.get('cpu_temperature'):
            logging.info(f"CPU温度: {sys_info['cpu_temperature']:.1f}°C")
        
        if sys_info.get('memory_available'):
            mem_mb = sys_info['memory_available'] / 1024 / 1024
            logging.info(f"可用内存: {mem_mb:.1f}MB")
    
    def _init_display(self):
        """初始化显示器"""
        try:
            self.display = EPaperDisplay(DISPLAY_CONFIG['epd_type'])
            logging.info("墨水屏显示器初始化成功")
        except Exception as e:
            logging.error(f"墨水屏显示器初始化失败: {e}")
            self.display = None
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        logging.info(f"收到信号 {signum}，准备退出...")
        self.running = False
    
    def update_display(self):
        """更新显示内容"""
        try:
            logging.info("开始更新每日单词显示...")
            
            # 检查系统状态
            sys_info = get_system_info()
            if sys_info.get('cpu_temperature', 0) > SYSTEM_CONFIG['max_temperature']:
                logging.warning(f"CPU温度过高: {sys_info['cpu_temperature']:.1f}°C")
                return False
            
            # 获取每日内容
            success = self.word_api.get_daily_content()
            if not success:
                logging.error("获取每日内容失败")
                return False
            
            # 准备显示数据
            word_data = {
                'word': self.word_api.word,
                'definition': self.word_api.word_definition,
                'pronunciation': self.word_api.word_pronunciation,
                'example': self.word_api.word_example
            }
            
            sentence_data = {
                'sentence': self.word_api.sentence,
                'author': self.word_api.sentence_author,
                'tags': self.word_api.sentence_tags
            }
            
            # 显示到墨水屏
            if self.display:
                success = self.display.display_content(word_data, sentence_data)
                if success:
                    logging.info("成功更新墨水屏显示")
                    return True
                else:
                    logging.error("墨水屏显示失败")
            else:
                # 如果没有墨水屏，输出到控制台
                self._console_display(word_data, sentence_data)
                return True
            
        except Exception as e:
            logging.error(f"更新显示时出错: {e}")
            return False
        
        return False
    
    def _console_display(self, word_data, sentence_data):
        """控制台显示（用于调试）"""
        print("\n" + "="*60)
        print("每日单词显示内容:")
        print("="*60)
        
        if word_data.get('word'):
            print(f"📚 单词: {word_data['word'].upper()}")
            if word_data.get('pronunciation'):
                print(f"   发音: {word_data['pronunciation']}")
            if word_data.get('definition'):
                print(f"   定义: {word_data['definition']}")
            if word_data.get('example'):
                print(f"   例句: {word_data['example']}")
            print()
        
        if sentence_data.get('sentence'):
            print(f"💭 每日一句: \"{sentence_data['sentence']}\"")
            if sentence_data.get('author'):
                print(f"   — {sentence_data['author']}")
            print()
        
        print(f"📅 日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*60)
    
    def run_once(self):
        """运行一次更新"""
        return self.update_display()
    
    def run_daemon(self):
        """以守护进程模式运行"""
        logging.info("启动守护进程模式")
        
        # 写入PID文件
        pid_file = DATA_CONFIG['data_dir'] / DATA_CONFIG['pid_file']
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))
        
        last_update = None
        update_times = [dt_time.fromisoformat(t) for t in SYSTEM_CONFIG['update_times']]
        
        try:
            while self.running:
                now = datetime.now()
                current_time = now.time()
                
                # 检查是否到了更新时间
                should_update = False
                for update_time in update_times:
                    if (current_time >= update_time and 
                        (last_update is None or 
                         last_update.date() < now.date() or
                         last_update.time() < update_time)):
                        should_update = True
                        break
                
                if should_update:
                    if self.update_display():
                        last_update = now
                    else:
                        logging.error("更新失败，将在下次尝试")
                
                # 休眠一分钟后再检查
                time.sleep(60)
                
        except KeyboardInterrupt:
            logging.info("收到中断信号，退出守护进程")
        finally:
            # 清理PID文件
            if pid_file.exists():
                pid_file.unlink()
            
            # 墨水屏进入睡眠
            if self.display:
                self.display.sleep()
    
    def run_scheduled(self):
        """定时运行模式（适合cron）"""
        logging.info("运行定时更新")
        success = self.update_display()
        
        if self.display and SYSTEM_CONFIG.get('sleep_between_updates', True):
            # 更新后让墨水屏进入睡眠模式以节省电力
            time.sleep(2)  # 等待显示完成
            self.display.sleep()
        
        return success


def main():
    """主函数"""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='树莓派每日单词显示系统')
    parser.add_argument('--mode', choices=['once', 'daemon', 'scheduled'], 
                       default='once', help='运行模式')
    parser.add_argument('--test', action='store_true', help='测试模式')
    parser.add_argument('--clear', action='store_true', help='清空显示')
    
    args = parser.parse_args()
    
    try:
        app = DailyWordRPi()
        
        if args.clear:
            if app.display:
                app.display.clear_display()
                logging.info("显示已清空")
            return 0
        
        if args.test:
            logging.info("运行测试模式")
            return 0 if app.run_once() else 1
        
        if args.mode == 'once':
            return 0 if app.run_once() else 1
        elif args.mode == 'daemon':
            app.run_daemon()
            return 0
        elif args.mode == 'scheduled':
            return 0 if app.run_scheduled() else 1
            
    except Exception as e:
        logging.error(f"程序运行出错: {e}")
        return 1


if __name__ == "__main__":
    exit(main())