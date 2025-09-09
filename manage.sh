#!/bin/bash
# 每日单词系统管理脚本

SERVICE_NAME="daily-word"
INSTALL_DIR="/opt/daily-word-epaper"

case "$1" in
    start)
        echo "启动服务..."
        sudo systemctl start $SERVICE_NAME
        ;;
    stop)
        echo "停止服务..."
        sudo systemctl stop $SERVICE_NAME
        ;;
    restart)
        echo "重启服务..."
        sudo systemctl restart $SERVICE_NAME
        ;;
    status)
        echo "服务状态:"
        sudo systemctl status $SERVICE_NAME
        ;;
    enable)
        echo "启用开机自启..."
        sudo systemctl enable $SERVICE_NAME
        ;;
    disable)
        echo "禁用开机自启..."
        sudo systemctl disable $SERVICE_NAME
        ;;
    logs)
        echo "查看日志:"
        sudo journalctl -u $SERVICE_NAME -f
        ;;
    test)
        echo "测试系统..."
        cd $INSTALL_DIR
        ./venv/bin/python src/daily_word_test.py
        ;;
    update)
        echo "更新显示..."
        cd $INSTALL_DIR
        ./venv/bin/python src/daily_word_main.py --force
        ;;
    clear)
        echo "清空显示..."
        cd $INSTALL_DIR
        ./venv/bin/python src/daily_word_main.py --clear
        ;;
    display)
        echo "从文件显示内容..."
        cd $INSTALL_DIR
        PYTHONPATH=$INSTALL_DIR/src ./venv/bin/python3 -c "
from daily_word_main import DailyWordSystem
system = DailyWordSystem()
system.display_from_file()
"
        ;;
    file-status)
        echo "文件管理器状态..."
        cd $INSTALL_DIR
        PYTHONPATH=$INSTALL_DIR/src ./venv/bin/python3 -c "
from daily_word_file_manager import DailyWordFileManager
import json
fm = DailyWordFileManager()
print('=== 文件统计 ===')
stats = fm.get_file_stats()
print(json.dumps(stats, indent=2, ensure_ascii=False))
"
        ;;
    vocab-list)
        echo "词汇库列表..."
        cd $INSTALL_DIR
        PYTHONPATH=$INSTALL_DIR/src ./venv/bin/python3 -c "
from daily_word_vocabulary_manager import VocabularyManager
import json
vm = VocabularyManager()
print('=== 可用词汇库 ===')
vocabs = vm.list_vocabularies()
for key, info in vocabs.items():
    status = '✅' if info['downloaded'] else '❌'
    current = '👈 当前' if info['current'] else ''
    print(f'{status} {key}: {info[\"name\"]} ({info[\"word_count\"]} 词) {current}')
print('\n=== 词汇库统计 ===')
stats = vm.get_vocabulary_stats()
print(json.dumps(stats, indent=2, ensure_ascii=False))
"
        ;;
    vocab-download)
        if [ -z "$2" ]; then
            echo "用法: $0 vocab-download <词汇库名称>"
            echo "可用词汇库: ielts, toefl, gre, cet4, cet6"
            exit 1
        fi
        echo "下载词汇库: $2"
        cd $INSTALL_DIR
        PYTHONPATH=$INSTALL_DIR/src ./venv/bin/python3 -c "
from daily_word_vocabulary_manager import VocabularyManager
vm = VocabularyManager()
success = vm.download_vocabulary('$2')
if success:
    print('✅ 词汇库下载成功')
else:
    print('❌ 词汇库下载失败')
"
        ;;
    vocab-set)
        if [ -z "$2" ]; then
            echo "用法: $0 vocab-set <词汇库名称>"
            echo "可用词汇库: ielts, toefl, gre, cet4, cet6, smart"
            exit 1
        fi
        echo "设置当前词汇库: $2"
        cd $INSTALL_DIR
        PYTHONPATH=$INSTALL_DIR/src ./venv/bin/python3 -c "
from daily_word_vocabulary_manager import VocabularyManager
vm = VocabularyManager()
success = vm.set_current_vocabulary('$2')
if success:
    print('✅ 词汇库设置成功')
else:
    print('❌ 词汇库设置失败')
"
        ;;
    vocab-test)
        echo "测试词汇库..."
        cd $INSTALL_DIR
        PYTHONPATH=$INSTALL_DIR/src ./venv/bin/python3 -c "
from daily_word_vocabulary_manager import VocabularyManager
vm = VocabularyManager()
print('=== 测试随机单词获取 ===')
for i in range(3):
    word = vm.get_random_word()
    if word:
        print(f'{i+1}. {word[\"word\"]} - {word[\"definition\"]} (来源: {word.get(\"source\", \"Unknown\")})')
    else:
        print(f'{i+1}. 获取单词失败')
"
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|enable|disable|logs|test|update|clear|display|file-status|vocab-list|vocab-download|vocab-set|vocab-test}"
        echo ""
        echo "词汇库管理命令:"
        echo "  vocab-list              - 列出所有词汇库"
        echo "  vocab-download <name>   - 下载指定词汇库 (ielts, toefl, gre, cet4, cet6)"
        echo "  vocab-set <name>        - 设置当前使用的词汇库"
        echo "  vocab-test              - 测试词汇库功能"
        exit 1
        ;;
esac
