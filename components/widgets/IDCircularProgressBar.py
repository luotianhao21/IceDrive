import typing

import math
from PyQt5.QtCore import QSize, QRectF, Qt
from PyQt5.QtGui import QPainter, QFont, QColor, QFontMetrics, QPen
from siui.components import SiLabel, WaveAnimation
from siui.core import SiExpAnimation, SiColor

from static.fonts import IceDriveFont


class IDCircularProgressBar(SiLabel):
    """圆环进度条"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setStyleSheet("""
            background: transparent;
            border: none;
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._value: float = 0 # 设置的数值
        self._showing_value = 0 # 显示的数值（缓动动画运行时更新）
        self._value_text_font: QFont = IceDriveFont.vivoSansSimplifiedChinese.Bold(18)
        self._inner_radius: int = 0
        self._outer_radius: int = 0
        self._bar_width: int = 0
        self._margins: tuple[int, int, int, int] = (3, 3, -3, -3) # left, top, right. bottom

        self._hint_text: str = '' # 提示文字
        self._inner_text: str = ''
        self._inner_text_font: QFont = IceDriveFont.vivoSansSimplifiedChinese.Bold(18)
        self._unit_text: str = '' # 单位
        self._unit_text_font: QFont = IceDriveFont.vivoSansSimplifiedChinese.Bold(10)
        self._unit_text_from_bottom: int = 8 # 单位到圆环的距离
        self._title_text: str = '' # 标题
        self._title_text_font: QFont = IceDriveFont.vivoSansSimplifiedChinese.ExtraBold(12)
        self._title_spacing: int = 20 # 圆环到标题之间的距离

        # 是否在加载
        self._indeterminate: bool = False
        self._indeterminate_value = 0

        # 注册动画组
        ## 加载动画
        self.animationGroup().addMember(WaveAnimation(self), 'indeterminate_process')
        self.animationGroup().fromToken('indeterminate_process').ticked.connect(
            self._on_indeterminate_process_ani_ticked
        )
        self.animationGroup().fromToken('indeterminate_process').setSpeedFactor(1/16*0.1)

        ## 改变数值动画
        self.animationGroup().addMember(SiExpAnimation(self), 'value')
        self.animationGroup().fromToken('value').ticked.connect(
            self._on_value_ani_ticked
        )
        self.animationGroup().fromToken('value').setFactor(1/16)
        self.animationGroup().fromToken("value").setBias(0.001) # 缓动曲线

        # 进度条颜色
        self._bar_color: QColor = QColor("#22C4DE")
        self._bar_bg_color: QColor = QColor("#383846")
        self._is_region_color: bool = False # 是否启用多颜色
        self._color_value_list: list[float] = [] # 颜色分割列表
        self._color_list: list[QColor] = [] # 颜色

        # 字体颜色
        self._inner_text_color = QColor("#FFFFFF")
        self._unit_text_color = QColor("#888899")
        self._title_text_color = QColor("#FFFFFF")

    @property
    def value(self) -> float:
        return self._value

    def _get_title_size(self) -> QSize:
        """获取标题大小"""
        title_metrics = QFontMetrics(self._title_text_font)
        title_width = title_metrics.horizontalAdvance(self._title_text)
        title_height = title_metrics.height()
        return QSize(title_width, title_height)

    def _get_inner_text_size(self) -> QSize:
        """获取内文字大小"""
        inner_text_metrics = QFontMetrics(self._inner_text_font)
        inner_text_width = inner_text_metrics.horizontalAdvance(self._inner_text)
        inner_text_height = inner_text_metrics.height()
        return QSize(inner_text_width, inner_text_height)

    def _get_unit_text_size(self) -> QSize:
        """获取符号文字大小"""
        unit_text_metrics = QFontMetrics(self._unit_text_font)
        unit_text_width = unit_text_metrics.horizontalAdvance(self._unit_text)
        unit_text_height = unit_text_metrics.height()
        return QSize(unit_text_width, unit_text_height)

    def _set_rect_size(self) -> None:
        """更新控件大小"""
        title_size = self._get_title_size() if self._title_text else QSize(0, 0)
        self.setFixedSize(
            QSize(
                max(self._outer_radius * 2, title_size.width()) + self._margins[0] - self._margins[2] + self._bar_width * 2,
                self._outer_radius * 2 + self._title_spacing + title_size.height() + self._margins[1] - self._margins[3]
            )
        )

    def _get_color(self, value: float) -> QColor:
        """
        根据颜色区间的数据返回对应的颜色
        :param value: 数值（0~1）应该为 self._showing_value
        :return: 对应颜色，找不到就返回 self._bar_color
        """
        if self._is_region_color:
            # 获取当前value处于self._color_value_list中的位置
            for i, value_ in enumerate(self._color_value_list):
                if value_ <= value:
                    return self._color_list[max(len(self._color_value_list) - 1, min(0, i - 1))]

        return self._bar_color

    @staticmethod
    def update_ui(func):
        """更新UI数据时修饰器"""
        def wrapper(self, *args, **kwargs):
            res = func(self, *args, **kwargs)
            self.update()
            return res
        return  wrapper

    @update_ui
    def _on_value_ani_ticked(self, value):
        self._showing_value = value

    @update_ui
    def _on_indeterminate_process_ani_ticked(self, value):
        self._indeterminate_value = value

    @update_ui
    def setMargins(self, left, top, right, bottom) -> None:
        self._margins = (left, top, -right, -bottom)

    @update_ui
    def setRadius(self, inner: int, outer: int) -> None:
        """
        设置半径
        :param inner: 内半径
        :param outer: 外半径
        :return:
        """
        self._inner_radius = inner
        self._outer_radius = outer
        self._bar_width = outer - inner

    @update_ui
    def setBarWidth(self, bar_width: int, outer_radius: int | None = None) -> None:
        """
        设置进度条宽度
        :param bar_width: 宽度
        :param outer_radius: 外半径
        :return:
        """
        if outer_radius is None:
            outer_radius: int = min(
                self.rect().size().width() - self._margins[0] + self._margins[2],
                self.rect().size().height() - self._margins[1] + self._margins[3]
            )
        self._bar_width = bar_width
        self._outer_radius = outer_radius
        self._inner_radius = self._outer_radius - self._bar_width

    def setBarColor(self, color: QColor) -> None:
        """
        设置颜色
        :param color: 颜色
        :return:
        """
        self._is_region_color = False
        self._bar_color = color

    def setBarRegionColor(self, values_list: list[float], colors_list: list[QColor]) -> None:
        """
        设置区间多颜色
        :param values_list: 区间分割 Example: [0, 0.1, 0.5, 1] （以 0，1 结尾）
        :param colors_list: 颜色列表（长度总小于区间分割列表小 1）
        :return:
        """
        if values_list[0] != 0 or values_list[-1] != 1:
            raise ValueError('区间分割列表错误')
        if len(values_list) != len(colors_list) + 1:
            raise ValueError('颜色列表长度错误')

        self._is_region_color = True
        self._color_value_list = values_list
        self._color_list = colors_list

    def setTitle(self, text: str) -> None:
        """
        设置标题
        :param text: 标题
        :return:
        """
        self._title_text = text

    def setTitleFont(self, font: QFont) -> None:
        """
        设置标题字体
        :param font: 字体
        :return:
        """
        self._title_text_font = font

    def setTitleSpacing(self, spacing: int) -> None:
        """
        设置标题到进度条的间距
        :param spacing: 间距
        :return:
        """
        self._title_spacing = spacing

    def isIndeterminate(self) -> bool:
        """是否在加载状态"""
        return self._indeterminate

    def setIndeterminate(self, loading: bool, hint: str = '加载中...') -> None:
        """
        设置加载状态
        :param loading: 是否加载中
        :param hint: 提示文字
        :return:
        """
        self._indeterminate = loading
        if loading:
            super().setHint(hint)
            self.animationGroup().fromToken("indeterminate_process").start()
        else:
            super().setHint(self._hint_text)
            self.animationGroup().fromToken("indeterminate_process").stop()

    def setHint(self, text: str) -> None:
        """
        设置提示文字
        :param text: 提示文字
        :return:
        """
        super().setHint(text)
        self._hint_text = text

    def setUnit(self, unit: str) -> None:
        """
        设置单位
        :param unit: 单位
        :return:
        """
        self._unit_text = unit

    def setUnitFont(self, font: QFont) -> None:
        """
        设置单位的字体
        :param font: 字体
        :return:
        """
        self._unit_text_font = font

    def setUnitFromBottom(self, spacing: int) -> None:
        """
        设置单位到圆环的距离
        :param spacing:
        :return:
        """
        self._unit_text_from_bottom = spacing

    def setInnerText(self, text: str) -> None:
        """
        设置内部文字
        :param text: 内部文字
        :return:
        """
        self._inner_text = text

    def setInnerFont(self, font: QFont) -> None:
        """
        设置内部文字的字体
        :param font: 字体
        :return:
        """
        self._inner_text_font = font

    def setValue(self, value: float | int) -> None:
        """
        设置进度值
        :param value: 进度值（0~1）
        :return:
        """
        if isinstance(value, int):
            value: float = float(value)

        self._value = value
        self.animationGroup().fromToken('value').setTarget(value)
        self.animationGroup().fromToken("value").try_to_start()

        if not self._indeterminate:
            self.setHint('')

    def hideEvent(self, event):
        super().hideEvent(event)
        self.animationGroup().fromToken("indeterminate_process").stop()

    def showEvent(self, event):
        super().showEvent(event)
        if self._indeterminate:
            self.animationGroup().fromToken("indeterminate_process").start()

    def paintEvent(self, event):
        """
        重写绘画事件
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self._set_rect_size()

        rect = self.rect()
        rect.adjust(*self._margins)
        process_bar_rect = QRectF(
            int((rect.width() - self._outer_radius * 2) / 2 + self._bar_width + self._margins[3]),
            self._bar_width / 2 + self._margins[1],
            self._outer_radius * 2 - int(self._bar_width / 2),
            self._outer_radius * 2 - int(self._bar_width / 2)
        )

        # 灰色底板
        bar_bg_pen = QPen(self._bar_bg_color, self._bar_width)
        bar_bg_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(bar_bg_pen)
        painter.drawArc(process_bar_rect, 0, 360 * 16)

        # 亮色进度条
        bar_pen = QPen(self._get_color(self._showing_value), self._bar_width)
        bar_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(bar_pen)
        if self.isIndeterminate():
            start_angle = 360 * (self._indeterminate_value % 1)
            span_angle = 40 + 140 * math.fabs(math.sin(150 * (self._indeterminate_value / 65 % 1)))
            painter.drawArc(process_bar_rect, int(start_angle * 16), int(span_angle * 16))
        else:
            start_angle = 360 * 0.25
            span_angle = -360 * self._showing_value

            if self._showing_value > 0:
                painter.drawArc(process_bar_rect, int(start_angle * 16), int(span_angle * 16))

        # 圆环内数值显示
        if self._inner_text:
            painter.setPen(self._inner_text_color)
            painter.setFont(self._inner_text_font)
            painter.drawText(process_bar_rect, Qt.AlignmentFlag.AlignCenter, self._inner_text)

        # 单位
        if self._unit_text:
            painter.setPen(self._unit_text_color)
            painter.setFont(self._unit_text_font)
            unit_rect = QRectF(
                process_bar_rect.x(),
                process_bar_rect.y() + process_bar_rect.height() - self._get_unit_text_size().height() - self._unit_text_from_bottom,
                process_bar_rect.width(), self._get_unit_text_size().height()
            )
            painter.drawText(unit_rect, Qt.AlignmentFlag.AlignCenter, self._unit_text)

        # 标题
        if self._title_text:
            painter.setPen(self._title_text_color)
            painter.setFont(self._title_text_font)
            title_rect = QRectF(
                process_bar_rect.x(),
                process_bar_rect.y() + process_bar_rect.height() + self._title_spacing,
                process_bar_rect.width(), self._get_title_size().height()
            )
            painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, self._title_text)

        painter.end()