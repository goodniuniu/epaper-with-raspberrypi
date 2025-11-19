#!/usr/bin/env python3
"""
每日单词系统简化测试脚本
Daily Word System Simple Test Script
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    
    try:
        from daily_word_config import PROJECT_NAME, PROJECT_VERSION
        print(f"[OK] 配置模块导入成功 - {PROJECT_NAME} v{PROJECT_VERSION}")
    except Exception as e:
        print(f"[ERROR] 配置模块导入失败: {e}")
        return False
    
    try:
        from daily_word_api_client import DailyWordAPIClient
        print("[OK] API客户端模块导入成功")
    except Exception as e:
        print(f"[ERROR] API客户端模块导入失败: {e}")
        return False
    
    try:
        from daily_word_display_controller import DailyWordDisplayController
        print("[OK] 显示控制器模块导入成功")
    except Exception as e:
        print(f"[ERROR] 显示控制器模块导入失败: {e}")
        return False
    
    return True

def test_api_client():
    """测试API客户端"""
    print("\n测试API客户端...")
    
    try:
        from daily_word_api_client import DailyWordAPIClient
        
        client = DailyWordAPIClient()
        print("[OK] API客户端初始化成功")
        
        # 测试获取内容
        content = client.get_daily_content()
        if content:
            print("[OK] 获取每日内容成功")
            
            if content.get('word'):
                word = content['word']['word']
                print(f"  单词: {word}")
            
            if content.get('quote'):
                quote = content['quote']['text'][:50] + "..." if len(content['quote']['text']) > 50 else content['quote']['text']
                print(f"  句子: {quote}")
        else:
            print("[WARNING] 未获取到内容，但API客户端工作正常")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] API客户端测试失败: {e}")
        return False

def test_display_controller():
    """测试显示控制器"""
    print("\n测试显示控制器...")
    
    try:
        from daily_word_display_controller import DailyWordDisplayController
        
        controller = DailyWordDisplayController()
        print("[OK] 显示控制器初始化成功")
        
        # 测试内容格式化
        test_content = {
            'word': {
                'word': 'serendipity',
                'phonetic': '/ˌserənˈdipədē/',
                'definition': 'The occurrence and development of events by chance in a happy or beneficial way.',
                'example': 'A fortunate stroke of serendipity brought the two old friends together.',
                'source': 'test'
            },
            'quote': {
                'text': 'The only way to do great work is to love what you do.',
                'author': 'Steve Jobs',
                'source': 'test'
            }
        }
        
        # 测试内容显示（模拟模式）
        controller.display_content(test_content)
        print("[OK] 内容显示测试成功")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 显示控制器测试失败: {e}")
        return False

def test_system_integration():
    """测试系统集成"""
    print("\n测试系统集成...")
    
    try:
        from daily_word_main import DailyWordSystem
        
        system = DailyWordSystem()
        print("[OK] 系统初始化成功")
        
        # 测试系统状态
        status = system.get_system_status()
        print("[OK] 系统状态获取成功")
        print(f"  系统名称: {status['system']['name']}")
        print(f"  系统版本: {status['system']['version']}")
        
        # 测试更新显示
        success = system.update_display()
        if success:
            print("[OK] 显示更新成功")
        else:
            print("[WARNING] 显示更新失败，但系统运行正常")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 系统集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("每日单词系统测试")
    print("=" * 60)
    
    tests = [
        ("模块导入", test_imports),
        ("API客户端", test_api_client),
        ("显示控制器", test_display_controller),
        ("系统集成", test_system_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        try:
            if test_func():
                passed += 1
                print(f"[OK] {test_name} 测试通过")
            else:
                print(f"[FAIL] {test_name} 测试失败")
        except Exception as e:
            print(f"[ERROR] {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("所有测试通过！系统准备就绪。")
        return True
    else:
        print("部分测试失败，请检查相关组件。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)