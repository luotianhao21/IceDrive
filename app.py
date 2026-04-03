# app.py
from static import icons
from static.fonts import IceDriveFont
from components import TopBar
from components import SystemTray
from libs import DeviceInfo, BLE, Commands

from PyQt5.QtCore import QTimer, Qt
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

        # 设置窗口标题和图标
        self.setWindowTitle("IceDrive - 外置水冷控制器")
        self.setWindowIcon(QIcon("./static/images/Snow.png"))

        # 设置TopBar
        self.top_bar = TopBar(self)
        self.layerMain().page_view.page_navigator.container.addPlaceholder(8)

        # 初始化系统托盘
        self.system_tray = SystemTray(self)

        SiGlobal.siui.reloadAllWindowsStyleSheet()

        # 初始化命令处理器
        self.ble = BLE()
        self.device_info = DeviceInfo()

        # 开启设备信息更新线程
        self.device_info.start()

    def showWindow(self):
        """用于调用显示主窗口"""
        self.show()
        # 置于顶层
        self.raise_()
        self.activateWindow()

    def exitConfirm(self):
        """退出确认"""
        self.show()
        self.raise_()
        self.activateWindow()

        # 弹出确认对话框