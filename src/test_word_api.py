#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
每日单词API测试脚本
用于测试WordAPI类的功能
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent))

from class_word_api import WordAPI


def main():
    """主测试函数"""
    print("=== 每日单词API测试 ===\n")
    
    # 创建WordAPI实例
    word_api = WordAPI()
    
    # 测试获取每日内容
    print("正在获取每日单词和句子...")
    success = word_api.get_daily_content()
    
    if success:
        print("✅ 成功获取内容！\n")
        
        # 显示格式化内容
        print("📄 格式化显示内容:")
        print("=" * 50)
        print(word_api.format_display_content())
        print("=" * 50)
        
        # 显示摘要信息
        print("\n📊 内容摘要:")
        summary = word_api.get_summary()
        
        if summary['word']['text']:
            print(f"单词: {summary['word']['text']}")
            print(f"定义: {summary['word']['definition']}")
        
        if summary['sentence']['text']:
            print(f"句子: {summary['sentence']['text'][:100]}...")
            print(f"作者: {summary['sentence']['author']}")
        
    else:
        print("❌ 获取内容失败")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())