from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtGui import QPixmap, QPainter

class IDLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent

        self.setStyleSheet("""
            padding: 0;
            margin: 0;
            border: none;
            background-color: transparent;
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def setFixedStyleSheet(self, style_sheet: str):
        """设置样式表"""
        if not "padding" in style_sheet:
            style_sheet += "padding: 0;"
        if not "margin" in style_sheet:
            style_sheet += "margin: 0;"
        if not "border" in style_sheet:
            style_sheet += "border: none;"
        if not "background-color" in style_sheet:
            style_sheet += "background-color: transparent;"
        self.setStyleSheet(style_sheet)

    def loadSvgData(self, svg_data: str, size: QSize | tuple[int, int] = QSize(32, 32)):
        """将SVG图像加载到QLabel中"""
        if isinstance(size, tuple):
            size = QSize(*size)

        renderer = QSvgRenderer(svg_data)
        pixmap = QPixmap(size)
        pixmap.fill(Qt.transparent)  # 透明背景

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        self.setPixmap(pixmap)
        self.setFixedSize(size)
        self.parent.adjustSize()

    def loadImage(self, image_path: str, size: QSize | tuple[int, int] = QSize(32, 32)):
        """将位图图像加载到QLabel中"""
        if isinstance(size, tuple):
            size = QSize(*size)

        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(pixmap)
            self.setFixedSize(size)
        self.parent.adjustSize()