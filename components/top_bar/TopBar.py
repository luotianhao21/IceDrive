import typing
from ..confirm_window import MainWindowExitConfirmWindow

from PyQt5.QtGui import QScreen

from static.fonts import IceDriveFont

from PyQt5 import QtGui
from PyQt5.QtCore import (
    Qt,
    QPoint
)

from siui.core import SiColor, SiGlobal
from siui.templates.application.application import SiliconApplication
from siui.components.widgets import (
    SiSimpleButton,
)

class TopBar:
    def __init__(self, app: SiliconApplication):
        # 保存应用实例和主层引用
        self.app = app
        self.layer_main = self.app.layerMain()

        # 拖动位置记录
        self.drag_start_position = QPoint()

        # 定义按钮颜色
        self.btn_min_color = "#8892EC"
        self.btn_max_color = "#98F5E1"
        self.btn_close_color = "#EC88AE"
        self.top_bar_btn_size = 64

        # 设置窗口 TopBar
        self.layer_main.app_title.setText("IceDrive")
        self.layer_main.app_title.setMinimumWidth(300) # 设置最小宽度
        self.layer_main.app_title.setFont(IceDriveFont.Others.YouSheBiaoTiHei(34)) # 设置字体
        self.layer_main.app_title.setFixedHeight(32) # 固定高度
        # 删除前两占位
        for i in range(2):
            self.layer_main.container_title.removeWidget(self.layer_main.container_title.widgets_left[0])
        # 再删除icon到title的占位
        self.layer_main.container_title.removeWidget(self.layer_main.container_title.widgets_left[1])

        self.layer_main.app_icon.load("static/images/Snow.png") # 加载图标

        self.layer_main.container_title.addPlaceholder(10, side="left", index=0)
        self.layer_main.container_title.addPlaceholder(8, side="left", index=2)
        self.layer_main.app_icon.setFixedSize(38, 38)

        # 创建三个按钮
        self.btn_min = SiSimpleButton(self.app)
        self.btn_max = SiSimpleButton(self.app)
        self.btn_close = SiSimpleButton(self.app)

        self.btn_min.setToolTip("最小化")
        self.btn_max.setToolTip("最大化")
        self.btn_close.setToolTip("关闭窗口")

        self.btn_min.resize(self.top_bar_btn_size, self.top_bar_btn_size)
        self.btn_max.resize(self.top_bar_btn_size, self.top_bar_btn_size)
        self.btn_close.resize(self.top_bar_btn_size, self.top_bar_btn_size)

        self.btn_min.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_line_horizontal_1_filled", self.btn_min_color))
        self.btn_max.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_arrow_maximize_filled", self.btn_max_color))
        self.btn_close.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_dismiss_filled", self.btn_close_color))

        # 添加按钮
        self.layer_main.container_title.addWidget(self.btn_close, "right")
        self.layer_main.container_title.addWidget(self.btn_max, "right")
        self.layer_main.container_title.addWidget(self.btn_min, "right")

        # 连接按钮事件
        self.btn_min.clicked.connect(self._event_btn_min)
        self.btn_max.clicked.connect(self._event_btn_max)
        self.btn_close.clicked.connect(self._event_btn_close)

        # 重写self.layer_main.layerMain().container_title的鼠标事件
        self.layer_main.container_title.mouseDoubleClickEvent = self.toggleMaximized  # 双击标题栏最大化/还原窗口
        self.layer_main.container_title.mousePressEvent = self.mousePressEvent
        self.layer_main.container_title.mouseMoveEvent = self.mouseMoveEvent
        self.layer_main.container_title.mouseReleaseEvent = self.mouseReleaseEvent

    def toggleMaximized(self, event: typing.Optional[QtGui.QMouseEvent]):
        # 判断双击的按键是否为左键
        try:
            if not event.button() == Qt.MouseButton.LeftButton:
                return
        except Exception as event:
            event = event

        if self.app.isMaximized():
            self.app.showNormal()
            self.btn_max.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_arrow_maximize_filled", self.btn_max_color))
        else:
            self.app.showMaximized()
            self.btn_max.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_arrow_minimize_filled", self.btn_max_color))

    def mousePressEvent(self, event):
        # 鼠标左键按下时记录鼠标位置
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.globalPos() - self.app.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        # 鼠标左键按下后移动窗口
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.app.isMaximized():
                # 当窗口最大化时，鼠标移动窗口后缩小窗口
                # 记录鼠标位置
                position = event.globalPos() - self.app.frameGeometry().topLeft()
                screen: QScreen | None = self.app.screen()
                if screen is None:
                    return
                max_size = screen.size()
                self.app.showNormal()  # 还原窗口
                # 按照比例计算常规窗口的位置
                normal_window_position = QPoint(
                    int(event.globalPos().x() - position.x() * self.app.width() / max_size.width()),
                    int(event.globalPos().y() - position.y() * self.app.height() / max_size.height())
                )
                self.btn_max.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_arrow_maximize_filled"))
                # 移动窗口到位置
                self.app.move(normal_window_position)
                self.drag_start_position = event.globalPos() - self.app.frameGeometry().topLeft()
                event.accept()
            else:
                self.app.move(event.globalPos() - self.drag_start_position)
                event.accept()

    @staticmethod
    def mouseReleaseEvent(event: typing.Optional[QtGui.QMouseEvent]):
        # 鼠标左键释放时恢复窗口
        if event.button() == Qt.MouseButton.LeftButton:
            event.accept()

    def _event_btn_min(self, *args, **kwargs):
        # 最小化窗口
        self.app.showMinimized()

    def _event_btn_max(self, *args, **kwargs):
        # 最大化/还原窗口
        self.toggleMaximized(*args, **kwargs)

    def _event_btn_close(self, *args, **kwargs):
        # 将窗口最小化到系统托盘
        MainWindowExitConfirmWindow(self.app).exec_()