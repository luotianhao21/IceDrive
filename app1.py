# app.py

from static import icons
from static.fonts import IceDriveFont
from components import TopBar
from components import SystemTray
from components.pages import PageHome
from libs import DeviceInfo, BLE, Commands

from PyQt5.QtCore import QTimer, Qt, QEvent
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDesktopWidget

import siui
from siui.core import SiColor, SiGlobal
from siui.templates.application.application import SiliconApplication

class IceDriveApp(SiliconApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        screen_geo = QDesktopWidget().screenGeometry()
        self.setMinimumSize(1024, 380)
        self.resize(1400, 916)
        self.move((screen_geo.width() - self.width()) // 2, (screen_geo.height() - self.height()) // 2)
        self.is_minimized = False

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 设置窗口标题和图标
        self.setWindowTitle("IceDrive - 外置水冷控制器")
        self.setWindowIcon(QIcon("./static/images/Snow.png"))

        # 设置TopBar
        self.top_bar = TopBar(self)
        self.layerMain().page_view.page_navigator.container.addPlaceholder(8)

        # 初始化系统托盘
        self.system_tray = SystemTray(self)

        # Pages
        self.addPage(
            PageHome(self),
            icon=SiGlobal.siui.iconpack.get("ic_fluent_home_filled"),
            hint="主页",
            side="top"
        )

        SiGlobal.siui.reloadAllWindowsStyleSheet()

        # 初始化命令处理器
        self.ble = BLE()
        self.device_info = DeviceInfo()

        # 开启设备信息更新线程
        self.device_info.start()

    def addPage(self, page, icon, hint: str, side="top"):
        """
        添加新页面
        :param page: 页面控件
        :param icon: 页面按钮的 svg 数据或路径
        :param hint: 页面按钮的工具提示
        :param side: 页面按钮置于哪一侧
        """
        self.layerMain().addPage(page, icon, hint, side)

    def setPage(self, index:  int):
        """
        设置显示的页面
        :param index: 页面的引索
        :return:
        """
        self.layerMain().setPage(index)

    def showWindow(self):
        """用于调用显示主窗口"""
        self.showNormal()
        self.show()
        # 置于顶层
        self.raise_()
        self.activateWindow()
        self.setFocus()

    def isActiveWindowFocused(self):
        """判断当前窗口是否聚焦"""
        return self.isVisible() and not self.isMinimized()

    def exitConfirm(self):
        """退出确认"""
        self.show()
        self.raise_()
        self.activateWindow()

    def mouseMoveEvent(self, event):
        """鼠标移动时"""
        super().mouseMoveEvent(event)