"""
多语言支持模块 - 中英文界面切换
"""
import json
import os


class I18n:
    """国际化支持类"""
    
    # 支持的语言
    LANGUAGES = {
        'zh': '中文',
        'en': 'English'
    }
    
    # 默认语言
    DEFAULT_LANG = 'zh'
    
    # 翻译字典
    TRANSLATIONS = {
        'zh': {
            'app_name': 'COA试验报告分析系统',
            'app_version': '版本 1.0.0',
            
            # 菜单
            'menu_file': '文件',
            'menu_settings': '设置',
            'menu_language': '语言',
            'menu_help': '帮助',
            
            # 文件菜单
            'action_import_pdf': '导入PDF',
            'action_import_folder': '导入文件夹',
            'action_export_excel': '导出Excel',
            'action_export_csv': '导出CSV',
            'action_exit': '退出',
            
            # 设置菜单
            'action_api_config': 'API配置',
            'action_threshold_settings': '阈值设置',
            
            # 语言菜单
            'lang_chinese': '中文',
            'lang_english': 'English',
            
            # 标签页
            'tab_import': '文件导入',
            'tab_reports': '报告列表',
            'tab_trend': '趋势分析',
            'tab_alerts': '告警设置',
            
            # 按钮
            'btn_select_pdf': '选择PDF文件',
            'btn_select_folder': '选择文件夹',
            'btn_refresh': '刷新',
            'btn_delete': '删除',
            'btn_view': '查看',
            'btn_export': '导出',
            'btn_export_chart': '导出图表',
            'btn_add': '添加',
            'btn_save': '保存',
            'btn_clear': '清空',
            'btn_ok': '确定',
            'btn_cancel': '取消',
            
            # 标签
            'label_test_item': '检测项目:',
            'label_lot_no': '材料批号',
            'label_coa_no': 'COA编号',
            'label_customer': '顾客名称',
            'label_brand': '材料牌号',
            'label_delivery_date': '发货日期',
            'label_test_count': '检测项目数',
            'label_min_value': '最小值',
            'label_max_value': '最大值',
            'label_api_key': 'API Key:',
            'label_api_url': 'API URL:',
            'label_model': '模型:',
            
            # 表格列
            'col_item_name': '检测项目',
            'col_item_name_en': '英文名称',
            'col_unit': '单位',
            'col_standard': '执行标准',
            'col_condition': '测试条件',
            'col_specification': '技术指标',
            'col_result': '检测结果',
            'col_conclusion': '结论',
            'col_operation': '操作',
            
            # 消息
            'msg_warning': '警告',
            'msg_info': '提示',
            'msg_error': '错误',
            'msg_success': '成功',
            'msg_confirm': '确认',
            'msg_no_api_key': '请先配置API密钥',
            'msg_parse_complete': 'PDF解析完成!',
            'msg_export_success': '导出成功!',
            'msg_save_success': '保存成功!',
            'msg_no_data': '无数据',
            'msg_select_report': '请先选择要删除的报告',
            'msg_confirm_delete': '确定要删除批号为 {} 的报告吗？',
            'msg_processing': '处理中...',
            'msg_parse_success': '✓ 解析成功: {} - {}',
            'msg_parse_error': '✗ {}',
            
            # 日志
            'log_processing_complete': '\n处理完成!',
            'log_group_title': '处理日志',
            
            # 告警
            'alert_title': '告警记录',
            'alert_below_min': '{} 数值 {} 低于最小阈值 {}',
            'alert_above_max': '{} 数值 {} 高于最大阈值 {}',
            
            # 图表
            'chart_title': '{} 趋势图',
            'chart_x_label': '材料批号',
            'chart_y_label': '数值',
            'chart_threshold_min': '下限: {}',
            'chart_threshold_max': '上限: {}',
        },
        'en': {
            'app_name': 'COA Report Analysis System',
            'app_version': 'Version 1.0.0',
            
            # Menu
            'menu_file': 'File',
            'menu_settings': 'Settings',
            'menu_language': 'Language',
            'menu_help': 'Help',
            
            # File menu
            'action_import_pdf': 'Import PDF',
            'action_import_folder': 'Import Folder',
            'action_export_excel': 'Export Excel',
            'action_export_csv': 'Export CSV',
            'action_exit': 'Exit',
            
            # Settings menu
            'action_api_config': 'API Config',
            'action_threshold_settings': 'Threshold Settings',
            
            # Language menu
            'lang_chinese': 'Chinese',
            'lang_english': 'English',
            
            # Tabs
            'tab_import': 'Import',
            'tab_reports': 'Reports',
            'tab_trend': 'Trend Analysis',
            'tab_alerts': 'Alert Settings',
            
            # Buttons
            'btn_select_pdf': 'Select PDF',
            'btn_select_folder': 'Select Folder',
            'btn_refresh': 'Refresh',
            'btn_delete': 'Delete',
            'btn_view': 'View',
            'btn_export': 'Export',
            'btn_export_chart': 'Export Chart',
            'btn_add': 'Add',
            'btn_save': 'Save',
            'btn_clear': 'Clear',
            'btn_ok': 'OK',
            'btn_cancel': 'Cancel',
            
            # Labels
            'label_test_item': 'Test Item:',
            'label_lot_no': 'LOT No.',
            'label_coa_no': 'COA No.',
            'label_customer': 'Customer',
            'label_brand': 'Brand',
            'label_delivery_date': 'Delivery Date',
            'label_test_count': 'Test Count',
            'label_min_value': 'Min Value',
            'label_max_value': 'Max Value',
            'label_api_key': 'API Key:',
            'label_api_url': 'API URL:',
            'label_model': 'Model:',
            
            # Table columns
            'col_item_name': 'Test Item',
            'col_item_name_en': 'Name (EN)',
            'col_unit': 'Unit',
            'col_standard': 'Standard',
            'col_condition': 'Condition',
            'col_specification': 'Specification',
            'col_result': 'Result',
            'col_conclusion': 'Conclusion',
            'col_operation': 'Operation',
            
            # Messages
            'msg_warning': 'Warning',
            'msg_info': 'Information',
            'msg_error': 'Error',
            'msg_success': 'Success',
            'msg_confirm': 'Confirm',
            'msg_no_api_key': 'Please configure API key first',
            'msg_parse_complete': 'PDF parsing completed!',
            'msg_export_success': 'Export successful!',
            'msg_save_success': 'Save successful!',
            'msg_no_data': 'No data',
            'msg_select_report': 'Please select a report to delete',
            'msg_confirm_delete': 'Are you sure to delete report with LOT No. {}?',
            'msg_processing': 'Processing...',
            'msg_parse_success': '✓ Parse success: {} - {}',
            'msg_parse_error': '✗ {}',
            
            # Log
            'log_processing_complete': '\nProcessing complete!',
            'log_group_title': 'Processing Log',
            
            # Alerts
            'alert_title': 'Alert Records',
            'alert_below_min': '{} value {} is below minimum threshold {}',
            'alert_above_max': '{} value {} is above maximum threshold {}',
            
            # Chart
            'chart_title': '{} Trend Chart',
            'chart_x_label': 'LOT Number',
            'chart_y_label': 'Value',
            'chart_threshold_min': 'Min: {}',
            'chart_threshold_max': 'Max: {}',
        }
    }
    
    def __init__(self, config_path: str = "config/settings.json"):
        self.config_path = config_path
        self.current_lang = self._load_language()
    
    def _load_language(self) -> str:
        """加载语言设置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    lang = config.get('language', self.DEFAULT_LANG)
                    if lang in self.LANGUAGES:
                        return lang
            except Exception as e:
                print(f"加载语言设置失败: {e}")
        return self.DEFAULT_LANG
    
    def save_language(self, lang: str):
        """保存语言设置"""
        if lang not in self.LANGUAGES:
            return False
        
        self.current_lang = lang
        
        try:
            config = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            config['language'] = lang
            
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存语言设置失败: {e}")
            return False
    
    def get_text(self, key: str, *args) -> str:
        """
        获取翻译文本
        
        Args:
            key: 翻译键
            *args: 格式化参数
            
        Returns:
            翻译后的文本
        """
        text = self.TRANSLATIONS.get(self.current_lang, {}).get(key, key)
        if args:
            try:
                text = text.format(*args)
            except:
                pass
        return text
    
    def get_current_language(self) -> str:
        """获取当前语言代码"""
        return self.current_lang
    
    def get_language_name(self, lang: str = None) -> str:
        """获取语言名称"""
        if lang is None:
            lang = self.current_lang
        return self.LANGUAGES.get(lang, lang)
    
    def get_supported_languages(self) -> dict:
        """获取支持的语言列表"""
        return self.LANGUAGES.copy()


# 全局实例
_i18n_instance = None

def get_i18n(config_path: str = "config/settings.json") -> I18n:
    """获取I18n单例实例"""
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18n(config_path)
    return _i18n_instance

def _(key: str, *args) -> str:
    """快捷翻译函数"""
    return get_i18n().get_text(key, *args)
