from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap, QPainter, QIcon, QColor
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QPushButton


class ICPushButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

    def loadSvgData(self, svg_data: str, size: QSize | tuple[int, int] = (30, 30), color: str = None):
        """加载 SVG 数据并设置图标大小 + 支持染色"""
        if isinstance(size, tuple):
            size = QSize(*size)

        # 创建透明 pixmap
        pixmap = QPixmap(size)
        pixmap.fill(Qt.transparent)

        # 渲染 SVG
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        renderer = QSvgRenderer(svg_data)
        renderer.render(painter)

        # 染色逻辑
        if color is not None:
            painter.setCompositionMode(painter.CompositionMode_SourceIn)
            painter.fillRect(pixmap.rect(), QColor(color))

        painter.end()

        # 设置图标
        self.setIcon(QIcon(pixmap))
        self.setIconSize(size)