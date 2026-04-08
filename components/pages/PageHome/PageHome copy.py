from PyQt5.QtCore import Qt, QSize
import typing

from siui.components import SiDenseHContainer, SiDenseVContainer, SiOptionCardPlane, SiLabel
from siui.components.page import SiPage
from siui.core import SiGlobal
from siui.templates.application.application import SiliconApplication

from components.system_tray.widgets import IDLabel
from static.fonts import IceDriveFont
from .components import IDScrollArea


class PageHome(SiPage):
    def __init__(self, parent: SiliconApplication):
        super().__init__(parent)

        self.app = parent
        self.bottom_height = 20 # 底部空白高度

        self.removeWidget(self.scroll_area)
        # 替换滚动区域
        self.scroll_area = IDScrollArea(self)
        self.setAdjustWidgetsSize(True)

        self.addWidget(self.scroll_area)

        self._root_container = SiDenseVContainer(self)
        self._root_container.setSpacing(0)
        self._root_container.setContentsMargins(0, 0, 0, 0)
        self._root_container.setAdjustWidgetsSize(True) # 适配子组件大小

        # 左侧区域
        self._left_area_width = 600 # 左侧区域宽度
        self._left_area = SiLabel(self)
        self._left_area.setFixedSize(
            self._left_area_width,
            self.app.height() - self.app.layer_main.container_title.height()
        )

        # 左侧区域容器
        self._left_container = SiDenseVContainer(self._left_area)
        # 左侧区域左上角的位置
        self._left_container_spacing_point = QSize(30, 30)
        # 左侧区域容器间距
        self._left_container.setSpacing(10)
        self._left_container.setContentsMargins(0, 0, 0, 0)

        # 左侧标题
        # 容器
        self._left_title_container = SiDenseHContainer(self._left_container)
        self._left_title_container.setAdjustWidgetsSize(True)
        self._left_title_container.setSpacing(0)
        # 左侧标题图标
        self._left_title_icon = IDLabel(self._left_title_container)
        self._left_title_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._left_title_icon.loadSvgData(SiGlobal.siui.iconpack.get("icedrive_ic_list"), size=QSize(32, 32))
        self._left_title_icon.adjustSize()
        # 左侧标题
        self._left_title = IDLabel(self._left_title_container)
        self._left_title.setFont(IceDriveFont.vivoSansSimplifiedChinese.ExtraBold(28))
        self._left_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._left_title.setText("DEVICE INFO")
        self._left_title.setStyleSheet("""
            IDLabel {
                color: #D2D2D2;
            }
        """)
        self._left_title.adjustSize()

        self._left_title_container.addPlaceholder(8)
        self._left_title_container.addWidget(self._left_title_icon)
        self._left_title_container.addPlaceholder(18)
        self._left_title_container.addWidget(self._left_title)
        self._left_title_container.adjustSize()

        # 左侧区域内容
        self._left_body_area = IDLabel(self._left_container)
        self._left_body_area.setFixedSize(
            self._left_area_width - self._left_container_spacing_point.width() * 2,
            self._left_area.height() - self._left_container.spacing - self._left_title_container.height() - self._left_container_spacing_point.height() - self.bottom_height
        )
        self._left_body_area.setFixedStyleSheet("""
            IDLabel {
                background-color: #252228;
                border-radius: 20px;
                border: 2px solid transparent;
                border-image: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(58, 55, 65, 0.3),
                    stop:0.5 rgba(58, 55, 65, 0.15),
                    stop:1 rgba(58, 55, 65, 0.05)
                );
                color: #D2D2D2;
            }
        """)

        self._left_container.addWidget(self._left_title_container)
        self._left_container.addWidget(self._left_body_area)
        self._left_container.setGeometry(
            self._left_container_spacing_point.width(),
            self._left_container_spacing_point.height(),
            self._left_area.width() - self._left_container_spacing_point.width() * 2,
            self._left_area.height() - self._left_container_spacing_point.height() - self.bottom_height
        )

        self._root_container.addWidget(self._left_area)

        # 设置根容器
        self.setAttachment(self._root_container)

    def resizeEvent(self, event):
        if event is not None:
            super().resizeEvent(event)

        self._left_area.setFixedSize(
            self._left_area_width,
            self.app.height() - self.app.layer_main.container_title.height()
        )
        self._left_body_area.setFixedSize(
            self._left_area_width - self._left_container_spacing_point.width() * 2,
            self._left_area.height() - self._left_container.spacing - self._left_title_container.height() - self._left_container_spacing_point.height() - self.bottom_height
        )
        self._left_container.setFixedSize(
            self._left_area.width() - self._left_container_spacing_point.width() * 2,
            self._left_area.height() - self._left_container_spacing_point.height() - self.bottom_height
        )
        self._root_container.adjustSize()

    @typing.overload
    def setLeftAreaPosition(self, point: QSize):
        ...

    @typing.overload
    def setLeftAreaPosition(self, x: int, y: int):
        ...

    def setLeftAreaPosition(self, *args):
        """
        设置左侧区域左上角位置
        """
        if len(args) == 1:
            point = args[0]
        elif len(args) == 2:
            point = QSize(args[0], args[1])
        else:
            point = QSize(0, 0)

        self._left_container_spacing_point = point
        self._left_area.setGeometry(
            point.width(),
            point.height(),
            self._left_area.width(),
            self._left_area.height()
        )
        self.resizeEvent(None)

    def setLeftAreaWidth(self, width: int):
        """
        设置左侧区域的宽度，会减去self._left_container_spacing_point.width() * 2的左右间隔
        :param width:
        :return:
        """
        self._left_area_width = width
        self.resizeEvent(None)