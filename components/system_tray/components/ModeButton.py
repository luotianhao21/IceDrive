from PyQt5.QtGui import QPixmap, QPainter, QIcon, QColor
from PyQt5.QtSvg import QSvgRenderer

from components.widgets import IDLabel

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QWidgetAction,
    QPushButton
)
from siui.components import (
    SiDenseHContainer,
    SiDenseVContainer
)

class ModeButton(SiDenseVContainer):
    def __init__(self, parent=None, active_mode: bool = False):
        super().__init__(parent)

        self.hover_color = "#48434D"

        self.setContentsMargins(0, 0, 0, 0)
        self.setFixedSize(100, 80)
        self.setSpacing(0)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn = QPushButton(parent)
        self.btn.setFixedSize(100, 70)
        self.btn.setIconSize(QSize(30, 30))
        self.btn.setStyleSheet(f"""
            QPushButton {{
                background: #332E38;
                border-radius: 8px;
                margin: 0;
                padding: 0;
            }}
            QPushButton:hover {{
                background: {self.hover_color};
            }}
            QPushButton:pressed {{
                background: #38363B;
            }}
        """)

        self.addWidget(self.btn)

        self.active_bar: QWidget

        if active_mode:
            self.active_bar = QLabel(self)
            self.active_bar.setFixedSize(40, 8)
            self.active_bar.setStyleSheet("""
                QLabel {
                    background: #535353;
                    border-radius: 4px;
                }
            """)
            self.addPlaceholder(2)
            self.addWidget(self.active_bar)

    def setActive(self, active: bool):
        """设置按钮的激活状态"""
        btn_color = "#4E4359" if active else "#332E38"
        active_bar_color = "#856B9F" if active else "#535353"

        self.btn.setStyleSheet(f"""
            QPushButton {{
                background: {btn_color};
                border-radius: 8px;
                margin: 0;
                padding: 0;
            }}
            QPushButton:hover {{
                background: #685C73;
            }}
            QPushButton:pressed {{
                background: #5B5462;
            }}
        """)
        if self.active_bar:
            self.active_bar.setStyleSheet(f"""
                QLabel {{
                    background: {active_bar_color};
                    border-radius: 4px;
                }}
            """)

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
        self.btn.setIcon(QIcon(pixmap))
        self.btn.setIconSize(size)