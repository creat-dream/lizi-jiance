"""
数据管理模块 - JSON数据存储和查询
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional


class DataManager:
    """数据管理器"""
    
    def __init__(self, data_path: str = "data/reports.json"):
        self.data_path = data_path
        self.data = []
        self._load_data()
    
    def _load_data(self):
        """加载数据"""
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"加载数据失败: {e}")
                self.data = []
        else:
            self.data = []
    
    def _save_data(self):
        """保存数据"""
        try:
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存数据失败: {e}")
            raise
    
    def save_report(self, report_data: Dict[str, Any]) -> bool:
        """
        保存报告数据
        
        Args:
            report_data: 报告数据
            
        Returns:
            是否保存成功
        """
        # 添加解析时间
        report_data["parse_date"] = datetime.now().isoformat()
        
        # 检查是否已存在（按lot_no）
        existing_idx = None
        for idx, report in enumerate(self.data):
            if report.get("lot_no") == report_data.get("lot_no"):
                existing_idx = idx
                break
        
        if existing_idx is not None:
            # 更新现有记录
            self.data[existing_idx] = report_data
            print(f"更新报告: {report_data.get('lot_no')}")
        else:
            # 添加新记录
            self.data.append(report_data)
            print(f"新增报告: {report_data.get('lot_no')}")
        
        self._save_data()
        return True
    
    def save_reports(self, reports: List[Dict[str, Any]]) -> int:
        """
        批量保存报告数据
        
        Args:
            reports: 报告数据列表
            
        Returns:
            保存成功的数量
        """
        count = 0
        for report in reports:
            if self.save_report(report):
                count += 1
        return count
    
    def get_all_reports(self) -> List[Dict[str, Any]]:
        """
        获取所有报告
        
        Returns:
            报告列表
        """
        return self.data.copy()
    
    def get_report_by_lot(self, lot_no: str) -> Optional[Dict[str, Any]]:
        """
        按材料批号获取报告
        
        Args:
            lot_no: 材料批号
            
        Returns:
            报告数据
        """
        for report in self.data:
            if report.get("lot_no") == lot_no:
                return report.copy()
        return None
    
    def get_all_lot_numbers(self) -> List[str]:
        """
        获取所有材料批号列表
        
        Returns:
            批号列表
        """
        return [report.get("lot_no", "") for report in self.data if report.get("lot_no")]
    
    def get_all_test_items(self) -> List[str]:
        """
        获取所有检测项目名称
        
        Returns:
            检测项目名称列表
        """
        items = set()
        for report in self.data:
            for item in report.get("test_items", []):
                if item.get("name"):
                    items.add(item["name"])
        return sorted(list(items))
    
    def get_trend_data(self, item_name: str) -> Dict[str, Any]:
        """
        获取某个检测项目的趋势数据
        
        Args:
            item_name: 检测项目名称
            
        Returns:
            趋势数据，包含lot_no列表和对应的数值列表
        """
        lot_numbers = []
        values = []
        units = ""
        
        # 按lot_no排序
        sorted_reports = sorted(self.data, key=lambda x: x.get("lot_no", ""))
        
        for report in sorted_reports:
            lot_no = report.get("lot_no")
            if not lot_no:
                continue
            
            for item in report.get("test_items", []):
                if item.get("name") == item_name:
                    result = item.get("result")
                    if result is not None and isinstance(result, (int, float)):
                        lot_numbers.append(lot_no)
                        values.append(float(result))
                        if not units and item.get("unit"):
                            units = item["unit"]
                    break
        
        return {
            "item_name": item_name,
            "unit": units,
            "lot_numbers": lot_numbers,
            "values": values,
            "count": len(values)
        }
    
    def delete_report(self, lot_no: str) -> bool:
        """
        删除报告
        
        Args:
            lot_no: 材料批号
            
        Returns:
            是否删除成功
        """
        for idx, report in enumerate(self.data):
            if report.get("lot_no") == lot_no:
                del self.data[idx]
                self._save_data()
                print(f"删除报告: {lot_no}")
                return True
        return False
    
    def clear_all(self):
        """清空所有数据"""
        self.data = []
        self._save_data()
        print("已清空所有数据")
