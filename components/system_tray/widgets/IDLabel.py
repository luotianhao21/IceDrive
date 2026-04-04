from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import QSize, Qt, QRectF
from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QMovie, QPainterPath, QLinearGradient, QColor, QPen
import re


class IDLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.gif: QMovie | None = None
        self.parent = parent
        self.gif_radius = 8
        
        # 渐变边框配置
        self.enable_gradient_border = False
        self.border_width = 2
        self.border_radius = 20
        self.border_color_start = (255, 255, 255, 60)  # RGBA: 起始颜色
        self.border_color_end = (255, 255, 255, 0)     # RGBA: 结束颜色(透明)
        
        # 存储解析后的样式
        self.parsed_style = {
            'border_image': None,
            'box_shadow': None
        }

        self.setStyleSheet("""
            padding: 0;
            margin: 0;
            border: none;
            background-color: transparent;
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def paintEvent(self, event):
        """重写绘画事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制渐变边框
        if self.enable_gradient_border:
            self._draw_gradient_border(painter)
        
        # 如果是 GIF 且有效，手动绘制带圆角的 GIF
        if self.gif is not None and self.gif.isValid():
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
            painter.end()
            return

        # 普通图片 / SVG 使用默认绘制
        painter.end()
        super().paintEvent(event)

    def setFixedStyleSheet(self, style_sheet: str):
        """设置样式表，自动识别 border-image 和 box-shadow"""
        if not "padding" in style_sheet:
            style_sheet += "padding: 0;"
        if not "margin" in style_sheet:
            style_sheet += "margin: 0;"
        if not "border" in style_sheet:
            style_sheet += "border: none;"
        if not "background-color" in style_sheet:
            style_sheet += "background-color: transparent;"
        
        # 解析 border-image
        self._parse_border_image(style_sheet)
        
        # 解析 box-shadow
        self._parse_box_shadow(style_sheet)
        
        self.setStyleSheet(style_sheet)
    
    def _parse_border_image(self, style_sheet: str):
        """解析 border-image 并启用渐变边框"""
        # 匹配 border-image: qlineargradient(...)
        pattern = r'border-image\s*:\s*qlineargradient\((.*?)\)\s*;'
        match = re.search(pattern, style_sheet, re.DOTALL)
        
        if match:
            gradient_params = match.group(1).strip()
            self.enable_gradient_border = True
            
            # 解析渐变参数
            # 匹配 stop:X rgba(r, g, b, a)
            stops = re.findall(r'stop\s*:\s*([\d.]+)\s+rgba\((\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d.]+)\)', gradient_params)
            if len(stops) >= 2:
                # 第一个 stop 作为起始颜色
                self.border_color_start = (
                    int(stops[0][1]),
                    int(stops[0][2]),
                    int(stops[0][3]),
                    int(float(stops[0][4]) * 255)
                )
                # 最后一个 stop 作为结束颜色
                self.border_color_end = (
                    int(stops[-1][1]),
                    int(stops[-1][2]),
                    int(stops[-1][3]),
                    int(float(stops[-1][4]) * 255)
                )
            
            # 解析 border-radius
            radius_match = re.search(r'border-radius\s*:\s*(\d+)px', style_sheet)
            if radius_match:
                self.border_radius = int(radius_match.group(1))
            
            # 解析 border-width
            width_match = re.search(r'border\s*:\s*(\d+)px', style_sheet)
            if width_match:
                self.border_width = int(width_match.group(1))
    
    def _parse_box_shadow(self, style_sheet: str):
        """解析 box-shadow (目前仅作标记，Qt 不支持 box-shadow)"""
        pattern = r'box-shadow:\s*(.*?);'
        match = re.search(pattern, style_sheet, re.DOTALL)
        
        if match:
            shadow_params = match.group(1).strip()
            self.parsed_style['box_shadow'] = shadow_params

    def loadSvgData(self, svg_data: str, size: QSize | tuple[int, int] = QSize(32, 32)):
        """将SVG图像加载到QLabel中"""
        if isinstance(size, tuple):
            size: QSize = QSize(*size)

        renderer = QSvgRenderer(svg_data)
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)  # 透明背景

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        self.setPixmap(pixmap)
        self.setFixedSize(size)
        self.parent.adjustSize()

    def loadImage(self, image_path: str, size: QSize | tuple[int, int] = QSize(32, 32)):
        """将位图图像加载到QLabel中"""
        if isinstance(size, tuple):
            size: QSize = QSize(*size)

        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.setPixmap(pixmap)
            self.setFixedSize(size)
        self.parent.adjustSize()

    def loadGifImage(self, image_path: str, size: QSize | tuple[int, int] = QSize(32, 32)):
        """将GIF图像加载到QLabel中"""
        if isinstance(size, tuple):
            size: QSize = QSize(*size)

        if self.gif is not None:
            # 先停止之前的 GIF
            self.gif.stop()

        self.gif: QMovie | None = QMovie(image_path)
        if not self.gif:
            return
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
    
    def enableGradientBorder(self, enable: bool = True):
        """启用/禁用渐变边框"""
        self.enable_gradient_border = enable
        self.update()
    
    def setGradientBorderConfig(self, width: int = 2, radius: int = 20, 
                                 color_start: tuple = (255, 255, 255, 60),
                                 color_end: tuple = (255, 255, 255, 0)):
        """
        设置渐变边框配置
        :param width: 边框宽度
        :param radius: 圆角半径
        :param color_start: 起始颜色 RGBA (255, 255, 255, 60)
        :param color_end: 结束颜色 RGBA (255, 255, 255, 0)
        """
        self.border_width = width
        self.border_radius = radius
        self.border_color_start = color_start
        self.border_color_end = color_end
        self.update()
    
    def _draw_gradient_border(self, painter: QPainter):
        """绘制四边渐变边框"""
        w, h = self.width(), self.height()
        bw = self.border_width
        r = self.border_radius
        
        # 绘制上边框渐变（从左到右：透明->可见->透明）
        top_gradient = QLinearGradient(0, 0, w, 0)
        top_gradient.setColorAt(0, QColor(*self.border_color_end))
        top_gradient.setColorAt(0.2, QColor(*self.border_color_start))
        top_gradient.setColorAt(0.8, QColor(*self.border_color_start))
        top_gradient.setColorAt(1, QColor(*self.border_color_end))
        
        painter.setPen(QPen(top_gradient, bw))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(
            QRectF(bw/2, bw/2, w-bw, h-bw),
            r, r
        )
        
        # 绘制左边框渐变（从上到下：透明->可见->透明）
        left_gradient = QLinearGradient(0, 0, 0, h)
        left_gradient.setColorAt(0, QColor(*self.border_color_end))
        left_gradient.setColorAt(0.2, QColor(*self.border_color_start))
        left_gradient.setColorAt(0.8, QColor(*self.border_color_start))
        left_gradient.setColorAt(1, QColor(*self.border_color_end))
        
        painter.setPen(QPen(left_gradient, bw))
        painter.drawRoundedRect(
            QRectF(bw/2, bw/2, w-bw, h-bw),
            r, r
        )
        
        # 绘制下边框渐变（从左到右：透明->可见->透明）
        bottom_gradient = QLinearGradient(0, h, w, h)
        bottom_gradient.setColorAt(0, QColor(*self.border_color_end))
        bottom_gradient.setColorAt(0.2, QColor(*self.border_color_start))
        bottom_gradient.setColorAt(0.8, QColor(*self.border_color_start))
        bottom_gradient.setColorAt(1, QColor(*self.border_color_end))
        
        painter.setPen(QPen(bottom_gradient, bw))
        painter.drawRoundedRect(
            QRectF(bw/2, bw/2, w-bw, h-bw),
            r, r
        )
        
        # 绘制右边框渐变（从上到下：透明->可见->透明）
        right_gradient = QLinearGradient(w, 0, w, h)
        right_gradient.setColorAt(0, QColor(*self.border_color_end))
        right_gradient.setColorAt(0.2, QColor(*self.border_color_start))
        right_gradient.setColorAt(0.8, QColor(*self.border_color_start))
        right_gradient.setColorAt(1, QColor(*self.border_color_end))
        
        painter.setPen(QPen(right_gradient, bw))
        painter.drawRoundedRect(
            QRectF(bw/2, bw/2, w-bw, h-bw),
            r, r
        )