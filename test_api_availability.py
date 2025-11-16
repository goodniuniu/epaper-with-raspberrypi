#!/usr/bin/env python3
"""
API可用性测试脚本
测试各个单词API的可用性
"""

import requests
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_api_endpoints():
    """测试各个API端点的可用性"""
    
    # 测试的API端点
    test_urls = [
        {
            'name': 'Free Dictionary API - Word of Day',
            'url': 'https://api.dictionaryapi.dev/api/v2/words.json/wordOfTheDay',
            'expected_format': 'json'
        },
        {
            'name': 'Free Dictionary API - Word Definition',
            'url': 'https://api.dictionaryapi.dev/api/v2/word.json/test/definitions',
            'expected_format': 'json'
        },
        {
            'name': 'Wordnik API - Word of Day',
            'url': 'https://api.wordnik.com/v4/words.json/wordOfTheDay',
            'expected_format': 'json'
        },
        {
            'name': 'Quotable API - Random Quote',
            'url': 'https://api.quotable.io/random',
            'expected_format': 'json'
        },
        {
            'name': 'ZenQuotes API - Random Quote',
            'url': 'https://zenquotes.io/api/random',
            'expected_format': 'json'
        }
    ]
    
    results = []
    
    for api_test in test_urls:
        try:
            logger.info(f"测试API: {api_test['name']}")
            logger.info(f"URL: {api_test['url']}")
            
            response = requests.get(api_test['url'], timeout=10)
            status_code = response.status_code
            
            logger.info(f"状态码: {status_code}")
            
            if status_code == 200:
                try:
                    data = response.json()
                    logger.info(f"响应格式正确，数据长度: {len(str(data))}")
                    result = {
                        'name': api_test['name'],
                        'url': api_test['url'],
                        'status': 'success',
                        'status_code': status_code,
                        'data_sample': str(data)[:200] + '...' if len(str(data)) > 200 else str(data)
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析失败: {e}")
                    result = {
                        'name': api_test['name'],
                        'url': api_test['url'],
                        'status': 'json_error',
                        'status_code': status_code,
                        'error': str(e)
                    }
            else:
                logger.error(f"请求失败，状态码: {status_code}")
                result = {
                    'name': api_test['name'],
                    'url': api_test['url'],
                    'status': 'http_error',
                    'status_code': status_code,
                    'error': f'HTTP {status_code}'
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求失败: {e}")
            result = {
                'name': api_test['name'],
                'url': api_test['url'],
                'status': 'network_error',
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"未知错误: {e}")
            result = {
                'name': api_test['name'],
                'url': api_test['url'],
                'status': 'unknown_error',
                'error': str(e)
            }
        
        results.append(result)
        logger.info("-" * 50)
    
    # 生成测试报告
    logger.info("\n" + "=" * 60)
    logger.info("API可用性测试报告")
    logger.info("=" * 60)
    
    working_apis = []
    failed_apis = []
    
    for result in results:
        if result['status'] == 'success':
            working_apis.append(result)
            logger.info(f"✅ {result['name']} - 可用")
        else:
            failed_apis.append(result)
            logger.info(f"❌ {result['name']} - 失败 ({result.get('status_code', 'N/A')})")
    
    logger.info(f"\n总结:")
    logger.info(f"可用API: {len(working_apis)} 个")
    logger.info(f"失败API: {len(failed_apis)} 个")
    
    if working_apis:
        logger.info(f"\n可用的API:")
        for api in working_apis:
            logger.info(f"  - {api['name']}: {api['url']}")
    
    if failed_apis:
        logger.info(f"\n失败的API:")
        for api in failed_apis:
            logger.info(f"  - {api['name']}: {api['url']} - {api.get('error', 'Unknown error')}")
    
    return results

def suggest_api_fixes():
    """提供API修复建议"""
    logger.info("\n" + "=" * 60)
    logger.info("API修复建议")
    logger.info("=" * 60)
    
    suggestions = [
        "1. Free Dictionary API 的 wordOfTheDay 端点不存在，建议:",
        "   - 使用备用单词列表",
        "   - 或者从词汇库中随机选择单词",
        "   - 或者使用其他支持每日单词的API",
        "",
        "2. 建议启用 Wordnik API (需要API密钥):",
        "   - 注册 Wordnik 账户获取免费API密钥",
        "   - 在配置中启用 Wordnik API",
        "",
        "3. 建议启用 WordsAPI (需要RapidAPI密钥):",
        "   - 注册 RapidAPI 账户",
        "   - 订阅 WordsAPI 服务",
        "   - 在配置中添加API密钥",
        "",
        "4. 当前备用机制工作正常:",
        "   - 词汇库管理器提供了高质量的单词",
        "   - 可以考虑扩展词汇库内容",
        "",
        "5. 建议配置修改:",
        "   - 修改主要API端点配置",
        "   - 启用可用的备用API",
        "   - 增加更多词汇库内容"
    ]
    
    for suggestion in suggestions:
        logger.info(suggestion)

if __name__ == "__main__":
    logger.info("开始API可用性测试...")
    test_api_endpoints()
    suggest_api_fixes()