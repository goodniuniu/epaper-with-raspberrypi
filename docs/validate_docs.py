#!/usr/bin/env python3
"""
文档完整性验证脚本
验证所有必要的文档文件是否已正确创建
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - 文件不存在")
        return False

def check_file_content(file_path, min_size=100):
    """检查文件内容是否充实"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if len(content) >= min_size:
                print(f"✅ 内容检查通过: {file_path} ({len(content)} 字符)")
                return True
            else:
                print(f"⚠️  内容过少: {file_path} ({len(content)} 字符)")
                return False
    except Exception as e:
        print(f"❌ 读取失败: {file_path} - {e}")
        return False

def main():
    """主验证函数"""
    print("🔍 开始验证文档完整性...")
    print("=" * 60)
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # 需要验证的文件列表
    required_files = [
        # 主要文档
        ("README.md", "项目主页说明"),
        ("PROJECT_STRUCTURE.md", "项目结构说明"),
        
        # 安装指南
        ("docs/README.md", "文档总览"),
        ("docs/installation-guide/README.md", "安装指南总览"),
        ("docs/installation-guide/01-system-requirements.md", "系统要求"),
        ("docs/installation-guide/02-hardware-setup.md", "硬件设置"),
        ("docs/installation-guide/03-software-installation.md", "软件安装"),
        ("docs/installation-guide/04-configuration.md", "系统配置"),
        ("docs/installation-guide/05-deployment.md", "部署运行"),
        ("docs/installation-guide/06-maintenance.md", "维护管理"),
        ("docs/installation-guide/07-troubleshooting.md", "故障排除"),
        
        # 用户手册
        ("docs/user-manual/user-guide.md", "用户指南"),
        
        # API参考
        ("docs/api-reference/api-documentation.md", "API文档"),
        
        # 安装脚本
        ("docs/assets/scripts/install.sh", "自动安装脚本"),
        ("docs/assets/scripts/manage.sh", "管理脚本"),
    ]
    
    # 验证文件存在性
    print("\n📋 检查文件存在性:")
    print("-" * 40)
    missing_files = []
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            missing_files.append(file_path)
    
    # 验证文件内容
    print("\n📄 检查文件内容:")
    print("-" * 40)
    empty_files = []
    for file_path, description in required_files:
        if os.path.exists(file_path):
            if not check_file_content(file_path, min_size=500):
                empty_files.append(file_path)
    
    # 验证目录结构
    print("\n📁 检查目录结构:")
    print("-" * 40)
    required_dirs = [
        "docs/installation-guide",
        "docs/user-manual", 
        "docs/api-reference",
        "docs/assets/scripts",
        "src"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ 目录存在: {dir_path}")
        else:
            print(f"❌ 目录缺失: {dir_path}")
            missing_dirs.append(dir_path)
    
    # 生成验证报告
    print("\n" + "=" * 60)
    print("📊 验证报告:")
    print("=" * 60)
    
    total_files = len(required_files)
    missing_count = len(missing_files)
    empty_count = len(empty_files)
    missing_dir_count = len(missing_dirs)
    
    print(f"📄 文件统计:")
    print(f"   - 总文件数: {total_files}")
    print(f"   - 存在文件: {total_files - missing_count}")
    print(f"   - 缺失文件: {missing_count}")
    print(f"   - 内容不足: {empty_count}")
    
    print(f"\n📁 目录统计:")
    print(f"   - 总目录数: {len(required_dirs)}")
    print(f"   - 存在目录: {len(required_dirs) - missing_dir_count}")
    print(f"   - 缺失目录: {missing_dir_count}")
    
    # 总体评估
    if missing_count == 0 and missing_dir_count == 0:
        if empty_count == 0:
            print(f"\n🎉 验证通过! 所有文档都已正确创建且内容充实。")
            return 0
        else:
            print(f"\n⚠️  基本通过，但有 {empty_count} 个文件内容不足。")
            return 1
    else:
        print(f"\n❌ 验证失败! 有 {missing_count} 个文件和 {missing_dir_count} 个目录缺失。")
        
        if missing_files:
            print(f"\n缺失文件:")
            for file_path in missing_files:
                print(f"   - {file_path}")
        
        if missing_dirs:
            print(f"\n缺失目录:")
            for dir_path in missing_dirs:
                print(f"   - {dir_path}")
        
        return 2

if __name__ == "__main__":
    sys.exit(main())