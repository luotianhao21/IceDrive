from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import QSize, Qt, QRectF
from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QMovie, QPainterPath


class IDLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.gif: QMovie | None = None
        self.parent = parent
        self.gif_radius = 8

        self.setStyleSheet("""
            padding: 0;
            margin: 0;
            border: none;
            background-color: transparent;
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def paintEvent(self, event):
        """重写绘画事件"""
        # 如果是 GIF 且有效，手动绘制带圆角的 GIF
        if self.gif is not None and self.gif.isValid():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)

            # 圆角裁剪路径
            rect = QRectF(self.rect())
            path = QPainterPath()
            path.addRoundedRect(rect, self.gif_radius, self.gif_radius)
            painter.setClipPath(path)

            # 绘制当前 GIF 帧
            current_pixmap = self.gif.currentPixmap()
            target_rect = current_pixmap.rect()
            target_rect.moveCenter(rect.center().toPoint())
            painter.drawPixmap(target_rect, current_pixmap)

            return

        # 普通图片 / SVG 使用默认绘制
        super().paintEvent(event)

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

    def loadGifImage(self, image_path: str, size: QSize | tuple[int, int] = QSize(32, 32)):
        """将GIF图像加载到QLabel中"""
        if isinstance(size, tuple):
            size = QSize(*size)

        if self.gif is not None:
            # 先停止之前的 GIF
            self.gif.stop()

        self.gif: QMovie = QMovie(image_path)
        self.gif.setScaledSize(size)
        self.setMovie(self.gif)
        self.setFixedSize(size)

        self.gif.frameChanged.connect(self.update)

    def startGif(self):
        """开始播放 GIF"""
        if self.gif is not None:
            self.gif.start()

    def stopGif(self):
        """停止播放 GIF"""
        if self.gif is not None:
            self.gif.stop()

    def setGifRadius(self, value: int):
        """设置Gif裁切圆角的半径"""
        self.gif_radius = value