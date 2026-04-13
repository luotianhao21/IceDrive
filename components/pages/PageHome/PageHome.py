from PyQt5.QtCore import Qt, QSize
import typing
import random

from siui.components import SiDenseHContainer, SiDenseVContainer, SiOptionCardPlane, SiLabel, SiMasonryContainer, \
    SiDraggableLabel, SiSimpleButton
from siui.components.page import SiPage
from siui.core import SiGlobal, SiColor
from siui.templates.application.application import SiliconApplication

from components.pages.PageHome.components import CPUInfoCard, GPUInfoCard, MemoryInfoCard
from components.widgets import IDLabel, IDScrollArea
from static.fonts import IceDriveFont


class PageHome(SiPage):
    def __init__(self, parent: SiliconApplication):
        super().__init__(parent)

        self.app = parent
        self.left_right_margin = 40 #左右间隔
        self.top_margin = 45 # 顶部间隔
        self.bottom_margin = 45 # 底部间隔

        self.removeWidget(self.scroll_area)
        # 替换滚动区域
        self.scroll_area = IDScrollArea(self)
        self.setAdjustWidgetsSize(True)
        self.addWidget(self.scroll_area)

        # 根容器
        self.__root_v_container = SiDenseVContainer(self)
        self.__root_v_container.setSpacing(0)
        self.__root_v_container.setContentsMargins(0, 0, 0, 0)
        self.__root_v_container.setAdjustWidgetsSize(True)
        self.__root_v_container.setFixedSize(self.size())

        self._root_container = SiDenseHContainer(self.__root_v_container)
        self._root_container.setSpacing(0)
        self._root_container.setContentsMargins(0, 0, 0, 0)
        self._root_container.setAdjustWidgetsSize(True)
        self._root_container.setFixedSize(
            self.__root_v_container.width() - self.left_right_margin * 2,
            self.__root_v_container.height() - self.top_margin - self.bottom_margin
        )

        self._container_1_context = SiDenseVContainer(self._root_container)
        self._container_1_context.setSpacing(30)
        self._container_1_context.setContentsMargins(0, 0, 0, 0)
        self._container_1_context.setAdjustWidgetsSize(True)
        self._container_1_context.setFixedSize(
            int(self.width() / 2) - self._root_container.spacing,
            self.height()
        )

        self.cpu_info_card = CPUInfoCard(self, self.app, self._container_1_context)
        #GPUcard
        self.gpu_info_card = GPUInfoCard(self, self.app, self._container_1_context)
        #Memory
        self .memory_info_card = MemoryInfoCard(self, self.app, self._container_1_context)
        '''
        self.cpu_info_card.setFixedSize(
            int(self._container_1_context.width()),
            int(self._container_1_context.height() / 3 - self._container_1_context.spacing * 2)
        )
        '''
        # 初始化时设定尺寸
        card_height = int(self._container_1_context.height() / 3 - self._container_1_context.spacing * 2)
        self.cpu_info_card.setFixedSize(int(self._container_1_context.width()), card_height)
        self.gpu_info_card.setFixedSize(int(self._container_1_context.width()), card_height)
        self.memory_info_card.setFixedSize(int(self._container_1_context.width()), card_height)


        self.__root_v_container.addPlaceholder(self.top_margin)
        self._root_container.addPlaceholder(self.left_right_margin)

        self._container_1_context.addWidget(self.cpu_info_card)
        self._container_1_context.addWidget(self.gpu_info_card)
        self._container_1_context.addWidget(self.memory_info_card)

        self._root_container.addWidget(self._container_1_context)
        self.__root_v_container.addWidget(self._root_container)
        # 设置根容器
        self.setAttachment(self.__root_v_container)

    def resizeEvent(self, event):
        if event is not None:
            super().resizeEvent(event)
        self.__root_v_container.setFixedSize(self.size())
        self._root_container.setFixedSize(
            self.__root_v_container.width() - self.left_right_margin * 2,
            self.__root_v_container.height() - self.top_margin - self.bottom_margin
        )
        self._container_1_context.setFixedSize(
            int(self.width() / 5 * 2) - self.left_right_margin - self._root_container.spacing,
            self._root_container.height()
        )
        '''
        self.cpu_info_card.setFixedSize(
            int(self._container_1_context.width()),
            int((self._container_1_context.height() - self._container_1_context.spacing * 2) / 3)
        )
        '''
        card_height = int((self._container_1_context.height() - self._container_1_context.spacing * 2) / 3)
        self.cpu_info_card.setFixedSize(int(self._container_1_context.width()), card_height)
        self.gpu_info_card.setFixedSize(int(self._container_1_context.width()), card_height)
        self.memory_info_card.setFixedSize(int(self._container_1_context.width()), card_height)
        # self._container_1_context.adjustSize()