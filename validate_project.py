#!/usr/bin/env python3
"""
项目完整性验证脚本
Project Integrity Validation Script

验证整个每日单词系统的完整性和准备状态
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class ProjectValidator:
    """项目验证器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0
    
    def check_file_exists(self, file_path: str, required: bool = True) -> bool:
        """检查文件是否存在"""
        self.total_checks += 1
        full_path = self.project_root / file_path
        
        if full_path.exists():
            self.success_count += 1
            print(f"✅ {file_path}")
            return True
        else:
            if required:
                self.errors.append(f"缺少必需文件: {file_path}")
                print(f"❌ {file_path} (必需)")
            else:
                self.warnings.append(f"缺少可选文件: {file_path}")
                print(f"⚠️ {file_path} (可选)")
            return False
    
    def check_directory_exists(self, dir_path: str, required: bool = True) -> bool:
        """检查目录是否存在"""
        self.total_checks += 1
        full_path = self.project_root / dir_path
        
        if full_path.exists() and full_path.is_dir():
            self.success_count += 1
            print(f"✅ {dir_path}/")
            return True
        else:
            if required:
                self.errors.append(f"缺少必需目录: {dir_path}")
                print(f"❌ {dir_path}/ (必需)")
            else:
                self.warnings.append(f"缺少可选目录: {dir_path}")
                print(f"⚠️ {dir_path}/ (可选)")
            return False
    
    def check_file_content(self, file_path: str, min_size: int = 100) -> bool:
        """检查文件内容是否充实"""
        self.total_checks += 1
        full_path = self.project_root / file_path
        
        if not full_path.exists():
            self.errors.append(f"文件不存在: {file_path}")
            print(f"❌ {file_path} (不存在)")
            return False
        
        try:
            size = full_path.stat().st_size
            if size >= min_size:
                self.success_count += 1
                print(f"✅ {file_path} ({size} bytes)")
                return True
            else:
                self.warnings.append(f"文件内容过少: {file_path} ({size} bytes)")
                print(f"⚠️ {file_path} ({size} bytes, 内容较少)")
                return False
        except Exception as e:
            self.errors.append(f"无法读取文件: {file_path} - {e}")
            print(f"❌ {file_path} (读取失败)")
            return False
    
    def validate_core_files(self):
        """验证核心代码文件"""
        print("\n🔧 验证核心代码文件")
        print("=" * 50)
        
        core_files = [
            "src/daily_word_config.py",
            "src/daily_word_api_client.py", 
            "src/daily_word_display_controller.py",
            "src/daily_word_main.py",
            "src/daily_word_test.py"
        ]
        
        for file_path in core_files:
            self.check_file_content(file_path, 1000)
    
    def validate_deployment_tools(self):
        """验证部署工具"""
        print("\n🛠️ 验证部署工具")
        print("=" * 50)
        
        deployment_files = [
            "install_daily_word.sh",
            "daily_word_service.py"
        ]
        
        for file_path in deployment_files:
            self.check_file_content(file_path, 500)
    
    def validate_documentation(self):
        """验证文档文件"""
        print("\n📚 验证文档文件")
        print("=" * 50)
        
        # 检查文档目录
        self.check_directory_exists("docs")
        self.check_directory_exists("docs/installation-guide")
        self.check_directory_exists("docs/user-manual")
        self.check_directory_exists("docs/api-reference")
        self.check_directory_exists("docs/assets/scripts")
        
        # 检查文档文件
        doc_files = [
            "docs/README.md",
            "docs/installation-guide/README.md",
            "docs/installation-guide/01-system-requirements.md",
            "docs/installation-guide/02-hardware-setup.md",
            "docs/installation-guide/03-software-installation.md",
            "docs/installation-guide/04-configuration.md",
            "docs/installation-guide/05-deployment.md",
            "docs/installation-guide/06-maintenance.md",
            "docs/installation-guide/07-troubleshooting.md",
            "docs/user-manual/user-guide.md",
            "docs/api-reference/api-documentation.md",
            "docs/assets/scripts/install.sh",
            "docs/assets/scripts/manage.sh"
        ]
        
        for file_path in doc_files:
            self.check_file_content(file_path, 500)
    
    def validate_project_files(self):
        """验证项目文件"""
        print("\n📋 验证项目文件")
        print("=" * 50)
        
        project_files = [
            "README.md",
            "PROJECT_STRUCTURE.md",
            "DEPLOYMENT_CHECKLIST.md",
            "RELEASE_NOTES.md",
            "COMPLETION_SUMMARY.md",
            "FINAL_DELIVERY.md"
        ]
        
        for file_path in project_files:
            self.check_file_content(file_path, 500)
    
    def validate_python_syntax(self):
        """验证Python语法"""
        print("\n🐍 验证Python语法")
        print("=" * 50)
        
        python_files = [
            "src/daily_word_config.py",
            "src/daily_word_api_client.py",
            "src/daily_word_display_controller.py", 
            "src/daily_word_main.py",
            "src/daily_word_test.py",
            "daily_word_service.py"
        ]
        
        for file_path in python_files:
            self.total_checks += 1
            full_path = self.project_root / file_path
            
            if not full_path.exists():
                self.errors.append(f"Python文件不存在: {file_path}")
                print(f"❌ {file_path} (不存在)")
                continue
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 简单的语法检查
                compile(content, str(full_path), 'exec')
                self.success_count += 1
                print(f"✅ {file_path} (语法正确)")
                
            except SyntaxError as e:
                self.errors.append(f"Python语法错误: {file_path} - {e}")
                print(f"❌ {file_path} (语法错误: {e})")
            except Exception as e:
                self.warnings.append(f"Python文件检查失败: {file_path} - {e}")
                print(f"⚠️ {file_path} (检查失败: {e})")
    
    def validate_executable_permissions(self):
        """验证可执行权限"""
        print("\n🔐 验证可执行权限")
        print("=" * 50)
        
        executable_files = [
            "install_daily_word.sh",
            "src/daily_word_main.py",
            "src/daily_word_test.py",
            "daily_word_service.py"
        ]
        
        for file_path in executable_files:
            self.total_checks += 1
            full_path = self.project_root / file_path
            
            if not full_path.exists():
                print(f"❌ {file_path} (不存在)")
                continue
            
            # 检查是否有执行权限或shebang
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                
                if first_line.startswith('#!'):
                    self.success_count += 1
                    print(f"✅ {file_path} (有shebang)")
                else:
                    self.warnings.append(f"缺少shebang: {file_path}")
                    print(f"⚠️ {file_path} (缺少shebang)")
                    
            except Exception as e:
                self.warnings.append(f"无法检查文件: {file_path} - {e}")
                print(f"⚠️ {file_path} (检查失败)")
    
    def run_system_test(self):
        """运行系统测试"""
        print("\n🧪 运行系统测试")
        print("=" * 50)
        
        test_script = self.project_root / "src" / "daily_word_test_simple.py"
        
        if not test_script.exists():
            self.errors.append("测试脚本不存在")
            print("❌ 测试脚本不存在")
            return False
        
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, str(test_script)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.success_count += 1
                print("✅ 系统测试通过")
                return True
            else:
                self.errors.append(f"系统测试失败: {result.stderr}")
                print("❌ 系统测试失败")
                print(result.stdout)
                print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            self.errors.append("系统测试超时")
            print("❌ 系统测试超时")
            return False
        except Exception as e:
            self.errors.append(f"无法运行系统测试: {e}")
            print(f"❌ 无法运行系统测试: {e}")
            return False
    
    def generate_report(self):
        """生成验证报告"""
        print("\n" + "=" * 60)
        print("📊 项目验证报告")
        print("=" * 60)
        
        # 统计信息
        success_rate = (self.success_count / self.total_checks * 100) if self.total_checks > 0 else 0
        
        print(f"总检查项: {self.total_checks}")
        print(f"通过项目: {self.success_count}")
        print(f"成功率: {success_rate:.1f}%")
        print(f"错误数量: {len(self.errors)}")
        print(f"警告数量: {len(self.warnings)}")
        
        # 错误列表
        if self.errors:
            print(f"\n❌ 错误列表 ({len(self.errors)}项):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        # 警告列表
        if self.warnings:
            print(f"\n⚠️ 警告列表 ({len(self.warnings)}项):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        # 总结
        print(f"\n{'=' * 60}")
        if len(self.errors) == 0:
            if len(self.warnings) == 0:
                print("🎉 项目验证完全通过！系统准备就绪。")
                return True
            else:
                print("✅ 项目验证基本通过，有少量警告。")
                return True
        else:
            print("❌ 项目验证失败，存在错误需要修复。")
            return False
    
    def run_full_validation(self):
        """运行完整验证"""
        print("🔍 开始项目完整性验证...")
        print("=" * 60)
        
        # 运行各项验证
        self.validate_core_files()
        self.validate_deployment_tools()
        self.validate_documentation()
        self.validate_project_files()
        self.validate_python_syntax()
        self.validate_executable_permissions()
        
        # 运行系统测试（可选）
        try:
            self.run_system_test()
        except Exception as e:
            self.warnings.append(f"系统测试跳过: {e}")
            print(f"⚠️ 系统测试跳过: {e}")
        
        # 生成报告
        return self.generate_report()

def main():
    """主函数"""
    print("🚀 每日单词墨水屏显示系统 - 项目验证")
    print("=" * 60)
    
    validator = ProjectValidator()
    success = validator.run_full_validation()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())