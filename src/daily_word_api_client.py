#!/usr/bin/env python3
"""
每日单词墨水屏显示系统 - API客户端
Daily Word E-Paper Display System - API Client

负责从各种API获取每日单词和励志句子
"""

import json
import logging
import random
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union

from daily_word_config import (
    WORD_API_CONFIG, QUOTE_API_CONFIG, CACHE_CONFIG, 
    FALLBACK_WORDS, FALLBACK_QUOTES, DATA_DIR
)

# 配置日志
logger = logging.getLogger(__name__)

class DailyWordAPIClient:
    """每日单词API客户端"""
    
    def __init__(self):
        """初始化API客户端"""
        self.cache_dir = Path(DATA_DIR)
        self.word_cache_file = self.cache_dir / CACHE_CONFIG['cache_files']['word_cache']
        self.quote_cache_file = self.cache_dir / CACHE_CONFIG['cache_files']['quote_cache']
        
        # 确保缓存目录存在
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载缓存
        self.word_cache = self._load_cache(self.word_cache_file)
        self.quote_cache = self._load_cache(self.quote_cache_file)
        
        logger.info("每日单词API客户端初始化完成")
    
    def _load_cache(self, cache_file: Path) -> Dict:
        """加载缓存文件"""
        try:
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    logger.debug(f"成功加载缓存文件: {cache_file}")
                    return cache_data
        except Exception as e:
            logger.warning(f"加载缓存文件失败 {cache_file}: {e}")
        
        return {}
    
    def _save_cache(self, cache_file: Path, cache_data: Dict) -> bool:
        """保存缓存文件"""
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            logger.debug(f"成功保存缓存文件: {cache_file}")
            return True
        except Exception as e:
            logger.error(f"保存缓存文件失败 {cache_file}: {e}")
            return False
    
    def _make_request(self, url: str, timeout: int = 10, retry_count: int = 3) -> Optional[Dict]:
        """发起HTTP请求"""
        for attempt in range(retry_count):
            try:
                logger.debug(f"请求URL: {url} (尝试 {attempt + 1}/{retry_count})")
                
                headers = {
                    'User-Agent': 'Daily-Word-EPaper/1.0.0',
                    'Accept': 'application/json',
                }
                
                response = requests.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()
                
                data = response.json()
                logger.debug(f"请求成功: {url}")
                return data
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{retry_count}): {e}")
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                continue
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}")
                break
        
        logger.error(f"所有请求尝试失败: {url}")
        return None
    
    def get_word_of_day(self, force_new: bool = False) -> Optional[Dict]:
        """获取每日单词"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 检查缓存
        if not force_new and today in self.word_cache:
            logger.info(f"使用缓存的每日单词: {today}")
            return self.word_cache[today]
        
        # 尝试从主要API获取
        word_data = self._fetch_word_from_primary_api()
        
        # 如果主要API失败，尝试备用API
        if not word_data:
            word_data = self._fetch_word_from_fallback_api()
        
        # 如果所有API都失败，使用本地备用内容
        if not word_data:
            word_data = self._get_fallback_word()
        
        if word_data:
            # 添加获取时间戳
            word_data['fetched_at'] = datetime.now().isoformat()
            word_data['date'] = today
            
            # 保存到缓存
            self.word_cache[today] = word_data
            self._save_cache(self.word_cache_file, self.word_cache)
            
            logger.info(f"成功获取每日单词: {word_data.get('word', 'Unknown')}")
            return word_data
        
        logger.error("无法获取每日单词")
        return None
    
    def _fetch_word_from_primary_api(self) -> Optional[Dict]:
        """从主要API获取单词"""
        try:
            config = WORD_API_CONFIG['primary']
            base_url = config['base_url']
            endpoint = config['endpoints']['word_of_day']
            timeout = config['timeout']
            
            url = f"{base_url}{endpoint}"
            if config.get('api_key'):
                url += f"?api_key={config['api_key']}"
            
            data = self._make_request(url, timeout, config['retry_count'])
            
            if data:
                # 解析Wordnik API响应
                return self._parse_wordnik_response(data)
                
        except Exception as e:
            logger.error(f"主要API请求失败: {e}")
        
        return None
    
    def _fetch_word_from_fallback_api(self) -> Optional[Dict]:
        """从备用API获取单词"""
        try:
            # 使用随机单词作为备用
            fallback_words = ['serendipity', 'ephemeral', 'mellifluous', 'ubiquitous', 'perspicacious']
            random_word = random.choice(fallback_words)
            
            config = WORD_API_CONFIG['fallback']
            base_url = config['base_url']
            endpoint = config['endpoints']['word_definition'].format(word=random_word)
            timeout = config['timeout']
            
            url = f"{base_url}{endpoint}"
            data = self._make_request(url, timeout, config['retry_count'])
            
            if data:
                # 解析Dictionary API响应
                return self._parse_dictionary_api_response(data)
                
        except Exception as e:
            logger.error(f"备用API请求失败: {e}")
        
        return None
    
    def _parse_wordnik_response(self, data: Dict) -> Optional[Dict]:
        """解析Wordnik API响应"""
        try:
            word = data.get('word', '')
            definitions = data.get('definitions', [])
            examples = data.get('examples', [])
            
            definition = ''
            if definitions:
                definition = definitions[0].get('text', '')
            
            example = ''
            if examples:
                example = examples[0].get('text', '')
            
            return {
                'word': word,
                'phonetic': '',  # Wordnik API可能不包含音标
                'definition': definition,
                'example': example,
                'source': 'Wordnik API'
            }
            
        except Exception as e:
            logger.error(f"解析Wordnik响应失败: {e}")
            return None
    
    def _parse_dictionary_api_response(self, data: List) -> Optional[Dict]:
        """解析Dictionary API响应"""
        try:
            if not data or not isinstance(data, list):
                return None
            
            entry = data[0]
            word = entry.get('word', '')
            
            # 获取音标
            phonetic = ''
            phonetics = entry.get('phonetics', [])
            for p in phonetics:
                if p.get('text'):
                    phonetic = p['text']
                    break
            
            # 获取定义
            definition = ''
            meanings = entry.get('meanings', [])
            if meanings:
                definitions = meanings[0].get('definitions', [])
                if definitions:
                    definition = definitions[0].get('definition', '')
            
            # 获取例句
            example = ''
            if meanings:
                definitions = meanings[0].get('definitions', [])
                for def_item in definitions:
                    if def_item.get('example'):
                        example = def_item['example']
                        break
            
            return {
                'word': word,
                'phonetic': phonetic,
                'definition': definition,
                'example': example,
                'source': 'Dictionary API'
            }
            
        except Exception as e:
            logger.error(f"解析Dictionary API响应失败: {e}")
            return None
    
    def _get_fallback_word(self) -> Dict:
        """获取备用单词"""
        today = datetime.now()
        # 使用日期作为种子，确保同一天返回相同的单词
        random.seed(today.strftime('%Y%m%d'))
        word_data = random.choice(FALLBACK_WORDS).copy()
        word_data['source'] = 'Local Fallback'
        
        logger.info(f"使用备用单词: {word_data['word']}")
        return word_data
    
    def get_daily_quote(self, force_new: bool = False) -> Optional[Dict]:
        """获取每日句子"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 检查缓存
        if not force_new and today in self.quote_cache:
            logger.info(f"使用缓存的每日句子: {today}")
            return self.quote_cache[today]
        
        # 尝试从主要API获取
        quote_data = self._fetch_quote_from_primary_api()
        
        # 如果主要API失败，尝试备用API
        if not quote_data:
            quote_data = self._fetch_quote_from_fallback_api()
        
        # 如果所有API都失败，使用本地备用内容
        if not quote_data:
            quote_data = self._get_fallback_quote()
        
        if quote_data:
            # 添加获取时间戳
            quote_data['fetched_at'] = datetime.now().isoformat()
            quote_data['date'] = today
            
            # 保存到缓存
            self.quote_cache[today] = quote_data
            self._save_cache(self.quote_cache_file, self.quote_cache)
            
            logger.info(f"成功获取每日句子: {quote_data.get('text', 'Unknown')[:50]}...")
            return quote_data
        
        logger.error("无法获取每日句子")
        return None
    
    def _fetch_quote_from_primary_api(self) -> Optional[Dict]:
        """从主要API获取句子"""
        try:
            config = QUOTE_API_CONFIG['primary']
            base_url = config['base_url']
            endpoint = config['endpoints']['random_quote']
            timeout = config['timeout']
            
            url = f"{base_url}{endpoint}"
            data = self._make_request(url, timeout, config['retry_count'])
            
            if data:
                return self._parse_quotable_response(data)
                
        except Exception as e:
            logger.error(f"主要句子API请求失败: {e}")
        
        return None
    
    def _fetch_quote_from_fallback_api(self) -> Optional[Dict]:
        """从备用API获取句子"""
        try:
            config = QUOTE_API_CONFIG['fallback']
            base_url = config['base_url']
            endpoint = config['endpoints']['random_quote']
            timeout = config['timeout']
            
            url = f"{base_url}{endpoint}"
            data = self._make_request(url, timeout, config['retry_count'])
            
            if data:
                return self._parse_zenquotes_response(data)
                
        except Exception as e:
            logger.error(f"备用句子API请求失败: {e}")
        
        return None
    
    def _parse_quotable_response(self, data: Dict) -> Optional[Dict]:
        """解析Quotable API响应"""
        try:
            return {
                'text': data.get('content', ''),
                'author': data.get('author', ''),
                'category': ', '.join(data.get('tags', [])),
                'source': 'Quotable API'
            }
        except Exception as e:
            logger.error(f"解析Quotable响应失败: {e}")
            return None
    
    def _parse_zenquotes_response(self, data: List) -> Optional[Dict]:
        """解析ZenQuotes API响应"""
        try:
            if not data or not isinstance(data, list):
                return None
            
            quote = data[0]
            return {
                'text': quote.get('q', ''),
                'author': quote.get('a', ''),
                'category': 'inspiration',
                'source': 'ZenQuotes API'
            }
        except Exception as e:
            logger.error(f"解析ZenQuotes响应失败: {e}")
            return None
    
    def _get_fallback_quote(self) -> Dict:
        """获取备用句子"""
        today = datetime.now()
        # 使用日期作为种子，确保同一天返回相同的句子
        random.seed(today.strftime('%Y%m%d') + 'quote')
        quote_data = random.choice(FALLBACK_QUOTES).copy()
        quote_data['source'] = 'Local Fallback'
        
        logger.info(f"使用备用句子: {quote_data['text'][:50]}...")
        return quote_data
    
    def get_daily_content(self, force_new: bool = False) -> Dict:
        """获取每日完整内容（单词+句子）"""
        logger.info("开始获取每日内容...")
        
        word_data = self.get_word_of_day(force_new)
        quote_data = self.get_daily_quote(force_new)
        
        content = {
            'word': word_data,
            'quote': quote_data,
            'generated_at': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        
        logger.info("每日内容获取完成")
        return content
    
    def cleanup_old_cache(self, days_to_keep: int = 30):
        """清理旧缓存"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_str = cutoff_date.strftime('%Y-%m-%d')
        
        # 清理单词缓存
        old_keys = [key for key in self.word_cache.keys() if key < cutoff_str]
        for key in old_keys:
            del self.word_cache[key]
        
        # 清理句子缓存
        old_keys = [key for key in self.quote_cache.keys() if key < cutoff_str]
        for key in old_keys:
            del self.quote_cache[key]
        
        # 保存清理后的缓存
        self._save_cache(self.word_cache_file, self.word_cache)
        self._save_cache(self.quote_cache_file, self.quote_cache)
        
        logger.info(f"清理了 {len(old_keys)} 个旧缓存条目")
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计信息"""
        return {
            'word_cache_size': len(self.word_cache),
            'quote_cache_size': len(self.quote_cache),
            'word_cache_file_size': self.word_cache_file.stat().st_size if self.word_cache_file.exists() else 0,
            'quote_cache_file_size': self.quote_cache_file.stat().st_size if self.quote_cache_file.exists() else 0,
            'last_word_date': max(self.word_cache.keys()) if self.word_cache else None,
            'last_quote_date': max(self.quote_cache.keys()) if self.quote_cache else None,
        }

def main():
    """测试函数"""
    import sys
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建API客户端
    client = DailyWordAPIClient()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--force':
        print("强制获取新内容...")
        content = client.get_daily_content(force_new=True)
    else:
        print("获取每日内容...")
        content = client.get_daily_content()
    
    # 显示结果
    print("\n" + "="*50)
    print("每日单词和句子")
    print("="*50)
    
    if content['word']:
        word = content['word']
        print(f"\n📚 今日单词: {word['word']}")
        if word.get('phonetic'):
            print(f"🔊 音标: {word['phonetic']}")
        print(f"📖 定义: {word['definition']}")
        if word.get('example'):
            print(f"💡 例句: {word['example']}")
        print(f"📡 来源: {word.get('source', 'Unknown')}")
    
    if content['quote']:
        quote = content['quote']
        print(f"\n💬 今日句子:")
        print(f"   \"{quote['text']}\"")
        print(f"   — {quote['author']}")
        if quote.get('category'):
            print(f"🏷️  分类: {quote['category']}")
        print(f"📡 来源: {quote.get('source', 'Unknown')}")
    
    # 显示缓存统计
    stats = client.get_cache_stats()
    print(f"\n📊 缓存统计:")
    print(f"   单词缓存: {stats['word_cache_size']} 条")
    print(f"   句子缓存: {stats['quote_cache_size']} 条")
    
    print("\n✅ 测试完成!")

if __name__ == "__main__":
    main()