"""
主窗口 - COA报告分析系统主界面
"""
import sys
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QListWidget, QComboBox,
    QFileDialog, QMessageBox, QTabWidget, QTableWidget,
    QTableWidgetItem, QGroupBox, QSplitter, QLineEdit,
    QDoubleSpinBox, QFormLayout, QDialog, QDialogButtonBox,
    QHeaderView, QProgressBar, QTextEdit, QMenu
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pdf_parser import PDFParser
from core.data_manager import DataManager
from core.alert_detector import AlertDetector
from core.llm_client import LLMClient
from core.data_exporter import DataExporter
from core.backup_manager import BackupManager
from core.i18n import get_i18n, _
from ui.trend_chart import TrendChart


class ParseWorker(QThread):
    """后台解析工作线程"""
    progress = pyqtSignal(int)
    result = pyqtSignal(dict)
    finished_signal = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, pdf_paths, llm_client):
        super().__init__()
        self.pdf_paths = pdf_paths
        self.llm_client = llm_client
        self.parser = PDFParser(llm_client)
    
    def run(self):
        try:
            total = len(self.pdf_paths)
            for i, path in enumerate(self.pdf_paths):
                self.progress.emit(int((i / total) * 100))
                try:
                    result = self.parser.parse_pdf(path)
                    if result:
                        self.result.emit(result)
                except Exception as e:
                    self.error.emit(f"解析失败 {path}: {str(e)}")
            self.progress.emit(100)
        finally:
            self.finished_signal.emit()


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化国际化
        self.i18n = get_i18n()
        
        self.setWindowTitle(_('app_name'))
        self.setMinimumSize(1200, 800)
        
        # 初始化组件
        self.data_manager = DataManager()
        self.alert_detector = AlertDetector()
        self.data_exporter = DataExporter(self.data_manager)
        self.backup_manager = BackupManager()
        self.llm_client = None
        self.parser = None
        self.parse_worker = None
        
        # 加载配置
        self._load_config()
        
        # 自动备份
        self._auto_backup()
        
        # 设置UI
        self._setup_ui()
        self._load_data()
    
    def _load_config(self):
        """加载配置"""
        import json
        config_path = "config/settings.json"
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                api_config = config.get("api_config", {})
                if api_config.get("api_key"):
                    self.llm_client = LLMClient(
                        api_key=api_config["api_key"],
                        api_url=api_config["api_url"],
                        model=api_config.get("model", "qwen-turbo")
                    )
                    self.parser = PDFParser(self.llm_client)
    
    def _auto_backup(self):
        """执行自动备份"""
        backup_path = self.backup_manager.auto_backup()
        if backup_path:
            print(f"自动备份已创建: {backup_path}")
    
    def _setup_ui(self):
        """设置UI"""
        # 创建菜单栏
        self._create_menu_bar()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 添加标签页
        self.tab_widget.addTab(self._create_import_tab(), "文件导入")
        self.tab_widget.addTab(self._create_reports_tab(), "报告列表")
        self.tab_widget.addTab(self._create_trend_tab(), "趋势分析")
        self.tab_widget.addTab(self._create_alert_tab(), "告警设置")
    
    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu(_('menu_file'))
        
        import_action = QAction(_('action_import_pdf'), self)
        import_action.triggered.connect(self._on_import_clicked)
        file_menu.addAction(import_action)
        
        import_folder_action = QAction(_('action_import_folder'), self)
        import_folder_action.triggered.connect(self._on_import_folder_clicked)
        file_menu.addAction(import_folder_action)
        
        file_menu.addSeparator()
        
        # 导出子菜单
        export_menu = QMenu(_('action_export_excel'), self)
        file_menu.addMenu(export_menu)
        
        export_excel_action = QAction("Excel", self)
        export_excel_action.triggered.connect(self._on_export_excel)
        export_menu.addAction(export_excel_action)
        
        export_csv_action = QAction("CSV", self)
        export_csv_action.triggered.connect(self._on_export_csv)
        export_menu.addAction(export_csv_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction(_('action_exit'), self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 设置菜单
        settings_menu = menubar.addMenu(_('menu_settings'))
        
        api_action = QAction(_('action_api_config'), self)
        api_action.triggered.connect(self._on_api_config_clicked)
        settings_menu.addAction(api_action)
        
        # 数据备份
        backup_action = QAction("数据备份", self)
        backup_action.triggered.connect(self._on_backup_manager)
        settings_menu.addAction(backup_action)
        
        # 语言菜单
        language_menu = menubar.addMenu(_('menu_language'))
        
        lang_group = QAction(self)
        lang_group.setCheckable(True)
        
        for lang_code, lang_name in self.i18n.get_supported_languages().items():
            action = QAction(lang_name, self)
            action.setCheckable(True)
            action.setChecked(lang_code == self.i18n.get_current_language())
            action.triggered.connect(lambda checked, code=lang_code: self._on_language_changed(code))
            language_menu.addAction(action)
    
    def _create_import_tab(self):
        """创建导入标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("选择PDF文件")
        self.import_btn.clicked.connect(self._on_import_clicked)
        btn_layout.addWidget(self.import_btn)
        
        self.import_folder_btn = QPushButton("选择文件夹")
        self.import_folder_btn.clicked.connect(self._on_import_folder_clicked)
        btn_layout.addWidget(self.import_folder_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 日志区域
        log_group = QGroupBox("处理日志")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        layout.addWidget(log_group)
        
        return widget
    
    def _create_reports_tab(self):
        """创建报告列表标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self._load_data)
        toolbar_layout.addWidget(refresh_btn)
        
        delete_btn = QPushButton("删除选中")
        delete_btn.clicked.connect(self._on_delete_report)
        toolbar_layout.addWidget(delete_btn)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # 报告列表表格
        self.reports_table = QTableWidget()
        self.reports_table.setColumnCount(6)
        self.reports_table.setHorizontalHeaderLabels([
            "材料批号", "COA编号", "顾客名称", "材料牌号", "检测项目数", "操作"
        ])
        self.reports_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.reports_table)
        
        return widget
    
    def _create_trend_tab(self):
        """创建趋势分析标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 控制面板
        control_layout = QHBoxLayout()
        
        control_layout.addWidget(QLabel("检测项目:"))
        self.item_combo = QComboBox()
        self.item_combo.setMinimumWidth(200)
        self.item_combo.currentTextChanged.connect(self._on_item_changed)
        control_layout.addWidget(self.item_combo)
        
        control_layout.addStretch()
        
        export_btn = QPushButton("导出图表")
        export_btn.clicked.connect(self._on_export_chart)
        control_layout.addWidget(export_btn)
        
        layout.addLayout(control_layout)
        
        # 图表区域
        self.trend_chart = TrendChart()
        layout.addWidget(self.trend_chart)
        
        return widget
    
    def _create_alert_tab(self):
        """创建告警设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 说明标签
        layout.addWidget(QLabel("设置各检测项目的阈值范围，当数值超出范围时将触发告警:"))
        
        # 阈值设置表格
        self.threshold_table = QTableWidget()
        self.threshold_table.setColumnCount(4)
        self.threshold_table.setHorizontalHeaderLabels(["检测项目", "最小值", "最大值", "操作"])
        self.threshold_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.threshold_table)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("添加阈值")
        add_btn.clicked.connect(self._on_add_threshold)
        btn_layout.addWidget(add_btn)
        
        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self._on_save_thresholds)
        btn_layout.addWidget(save_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 告警记录
        alert_group = QGroupBox("告警记录")
        alert_layout = QVBoxLayout(alert_group)
        
        self.alert_list = QListWidget()
        alert_layout.addWidget(self.alert_list)
        
        clear_alert_btn = QPushButton("清空告警")
        clear_alert_btn.clicked.connect(self._on_clear_alerts)
        alert_layout.addWidget(clear_alert_btn)
        
        layout.addWidget(alert_group)
        
        # 加载现有阈值
        self._load_thresholds()
        
        return widget
    
    def _load_data(self):
        """加载数据"""
        # 加载报告列表
        reports = self.data_manager.get_all_reports()
        self.reports_table.setRowCount(len(reports))
        
        for i, report in enumerate(reports):
            self.reports_table.setItem(i, 0, QTableWidgetItem(report.get("lot_no", "")))
            self.reports_table.setItem(i, 1, QTableWidgetItem(report.get("coa_no", "")))
            self.reports_table.setItem(i, 2, QTableWidgetItem(report.get("customer", "")))
            self.reports_table.setItem(i, 3, QTableWidgetItem(report.get("brand", "")))
            self.reports_table.setItem(i, 4, QTableWidgetItem(str(len(report.get("test_items", [])))))
            
            view_btn = QPushButton("查看")
            view_btn.clicked.connect(lambda checked, r=report: self._on_view_report(r))
            self.reports_table.setCellWidget(i, 5, view_btn)
        
        # 加载检测项目列表
        self.item_combo.clear()
        items = self.data_manager.get_all_test_items()
        self.item_combo.addItems(items)
    
    def _load_thresholds(self):
        """加载阈值设置"""
        thresholds = self.alert_detector.get_all_thresholds()
        self.threshold_table.setRowCount(len(thresholds))
        
        for i, (item_name, threshold) in enumerate(thresholds.items()):
            self.threshold_table.setItem(i, 0, QTableWidgetItem(item_name))
            
            min_val = threshold.get("min")
            max_val = threshold.get("max")
            
            min_item = QTableWidgetItem(str(min_val) if min_val is not None else "")
            self.threshold_table.setItem(i, 1, min_item)
            
            max_item = QTableWidgetItem(str(max_val) if max_val is not None else "")
            self.threshold_table.setItem(i, 2, max_item)
            
            del_btn = QPushButton("删除")
            del_btn.clicked.connect(lambda checked, name=item_name: self._on_delete_threshold(name))
            self.threshold_table.setCellWidget(i, 3, del_btn)
    
    def _on_import_clicked(self):
        """导入PDF文件"""
        if not self.llm_client:
            QMessageBox.warning(self, "警告", "请先配置API密钥")
            return
        
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择PDF文件", "", "PDF Files (*.pdf)"
        )
        
        if files:
            self._parse_pdfs(files)
    
    def _on_import_folder_clicked(self):
        """导入文件夹"""
        if not self.llm_client:
            QMessageBox.warning(self, "警告", "请先配置API密钥")
            return
        
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        
        if folder:
            pdf_files = []
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(root, file))
            
            if pdf_files:
                self._parse_pdfs(pdf_files)
            else:
                QMessageBox.information(self, "提示", "未找到PDF文件")
    
    def _parse_pdfs(self, pdf_paths):
        """解析PDF文件"""
        self.import_btn.setEnabled(False)
        self.import_folder_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.log_text.clear()
        
        self.parse_worker = ParseWorker(pdf_paths, self.llm_client)
        self.parse_worker.progress.connect(self.progress_bar.setValue)
        self.parse_worker.result.connect(self._on_parse_result)
        self.parse_worker.error.connect(self._on_parse_error)
        self.parse_worker.finished_signal.connect(self._on_parse_finished)
        self.parse_worker.start()
    
    def _on_parse_result(self, result):
        """解析结果回调"""
        # 保存到数据管理器
        self.data_manager.save_report(result)
        
        # 检查告警
        alerts = self.alert_detector.check_report(result)
        for alert in alerts:
            self.alert_list.addItem(alert["message"])
        
        # 记录日志
        self.log_text.append(f"✓ 解析成功: {result.get('lot_no', 'Unknown')} - {result.get('file_name', '')}")
    
    def _on_parse_error(self, error_msg):
        """解析错误回调"""
        self.log_text.append(f"✗ {error_msg}")
    
    def _on_parse_finished(self):
        """解析完成回调"""
        self.import_btn.setEnabled(True)
        self.import_folder_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.log_text.append("\n处理完成!")
        
        # 刷新数据
        self._load_data()
        
        QMessageBox.information(self, "完成", "PDF解析完成!")
    
    def _on_delete_report(self):
        """删除报告"""
        current_row = self.reports_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要删除的报告")
            return
        
        lot_no = self.reports_table.item(current_row, 0).text()
        
        reply = QMessageBox.question(
            self, "确认", f"确定要删除批号为 {lot_no} 的报告吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.data_manager.delete_report(lot_no)
            self._load_data()
    
    def _on_view_report(self, report):
        """查看报告详情"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"报告详情 - {report.get('lot_no', '')}")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # 基本信息
        info_text = f"""
        <b>COA编号:</b> {report.get('coa_no', '')}<br>
        <b>材料批号:</b> {report.get('lot_no', '')}<br>
        <b>顾客名称:</b> {report.get('customer', '')}<br>
        <b>材料牌号:</b> {report.get('brand', '')}<br>
        <b>发货日期:</b> {report.get('delivery_date', '')}
        """
        info_label = QLabel(info_text)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info_label)
        
        # 检测项目表格
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["检测项目", "单位", "技术指标", "检测结果", "结论"])
        
        test_items = report.get("test_items", [])
        table.setRowCount(len(test_items))
        
        for i, item in enumerate(test_items):
            table.setItem(i, 0, QTableWidgetItem(item.get("name", "")))
            table.setItem(i, 1, QTableWidgetItem(item.get("unit", "")))
            table.setItem(i, 2, QTableWidgetItem(item.get("specification", "")))
            table.setItem(i, 3, QTableWidgetItem(str(item.get("result", ""))))
            table.setItem(i, 4, QTableWidgetItem(item.get("conclusion", "")))
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(table)
        
        # 关闭按钮
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn_box.rejected.connect(dialog.reject)
        layout.addWidget(btn_box)
        
        dialog.exec()
    
    def _on_item_changed(self, item_name):
        """检测项目改变"""
        if not item_name:
            return
        
        trend_data = self.data_manager.get_trend_data(item_name)
        threshold = self.alert_detector.get_threshold(item_name)
        
        self.trend_chart.plot_trend(
            trend_data,
            threshold_min=threshold.get("min"),
            threshold_max=threshold.get("max")
        )
    
    def _on_export_chart(self):
        """导出图表"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存图表", "", "PNG Files (*.png);;All Files (*)"
        )
        
        if file_path:
            self.trend_chart.export_image(file_path)
            QMessageBox.information(self, "成功", "图表已保存!")
    
    def _on_add_threshold(self):
        """添加阈值"""
        dialog = QDialog(self)
        dialog.setWindowTitle("添加阈值")
        layout = QFormLayout(dialog)
        
        # 检测项目
        item_combo = QComboBox()
        items = self.data_manager.get_all_test_items()
        item_combo.addItems(items)
        layout.addRow("检测项目:", item_combo)
        
        # 最小值
        min_spin = QDoubleSpinBox()
        min_spin.setRange(-999999, 999999)
        min_spin.setDecimals(4)
        min_spin.setSpecialValueText("无限制")
        layout.addRow("最小值:", min_spin)
        
        # 最大值
        max_spin = QDoubleSpinBox()
        max_spin.setRange(-999999, 999999)
        max_spin.setDecimals(4)
        max_spin.setSpecialValueText("无限制")
        layout.addRow("最大值:", max_spin)
        
        # 按钮
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        layout.addRow(btn_box)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            item_name = item_combo.currentText()
            min_val = min_spin.value() if min_spin.value() != min_spin.minimum() else None
            max_val = max_spin.value() if max_spin.value() != max_spin.minimum() else None
            
            self.alert_detector.set_threshold(item_name, min_val, max_val)
            self._load_thresholds()
    
    def _on_delete_threshold(self, item_name):
        """删除阈值"""
        self.alert_detector.remove_threshold(item_name)
        self._load_thresholds()
    
    def _on_save_thresholds(self):
        """保存阈值设置"""
        # 从表格读取阈值
        for i in range(self.threshold_table.rowCount()):
            item_name = self.threshold_table.item(i, 0).text()
            min_text = self.threshold_table.item(i, 1).text()
            max_text = self.threshold_table.item(i, 2).text()
            
            min_val = float(min_text) if min_text else None
            max_val = float(max_text) if max_text else None
            
            self.alert_detector.set_threshold(item_name, min_val, max_val)
        
        QMessageBox.information(self, "成功", "阈值设置已保存!")
    
    def _on_clear_alerts(self):
        """清空告警"""
        self.alert_detector.clear_alerts()
        self.alert_list.clear()
    
    def _on_api_config_clicked(self):
        """API配置"""
        dialog = QDialog(self)
        dialog.setWindowTitle("API配置")
        layout = QFormLayout(dialog)
        
        # API Key
        api_key_edit = QLineEdit()
        if self.llm_client:
            api_key_edit.setText(self.llm_client.api_key)
        layout.addRow("API Key:", api_key_edit)
        
        # API URL
        api_url_edit = QLineEdit()
        api_url_edit.setText("https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation")
        if self.llm_client:
            api_url_edit.setText(self.llm_client.api_url)
        layout.addRow("API URL:", api_url_edit)
        
        # Model
        model_edit = QLineEdit()
        model_edit.setText("qwen-turbo")
        if self.llm_client:
            model_edit.setText(self.llm_client.model)
        layout.addRow("Model:", model_edit)
        
        # 按钮
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        layout.addRow(btn_box)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 保存配置
            import json
            config_path = "config/settings.json"
            config = {}
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            config["api_config"] = {
                "provider": "通义千问",
                "api_key": api_key_edit.text(),
                "api_url": api_url_edit.text(),
                "model": model_edit.text()
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            # 重新初始化LLM客户端
            if api_key_edit.text():
                self.llm_client = LLMClient(
                    api_key=api_key_edit.text(),
                    api_url=api_url_edit.text(),
                    model=model_edit.text()
                )
                self.parser = PDFParser(self.llm_client)
            
            QMessageBox.information(self, _('msg_success'), _('msg_save_success'))
    
    def _on_export_excel(self):
        """导出Excel"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出Excel", "COA报告数据.xlsx", "Excel Files (*.xlsx)"
        )
        
        if file_path:
            if self.data_exporter.export_to_excel(file_path):
                QMessageBox.information(self, _('msg_success'), _('msg_export_success'))
            else:
                QMessageBox.warning(self, _('msg_warning'), _('msg_no_data'))
    
    def _on_export_csv(self):
        """导出CSV"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出CSV", "COA报告数据.csv", "CSV Files (*.csv)"
        )
        
        if file_path:
            if self.data_exporter.export_to_csv(file_path, 'detail'):
                QMessageBox.information(self, _('msg_success'), _('msg_export_success'))
            else:
                QMessageBox.warning(self, _('msg_warning'), _('msg_no_data'))
    
    def _on_language_changed(self, lang_code: str):
        """切换语言"""
        if lang_code != self.i18n.get_current_language():
            self.i18n.save_language(lang_code)
            QMessageBox.information(
                self, 
                _('msg_info'), 
                "语言设置已保存，重启程序后生效。\nLanguage setting saved, please restart the application."
            )
    
    def _on_backup_manager(self):
        """打开备份管理器"""
        dialog = QDialog(self)
        dialog.setWindowTitle("数据备份管理")
        dialog.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(dialog)
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        create_btn = QPushButton("创建备份")
        create_btn.clicked.connect(lambda: self._create_manual_backup(dialog))
        toolbar.addWidget(create_btn)
        
        restore_btn = QPushButton("恢复选中")
        restore_btn.clicked.connect(lambda: self._restore_selected_backup(backup_table, dialog))
        toolbar.addWidget(restore_btn)
        
        delete_btn = QPushButton("删除选中")
        delete_btn.clicked.connect(lambda: self._delete_selected_backup(backup_table))
        toolbar.addWidget(delete_btn)
        
        export_btn = QPushButton("导出备份")
        export_btn.clicked.connect(lambda: self._export_selected_backup(backup_table))
        toolbar.addWidget(export_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # 备份列表
        backup_table = QTableWidget()
        backup_table.setColumnCount(5)
        backup_table.setHorizontalHeaderLabels(["备份文件名", "备份时间", "文件大小", "记录数", "操作"])
        backup_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(backup_table)
        
        # 加载备份列表
        self._load_backup_list(backup_table)
        
        # 关闭按钮
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn_box.rejected.connect(dialog.reject)
        layout.addWidget(btn_box)
        
        dialog.exec()
    
    def _load_backup_list(self, table: QTableWidget):
        """加载备份列表"""
        backups = self.backup_manager.get_backup_list()
        table.setRowCount(len(backups))
        
        for i, backup in enumerate(backups):
            table.setItem(i, 0, QTableWidgetItem(backup['file_name']))
            table.setItem(i, 1, QTableWidgetItem(backup['backup_time']))
            table.setItem(i, 2, QTableWidgetItem(backup['file_size']))
            table.setItem(i, 3, QTableWidgetItem(str(backup['record_count'])))
            
            # 保存文件路径到item的data中
            for col in range(5):
                item = table.item(i, col)
                if item:
                    item.setData(Qt.ItemDataRole.UserRole, backup['file_path'])
    
    def _create_manual_backup(self, parent_dialog: QDialog):
        """创建手动备份"""
        backup_path = self.backup_manager.create_backup()
        if backup_path:
            QMessageBox.information(parent_dialog, "成功", f"备份创建成功!\n{backup_path}")
            # 刷新列表
            backup_table = parent_dialog.findChild(QTableWidget)
            if backup_table:
                self._load_backup_list(backup_table)
        else:
            QMessageBox.warning(parent_dialog, "失败", "备份创建失败!")
    
    def _restore_selected_backup(self, table: QTableWidget, parent_dialog: QDialog):
        """恢复选中的备份"""
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(parent_dialog, "警告", "请先选择要恢复的备份")
            return
        
        file_path = table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        file_name = table.item(current_row, 0).text()
        
        reply = QMessageBox.question(
            parent_dialog, 
            "确认", 
            f"确定要恢复备份 {file_name} 吗？\n当前数据将被覆盖!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.backup_manager.restore_backup(file_path):
                QMessageBox.information(parent_dialog, "成功", "数据恢复成功!\n请重启程序以加载新数据。")
                parent_dialog.accept()
            else:
                QMessageBox.warning(parent_dialog, "失败", "数据恢复失败!")
    
    def _delete_selected_backup(self, table: QTableWidget):
        """删除选中的备份"""
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要删除的备份")
            return
        
        file_path = table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        file_name = table.item(current_row, 0).text()
        
        reply = QMessageBox.question(
            self, 
            "确认", 
            f"确定要删除备份 {file_name} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.backup_manager.delete_backup(file_path):
                QMessageBox.information(self, "成功", "备份已删除!")
                self._load_backup_list(table)
            else:
                QMessageBox.warning(self, "失败", "删除备份失败!")
    
    def _export_selected_backup(self, table: QTableWidget):
        """导出选中的备份"""
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要导出的备份")
            return
        
        file_path = table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        file_name = table.item(current_row, 0).text()
        
        export_path, _ = QFileDialog.getSaveFileName(
            self, "导出备份", file_name, "JSON Files (*.json)"
        )
        
        if export_path:
            if self.backup_manager.export_backup(file_path, export_path):
                QMessageBox.information(self, "成功", f"备份已导出到:\n{export_path}")
            else:
                QMessageBox.warning(self, "失败", "导出备份失败!")
