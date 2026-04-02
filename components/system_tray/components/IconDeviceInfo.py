from PyQt5.QtGui import QCursor

from static.fonts import IceDriveFont
from ..widgets import IDLabel

from PyQt5.QtCore import Qt, QSize, QPoint, QTimer, QEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from siui.core import SiColor, SiGlobal
from siui.components import (
    SiDenseHContainer,
    SiDenseVContainer
)

class DeviceInfoTooltip(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.targe_widget = parent

        # 样式
        self.setStyleSheet("""
            background-color: rgba(30, 30, 35, 0.92);
            color: #ffffff;
            border-radius: 6px;
            padding: 6px 8px 2px 8px;
            border: 1px solid rgba(255,255,255,0.1);
        """)

        # 垂直布局
        layout = QVBoxLayout(self)
        # 设置内边距和间距
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(0)

        # 文字标签
        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignCenter) # 文字居中
        self.label.setFont(IceDriveFont.Others.AaJianHaoTi(16))
        self.label.setStyleSheet("color: #ffffff;") # 白色文字
        layout.addWidget(self.label)
        self.adjustSize()

        # 粘滞感
        self._smooth_factor = 0.15  # 粘滞强度
        self._target_pos = QPoint()

        # 定时器用于更新位置
        self._follow_timer: QTimer = QTimer(self)
        self._follow_timer.setInterval(10)
        self._follow_timer.timeout.connect(self._update_follow_position)

    def setText(self, text):
        self.label.setText(text)
        self.adjustSize()

    def _update_follow_position(self):
        if not self.isVisible():
            self._follow_timer.stop()
            return

        # 鼠标目标位置
        mouse_pos = QCursor.pos() - QPoint(0, self.height()) + QPoint(10, -5)

        # 粘滞缓动算法
        self._target_pos = mouse_pos
        current_x, current_y = self.pos().x(), self.pos().y()
        target_x, target_y = self._target_pos.x(), self._target_pos.y()

        # 简单线性插值，越接近目标越慢
        new_x = current_x + (target_x - current_x) * self._smooth_factor
        new_y = current_y + (target_y - current_y) * self._smooth_factor

        self.move(int(new_x), int(new_y))

    def show(self):
        super().show()
        # 初始位置在鼠标上方
        self.move(QCursor.pos() - QPoint(0, self.height()) + QPoint(10, -5))
        self._follow_timer.start()

    def hide(self):
        super().hide()
        self._follow_timer.stop()


class IconDeviceInfo(SiDenseVContainer):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSpacing(4)  # 图标和文字间距
        self.setAlignment(Qt.AlignCenter)  # 整体居中

        # 关键：固定宽度，保证四个卡片一样大
        self.setFixedWidth(100)

        # 自己设置背景样式
        self.setFixedStyleSheet("""
            background-color: transparent;
            border-radius: 6px;
            padding: 8px 0px;
        """)

        # 图标
        self.icon = IDLabel(self)

        # 文字
        self.label = IDLabel(self)
        self.label.setFont(IceDriveFont.vivoSansGlobal.Heavy(15))
        self.label.setFixedStyleSheet("color: rgba(255, 255, 255, 0.9);")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 文字居中

        # 垂直添加：上图标、下文字
        self.addWidget(self.icon)
        self.addWidget(self.label)
        self.adjustSize()

        self.tooltip = DeviceInfoTooltip(parent=self)
        self.tooltip_text = ""

    def setToolTip(self, text):
        """设置提示文本"""
        self.tooltip_text = text
        self.tooltip.setText(text)

    def loadSvgData(self, svg_data: str, size: QSize | tuple[int, int] = (30, 30)):
        """加载 SVG 数据并设置图标大小"""
        self.icon.loadSvgData(svg_data, size)

    def setRPMInfo(self, value: int):
        """设置转速信息，自动添加 RPM 单位"""
        self.label.setText(f"{value} RPM")
        self.label.adjustSize()

    def setTemperatureInfo(self, value: float | int):
        """设置温度信息，自动添加 °C 单位"""
        self.label.setText(f"{value}°C")
        self.label.adjustSize()

    def enterEvent(self, event):
        """鼠标进入时显示提示"""
        super().enterEvent(event)
        if not self.tooltip_text:
            return
        # 显示
        self.tooltip.show()

    def leaveEvent(self, event):
        """鼠标离开时隐藏提示"""
        self.tooltip.hide()
        super().leaveEvent(event)