#!/usr/bin/env python3
"""
每日单词词汇库管理器
Daily Word Vocabulary Manager

支持多种单词库：雅思、托福、GRE、四六级等
"""

import json
import logging
import os
import random
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import time

logger = logging.getLogger(__name__)

class VocabularyManager:
    """词汇库管理器"""
    
    def __init__(self, data_dir: str = "/opt/daily-word-epaper/data"):
        """初始化词汇库管理器"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 词汇库文件路径
        self.vocab_dir = self.data_dir / "vocabularies"
        self.vocab_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置文件
        self.config_file = self.data_dir / "vocabulary_config.json"
        
        # 默认配置
        self.default_config = {
            "current_vocabulary": "ielts",
            "vocabularies": {
                "ielts": {
                    "name": "雅思词汇",
                    "description": "IELTS 雅思考试核心词汇",
                    "file": "ielts_vocabulary.json",
                    "url": None,  # 使用内置词汇库
                    "enabled": True
                },
                "toefl": {
                    "name": "托福词汇",
                    "description": "TOEFL 托福考试核心词汇",
                    "file": "toefl_vocabulary.json",
                    "url": None,  # 需要手动添加
                    "enabled": False
                },
                "gre": {
                    "name": "GRE词汇",
                    "description": "GRE 研究生入学考试词汇",
                    "file": "gre_vocabulary.json",
                    "url": None,  # 需要手动添加
                    "enabled": False
                },
                "cet4": {
                    "name": "英语四级",
                    "description": "大学英语四级考试词汇",
                    "file": "cet4_vocabulary.json",
                    "url": None,  # 需要手动添加
                    "enabled": False
                },
                "cet6": {
                    "name": "英语六级",
                    "description": "大学英语六级考试词汇",
                    "file": "cet6_vocabulary.json",
                    "url": None,  # 需要手动添加
                    "enabled": False
                },
                "smart": {
                    "name": "智能词汇",
                    "description": "内置高质量主题词汇",
                    "file": "smart_vocabulary.json",
                    "url": None,
                    "enabled": True
                }
            }
        }
        
        # 加载配置
        self.config = self.load_config()
        
        # 初始化内置智能词汇库
        self.init_smart_vocabulary()
        
        logger.info("词汇库管理器初始化完成")
    
    def load_config(self) -> Dict:
        """加载配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并默认配置
                for key, value in self.default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            else:
                return self.default_config.copy()
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            return self.default_config.copy()
    
    def save_config(self) -> bool:
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False
    
    def init_smart_vocabulary(self):
        """初始化内置智能词汇库"""
        smart_vocab_file = self.vocab_dir / "smart_vocabulary.json"
        
        if smart_vocab_file.exists():
            return
        
        # 扩展的高质量单词库
        smart_vocabulary = {
            "metadata": {
                "name": "智能词汇库",
                "description": "精选高质量英语词汇，按主题分类",
                "version": "1.0",
                "created": datetime.now().isoformat(),
                "total_words": 0
            },
            "words": [
                # Nature & Environment
                {"word": "serendipity", "phonetic": "/ˌserənˈdipədē/", "definition": "The occurrence and development of events by chance in a happy or beneficial way.", "example": "A fortunate stroke of serendipity brought the old friends together after decades.", "category": "nature", "difficulty": "advanced"},
                {"word": "petrichor", "phonetic": "/ˈpetrɪkɔr/", "definition": "A pleasant smell frequently accompanying the first rain after a long period of warm, dry weather.", "example": "The petrichor filled the air as the summer rain began to fall.", "category": "nature", "difficulty": "advanced"},
                {"word": "ephemeral", "phonetic": "/əˈfem(ə)rəl/", "definition": "Lasting for a very short time.", "example": "The beauty of cherry blossoms is ephemeral, lasting only a few weeks each spring.", "category": "nature", "difficulty": "intermediate"},
                {"word": "verdant", "phonetic": "/ˈvərdnt/", "definition": "Green with grass or other rich vegetation.", "example": "The verdant hills stretched as far as the eye could see.", "category": "nature", "difficulty": "intermediate"},
                {"word": "pristine", "phonetic": "/ˈprɪstiːn/", "definition": "In its original condition; unspoiled.", "example": "The pristine wilderness was untouched by human development.", "category": "nature", "difficulty": "intermediate"},
                
                # Emotions & Feelings
                {"word": "mellifluous", "phonetic": "/məˈliflo͞oəs/", "definition": "Sweet or musical; pleasant to hear.", "example": "Her mellifluous voice captivated the entire audience.", "category": "emotions", "difficulty": "advanced"},
                {"word": "euphoria", "phonetic": "/yo͞oˈfôrēə/", "definition": "A feeling or state of intense excitement and happiness.", "example": "The team felt euphoria after winning the championship.", "category": "emotions", "difficulty": "intermediate"},
                {"word": "tranquil", "phonetic": "/ˈtraNGkwəl/", "definition": "Free from disturbance; calm.", "example": "The tranquil lake reflected the mountains perfectly.", "category": "emotions", "difficulty": "basic"},
                {"word": "exuberant", "phonetic": "/ɪɡˈzuːbərənt/", "definition": "Filled with or characterized by a lively energy and excitement.", "example": "The children were exuberant on the last day of school.", "category": "emotions", "difficulty": "intermediate"},
                {"word": "serene", "phonetic": "/səˈriːn/", "definition": "Calm, peaceful, and untroubled.", "example": "She maintained a serene expression despite the chaos around her.", "category": "emotions", "difficulty": "basic"},
                
                # Beauty & Aesthetics
                {"word": "luminous", "phonetic": "/ˈlo͞omənəs/", "definition": "Full of or shedding light; bright or shining.", "example": "The luminous moon cast a silver glow over the landscape.", "category": "beauty", "difficulty": "intermediate"},
                {"word": "ethereal", "phonetic": "/əˈTHirēəl/", "definition": "Extremely delicate and light in a way that seems too perfect for this world.", "example": "The dancer moved with an ethereal grace across the stage.", "category": "beauty", "difficulty": "advanced"},
                {"word": "sublime", "phonetic": "/səˈblīm/", "definition": "Of such excellence, grandeur, or beauty as to inspire great admiration or awe.", "example": "The view from the mountain peak was absolutely sublime.", "category": "beauty", "difficulty": "intermediate"},
                {"word": "resplendent", "phonetic": "/rɪˈsplendənt/", "definition": "Attractive and impressive through being richly colorful or sumptuous.", "example": "The bride looked resplendent in her wedding gown.", "category": "beauty", "difficulty": "advanced"},
                {"word": "exquisite", "phonetic": "/ɪkˈskwɪzɪt/", "definition": "Extremely beautiful and delicate.", "example": "The exquisite craftsmanship of the jewelry was evident in every detail.", "category": "beauty", "difficulty": "intermediate"}
            ]
        }
        
        # 更新总词数
        smart_vocabulary["metadata"]["total_words"] = len(smart_vocabulary["words"])
        
        try:
            with open(smart_vocab_file, 'w', encoding='utf-8') as f:
                json.dump(smart_vocabulary, f, ensure_ascii=False, indent=2)
            logger.info(f"智能词汇库已创建: {len(smart_vocabulary['words'])} 个单词")
        except Exception as e:
            logger.error(f"创建智能词汇库失败: {e}")
    
    def download_vocabulary(self, vocab_key: str) -> bool:
        """下载词汇库"""
        if vocab_key not in self.config["vocabularies"]:
            logger.error(f"未知的词汇库: {vocab_key}")
            return False
        
        vocab_config = self.config["vocabularies"][vocab_key]
        
        # 如果是雅思词汇库，使用内置词汇库
        if vocab_key == "ielts":
            return self._create_builtin_ielts_vocabulary()
        
        url = vocab_config.get("url")
        
        if not url:
            logger.warning(f"词汇库 {vocab_key} 没有下载链接")
            return False
        
        vocab_file = self.vocab_dir / vocab_config["file"]
        
        try:
            logger.info(f"开始下载词汇库: {vocab_config['name']}")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # 尝试解析JSON以验证格式
            data = response.json()
            
            # 转换为标准格式
            standardized_data = self._standardize_vocabulary_format(data, vocab_key)
            
            with open(vocab_file, 'w', encoding='utf-8') as f:
                json.dump(standardized_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"词汇库下载成功: {vocab_config['name']} ({len(standardized_data.get('words', []))} 个单词)")
            return True
            
        except Exception as e:
            logger.error(f"下载词汇库失败 {vocab_key}: {e}")
            return False
    
    def _create_builtin_ielts_vocabulary(self) -> bool:
        """创建内置雅思词汇库"""
        vocab_file = self.vocab_dir / "ielts_vocabulary.json"
        
        ielts_words = [
            # Academic & Education
            {"word": "academic", "phonetic": "/ˌækəˈdemɪk/", "definition": "Relating to education and scholarship", "example": "She has an academic background in linguistics.", "category": "education", "difficulty": "intermediate"},
            {"word": "curriculum", "phonetic": "/kəˈrɪkjələm/", "definition": "The subjects comprising a course of study", "example": "The new curriculum includes more practical skills.", "category": "education", "difficulty": "intermediate"},
            {"word": "methodology", "phonetic": "/ˌmeθəˈdɒlədʒi/", "definition": "A system of methods used in a particular area of study", "example": "The research methodology was clearly explained.", "category": "education", "difficulty": "advanced"},
            {"word": "hypothesis", "phonetic": "/haɪˈpɒθəsɪs/", "definition": "A supposition or proposed explanation", "example": "The scientist tested her hypothesis through experiments.", "category": "education", "difficulty": "advanced"},
            {"word": "analysis", "phonetic": "/əˈnæləsɪs/", "definition": "Detailed examination of the elements or structure", "example": "The analysis revealed interesting patterns in the data.", "category": "education", "difficulty": "intermediate"},
            
            # Environment & Nature
            {"word": "sustainable", "phonetic": "/səˈsteɪnəbl/", "definition": "Able to be maintained at a certain rate or level", "example": "We need sustainable energy sources for the future.", "category": "environment", "difficulty": "intermediate"},
            {"word": "biodiversity", "phonetic": "/ˌbaɪəʊdaɪˈvɜːsəti/", "definition": "The variety of plant and animal life", "example": "The rainforest has incredible biodiversity.", "category": "environment", "difficulty": "advanced"},
            {"word": "ecosystem", "phonetic": "/ˈiːkəʊˌsɪstəm/", "definition": "A biological community of interacting organisms", "example": "The coral reef ecosystem is very fragile.", "category": "environment", "difficulty": "intermediate"},
            {"word": "conservation", "phonetic": "/ˌkɒnsəˈveɪʃn/", "definition": "The protection of plants, animals, and natural areas", "example": "Wildlife conservation is crucial for future generations.", "category": "environment", "difficulty": "intermediate"},
            {"word": "renewable", "phonetic": "/rɪˈnjuːəbl/", "definition": "Not depleted when used", "example": "Solar power is a renewable energy source.", "category": "environment", "difficulty": "intermediate"},
            
            # Technology & Innovation
            {"word": "innovation", "phonetic": "/ˌɪnəˈveɪʃn/", "definition": "The action or process of innovating", "example": "Technological innovation drives economic growth.", "category": "technology", "difficulty": "intermediate"},
            {"word": "artificial", "phonetic": "/ˌɑːtɪˈfɪʃl/", "definition": "Made or produced by human beings rather than occurring naturally", "example": "Artificial intelligence is transforming many industries.", "category": "technology", "difficulty": "basic"},
            {"word": "automation", "phonetic": "/ˌɔːtəˈmeɪʃn/", "definition": "The use of largely automatic equipment", "example": "Factory automation has increased productivity.", "category": "technology", "difficulty": "intermediate"},
            {"word": "digital", "phonetic": "/ˈdɪdʒɪtl/", "definition": "Relating to computer technology", "example": "The digital revolution changed how we communicate.", "category": "technology", "difficulty": "basic"},
            {"word": "algorithm", "phonetic": "/ˈælɡərɪðəm/", "definition": "A process or set of rules to be followed", "example": "The search algorithm finds relevant results quickly.", "category": "technology", "difficulty": "advanced"},
            
            # Society & Culture
            {"word": "diversity", "phonetic": "/daɪˈvɜːsəti/", "definition": "The state of being diverse; variety", "example": "Cultural diversity enriches our society.", "category": "society", "difficulty": "intermediate"},
            {"word": "globalization", "phonetic": "/ˌɡləʊbəlaɪˈzeɪʃn/", "definition": "The process by which businesses develop international influence", "example": "Globalization has connected markets worldwide.", "category": "society", "difficulty": "advanced"},
            {"word": "urbanization", "phonetic": "/ˌɜːbənaɪˈzeɪʃn/", "definition": "The process of making an area more urban", "example": "Rapid urbanization has created megacities.", "category": "society", "difficulty": "advanced"},
            {"word": "demographic", "phonetic": "/ˌdeməˈɡræfɪk/", "definition": "Relating to the structure of populations", "example": "Demographic changes affect economic planning.", "category": "society", "difficulty": "advanced"},
            {"word": "multicultural", "phonetic": "/ˌmʌltiˈkʌltʃərəl/", "definition": "Relating to several cultural groups", "example": "Australia is a multicultural society.", "category": "society", "difficulty": "intermediate"},
            
            # Health & Medicine
            {"word": "pharmaceutical", "phonetic": "/ˌfɑːməˈsuːtɪkl/", "definition": "Relating to medicinal drugs", "example": "The pharmaceutical industry develops new treatments.", "category": "health", "difficulty": "advanced"},
            {"word": "epidemic", "phonetic": "/ˌepɪˈdemɪk/", "definition": "A widespread occurrence of an infectious disease", "example": "The flu epidemic affected thousands of people.", "category": "health", "difficulty": "intermediate"},
            {"word": "nutrition", "phonetic": "/njuˈtrɪʃn/", "definition": "The process of providing food necessary for health", "example": "Good nutrition is essential for children's development.", "category": "health", "difficulty": "basic"},
            {"word": "therapy", "phonetic": "/ˈθerəpi/", "definition": "Treatment intended to relieve or heal a disorder", "example": "Physical therapy helped her recover from the injury.", "category": "health", "difficulty": "basic"},
            {"word": "diagnosis", "phonetic": "/ˌdaɪəɡˈnəʊsɪs/", "definition": "The identification of the nature of an illness", "example": "Early diagnosis improves treatment outcomes.", "category": "health", "difficulty": "intermediate"},
            
            # Economics & Business
            {"word": "entrepreneur", "phonetic": "/ˌɒntrəprəˈnɜː/", "definition": "A person who organizes and operates a business", "example": "The young entrepreneur started three successful companies.", "category": "business", "difficulty": "intermediate"},
            {"word": "investment", "phonetic": "/ɪnˈvestmənt/", "definition": "The action of investing money for profit", "example": "Foreign investment boosted the local economy.", "category": "business", "difficulty": "basic"},
            {"word": "infrastructure", "phonetic": "/ˈɪnfrəˌstrʌktʃə/", "definition": "The basic physical systems of a country or organization", "example": "Good infrastructure attracts business investment.", "category": "business", "difficulty": "advanced"},
            {"word": "recession", "phonetic": "/rɪˈseʃn/", "definition": "A period of temporary economic decline", "example": "The recession led to higher unemployment rates.", "category": "business", "difficulty": "intermediate"},
            {"word": "commodity", "phonetic": "/kəˈmɒdəti/", "definition": "A raw material or primary agricultural product", "example": "Oil is an important global commodity.", "category": "business", "difficulty": "intermediate"},
            
            # Communication & Media
            {"word": "journalism", "phonetic": "/ˈdʒɜːnəlɪzəm/", "definition": "The activity of writing for newspapers or magazines", "example": "Investigative journalism exposed the corruption scandal.", "category": "media", "difficulty": "intermediate"},
            {"word": "broadcast", "phonetic": "/ˈbrɔːdkɑːst/", "definition": "Transmit a programme on television or radio", "example": "The news was broadcast live from the scene.", "category": "media", "difficulty": "basic"},
            {"word": "propaganda", "phonetic": "/ˌprɒpəˈɡændə/", "definition": "Information used to promote a political cause", "example": "The government used propaganda to influence public opinion.", "category": "media", "difficulty": "advanced"},
            {"word": "censorship", "phonetic": "/ˈsensəʃɪp/", "definition": "The suppression of speech or information", "example": "Internet censorship limits access to information.", "category": "media", "difficulty": "intermediate"},
            {"word": "documentary", "phonetic": "/ˌdɒkjuˈmentri/", "definition": "A film or television programme that provides factual information", "example": "The documentary explored climate change issues.", "category": "media", "difficulty": "basic"}
        ]
        
        ielts_vocabulary = {
            "metadata": {
                "name": "雅思词汇库",
                "description": "IELTS 雅思考试核心词汇 - 内置高质量词汇",
                "source": "builtin",
                "created": datetime.now().isoformat(),
                "total_words": len(ielts_words)
            },
            "words": ielts_words
        }
        
        try:
            with open(vocab_file, 'w', encoding='utf-8') as f:
                json.dump(ielts_vocabulary, f, ensure_ascii=False, indent=2)
            logger.info(f"雅思词汇库已创建: {len(ielts_words)} 个单词")
            return True
        except Exception as e:
            logger.error(f"创建雅思词汇库失败: {e}")
            return False
    
    def _standardize_vocabulary_format(self, data: Any, vocab_key: str) -> Dict:
        """标准化词汇库格式"""
        standardized = {
            "metadata": {
                "name": self.config["vocabularies"][vocab_key]["name"],
                "description": self.config["vocabularies"][vocab_key]["description"],
                "source": vocab_key,
                "downloaded": datetime.now().isoformat(),
                "total_words": 0
            },
            "words": []
        }
        
        # 根据不同的数据格式进行转换
        if isinstance(data, list):
            # 简单的单词列表
            for item in data:
                if isinstance(item, str):
                    standardized["words"].append({
                        "word": item.lower().strip(),
                        "phonetic": "",
                        "definition": "",
                        "example": "",
                        "category": "general",
                        "difficulty": "intermediate"
                    })
                elif isinstance(item, dict):
                    word_entry = {
                        "word": item.get("word", "").lower().strip(),
                        "phonetic": item.get("phonetic", item.get("pronunciation", "")),
                        "definition": item.get("definition", item.get("meaning", "")),
                        "example": item.get("example", item.get("sentence", "")),
                        "category": item.get("category", "general"),
                        "difficulty": item.get("difficulty", "intermediate")
                    }
                    if word_entry["word"]:
                        standardized["words"].append(word_entry)
        
        elif isinstance(data, dict):
            # 字典格式
            if "words" in data:
                standardized["words"] = data["words"]
            else:
                # 可能是其他格式，尝试提取
                for key, value in data.items():
                    if isinstance(value, str):
                        standardized["words"].append({
                            "word": key.lower().strip(),
                            "phonetic": "",
                            "definition": value,
                            "example": "",
                            "category": "general",
                            "difficulty": "intermediate"
                        })
        
        standardized["metadata"]["total_words"] = len(standardized["words"])
        return standardized
    
    def get_random_word(self, vocab_key: Optional[str] = None) -> Optional[Dict]:
        """获取随机单词"""
        if not vocab_key:
            vocab_key = self.config["current_vocabulary"]
        
        vocab_file = self.vocab_dir / self.config["vocabularies"][vocab_key]["file"]
        
        if not vocab_file.exists():
            logger.warning(f"词汇库文件不存在: {vocab_file}")
            # 尝试下载
            if vocab_key == "ielts":
                self._create_builtin_ielts_vocabulary()
            elif vocab_key != "smart":
                self.download_vocabulary(vocab_key)
            
            if not vocab_file.exists():
                logger.error(f"无法获取词汇库: {vocab_key}")
                return None
        
        try:
            with open(vocab_file, 'r', encoding='utf-8') as f:
                vocab_data = json.load(f)
            
            words = vocab_data.get("words", [])
            if not words:
                logger.error(f"词汇库为空: {vocab_key}")
                return None
            
            # 使用当前时间戳作为随机种子，确保真正随机
            random.seed(int(time.time() * 1000000) % 1000000)
            
            word_entry = random.choice(words)
            
            # 添加来源信息
            word_entry = word_entry.copy()
            word_entry["source"] = f"{vocab_data['metadata']['name']}"
            word_entry["date"] = datetime.now().strftime('%Y-%m-%d')
            
            logger.info(f"从 {vocab_key} 词汇库获取随机单词: {word_entry['word']}")
            return word_entry
            
        except Exception as e:
            logger.error(f"读取词汇库失败 {vocab_key}: {e}")
            return None
    
    def get_word_by_category(self, category: str, vocab_key: Optional[str] = None) -> Optional[Dict]:
        """根据分类获取单词"""
        if not vocab_key:
            vocab_key = self.config["current_vocabulary"]
        
        vocab_file = self.vocab_dir / self.config["vocabularies"][vocab_key]["file"]
        
        if not vocab_file.exists():
            return None
        
        try:
            with open(vocab_file, 'r', encoding='utf-8') as f:
                vocab_data = json.load(f)
            
            words = vocab_data.get("words", [])
            category_words = [w for w in words if w.get("category", "").lower() == category.lower()]
            
            if not category_words:
                logger.warning(f"分类 {category} 中没有单词")
                return None
            
            # 使用当前时间戳作为随机种子
            random.seed(int(time.time() * 1000000) % 1000000)
            
            word_entry = random.choice(category_words)
            word_entry = word_entry.copy()
            word_entry["source"] = f"{vocab_data['metadata']['name']} ({category.title()} Category)"
            word_entry["date"] = datetime.now().strftime('%Y-%m-%d')
            
            return word_entry
            
        except Exception as e:
            logger.error(f"按分类获取单词失败: {e}")
            return None
    
    def set_current_vocabulary(self, vocab_key: str) -> bool:
        """设置当前使用的词汇库"""
        if vocab_key not in self.config["vocabularies"]:
            logger.error(f"未知的词汇库: {vocab_key}")
            return False
        
        self.config["current_vocabulary"] = vocab_key
        success = self.save_config()
        
        if success:
            logger.info(f"当前词汇库已设置为: {self.config['vocabularies'][vocab_key]['name']}")
        
        return success
    
    def list_vocabularies(self) -> Dict:
        """列出所有可用的词汇库"""
        result = {}
        
        for key, vocab in self.config["vocabularies"].items():
            vocab_file = self.vocab_dir / vocab["file"]
            
            status = {
                "name": vocab["name"],
                "description": vocab["description"],
                "enabled": vocab["enabled"],
                "downloaded": vocab_file.exists(),
                "current": key == self.config["current_vocabulary"]
            }
            
            if vocab_file.exists():
                try:
                    with open(vocab_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    status["word_count"] = data.get("metadata", {}).get("total_words", 0)
                except:
                    status["word_count"] = 0
            else:
                status["word_count"] = 0
            
            result[key] = status
        
        return result
    
    def get_vocabulary_stats(self) -> Dict:
        """获取词汇库统计信息"""
        stats = {
            "current_vocabulary": self.config["current_vocabulary"],
            "total_vocabularies": len(self.config["vocabularies"]),
            "downloaded_vocabularies": 0,
            "total_words": 0,
            "vocabularies": {}
        }
        
        for key, vocab in self.config["vocabularies"].items():
            vocab_file = self.vocab_dir / vocab["file"]
            
            if vocab_file.exists():
                stats["downloaded_vocabularies"] += 1
                try:
                    with open(vocab_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    word_count = data.get("metadata", {}).get("total_words", 0)
                    stats["total_words"] += word_count
                    stats["vocabularies"][key] = {
                        "name": vocab["name"],
                        "word_count": word_count,
                        "downloaded": True
                    }
                except:
                    stats["vocabularies"][key] = {
                        "name": vocab["name"],
                        "word_count": 0,
                        "downloaded": False
                    }
            else:
                stats["vocabularies"][key] = {
                    "name": vocab["name"],
                    "word_count": 0,
                    "downloaded": False
                }
        
        return stats