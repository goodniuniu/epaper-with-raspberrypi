#!/usr/bin/env python3
"""
每日单词文件管理器
Daily Word File Manager

负责内容的持久化存储和读取，解决内存缓存不更新的问题
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import fcntl
import tempfile
import shutil

logger = logging.getLogger(__name__)

class DailyWordFileManager:
    """每日单词文件管理器"""
    
    def __init__(self, data_dir: str = "/opt/daily-word-epaper/data"):
        """初始化文件管理器"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 定义文件路径
        self.current_content_file = self.data_dir / "current_content.json"
        self.content_history_file = self.data_dir / "content_history.json"
        self.system_status_file = self.data_dir / "system_status.json"
        self.update_log_file = self.data_dir / "update_log.json"
        
        logger.info("文件管理器初始化完成")
    
    def _safe_write_json(self, file_path: Path, data: Dict) -> bool:
        """安全写入JSON文件（原子操作）"""
        try:
            # 使用临时文件确保原子写入
            temp_file = file_path.with_suffix('.tmp')
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                # 添加文件锁
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            
            # 原子替换
            shutil.move(str(temp_file), str(file_path))
            return True
            
        except Exception as e:
            logger.error(f"写入文件失败 {file_path}: {e}")
            # 清理临时文件
            if temp_file.exists():
                temp_file.unlink()
            return False
    
    def _safe_read_json(self, file_path: Path) -> Optional[Dict]:
        """安全读取JSON文件"""
        try:
            if not file_path.exists():
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                # 添加文件锁
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                return json.load(f)
                
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {e}")
            return None
    
    def save_current_content(self, word_data: Dict, quote_data: Dict) -> bool:
        """保存当前内容到文件"""
        try:
            current_time = datetime.now()
            content = {
                "word": word_data,
                "quote": quote_data,
                "generated_at": current_time.isoformat(),
                "date": current_time.strftime('%Y-%m-%d'),
                "timestamp": current_time.timestamp()
            }
            
            success = self._safe_write_json(self.current_content_file, content)
            if success:
                logger.info(f"当前内容已保存到文件: {self.current_content_file}")
                
                # 同时保存到历史记录
                self._save_to_history(content)
                
                # 记录更新日志
                self._log_update(content)
                
            return success
            
        except Exception as e:
            logger.error(f"保存当前内容失败: {e}")
            return False
    
    def load_current_content(self) -> Optional[Dict]:
        """从文件加载当前内容"""
        try:
            content = self._safe_read_json(self.current_content_file)
            if content:
                logger.info(f"从文件加载当前内容: {content.get('date', 'Unknown')}")
                return content
            else:
                logger.warning("当前内容文件不存在或为空")
                return None
                
        except Exception as e:
            logger.error(f"加载当前内容失败: {e}")
            return None
    
    def is_content_current(self) -> bool:
        """检查当前内容是否是今天的"""
        try:
            content = self.load_current_content()
            if not content:
                return False
                
            content_date = content.get('date')
            today = datetime.now().strftime('%Y-%m-%d')
            
            is_current = content_date == today
            logger.info(f"内容日期检查: {content_date} vs {today} = {'当前' if is_current else '过期'}")
            return is_current
            
        except Exception as e:
            logger.error(f"检查内容日期失败: {e}")
            return False
    
    def _save_to_history(self, content: Dict) -> bool:
        """保存内容到历史记录"""
        try:
            history = self._safe_read_json(self.content_history_file) or {}
            
            date_key = content['date']
            history[date_key] = content
            
            # 只保留最近30天的历史记录
            cutoff_date = datetime.now() - timedelta(days=30)
            cutoff_str = cutoff_date.strftime('%Y-%m-%d')
            
            # 清理旧记录
            keys_to_remove = [k for k in history.keys() if k < cutoff_str]
            for key in keys_to_remove:
                del history[key]
            
            success = self._safe_write_json(self.content_history_file, history)
            if success:
                logger.info(f"内容已保存到历史记录: {date_key}")
            
            return success
            
        except Exception as e:
            logger.error(f"保存历史记录失败: {e}")
            return False
    
    def _log_update(self, content: Dict) -> bool:
        """记录更新日志"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "date": content['date'],
                "word": content['word'].get('word', 'Unknown'),
                "word_source": content['word'].get('source', 'Unknown'),
                "quote_author": content['quote'].get('author', 'Unknown'),
                "quote_source": content['quote'].get('source', 'Unknown')
            }
            
            # 读取现有日志
            logs = self._safe_read_json(self.update_log_file) or {"updates": []}
            
            # 添加新日志条目
            logs["updates"].append(log_entry)
            
            # 只保留最近100条记录
            if len(logs["updates"]) > 100:
                logs["updates"] = logs["updates"][-100:]
            
            success = self._safe_write_json(self.update_log_file, logs)
            if success:
                logger.info(f"更新日志已记录: {log_entry['word']} ({log_entry['word_source']})")
            
            return success
            
        except Exception as e:
            logger.error(f"记录更新日志失败: {e}")
            return False
    
    def save_system_status(self, status: Dict) -> bool:
        """保存系统状态"""
        try:
            status_data = {
                **status,
                "last_updated": datetime.now().isoformat(),
                "timestamp": datetime.now().timestamp()
            }
            
            success = self._safe_write_json(self.system_status_file, status_data)
            if success:
                logger.debug("系统状态已保存")
            
            return success
            
        except Exception as e:
            logger.error(f"保存系统状态失败: {e}")
            return False
    
    def load_system_status(self) -> Optional[Dict]:
        """加载系统状态"""
        try:
            return self._safe_read_json(self.system_status_file)
        except Exception as e:
            logger.error(f"加载系统状态失败: {e}")
            return None
    
    def get_content_history(self, days: int = 7) -> List[Dict]:
        """获取内容历史记录"""
        try:
            history = self._safe_read_json(self.content_history_file) or {}
            
            # 获取最近N天的记录
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff_date.strftime('%Y-%m-%d')
            
            recent_history = []
            for date_key, content in history.items():
                if date_key >= cutoff_str:
                    recent_history.append(content)
            
            # 按日期排序
            recent_history.sort(key=lambda x: x.get('date', ''), reverse=True)
            
            return recent_history
            
        except Exception as e:
            logger.error(f"获取内容历史失败: {e}")
            return []
    
    def get_update_logs(self, limit: int = 20) -> List[Dict]:
        """获取更新日志"""
        try:
            logs = self._safe_read_json(self.update_log_file) or {"updates": []}
            
            # 返回最近的N条记录
            updates = logs.get("updates", [])
            return updates[-limit:] if len(updates) > limit else updates
            
        except Exception as e:
            logger.error(f"获取更新日志失败: {e}")
            return []
    
    def cleanup_old_files(self, days: int = 30) -> bool:
        """清理旧文件"""
        try:
            cleaned_count = 0
            
            # 清理历史记录
            history = self._safe_read_json(self.content_history_file) or {}
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff_date.strftime('%Y-%m-%d')
            
            original_count = len(history)
            history = {k: v for k, v in history.items() if k >= cutoff_str}
            cleaned_count += original_count - len(history)
            
            if cleaned_count > 0:
                self._safe_write_json(self.content_history_file, history)
                logger.info(f"清理了 {cleaned_count} 条旧历史记录")
            
            return True
            
        except Exception as e:
            logger.error(f"清理旧文件失败: {e}")
            return False
    
    def get_file_stats(self) -> Dict:
        """获取文件统计信息"""
        try:
            stats = {}
            
            files_to_check = [
                ("current_content", self.current_content_file),
                ("content_history", self.content_history_file),
                ("system_status", self.system_status_file),
                ("update_log", self.update_log_file)
            ]
            
            for name, file_path in files_to_check:
                if file_path.exists():
                    stat = file_path.stat()
                    stats[name] = {
                        "exists": True,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    }
                else:
                    stats[name] = {"exists": False}
            
            return stats
            
        except Exception as e:
            logger.error(f"获取文件统计失败: {e}")
            return {}