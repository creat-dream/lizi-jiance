"""
数据导出模块 - 支持导出Excel/CSV
"""
import pandas as pd
import csv
import os
from typing import List, Dict, Any
from datetime import datetime


class DataExporter:
    """数据导出器"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def export_to_excel(self, file_path: str) -> bool:
        """
        导出所有数据到Excel文件
        
        Args:
            file_path: 保存路径
            
        Returns:
            是否导出成功
        """
        try:
            reports = self.data_manager.get_all_reports()
            
            if not reports:
                return False
            
            # 创建Excel写入器
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # 1. 导出报告汇总表
                summary_data = []
                for report in reports:
                    summary_data.append({
                        'COA编号': report.get('coa_no', ''),
                        '材料批号': report.get('lot_no', ''),
                        '顾客名称': report.get('customer', ''),
                        '材料牌号': report.get('brand', ''),
                        '发货日期': report.get('delivery_date', ''),
                        '检测项目数': len(report.get('test_items', [])),
                        '解析日期': report.get('parse_date', '')
                    })
                
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name='报告汇总', index=False)
                
                # 2. 导出详细检测数据
                detail_data = []
                for report in reports:
                    lot_no = report.get('lot_no', '')
                    coa_no = report.get('coa_no', '')
                    customer = report.get('customer', '')
                    brand = report.get('brand', '')
                    
                    for item in report.get('test_items', []):
                        detail_data.append({
                            '材料批号': lot_no,
                            'COA编号': coa_no,
                            '顾客名称': customer,
                            '材料牌号': brand,
                            '检测项目': item.get('name', ''),
                            '英文名称': item.get('name_en', ''),
                            '单位': item.get('unit', ''),
                            '执行标准': item.get('standard', ''),
                            '测试条件': item.get('condition', ''),
                            '技术指标': item.get('specification', ''),
                            '检测结果': item.get('result', ''),
                            '结论': item.get('conclusion', '')
                        })
                
                df_detail = pd.DataFrame(detail_data)
                df_detail.to_excel(writer, sheet_name='检测详情', index=False)
                
                # 3. 导出趋势数据表（按检测项目）
                test_items = self.data_manager.get_all_test_items()
                for item_name in test_items:
                    trend_data = self.data_manager.get_trend_data(item_name)
                    if trend_data.get('count', 0) > 0:
                        trend_df = pd.DataFrame({
                            '材料批号': trend_data['lot_numbers'],
                            '检测结果': trend_data['values'],
                            '单位': trend_data['unit']
                        })
                        # 工作表名称不能超过31个字符
                        sheet_name = f"趋势_{item_name[:20]}"
                        trend_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            return True
        except Exception as e:
            print(f"导出Excel失败: {e}")
            return False
    
    def export_to_csv(self, file_path: str, data_type: str = 'detail') -> bool:
        """
        导出数据到CSV文件
        
        Args:
            file_path: 保存路径
            data_type: 数据类型 - 'summary'(汇总) / 'detail'(详情) / 'trend'(趋势)
            
        Returns:
            是否导出成功
        """
        try:
            reports = self.data_manager.get_all_reports()
            
            if not reports:
                return False
            
            if data_type == 'summary':
                # 导出汇总数据
                data = []
                for report in reports:
                    data.append({
                        'COA编号': report.get('coa_no', ''),
                        '材料批号': report.get('lot_no', ''),
                        '顾客名称': report.get('customer', ''),
                        '材料牌号': report.get('brand', ''),
                        '发货日期': report.get('delivery_date', ''),
                        '检测项目数': len(report.get('test_items', [])),
                        '解析日期': report.get('parse_date', '')
                    })
                df = pd.DataFrame(data)
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
                
            elif data_type == 'detail':
                # 导出详细数据
                data = []
                for report in reports:
                    for item in report.get('test_items', []):
                        data.append({
                            '材料批号': report.get('lot_no', ''),
                            'COA编号': report.get('coa_no', ''),
                            '顾客名称': report.get('customer', ''),
                            '材料牌号': report.get('brand', ''),
                            '检测项目': item.get('name', ''),
                            '单位': item.get('unit', ''),
                            '技术指标': item.get('specification', ''),
                            '检测结果': item.get('result', ''),
                            '结论': item.get('conclusion', '')
                        })
                df = pd.DataFrame(data)
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
                
            elif data_type == 'trend':
                # 导出所有趋势数据
                test_items = self.data_manager.get_all_test_items()
                all_trend_data = []
                
                for item_name in test_items:
                    trend_data = self.data_manager.get_trend_data(item_name)
                    for i, lot_no in enumerate(trend_data['lot_numbers']):
                        all_trend_data.append({
                            '检测项目': item_name,
                            '材料批号': lot_no,
                            '检测结果': trend_data['values'][i],
                            '单位': trend_data['unit']
                        })
                
                df = pd.DataFrame(all_trend_data)
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
            
            return True
        except Exception as e:
            print(f"导出CSV失败: {e}")
            return False
    
    def export_trend_to_csv(self, file_path: str, item_name: str) -> bool:
        """
        导出单个检测项目的趋势数据到CSV
        
        Args:
            file_path: 保存路径
            item_name: 检测项目名称
            
        Returns:
            是否导出成功
        """
        try:
            trend_data = self.data_manager.get_trend_data(item_name)
            
            if trend_data.get('count', 0) == 0:
                return False
            
            df = pd.DataFrame({
                '材料批号': trend_data['lot_numbers'],
                '检测结果': trend_data['values'],
                '单位': trend_data['unit']
            })
            
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            return True
        except Exception as e:
            print(f"导出趋势数据失败: {e}")
            return False
