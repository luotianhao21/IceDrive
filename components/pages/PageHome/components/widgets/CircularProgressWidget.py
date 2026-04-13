from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRectF, pyqtProperty, QPropertyAnimation, QEasingCurve
from static.fonts import IceDriveFont


class CircularProgressWidget(QWidget):
    def __init__(self, parent=None, title="Title", unit="%", color="#22C4DE"):
        super().__init__(parent)
        self.title_text = title
        self.unit_text = unit
        self.ring_color = QColor(color)
        self.bg_color = QColor("#383846")  # 圆环底色

        self._value = 0.0
        self._max_value = 100.0

        # 动画平滑滚动
        self.animation = QPropertyAnimation(self, b"anim_value")
        self.animation.setDuration(800)  # 800ms
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

    @pyqtProperty(float)
    def anim_value(self):
        return self._value

    @anim_value.setter
    def anim_value(self, val):
        self._value = val
        self.update()

    def setValue(self, val, max_val=None):
        """外部调用这个方法来更新进度条的值"""
        if max_val is not None:
            self._max_value = max_val

        # 动画起点和终点
        self.animation.setStartValue(self._value)
        self.animation.setEndValue(val)
        self.animation.start()

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()

        # 圆环的尺寸和位置
        margin = 6
        title_space = 28
        circle_diameter = min(width, height - title_space) - margin * 2
        circle_diameter = max(circle_diameter, 0)

        ring_thickness = max(8, int(circle_diameter * 0.08))
        ring_thickness = min(ring_thickness, max(2, int(circle_diameter / 4)))

        inner_diameter = max(circle_diameter - ring_thickness, 0)
        x = (width - inner_diameter) / 2
        y = (height - title_space - inner_diameter) / 2
        rect = QRectF(x, y, inner_diameter, inner_diameter)

        # 底层灰圈
        bg_pen = QPen(self.bg_color, ring_thickness)
        bg_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(bg_pen)
        painter.drawArc(rect, 0, 360 * 16)

        # 亮色进度条
        if self._max_value > 0:
            percentage = self._value / self._max_value
            percentage = min(max(percentage, 0.0), 1.0)

            progress_pen = QPen(self.ring_color, ring_thickness)
            progress_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(progress_pen)

            start_angle = 90 * 16
            span_angle = -int(percentage * 360 * 16)
            if span_angle != 0:
                painter.drawArc(rect, start_angle, span_angle)

        # 圆环数值显示
        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(IceDriveFont.vivoSansSimplifiedChinese.Bold(18))
        value_str = f"{int(self._value)}"

        # 数字 / 单位 分隔
        text_rect = QRectF(x, y, inner_diameter, inner_diameter)
        painter.drawText(text_rect, Qt.AlignCenter, value_str)

        # 单位符号
        painter.setPen(QColor("#888899"))
        painter.setFont(IceDriveFont.vivoSansSimplifiedChinese.Medium(10))
        unit_rect = QRectF(x, y + inner_diameter * 0.35, inner_diameter, inner_diameter)
        painter.drawText(unit_rect, Qt.AlignCenter, self.unit_text)

        # 底部标题
        painter.setPen(QColor("#AAAAAA"))
        painter.setFont(IceDriveFont.vivoSansSimplifiedChinese.Medium(11))
        title_rect = QRectF(0, height - 25, width, 25)
        painter.drawText(title_rect, Qt.AlignCenter, self.title_text)

        painter.end()