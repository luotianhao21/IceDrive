from typing import Optional

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from siui.components import SiLabel, SiDenseVContainer, SiDenseHContainer
from siui.core import SiGlobal
from siui.templates.application.application import SiliconApplication

from components.pages import PageHome
from components.widgets import IDLabel, IDCircularProgressBar
from static.fonts import IceDriveFont
from static.icons import IceDriveCustomIconDictionary


class CPUInfoCard(IDLabel):
    def __init__(self, page: Optional[PageHome], app: SiliconApplication, parent: SiDenseVContainer | SiDenseHContainer):
        super().__init__(parent)
        if page is None:
            raise ValueError("PageHome instance is required")

        self.app = app
        self._page = page
        self._parent = parent
        self._border_radius = 8

        self._width = 0
        self._height = 0

        self.setStyleSheet(f"""
            background: #332E38;
            border-radius: {self._border_radius}px;
            border: 1px solid #433D4A;
        """)
        self.enableGradientBorder(True)
        self.setGradientBorderConfig(
            width=1,
            radius=self._border_radius,
            color_start=(131, 122, 130, 70),
            color_end=(131, 122, 130, 15)
        )

        self._root_container = SiDenseVContainer(self)
        self._root_container.setSpacing(0)
        self._root_container.setContentsMargins(0, 0, 0, 0)
        self._root_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._root_container.setFixedSize(self.size())

        self._header_height = 60
        self._header_area = SiLabel(self._root_container)
        self._header_area.setFixedSize(self.width(), self._header_height)
        self._header_area.setStyleSheet(f"""
            SiLabel {{
                background: transparent;
                border-top-right-radius: {self._border_radius}px;
                border-top-left-radius: {self._border_radius}px;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: 0px;
                border: none;
            }}
        """)

        self._body_area = SiLabel(self._root_container)
        self._body_area.setGeometry(
            0, self._header_height,
            self.width(), self.height() - self._header_height
        )
        self._body_area.setStyleSheet(f"""
            SiLabel {{
                background: transparent;
                border-top-right-radius: 0px;
                border-top-left-radius: 0px;
                border-bottom-right-radius: {self._border_radius}px;
                border-bottom-left-radius: {self._border_radius}px;
                border: none;
            }}
        """)

        self._header_container = SiDenseHContainer(self._header_area)
        self._header_container.setSpacing(0)
        self._header_container.setContentsMargins(0, 0, 0, 0)
        self._header_container.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._header_container.setFixedSize(self._header_area.size())

        self._body_container = SiDenseHContainer(self._body_area)
        self._body_container.setSpacing(0)
        self._body_container.setContentsMargins(0, 0, 0, 0)
        #self._body_container.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._body_container.setFixedSize(self._body_area.size())

        self.title_icon = IDLabel(self._header_container)
        self.title_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_icon.loadSvgData(SiGlobal.siui.iconpack.get("icedrive_ic_cpu", "#22C4DE"), QSize(28, 28))
        self.title_icon.setTextGlow(
            enable=True,
            color=(0, 0, 0, 0),
            blur_radius=9,
            spread=4
        )
        self.title_icon.setSimpleBorderGlow(
            enable=True,
            color=(88, 107, 111, 180),
            blur_radius=20,
            offset=0
        )
        self.title_icon.adjustSize()

        self.title_text = IDLabel(self._header_container)
        self.title_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_text.setFont(IceDriveFont.vivoSansSimplifiedChinese.ExtraBold(18))
        self.title_text.setText("CPU 状态")
        self.title_text.setStyleSheet("""
            IDLabel {
                color: #FFFFFF;
                border: none;
            }
        """)
        self.title_text.setTextGlow(
            enable=False,
            color=(255, 255, 255, 6),
            blur_radius=15,
            spread=3
        )
        self.title_text.adjustSize()

        self._header_container.addPlaceholder(int((self._header_height - self.title_icon.height()) / 2))
        self._header_container.addWidget(self.title_icon)
        #self._header_container.addPlaceholder(6)
        self._header_container.addWidget(self.title_text)

        self.test = IDCircularProgressBar(self._body_container)
        self.test.setBarWidth(10, 15)
        self.test.setValue(71 * 0.01)
        #self.test.setIndeterminate(True)
        self.test.setInnerText("71")
        self.test.setUnitFromBottom(20)
        self.test.setUnit("度")
        self.test.setTitle("CPU 温度")
        self._body_container.addWidget(self.test)

        self._root_container.addWidget(self._header_container)
        self._root_container.addWidget(self._body_container)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._root_container.setFixedSize(self.size())
        self._header_area.setFixedSize(self.width(), self._header_height)
        self._body_area.setGeometry(
            0, self._header_height,
            self.width(), self.height() - self._header_height
        )
        self._header_container.setFixedSize(self._header_area.size())
        self._body_container.setFixedSize(self._body_area.size())
        self.test.setBarWidth(10, 60)
        self.title_icon.adjustSize()
        self.title_text.adjustSize()