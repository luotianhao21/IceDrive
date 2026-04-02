from siui.core import SiGlobal
from siui.templates.application.application import SiliconApplication

from components.confirm_window.components import IDPushButton
from components.system_tray.widgets import IDLabel
from libs import Signal
from static.fonts import IceDriveFont

from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget, QPushButton, QLabel

from siui.components import SiDenseVContainer, SiDenseHContainer, SiLabel


class TrayExitConfirmWindow(QDialog):

    class confirm:
        exit = Signal() # 确认退出
        cancel = Signal() # 取消

    def __init__(self, parent: SiliconApplication | None = None):
        super().__init__(parent)

        self._width = 360
        self._height = 250
        self.app = parent

        self.setWindowTitle("确认退出IceDrive")
        self.setFixedSize(self._width, self._height)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("""
            QDialog {
                padding: 0;
                margin: 0;
                border: 2px solid rgba(48, 47, 50, 0.8);
            }
        """)

        # 无边框
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.m_drag = False
        self.m_dragPos = QPoint(0, 0)

        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        self._header = QWidget()
        self._header.setContentsMargins(0, 0, 0, 0)
        self._header.setStyleSheet("""
            QWidget {
                background-color: #333038;
                border-top-left-radius: 12px;     /* 左上角 */
                border-top-right-radius: 12px;     /* 右上角 */
            }
        """)
        self._header.setFixedHeight(40)
        self._header_container = SiDenseHContainer(self._header)
        self._header_container.setSpacing(0)
        self._header_container.setFixedSize(self._width, self._header.height())
        self._header_container.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self._body = QWidget()
        self._body.setContentsMargins(0, 0, 0, 0)
        self._body.setStyleSheet("""
            QWidget {
                background-color: #201E22;
                border-radius: 0px;
            }
        """)
        self._body.setFixedHeight(160)
        self._body_container = SiDenseVContainer(self._body)
        self._body_container.setSpacing(0)
        self._body_container.setFixedSize(self._width, self._body.height())
        self._body_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._foot = QWidget()
        self._foot.setContentsMargins(0, 0, 0, 0)
        self._foot.setStyleSheet("""
            QWidget {
                background-color: #201E22;
                border-bottom-left-radius: 12px;     /* 左下角 */
                border-bottom-right-radius: 12px;     /* 右下角 */
            }
        """)
        self._foot.setFixedHeight(50)
        self._foot_container = SiDenseHContainer(self._foot)
        self._foot_container.setSpacing(0)
        self._foot_container.setFixedSize(self._width, self._foot.height())
        self._foot_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # =========添加控件========
        # Header
        self.title = SiLabel(self._header)
        self.title.setText("确认退出IceDrive吗？")
        self.title.setStyleSheet("""
            SiLabel {
                color: #D0D0D0;
            }
        """)
        self.title.setFont(IceDriveFont.vivoSansSimplifiedChinese.Bold(14))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.adjustSize()

        self.close_btn = IDPushButton(self._header)
        self.close_btn.setFixedSize(self._header.height(), self._header.height())
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-top-right-radius: 12px;     /* 右上角 */
                border-top-left-radius: 0px;     /* 左上角 */
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.close_btn.loadSvgData(SiGlobal.siui.iconpack.get("ic_fluent_dismiss_filled"), size=QSize(20, 20), color="#F19DBD")
        self.close_btn.adjustSize()
        self.close_btn.clicked.connect(lambda _: self.close())

        self._header_container.addPlaceholder(10)
        self._header_container.addWidget(self.title)
        self._header_container.addWidget(self.close_btn, "right")


        # Body
        self.label = IDLabel(self._body)
        self.label.setFont(IceDriveFont.vivoSansSimplifiedChinese.Bold(16))
        self.label.setStyleSheet("""
            IDLabel {
                color: #D0D0D0;
            }
        """)
        self.label.setText("呜呜呜…\n真的要退出IceDrive吗？")
        self.label.adjustSize()

        self.label_image = IDLabel(self._body)
        self.label_image.loadGifImage("static/images/exit/1.gif", QSize(78, 78))
        self.label_image.adjustSize()

        self._body_container.addPlaceholder(20)
        self._body_container.addWidget(self.label)
        self._body_container.addPlaceholder(10)
        self._body_container.addWidget(self.label_image)


        # Foot
        self.exit_btn = IDPushButton(self._foot)
        self.exit_btn.setStyleSheet("""
            IDPushButton {
                color: #D0D0D0;
                background: #5B865E;
                border: none;
                border-radius: 8px;
                padding: 0 4px 0 10px;
            }
            IDPushButton:hover {
                background: #405E42;
            }
            IDPushButton:pressed {
                background: #2C402E;
            }
        """)
        self.exit_btn.setFont(IceDriveFont.vivoSansSimplifiedChinese.Bold(14))
        self.exit_btn.setText("我就是要退出！")
        self.exit_btn.adjustSize()
        self.exit_btn.setFixedWidth(int(self.width() / 2) - 15)
        self.exit_btn.setFixedHeight(self._foot.height() - 22)
        self.exit_btn.clicked.connect(lambda _: self.app.close())

        self.cancel_btn = IDPushButton(self._foot)
        self.cancel_btn.setStyleSheet("""
            IDPushButton {
                color: #D0D0D0;
                background: #865F5E;
                border: none;
                border-radius: 8px;
                padding: 0 10px 0 10px;
            }
            IDPushButton:hover {
                background: #5B403F;
            }
            IDPushButton:pressed {
                background: #3A2928;
            }
        """)
        self.cancel_btn.setFont(IceDriveFont.vivoSansSimplifiedChinese.Bold(14))
        self.cancel_btn.setText("不退了")
        self.cancel_btn.adjustSize()
        self.cancel_btn.setFixedWidth(int(self.width() / 2) - 15)
        self.cancel_btn.setFixedHeight(self._foot.height() - 22)
        self.cancel_btn.clicked.connect(lambda _: self.closeConfirmWindow())

        self._foot_container.addPlaceholder(10, "right")
        self._foot_container.addWidget(self.exit_btn, "right")
        self._foot_container.addPlaceholder(10, "left")
        self._foot_container.addWidget(self.cancel_btn, "left")

        self.root_layout.addWidget(self._header)
        self.root_layout.addWidget(self._body)
        self.root_layout.addWidget(self._foot)

    def exec_(self):
        # 启动Gif动画
        self.label_image.startGif()
        super().exec_()
        
    def close(self):
        self.label_image.stopGif()
        super().close()

    def closeConfirmWindow(self):
        self.confirm.cancel.emit()
        self.close()
        # 释放资源
        del self