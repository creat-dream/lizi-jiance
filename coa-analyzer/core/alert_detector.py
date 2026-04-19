"""
告警检测模块 - 检测数值是否超出阈值
"""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime


class AlertDetector:
    """告警检测器"""
    
    def __init__(self, config_path: str = "config/settings.json"):
        self.config_path = config_path
        self.thresholds = {}
        self.alerts = []
        self._load_thresholds()
    
    def _load_thresholds(self):
        """加载阈值配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.thresholds = config.get("thresholds", {})
            except Exception as e:
                print(f"加载阈值配置失败: {e}")
                self.thresholds = {}
    
    def save_thresholds(self):
        """保存阈值配置"""
        try:
            config = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            config["thresholds"] = self.thresholds
            
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存阈值配置失败: {e}")
            return False
    
    def set_threshold(self, item_name: str, min_val: Optional[float], max_val: Optional[float]):
        """
        设置检测项目的阈值
        
        Args:
            item_name: 检测项目名称
            min_val: 最小值，None表示不限制
            max_val: 最大值，None表示不限制
        """
        self.thresholds[item_name] = {
            "min": min_val,
            "max": max_val
        }
        self.save_thresholds()
    
    def get_threshold(self, item_name: str) -> Dict[str, Any]:
        """
        获取检测项目的阈值
        
        Args:
            item_name: 检测项目名称
            
        Returns:
            阈值配置
        """
        return self.thresholds.get(item_name, {"min": None, "max": None})
    
    def get_all_thresholds(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有阈值配置
        
        Returns:
            所有阈值配置
        """
        return self.thresholds.copy()
    
    def check_value(self, item_name: str, value: float) -> Optional[Dict[str, Any]]:
        """
        检查单个数值是否超出阈值
        
        Args:
            item_name: 检测项目名称
            value: 检测数值
            
        Returns:
            如果超出阈值返回告警信息，否则返回None
        """
        threshold = self.get_threshold(item_name)
        min_val = threshold.get("min")
        max_val = threshold.get("max")
        
        # 如果没有设置阈值，不告警
        if min_val is None and max_val is None:
            return None
        
        alert = None
        
        if min_val is not None and value < min_val:
            alert = {
                "item_name": item_name,
                "value": value,
                "threshold_type": "min",
                "threshold": min_val,
                "message": f"{item_name} 数值 {value} 低于最小阈值 {min_val}",
                "timestamp": datetime.now().isoformat()
            }
        elif max_val is not None and value > max_val:
            alert = {
                "item_name": item_name,
                "value": value,
                "threshold_type": "max",
                "threshold": max_val,
                "message": f"{item_name} 数值 {value} 高于最大阈值 {max_val}",
                "timestamp": datetime.now().isoformat()
            }
        
        if alert:
            self.alerts.append(alert)
        
        return alert
    
    def check_report(self, report_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        检查整份报告的告警
        
        Args:
            report_data: 报告数据
            
        Returns:
            告警列表
        """
        alerts = []
        lot_no = report_data.get("lot_no", "Unknown")
        
        for item in report_data.get("test_items", []):
            item_name = item.get("name")
            result = item.get("result")
            
            if item_name and result is not None and isinstance(result, (int, float)):
                alert = self.check_value(item_name, float(result))
                if alert:
                    alert["lot_no"] = lot_no
                    alerts.append(alert)
        
        return alerts
    
    def check_reports(self, reports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量检查多份报告
        
        Args:
            reports: 报告列表
            
        Returns:
            所有告警列表
        """
        all_alerts = []
        for report in reports:
            alerts = self.check_report(report)
            all_alerts.extend(alerts)
        return all_alerts
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """
        获取所有历史告警
        
        Returns:
            告警列表
        """
        return self.alerts.copy()
    
    def clear_alerts(self):
        """清空告警记录"""
        self.alerts = []
    
    def remove_threshold(self, item_name: str):
        """
        删除检测项目的阈值配置
        
        Args:
            item_name: 检测项目名称
        """
        if item_name in self.thresholds:
            del self.thresholds[item_name]
            self.save_thresholds()
