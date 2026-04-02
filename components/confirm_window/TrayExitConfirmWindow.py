from siui.core import SiGlobal

from components.confirm_window.components import ICPushButton
from libs import Signal
from static.fonts import IceDriveFont

from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget, QPushButton

from siui.components import SiDenseVContainer, SiDenseHContainer, SiLabel


class TrayExitConfirmWindow(QDialog):

    class confirm:
        exit = Signal() # 确认退出
        cancel = Signal() # 取消

    def __init__(self, parent=None):
        super().__init__(parent)

        self._width = 360
        self._height = 240

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
        self._header_container.setFixedSize(self._width, self._header.height())
        self._header_container.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self._body = QWidget()
        self._body.setContentsMargins(0, 0, 0, 0)
        self._body.setStyleSheet("""
            QWidget {
                background-color: #201E22;
                border-bottom-right-radius: 12px;  /* 右下角 */
                border-bottom-left-radius: 12px;   /* 左下角 */
            }
        """)
        self._body.setFixedHeight(200)
        self._body_container = SiDenseVContainer(self._body)
        self._body_container.setFixedSize(self._width, self._body.height())


        # =========添加控件========
        # Header
        self.title = SiLabel(self._header)
        self.title.setText("确认退出IceDrive吗？")
        self.title.setStyleSheet("""
            SiLabel {
                color: rgba(255, 255, 255, 0.9);
            }
        """)
        self.title.setFont(IceDriveFont.vivoSansSimplifiedChinese.Bold(14))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.adjustSize()

        self.close_btn = ICPushButton(self._header)
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
        self.close_btn.loadSvgData(SiGlobal.siui.iconpack.get("ic_fluent_dismiss_filled"), size=QSize(24, 24), color="#FFFFFF")
        self.close_btn.adjustSize()

        self._header_container.addPlaceholder(4)
        self._header_container.addWidget(self.title)
        self._header_container.addWidget(self.close_btn, "right")


        self.root_layout.addWidget(self._header)
        self.root_layout.addWidget(self._body)

    def headerAddWidget(self, widget: QWidget, side="left", index=10000):
        """
        给Header添加一个控件
        :param widget: 控件
        :param side: 添加侧
        :param index: 插入位置
        :return:
        """
        self._header_container.addWidget(widget, side, index)

    def bodyAddWidget(self, widget: QWidget, side="top", index=10000):
        """
        给Body添加一个控件
        :param widget: 控件
        :param side: 添加侧
        :param index: 插入位置
        :return:
        """
        self._body_container.addWidget(widget, side, index)