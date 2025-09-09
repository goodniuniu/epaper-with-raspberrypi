#!/usr/bin/env python3
"""
每日单词系统服务管理器
Daily Word System Service Manager

提供简单的服务管理功能
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# 服务配置
SERVICE_CONFIG = {
    'name': 'daily-word',
    'description': '每日单词墨水屏显示系统',
    'install_dir': '/opt/daily-word-epaper',
    'user': 'pi',
    'python_path': '/opt/daily-word-epaper/venv/bin/python',
    'main_script': '/opt/daily-word-epaper/src/daily_word_main.py'
}

class ServiceManager:
    """服务管理器"""
    
    def __init__(self):
        self.service_name = SERVICE_CONFIG['name']
        self.install_dir = Path(SERVICE_CONFIG['install_dir'])
        
    def run_command(self, command, check=True, capture_output=True):
        """运行系统命令"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=check,
                capture_output=capture_output,
                text=True
            )
            return result
        except subprocess.CalledProcessError as e:
            print(f"命令执行失败: {command}")
            print(f"错误: {e}")
            return None
    
    def is_service_exists(self):
        """检查服务是否存在"""
        result = self.run_command(f"systemctl list-unit-files | grep {self.service_name}")
        return result is not None and result.returncode == 0
    
    def is_service_running(self):
        """检查服务是否运行"""
        result = self.run_command(f"systemctl is-active {self.service_name}")
        return result is not None and result.stdout.strip() == "active"
    
    def is_service_enabled(self):
        """检查服务是否启用"""
        result = self.run_command(f"systemctl is-enabled {self.service_name}")
        return result is not None and result.stdout.strip() == "enabled"
    
    def start_service(self):
        """启动服务"""
        print(f"启动服务 {self.service_name}...")
        result = self.run_command(f"sudo systemctl start {self.service_name}")
        
        if result and result.returncode == 0:
            print("✅ 服务启动成功")
            return True
        else:
            print("❌ 服务启动失败")
            return False
    
    def stop_service(self):
        """停止服务"""
        print(f"停止服务 {self.service_name}...")
        result = self.run_command(f"sudo systemctl stop {self.service_name}")
        
        if result and result.returncode == 0:
            print("✅ 服务停止成功")
            return True
        else:
            print("❌ 服务停止失败")
            return False
    
    def restart_service(self):
        """重启服务"""
        print(f"重启服务 {self.service_name}...")
        result = self.run_command(f"sudo systemctl restart {self.service_name}")
        
        if result and result.returncode == 0:
            print("✅ 服务重启成功")
            return True
        else:
            print("❌ 服务重启失败")
            return False
    
    def enable_service(self):
        """启用服务（开机自启）"""
        print(f"启用服务 {self.service_name}...")
        result = self.run_command(f"sudo systemctl enable {self.service_name}")
        
        if result and result.returncode == 0:
            print("✅ 服务启用成功")
            return True
        else:
            print("❌ 服务启用失败")
            return False
    
    def disable_service(self):
        """禁用服务"""
        print(f"禁用服务 {self.service_name}...")
        result = self.run_command(f"sudo systemctl disable {self.service_name}")
        
        if result and result.returncode == 0:
            print("✅ 服务禁用成功")
            return True
        else:
            print("❌ 服务禁用失败")
            return False
    
    def get_service_status(self):
        """获取服务状态"""
        status_info = {
            'exists': self.is_service_exists(),
            'running': False,
            'enabled': False,
            'details': None
        }
        
        if status_info['exists']:
            status_info['running'] = self.is_service_running()
            status_info['enabled'] = self.is_service_enabled()
            
            # 获取详细状态
            result = self.run_command(f"systemctl status {self.service_name}")
            if result:
                status_info['details'] = result.stdout
        
        return status_info
    
    def show_service_status(self):
        """显示服务状态"""
        print(f"📊 服务状态: {self.service_name}")
        print("=" * 50)
        
        status = self.get_service_status()
        
        if not status['exists']:
            print("❌ 服务不存在")
            return False
        
        print(f"存在: ✅")
        print(f"运行: {'✅' if status['running'] else '❌'}")
        print(f"启用: {'✅' if status['enabled'] else '❌'}")
        
        if status['details']:
            print("\n详细信息:")
            print(status['details'])
        
        return True
    
    def show_service_logs(self, lines=50, follow=False):
        """显示服务日志"""
        print(f"📋 服务日志: {self.service_name}")
        print("=" * 50)
        
        cmd = f"sudo journalctl -u {self.service_name} -n {lines}"
        if follow:
            cmd += " -f"
        
        # 直接运行，不捕获输出
        self.run_command(cmd, capture_output=False)
    
    def test_system(self):
        """测试系统"""
        print("🧪 测试系统功能...")
        
        test_script = self.install_dir / "src" / "daily_word_test.py"
        if not test_script.exists():
            print("❌ 测试脚本不存在")
            return False
        
        python_path = SERVICE_CONFIG['python_path']
        result = self.run_command(f"{python_path} {test_script}")
        
        if result and result.returncode == 0:
            print("✅ 系统测试通过")
            return True
        else:
            print("❌ 系统测试失败")
            if result:
                print(result.stdout)
                print(result.stderr)
            return False
    
    def update_display(self, force=False):
        """更新显示"""
        print("🔄 更新显示内容...")
        
        python_path = SERVICE_CONFIG['python_path']
        main_script = SERVICE_CONFIG['main_script']
        
        cmd = f"{python_path} {main_script}"
        if force:
            cmd += " --force"
        
        result = self.run_command(cmd)
        
        if result and result.returncode == 0:
            print("✅ 显示更新成功")
            return True
        else:
            print("❌ 显示更新失败")
            if result:
                print(result.stdout)
                print(result.stderr)
            return False
    
    def clear_display(self):
        """清空显示"""
        print("🧹 清空显示...")
        
        python_path = SERVICE_CONFIG['python_path']
        main_script = SERVICE_CONFIG['main_script']
        
        result = self.run_command(f"{python_path} {main_script} --clear")
        
        if result and result.returncode == 0:
            print("✅ 显示清空成功")
            return True
        else:
            print("❌ 显示清空失败")
            if result:
                print(result.stdout)
                print(result.stderr)
            return False
    
    def get_system_info(self):
        """获取系统信息"""
        info = {
            'timestamp': datetime.now().isoformat(),
            'service': self.get_service_status(),
            'system': {},
            'files': {}
        }
        
        # 系统信息
        try:
            result = self.run_command("uname -a")
            if result:
                info['system']['uname'] = result.stdout.strip()
        except:
            pass
        
        try:
            result = self.run_command("python3 --version")
            if result:
                info['system']['python'] = result.stdout.strip()
        except:
            pass
        
        # 文件信息
        important_files = [
            'src/daily_word_main.py',
            'src/daily_word_config.py',
            'src/daily_word_api_client.py',
            'src/daily_word_display_controller.py'
        ]
        
        for file_path in important_files:
            full_path = self.install_dir / file_path
            info['files'][file_path] = {
                'exists': full_path.exists(),
                'size': full_path.stat().st_size if full_path.exists() else 0
            }
        
        return info
    
    def show_system_info(self):
        """显示系统信息"""
        print("ℹ️ 系统信息")
        print("=" * 50)
        
        info = self.get_system_info()
        
        print(f"时间: {info['timestamp']}")
        print(f"系统: {info['system'].get('uname', '未知')}")
        print(f"Python: {info['system'].get('python', '未知')}")
        
        print("\n📁 文件状态:")
        for file_path, file_info in info['files'].items():
            status = "✅" if file_info['exists'] else "❌"
            size = f"({file_info['size']} bytes)" if file_info['exists'] else ""
            print(f"  {status} {file_path} {size}")
        
        print(f"\n🔧 服务状态:")
        service_status = info['service']
        print(f"  存在: {'✅' if service_status['exists'] else '❌'}")
        print(f"  运行: {'✅' if service_status['running'] else '❌'}")
        print(f"  启用: {'✅' if service_status['enabled'] else '❌'}")

def create_argument_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="每日单词系统服务管理器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s start          # 启动服务
  %(prog)s stop           # 停止服务
  %(prog)s restart        # 重启服务
  %(prog)s status         # 查看状态
  %(prog)s logs           # 查看日志
  %(prog)s test           # 测试系统
  %(prog)s update         # 更新显示
  %(prog)s clear          # 清空显示
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 服务控制命令
    subparsers.add_parser('start', help='启动服务')
    subparsers.add_parser('stop', help='停止服务')
    subparsers.add_parser('restart', help='重启服务')
    subparsers.add_parser('enable', help='启用服务（开机自启）')
    subparsers.add_parser('disable', help='禁用服务')
    subparsers.add_parser('status', help='查看服务状态')
    
    # 日志命令
    logs_parser = subparsers.add_parser('logs', help='查看服务日志')
    logs_parser.add_argument('-n', '--lines', type=int, default=50, help='显示行数')
    logs_parser.add_argument('-f', '--follow', action='store_true', help='实时跟踪日志')
    
    # 系统命令
    subparsers.add_parser('test', help='测试系统功能')
    subparsers.add_parser('info', help='显示系统信息')
    
    # 显示命令
    update_parser = subparsers.add_parser('update', help='更新显示内容')
    update_parser.add_argument('-f', '--force', action='store_true', help='强制获取新内容')
    subparsers.add_parser('clear', help='清空显示')
    
    return parser

def main():
    """主函数"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    manager = ServiceManager()
    
    try:
        if args.command == 'start':
            success = manager.start_service()
        elif args.command == 'stop':
            success = manager.stop_service()
        elif args.command == 'restart':
            success = manager.restart_service()
        elif args.command == 'enable':
            success = manager.enable_service()
        elif args.command == 'disable':
            success = manager.disable_service()
        elif args.command == 'status':
            success = manager.show_service_status()
        elif args.command == 'logs':
            manager.show_service_logs(lines=args.lines, follow=args.follow)
            success = True
        elif args.command == 'test':
            success = manager.test_system()
        elif args.command == 'info':
            manager.show_system_info()
            success = True
        elif args.command == 'update':
            success = manager.update_display(force=args.force)
        elif args.command == 'clear':
            success = manager.clear_display()
        else:
            print(f"未知命令: {args.command}")
            success = False
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n用户中断操作")
        return 130
    except Exception as e:
        print(f"执行失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())