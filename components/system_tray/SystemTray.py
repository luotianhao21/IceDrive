import typing
from libs import Signal
from static.fonts import IceDriveFont
from .components import IconDeviceInfo, ModeButton
from .widgets import IDLabel
from ..confirm_window import TrayExitConfirmWindow

from PyQt5.QtWidgets import (
    QWidget,
    QMenu,
    QLabel,
    QSystemTrayIcon,
    QVBoxLayout,
    QHBoxLayout,
    QApplication,
    QWidgetAction,
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QEvent, QSize

from siui.core import SiColor, SiGlobal
from siui.components import (
    SiDenseHContainer,
    SiDenseVContainer,
    SiLabel
)

class SystemTray:

    normal_mode: Signal = Signal() # 切换普通模式
    rage_mode: Signal = Signal() # 切换狂暴模式

    def __init__(self, app):
        self.app = app

        # 初始化系统托盘图标
        self.tray_icon: QSystemTrayIcon = QSystemTrayIcon(self.app)
        self.tray_icon.setIcon(QIcon("./static/images/Snow.png"))
        self.tray_icon.setToolTip("IceDrive")
        self.tray_icon.activated.connect(self.on_tray_clicked)

        self.tray_menu = IceDriveTrayMenu(self, app)
        self.tray_menu.normal_mode_btn.btn.clicked.connect(
            lambda _: (self.setMode("normal"), self.normal_mode.emit())
        )
        self.tray_menu.rage_mode_btn.btn.clicked.connect(
            lambda _: (self.setMode("rage"), self.rage_mode.emit())
        )
        # 设置菜单为空，使用自定义的窗口
        self.tray_icon.setContextMenu(self.tray_menu)

        # 显示托盘
        self.tray_icon.show()

    def setCPUTemperature(self, temp: float | int):
        """设置CPU温度显示"""
        self.tray_menu.cpu_info.setTemperatureInfo(temp)
        self.tray_menu.cpu_info.setToolTip(f"CPU 温度\n{temp}°C")

    def setGPUTemperature(self, temp: float | int):
        """设置GPU温度显示"""
        self.tray_menu.gpu_info.setTemperatureInfo(temp)
        self.tray_menu.gpu_info.setToolTip(f"GPU 温度\n{temp}°C")

    def setFanRPM(self, rpm: int):
        """设置风扇转速显示"""
        self.tray_menu.fan_info.setRPMInfo(rpm)
        self.tray_menu.fan_info.setToolTip(f"风扇转速\n{rpm} RPM")

    def setPumpRPM(self, rpm: int):
        """设置水泵转速显示"""
        self.tray_menu.pump_info.setRPMInfo(rpm)
        self.tray_menu.pump_info.setToolTip(f"水泵转速\n{rpm} RPM")

    def setMode(self, mode: str):
        """设置当前模式显示"""
        if mode == "normal":
            self.tray_menu.normal_mode_btn.setActive(True)
            self.tray_menu.rage_mode_btn.setActive(False)
        elif mode == "rage":
            self.tray_menu.normal_mode_btn.setActive(False)
            self.tray_menu.rage_mode_btn.setActive(True)

    def on_tray_clicked(self, reason):
        """被点击事件处理"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.app.showWindow()

    def quit_app(self):
        """退出程序"""
        self.tray_icon.hide()
        self.app.close()
        QApplication.quit()


class IceDriveTrayMenu(QMenu):
    def __init__(self, tray: SystemTray, app):
        super().__init__()
        self.app = app
        self.tray = tray
        self._is_showing = False

        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint | Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: transparent; border: none;")

        self.widget = QWidget()
        self.widget.setStyleSheet("""
            background-color: rgba(37, 34, 42, 0.99);
            border-radius: 12px;
            border: 2px solid rgba(30, 31, 34, 0.3);
            padding: 0;
            margin: 0;
        """)
        self.setContentsMargins(0, 0, 0, 0)
        self.widget.setMinimumSize(250, 440)

        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # 添加控件
        # 1. LOGO标签
        self.addPlaceholder(18)
        self.logo_container = SiDenseHContainer(self.widget) # 容器
        self.logo_container.setSpacing(4)
        self.logo_container.setAlignment(Qt.AlignmentFlag.AlignCenter) # 设置内容为全部居中

        self.logo = IDLabel(self.widget) # LOGO图标
        self.logo.loadImage("static/images/Snow.png")

        self.logo_label = IDLabel(self.widget) # LOGO文字
        self.logo_label.setText("ICEDRIVE")
        self.logo_label.setFont(IceDriveFont.Others.YouSheBiaoTiHei(28))
        self.logo_label.setFixedStyleSheet("color: rgba(255, 255, 255, 0.9);")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.logo_label.adjustSize()

        self.logo_container.addPlaceholder(2)
        self.logo_container.addWidget(self.logo)
        self.logo_container.addWidget(self.logo_label)
        self.logo_container.adjustSize()

        self.addWidget(self.logo_container)

        self.addPlaceholder(12)
        self.addHSeparatorLine(2)

        # 2. CPU温度、GPU温度、风扇转速、水泵转速
        self.info_container = SiDenseVContainer(self.widget)
        self.info_container.setSpacing(4)
        # 第一部分
        self.info_container_1 = SiDenseHContainer(self.info_container)
        self.info_container_1.setAlignment(Qt.AlignCenter)
        self.info_container_1.setSpacing(12)

        self.cpu_info = IconDeviceInfo(self.widget)
        self.cpu_info.loadSvgData(SiGlobal.siui.iconpack.get("icedrive_ic_cpu"))
        self.cpu_info.setTemperatureInfo(0)
        self.cpu_info.setToolTip("CPU 温度\n0°C")

        self.gpu_info = IconDeviceInfo(self.widget)
        self.gpu_info.loadSvgData(SiGlobal.siui.iconpack.get("icedrive_ic_gpu"))
        self.gpu_info.setTemperatureInfo(0)
        self.gpu_info.setToolTip("GPU 温度\n0°C")

        self.info_container_1.addWidget(self.cpu_info)
        self.info_container_1.addWidget(self.gpu_info, "right")

        # 第二部分
        self.info_container_2 = SiDenseHContainer(self.info_container)
        self.info_container_2.setAlignment(Qt.AlignCenter)
        self.info_container_2.setSpacing(12)

        self.fan_info = IconDeviceInfo(self.widget)
        self.fan_info.loadSvgData(SiGlobal.siui.iconpack.get("icedrive_ic_fan"))
        self.fan_info.setRPMInfo(0)
        self.fan_info.setToolTip("风扇转速\n0 RPM")

        self.pump_info = IconDeviceInfo(self.widget)
        self.pump_info.loadSvgData(SiGlobal.siui.iconpack.get("icedrive_ic_pump"))
        self.pump_info.setRPMInfo(0)
        self.pump_info.setToolTip("水泵转速\n0 RPM")

        self.info_container_2.addWidget(self.fan_info)
        self.info_container_2.addWidget(self.pump_info, "right")

        self.info_container.addPlaceholder(16)
        self.info_container.addWidget(self.info_container_1)
        self.info_container.addPlaceholder(8)
        self.info_container.addWidget(self.info_container_2)
        self.info_container.addPlaceholder(8)

        self.addWidget(self.info_container)

        self.addHSeparatorLine(2)

        self.button_container_1 = SiDenseHContainer(self.widget)
        self.button_container_1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.button_container_1.setSpacing(8)
        self.button_container_1.setFixedStyleSheet("""
            margin: 0;
            padding: 0;
        """)

        self.normal_mode_btn = ModeButton(self.widget, active_mode=True)
        self.normal_mode_btn.loadSvgData(SiGlobal.siui.iconpack.get("icedrive_ic_normal_mode"))
        self.normal_mode_btn.setActive(True)
        self.rage_mode_btn = ModeButton(self.widget, active_mode=True)
        self.rage_mode_btn.loadSvgData(SiGlobal.siui.iconpack.get("icedrive_ic_rage_mode"))

        self.addPlaceholder(16)
        self.button_container_1.addWidget(self.normal_mode_btn)
        self.button_container_1.addWidget(self.rage_mode_btn)
        self.addWidget(self.button_container_1)
        self.addPlaceholder(8)

        self.button_container_2 = SiDenseHContainer(self.widget)
        self.button_container_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.button_container_2.setSpacing(8)
        self.button_container_2.setFixedStyleSheet("""
            margin: 0;
            padding: 0;
        """)

        self.home_btn = ModeButton(self.widget, active_mode=False)
        self.home_btn.loadSvgData(SiGlobal.siui.iconpack.get("icedrive_ic_home"))
        self.home_btn.btn.clicked.connect(lambda _: (self.app.showWindow(), self.hideMenu()))
        self.exit_btn = ModeButton(self.widget, active_mode=False)
        self.exit_btn.btn.clicked.connect(lambda _: (self.hideMenu(), TrayExitConfirmWindow(self.app).exec_()))
        self.exit_btn.loadSvgData(SiGlobal.siui.iconpack.get("icedrive_ic_exit"))

        self.button_container_2.addWidget(self.home_btn)
        self.button_container_2.addWidget(self.exit_btn)
        self.addWidget(self.button_container_2)

        # ===================== 菜单主体 =====================
        self.action = QWidgetAction(self)
        self.action.setDefaultWidget(self.widget)
        self.addAction(self.action)

        self.widget.adjustSize()
        self.adjustSize()

    def addHSeparatorLine(self, height: int, color: str = "rgba(28, 25, 31, 1)"):
        """添加水平分割线（左右淡化渐变）"""
        line = QWidget()
        line.setFixedHeight(height)

        # 线性渐变：两端透明 → 中间实色（你传入的 color）
        line.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 transparent,
                    stop:0.1 {color},
                    stop:0.9 {color},
                    stop:1 transparent
                );
                border: none;
                border-radius: 1px;
                margin: 0px 10px;
            }}
        """)

        self.addWidget(line)

    def addPlaceholder(self, height: int):
        """添加占位符"""
        placeholder = QWidget()
        placeholder.setStyleSheet("""
            background-color: transparent;
            border: none;
            margin: 0;
            padding: 0;
        """)
        placeholder.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        placeholder.setFixedHeight(height)
        self.layout.addWidget(placeholder)

    def addWidget(self, widget: QWidget):
        """添加控件到菜单"""
        self.layout.addWidget(widget)

    def mousePressEvent(self, event):
        # 当鼠标点击时
        if self.rect().contains(event.pos()):
            # 检测是否是在菜单内点击，如果是则拦截
            event.accept()
            return None

        self.cpu_info.tooltip.hide()
        self.gpu_info.tooltip.hide()
        self.fan_info.tooltip.hide()
        self.pump_info.tooltip.hide()

        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # 当鼠标释放时
        if self.rect().contains(event.pos()):
            # 检测是否是在菜单内点击，如果是则拦截
            event.accept()
            return None

        self.cpu_info.tooltip.hide()
        self.gpu_info.tooltip.hide()
        self.fan_info.tooltip.hide()
        self.pump_info.tooltip.hide()

        return super().mouseReleaseEvent(event)

    def hideMenu(self):
        """隐藏菜单"""
        self.hide()
        self.cpu_info.tooltip.hide()
        self.gpu_info.tooltip.hide()
        self.fan_info.tooltip.hide()
        self.pump_info.tooltip.hide()

    def showEvent(self, event):
        # 当菜单显示时，调整位置
        if self._is_showing:  # 防止递归
            return

        self._is_showing = True
        try:
            self.adjustSize()
            pos = self.pos()
            size = self.size()

            # 获取屏幕可用区域
            screen = QApplication.screenAt(pos) or QApplication.primaryScreen()
            rect = screen.availableGeometry()

            x = pos.x()
            y = pos.y()

            # 右边超出 → 左移
            if x + size.width() > rect.right():
                x = rect.right() - size.width() - 20
            # 左边超出 → 右移
            if x < rect.left():
                x = rect.left()
            # 下边超出 → 上移
            if y + size.height() > rect.bottom():
                y = rect.bottom() - size.height() - 20
            # 上边超出 → 下移
            if y < rect.top():
                y = rect.top()

            self.move(x, y)  # 安全移动
        finally:
            self._is_showing = False

        self.adjustSize()
        super().showEvent(event)