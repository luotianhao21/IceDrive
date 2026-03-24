from static.fonts import IceDriveFont
from ..widgets import IDLabel

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from siui.core import SiColor, SiGlobal
from siui.components import (
    SiDenseHContainer,
    SiDenseVContainer
)


class IconDeviceInfo(SiDenseVContainer):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSpacing(4)  # 图标和文字间距
        self.setAlignment(Qt.AlignCenter)  # 整体居中

        # 关键：固定宽度，保证四个卡片一样大，绝不偏移
        self.setFixedWidth(100)

        # 自己设置背景样式（SiUI 容器这样写才生效）
        self.setFixedStyleSheet("""
            background-color: rgba(42, 40, 48, 1);
            border-radius: 6px;
            padding: 8px 0px;
        """)

        # 图标
        self.icon = IDLabel(self)

        # 文字
        self.label = IDLabel(self)
        self.label.setFont(IceDriveFont.vivoSans.Heavy(15))
        self.label.setFixedStyleSheet("color: rgba(255, 255, 255, 0.9);")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 文字居中

        # 垂直添加：上图标、下文字
        self.addWidget(self.icon)
        self.addWidget(self.label)
        self.adjustSize()

    def loadSvgData(self, svg_data: str, size: QSize | tuple[int, int] = (24, 24)):
        self.icon.loadSvgData(svg_data, size)

    def setRPMInfo(self, value):
        self.label.setText(f"{value} RPM")
        self.label.adjustSize()

    def setTemperatureInfo(self, value):
        # 根据数值自动显示 °C 或 转速
        self.label.setText(f"{value}°C")
        self.label.adjustSize()