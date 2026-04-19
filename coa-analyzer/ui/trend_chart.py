"""
趋势图表组件 - 使用PyQtGraph绘制曲线图
"""
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from typing import Dict, Any, Optional, List


class TrendChart(QWidget):
    """趋势图表组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plot_widget = None
        self.threshold_lines = []
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建PyQtGraph绘图部件
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True)
        
        # 设置标签样式
        self.plot_widget.getAxis('bottom').setPen(pg.mkPen(color='k', width=1))
        self.plot_widget.getAxis('left').setPen(pg.mkPen(color='k', width=1))
        self.plot_widget.getAxis('bottom').setTextPen(pg.mkPen(color='k'))
        self.plot_widget.getAxis('left').setTextPen(pg.mkPen(color='k'))
        
        layout.addWidget(self.plot_widget)
    
    def plot_trend(self, trend_data: Dict[str, Any], 
                   threshold_min: Optional[float] = None,
                   threshold_max: Optional[float] = None):
        """
        绘制趋势图
        
        Args:
            trend_data: 趋势数据，包含lot_numbers和values
            threshold_min: 最小阈值线
            threshold_max: 最大阈值线
        """
        # 清除之前的绘图
        self.plot_widget.clear()
        self.threshold_lines = []
        
        lot_numbers = trend_data.get("lot_numbers", [])
        values = trend_data.get("values", [])
        item_name = trend_data.get("item_name", "")
        unit = trend_data.get("unit", "")
        
        if not lot_numbers or not values:
            self.plot_widget.setTitle("无数据")
            return
        
        # 设置标题和标签
        title = f"{item_name} 趋势图"
        if unit:
            title += f" ({unit})"
        self.plot_widget.setTitle(title, color='k', size='14pt')
        
        self.plot_widget.setLabel('left', '数值', color='k')
        self.plot_widget.setLabel('bottom', '材料批号', color='k')
        
        # 使用数字索引作为X轴
        x_data = list(range(len(lot_numbers)))
        
        # 绘制数据曲线
        pen = pg.mkPen(color=(0, 100, 200), width=2)
        scatter = pg.ScatterPlotItem(size=10, brush=pg.mkBrush(0, 100, 200))
        scatter.addPoints(x=x_data, y=values)
        
        line = self.plot_widget.plot(x=x_data, y=values, pen=pen, symbol='o', 
                                     symbolSize=8, symbolBrush=(0, 100, 200))
        
        # 添加阈值线
        if threshold_min is not None:
            min_line = self.plot_widget.addLine(
                y=threshold_min, 
                pen=pg.mkPen(color=(255, 0, 0), width=2, style=Qt.PenStyle.DashLine),
                label=f'下限: {threshold_min}',
                labelOpts={'color': (255, 0, 0), 'movable': True}
            )
            self.threshold_lines.append(min_line)
        
        if threshold_max is not None:
            max_line = self.plot_widget.addLine(
                y=threshold_max, 
                pen=pg.mkPen(color=(255, 0, 0), width=2, style=Qt.PenStyle.DashLine),
                label=f'上限: {threshold_max}',
                labelOpts={'color': (255, 0, 0), 'movable': True}
            )
            self.threshold_lines.append(max_line)
        
        # 设置X轴刻度标签
        axis = self.plot_widget.getAxis('bottom')
        axis.setTicks([[(i, lot_numbers[i]) for i in range(len(lot_numbers))]])
        axis.setTickRotation(-45)
        
        # 自动调整范围
        self.plot_widget.autoRange()
        
        # 添加悬停提示
        self._add_hover_tooltip(x_data, values, lot_numbers)
    
    def _add_hover_tooltip(self, x_data: List[int], y_data: List[float], labels: List[str]):
        """添加悬停提示"""
        scatter = pg.ScatterPlotItem(size=10)
        spots = []
        for i, (x, y) in enumerate(zip(x_data, y_data)):
            spots.append({
                'pos': (x, y),
                'data': labels[i],
                'brush': pg.mkBrush(0, 100, 200),
                'pen': pg.mkPen(None)
            })
        scatter.addPoints(spots)
        
        # 创建代理项用于显示悬停信息
        proxy = pg.SignalProxy(scatter.scene().sigMouseMoved, rateLimit=60, slot=self._mouse_moved)
        self.plot_widget.addItem(scatter)
    
    def _mouse_moved(self, evt):
        """鼠标移动事件"""
        pos = evt[0]
        # 这里可以添加更复杂的悬停逻辑
    
    def clear(self):
        """清除图表"""
        self.plot_widget.clear()
        self.threshold_lines = []
        self.plot_widget.setTitle("")
    
    def export_image(self, file_path: str):
        """
        导出图表为图片
        
        Args:
            file_path: 保存路径
        """
        exporter = pg.exporters.ImageExporter(self.plot_widget.plotItem)
        exporter.export(file_path)
