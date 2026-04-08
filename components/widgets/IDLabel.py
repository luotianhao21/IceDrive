from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import QSize, Qt, QRectF, QRect
from PyQt5.QtWidgets import QLabel, QWidget, QGraphicsDropShadowEffect
from PyQt5.QtGui import QPixmap, QPainter, QMovie, QPainterPath, QLinearGradient, QColor, QPen, QFontMetrics
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

        # 简易边框发光配置
        self.enable_simple_border_glow = False
        self.simple_border_glow_color = (255, 255, 255, 200)
        self.simple_border_glow_blur_radius = 15
        self.simple_border_glow_offset = 0
        self.simple_border_glow_effect = None

        # 文本发光配置
        self.enable_text_glow = False
        self.text_glow_color = (255, 255, 255, 200)
        self.text_glow_blur_radius = 15
        self.text_glow_spread = 3
        
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

        # 如果有文本或SVG且启用了发光效果，手动绘制带发光的内容
        if self.enable_text_glow and (self.text() or self.pixmap()):
            if self.text():
                self._draw_text_with_glow(painter)
            elif self.pixmap():
                if not self.pixmap().isNull():
                    self._draw_pixmap_with_glow(painter)
            painter.end()
            return

        # 普通图片 / SVG 使用默认绘制
        painter.end()
        super().paintEvent(event)

    def setSimpleBorderGlow(self,
                            enable: bool = True,
                            color: tuple = (255, 255, 255, 200),
                            blur_radius: int = 15,
                            offset: int = 0):
        """
        设置边框发光效果
        :param enable: 是否启用发光
        :param color: 发光颜色 RGBA (255, 255, 255, 200)
        :param blur_radius: 模糊半径，控制发光范围
        :param offset: 光晕偏移量，0表示均匀发光
        """
        self.enable_simple_border_glow = enable

        if enable:
            self.simple_border_glow_color = color
            self.simple_border_glow_blur_radius = blur_radius
            self.simple_border_glow_offset = offset

            # 创建或更新发光效果
            if self.simple_border_glow_effect is None:
                self.simple_border_glow_effect = QGraphicsDropShadowEffect(self)

            self.simple_border_glow_effect.setBlurRadius(blur_radius)
            self.simple_border_glow_effect.setColor(QColor(*color))
            self.simple_border_glow_effect.setOffset(offset, offset)
            self.setGraphicsEffect(self.simple_border_glow_effect)
        else:
            # 禁用发光效果
            if self.simple_border_glow_effect is not None:
                self.setGraphicsEffect(None)
                self.simple_border_glow_effect = None

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

    def setTextGlow(self, enable: bool = True, color: tuple = (255, 255, 255, 200),
                    blur_radius: int = 15, spread: int = 3):
        """
        设置文本发光效果（仅对文字生效，不影响边框）
        :param enable: 是否启用发光
        :param color: 发光颜色 RGBA (255, 255, 255, 200)
        :param blur_radius: 模糊半径，控制发光范围 (5-30)
        :param spread: 发光扩散范围 (1-5)
        """
        self.enable_text_glow = enable

        if enable:
            self.text_glow_color = color
            self.text_glow_blur_radius = max(5, min(30, blur_radius))
            self.text_glow_spread = max(1, min(5, spread))
            self.update()
        else:
            self.update()

    def _draw_text_with_glow(self, painter: QPainter):
        """绘制带发光效果的文本"""
        text = self.text()
        if not text:
            return

        # 获取文本矩形区域
        metrics = QFontMetrics(self.font())
        text_rect = metrics.boundingRect(self.rect(), int(self.alignment()), text)

        # 保存原始画笔颜色
        original_pen = painter.pen()

        # 绘制发光层（多层半透明叠加）
        glow_color = QColor(*self.text_glow_color)
        spread = self.text_glow_spread
        blur_steps = max(3, self.text_glow_blur_radius // 5)

        for i in range(blur_steps, 0, -1):
            alpha = glow_color.alpha() * (1 - i / (blur_steps + 1)) * 0.3
            glow_color_with_alpha = QColor(glow_color.red(), glow_color.green(),
                                           glow_color.blue(), int(alpha))
            painter.setPen(glow_color_with_alpha)
            painter.setFont(self.font())

            # 在多个方向偏移绘制，模拟模糊效果
            for dx in range(-spread, spread + 1):
                for dy in range(-spread, spread + 1):
                    offset_rect = text_rect.translated(dx, dy)
                    painter.drawText(offset_rect, int(self.alignment()), text)

        # 绘制正常文本
        painter.setPen(original_pen)
        painter.setFont(self.font())
        painter.drawText(text_rect, int(self.alignment()), text)

    def _draw_pixmap_with_glow(self, painter: QPainter):
        """绘制带发光效果的图片/SVG"""
        if self.pixmap() is None:
            return
        pixmap: QPixmap = self.pixmap()
        if pixmap.isNull():
            return

        # 计算图片绘制区域
        pixmap_rect = pixmap.rect()
        pixmap_rect.moveCenter(self.rect().center())

        # 绘制发光层（多层半透明叠加）
        glow_color = QColor(*self.text_glow_color)
        spread = self.text_glow_spread
        blur_steps = max(3, self.text_glow_blur_radius // 5)

        for i in range(blur_steps, 0, -1):
            alpha = int(glow_color.alpha() * (1 - i / (blur_steps + 1)) * 0.3)

            # 在多个方向偏移绘制，模拟模糊效果
            for dx in range(-spread, spread + 1):
                for dy in range(-spread, spread + 1):
                    offset_rect = pixmap_rect.translated(dx, dy)
                    painter.setOpacity(alpha / 255.0)
                    painter.drawPixmap(offset_rect, pixmap)

        # 恢复正常透明度并绘制原图
        painter.setOpacity(1.0)
        painter.drawPixmap(pixmap_rect, pixmap)

    def _get_glow_padding(self):
        """计算发光效果所需得额外边距"""
        if not self.enable_text_glow:
            return 0

        # 发光需要的额外空间 = 模糊半径 + 扩散范围 * 2
        # glow_radius = self.text_glow_blur_radius + self.text_glow_spread * 2
        glow_radius = self.text_glow_spread * 2
        return int(glow_radius)

    def getRequiredSizeForTextGlow(self):
        """
        计算包含发光效果所需的完整尺寸（支持文字和SVG）
        :return: QSize 对象，包含推荐的宽度和高度
        """
        # 如果有文本，按文本计算
        if self.text():
            metrics = QFontMetrics(self.font())
            text_rect = metrics.boundingRect(QRect(0, 0, 10000, 10000),
                                             int(self.alignment()), self.text())
            glow_padding = self._get_glow_padding()
            required_width = text_rect.width() + glow_padding * 2
            required_height = text_rect.height() + glow_padding * 2
            return QSize(required_width, required_height)

        # 如果有图片/SVG，按图片计算
        elif self.pixmap() and not self.pixmap().isNull():
            pixmap_size = self.pixmap().size()
            glow_padding = self._get_glow_padding()
            required_width = pixmap_size.width() + glow_padding * 2
            required_height = pixmap_size.height() + glow_padding * 2
            return QSize(required_width, required_height)

        # 默认返回当前尺寸
        return self.size()

    def resizeEvent(self, event):
        """重写尺寸变化事件，确保发光效果完整显示"""
        super().resizeEvent(event)

        # 如果启用了文字发光，确保有足够的空间
        if self.enable_text_glow and self.text():
            glow_padding = self._get_glow_padding()

            # 获取当前文字所需的实际空间
            metrics = QFontMetrics(self.font())
            text_rect = metrics.boundingRect(self.rect(), int(self.alignment()), self.text())

            # 计算包含发光的完整区域
            glow_rect = text_rect.adjusted(
                -glow_padding, -glow_padding,
                glow_padding, glow_padding
            )

            # 如果当前尺寸不足以显示完整发光，触发更新
            if not self.rect().contains(glow_rect):
                self.update()
                
    def adjustSize(self):
        super().adjustSize()
        if self.enable_text_glow and (self.text() or self.pixmap()):
            self.setFixedSize(self.getRequiredSizeForTextGlow())