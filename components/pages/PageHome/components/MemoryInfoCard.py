from typing import Optional

from PyQt5.QtCore import Qt, QSize
from siui.components import SiLabel, SiDenseVContainer, SiDenseHContainer
from siui.core import SiGlobal
from siui.templates.application.application import SiliconApplication

from components.pages import PageHome
from components.widgets import IDLabel
from components.pages.PageHome.components.widgets.CircularProgressWidget import CircularProgressWidget
from static.fonts import IceDriveFont


class MemoryInfoCard(IDLabel):
    def __init__(self, page: Optional[PageHome], app: SiliconApplication,
                 parent: SiDenseVContainer | SiDenseHContainer):
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
        self._body_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._body_container.setFixedSize(self._body_area.size())

        self.title_icon = IDLabel(self._header_container)
        self.title_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_icon.loadSvgData(SiGlobal.siui.iconpack.get("icedrive_ic_cpu", "#A855F7"), QSize(28, 28))
        self.title_icon.setTextGlow(
            enable=True,
            color=(0, 0, 0, 0),
            blur_radius=9,
            spread=4
        )
        self.title_icon.setSimpleBorderGlow(
            enable=True,
            color=(168, 85, 247, 80),
            blur_radius=20,
            offset=0
        )
        self.title_icon.adjustSize()

        self.title_text = IDLabel(self._header_container)
        self.title_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_text.setFont(IceDriveFont.vivoSansSimplifiedChinese.ExtraBold(18))
        self.title_text.setText("Memory 资源")
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
        self._header_container.addWidget(self.title_text)

        # 环形进度条
        self.ram_ring = CircularProgressWidget(self._body_area, title="内存使用率", unit="%", color="#A855F7")  # 紫色
        self.vram_ring = CircularProgressWidget(self._body_area, title="显存使用率", unit="%", color="#EC4899")  # 粉色

        self._body_container.addPlaceholder(20, "left")
        self._body_container.addWidget(self.ram_ring)
        self._body_container.addPlaceholder(20)
        self._body_container.addWidget(self.vram_ring)
        self._body_container.addPlaceholder(20, "right")

        # 初始数据
        self.ram_ring.setValue(45, max_val=100)
        self.vram_ring.setValue(82, max_val=100)

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

        # 自适应居中
        body_width = self._body_area.width()
        body_height = self._body_area.height()
        gap = 40
        max_ring_width = int((body_width - gap * 3) / 2)
        ring_size = min(max_ring_width, body_height - 20)

        if ring_size > 0:
            content_width = ring_size * 2 + gap
            x_start = max(int((body_width - content_width) / 2), gap)
            y_start = max(int((body_height - ring_size) / 2), 10)

            self.ram_ring.setGeometry(x_start, y_start, ring_size, ring_size)
            self.vram_ring.setGeometry(x_start + ring_size + gap, y_start, ring_size, ring_size)

        self.title_icon.adjustSize()
        self.title_text.adjustSize()