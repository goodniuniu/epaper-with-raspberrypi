#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Windows环境测试脚本
Daily Word System Windows Test Script
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_basic_imports():
    """测试基本模块导入"""
    print("🔍 测试基本模块导入...")
    
    try:
        import requests
        print(f"[OK] requests模块导入成功 - 版本: {requests.__version__}")
    except Exception as e:
        print(f"[ERROR] requests模块导入失败: {e}")
        return False
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        print(f"[OK] PIL模块导入成功 - 版本: {Image.__version__}")
    except Exception as e:
        print(f"[ERROR] PIL模块导入失败: {e}")
        return False
    
    return True

def test_config_loading():
    """测试配置文件加载"""
    print("\n🔧 测试配置文件加载...")
    
    try:
        # 测试配置文件是否存在
        config_files = [
            "config.ini",
            "src/word_config.py",
            "src/daily_word_config.py"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                print(f"[OK] 配置文件存在: {config_file}")
            else:
                print(f"[WARNING] 配置文件不存在: {config_file}")
        
        # 尝试导入配置模块
        try:
            from daily_word_config import PROJECT_NAME, PROJECT_VERSION
            print(f"[OK] 配置模块导入成功 - {PROJECT_NAME} v{PROJECT_VERSION}")
        except Exception as e:
            print(f"[INFO] 配置模块导入失败（正常，可能需要树莓派环境）: {e}")
        
        return True
    except Exception as e:
        print(f"[ERROR] 配置加载失败: {e}")
        return False

def test_api_connection():
    """测试API连接"""
    print("\n🌐 测试API连接...")
    
    try:
        import requests
        
        # 测试基本网络连接
        test_urls = [
            "https://api.quotable.io/random",
            "https://httpbin.org/get"
        ]
        
        for url in test_urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"[OK] API连接成功: {url}")
                else:
                    print(f"[WARNING] API响应异常: {url} - 状态码: {response.status_code}")
            except Exception as e:
                print(f"[ERROR] API连接失败: {url} - {e}")
        
        return True
    except Exception as e:
        print(f"[ERROR] API测试失败: {e}")
        return False

def test_image_processing():
    """测试图像处理功能"""
    print("\n🎨 测试图像处理功能...")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # 创建测试图像
        width, height = 400, 300
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # 绘制测试文本
        text = "Daily Word Test"
        try:
            # 尝试使用系统字体
            font = ImageFont.load_default()
            draw.text((10, 10), text, fill='black', font=font)
            print("[OK] 文本绘制成功")
        except Exception as e:
            print(f"[WARNING] 字体加载失败，使用默认字体: {e}")
            draw.text((10, 10), text, fill='black')
        
        # 保存测试图像
        test_image_path = "test_output.png"
        image.save(test_image_path)
        print(f"[OK] 测试图像保存成功: {test_image_path}")
        
        # 清理测试文件
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
            print("[OK] 测试文件清理完成")
        
        return True
    except Exception as e:
        print(f"[ERROR] 图像处理测试失败: {e}")
        return False

def test_project_structure():
    """测试项目结构"""
    print("\n📁 测试项目结构...")
    
    required_dirs = [
        "src",
        "docs",
        "data",
        "example"
    ]
    
    required_files = [
        "README.md",
        "requirements.txt",
        "config.ini",
        "manage.sh"
    ]
    
    all_good = True
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"[OK] 目录存在: {directory}")
        else:
            print(f"[ERROR] 目录缺失: {directory}")
            all_good = False
    
    for file in required_files:
        if os.path.exists(file):
            print(f"[OK] 文件存在: {file}")
        else:
            print(f"[WARNING] 文件缺失: {file}")
    
    # 检查src目录中的Python文件
    src_dir = Path("src")
    if src_dir.exists():
        py_files = list(src_dir.glob("*.py"))
        print(f"[INFO] src目录包含 {len(py_files)} 个Python文件")
        
        key_files = [
            "daily_word_config.py",
            "daily_word_api_client.py",
            "daily_word_main.py"
        ]
        
        for key_file in key_files:
            if (src_dir / key_file).exists():
                print(f"[OK] 核心文件存在: src/{key_file}")
            else:
                print(f"[WARNING] 核心文件缺失: src/{key_file}")
    
    return all_good

def main():
    """主测试函数"""
    print("=" * 60)
    print("🚀 每日单词墨水屏系统 - Windows环境测试")
    print("=" * 60)
    
    tests = [
        ("基本模块导入", test_basic_imports),
        ("配置文件加载", test_config_loading),
        ("API连接测试", test_api_connection),
        ("图像处理功能", test_image_processing),
        ("项目结构检查", test_project_structure)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[ERROR] {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！Windows开发环境准备就绪。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查上述错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())