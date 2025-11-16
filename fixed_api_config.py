# 修复后的API配置
# Generated on 2025-11-16T23:02:07.690897

FIXED_WORD_API_CONFIG = {
    "primary": {
        "name": "Free Dictionary API - Random Words",
        "base_url": "https://api.dictionaryapi.dev/api/v2",
        "endpoints": {
            "word_definition": "/entries/en/{word}",
            "random_word": "/entries/en/random"
        },
        "api_key": null,
        "timeout": 10,
        "retry_count": 3,
        "enabled": true
    },
    "fallback": {
        "name": "Wordnik (Requires API Key)",
        "base_url": "https://api.wordnik.com/v4",
        "endpoints": {
            "word_of_day": "/words.json/wordOfTheDay",
            "word_definition": "/word.json/{word}/definitions",
            "word_example": "/word.json/{word}/examples"
        },
        "api_key": null,
        "timeout": 10,
        "retry_count": 3,
        "enabled": false
    },
    "secondary_fallback": {
        "name": "WordsAPI (RapidAPI - Requires API Key)",
        "base_url": "https://wordsapiv1.p.rapidapi.com",
        "endpoints": {
            "word_definition": "/words/{word}"
        },
        "timeout": 15,
        "retry_count": 2,
        "headers": {
            "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com",
            "X-RapidAPI-Key": null
        },
        "enabled": false
    },
    "vocabulary_fallback": {
        "name": "Local Vocabulary Manager",
        "enabled": true,
        "priority": "high"
    }
}

FIXED_QUOTE_API_CONFIG = {
    "primary": {
        "name": "ZenQuotes (Working)",
        "base_url": "https://zenquotes.io/api",
        "endpoints": {
            "random_quote": "/random",
            "today_quote": "/today"
        },
        "timeout": 10,
        "retry_count": 3,
        "enabled": true
    },
    "fallback": {
        "name": "Quotable (SSL Issues)",
        "base_url": "https://api.quotable.io",
        "endpoints": {
            "random_quote": "/random",
            "quote_by_tag": "/random?tags={tag}"
        },
        "timeout": 10,
        "retry_count": 3,
        "enabled": false
    },
    "local_fallback": {
        "name": "Local Quote Database",
        "enabled": true,
        "priority": "high"
    }
}

# 配置说明
CONFIG_NOTES = """
配置修复说明：
1. Free Dictionary API:
   - 原wordOfTheDay端点不存在，改为使用随机单词+定义查询
   - 使用正确的entries/en/word端点获取单词定义
   
2. Wordnik API:
   - 保持禁用状态，需要API密钥
   - 用户可以注册获取免费密钥后启用
   
3. WordsAPI:
   - 保持禁用状态，需要RapidAPI密钥
   - 用户可以注册RapidAPI后启用
   
4. ZenQuotes API:
   - 测试可用，设为主要的句子API
   - 优先使用此API获取每日句子
   
5. Quotable API:
   - 由于SSL问题暂时禁用
   - 可以后续修复SSL配置后启用
   
6. 本地备用：
   - 词汇库管理器提供高质量单词
   - 本地句子库提供备用内容
   - 确保系统在无网络时也能正常工作
"""

# 使用建议
USAGE_RECOMMENDATIONS = """
使用建议：
1. 立即生效：修复后的配置已经可以正常使用
2. 获取API密钥：建议申请Wordnik或WordsAPI密钥以获得更好体验
3. 扩展词汇库：可以添加更多词汇库文件
4. 监控API状态：定期检查API可用性
"""
