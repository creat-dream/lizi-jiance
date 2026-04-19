"""
数据备份模块 - 自动备份JSON数据
"""
import os
import json
import shutil
from datetime import datetime, timedelta
from typing import List, Optional
import glob


class BackupManager:
    """备份管理器"""
    
    def __init__(self, data_path: str = "data/reports.json", 
                 backup_dir: str = "data/backups",
                 max_backups: int = 10,
                 auto_backup_interval: int = 7):
        """
        初始化备份管理器
        
        Args:
            data_path: 数据文件路径
            backup_dir: 备份目录
            max_backups: 最大保留备份数量
            auto_backup_interval: 自动备份间隔（天）
        """
        self.data_path = data_path
        self.backup_dir = backup_dir
        self.max_backups = max_backups
        self.auto_backup_interval = auto_backup_interval
        
        # 确保备份目录存在
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, backup_name: str = None) -> Optional[str]:
        """
        创建备份
        
        Args:
            backup_name: 备份文件名（不含扩展名），默认使用时间戳
            
        Returns:
            备份文件路径，失败返回None
        """
        if not os.path.exists(self.data_path):
            print(f"数据文件不存在: {self.data_path}")
            return None
        
        # 生成备份文件名
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"reports_backup_{timestamp}"
        
        backup_path = os.path.join(self.backup_dir, f"{backup_name}.json")
        
        try:
            # 复制文件
            shutil.copy2(self.data_path, backup_path)
            print(f"备份创建成功: {backup_path}")
            
            # 清理旧备份
            self._cleanup_old_backups()
            
            return backup_path
        except Exception as e:
            print(f"创建备份失败: {e}")
            return None
    
    def restore_backup(self, backup_path: str) -> bool:
        """
        从备份恢复数据
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            是否恢复成功
        """
        if not os.path.exists(backup_path):
            print(f"备份文件不存在: {backup_path}")
            return False
        
        try:
            # 先创建当前数据的备份（防止误操作）
            if os.path.exists(self.data_path):
                self.create_backup("auto_before_restore")
            
            # 恢复数据
            shutil.copy2(backup_path, self.data_path)
            print(f"数据恢复成功: {backup_path} -> {self.data_path}")
            return True
        except Exception as e:
            print(f"恢复备份失败: {e}")
            return False
    
    def get_backup_list(self) -> List[dict]:
        """
        获取备份列表
        
        Returns:
            备份信息列表
        """
        backups = []
        
        if not os.path.exists(self.backup_dir):
            return backups
        
        pattern = os.path.join(self.backup_dir, "reports_backup_*.json")
        backup_files = glob.glob(pattern)
        
        for file_path in sorted(backup_files, reverse=True):
            try:
                stat = os.stat(file_path)
                file_name = os.path.basename(file_path)
                
                # 解析时间戳
                timestamp_str = file_name.replace("reports_backup_", "").replace(".json", "")
                try:
                    backup_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    time_str = backup_time.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    time_str = timestamp_str
                
                # 获取数据条数
                record_count = 0
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        record_count = len(data)
                except:
                    pass
                
                backups.append({
                    'file_name': file_name,
                    'file_path': file_path,
                    'backup_time': time_str,
                    'file_size': self._format_file_size(stat.st_size),
                    'record_count': record_count
                })
            except Exception as e:
                print(f"读取备份信息失败 {file_path}: {e}")
        
        return backups
    
    def delete_backup(self, backup_path: str) -> bool:
        """
        删除备份
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            是否删除成功
        """
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
                print(f"备份已删除: {backup_path}")
                return True
            return False
        except Exception as e:
            print(f"删除备份失败: {e}")
            return False
    
    def auto_backup(self) -> Optional[str]:
        """
        自动备份（检查间隔，必要时创建备份）
        
        Returns:
            备份文件路径，如果不需要备份返回None
        """
        # 检查是否需要自动备份
        last_backup_time = self._get_last_backup_time()
        
        if last_backup_time:
            days_since_last_backup = (datetime.now() - last_backup_time).days
            if days_since_last_backup < self.auto_backup_interval:
                return None  # 不需要备份
        
        return self.create_backup()
    
    def _get_last_backup_time(self) -> Optional[datetime]:
        """获取最后一次备份时间"""
        backups = self.get_backup_list()
        if not backups:
            return None
        
        # 最新的备份
        latest = backups[0]
        try:
            return datetime.strptime(latest['backup_time'], "%Y-%m-%d %H:%M:%S")
        except:
            return None
    
    def _cleanup_old_backups(self):
        """清理旧备份，只保留最新的max_backups个"""
        backups = self.get_backup_list()
        
        if len(backups) <= self.max_backups:
            return
        
        # 删除旧的备份
        backups_to_delete = backups[self.max_backups:]
        for backup in backups_to_delete:
            self.delete_backup(backup['file_path'])
    
    def _format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def export_backup(self, backup_path: str, export_path: str) -> bool:
        """
        导出备份到指定位置
        
        Args:
            backup_path: 备份文件路径
            export_path: 导出目标路径
            
        Returns:
            是否导出成功
        """
        try:
            shutil.copy2(backup_path, export_path)
            return True
        except Exception as e:
            print(f"导出备份失败: {e}")
            return False

