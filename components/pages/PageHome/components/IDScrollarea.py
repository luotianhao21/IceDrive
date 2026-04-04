# 重写SiScrollArea
from siui.components import SiScrollArea


class IDScrollArea(SiScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

    def wheelEvent(self, event):
        # 滚轮只在竖直方向上滚动
        # TODO: 后期滚动条和滚动区域分开，鼠标移动到不同滚动条上控制不同方向上的滚动

        # 滚动强度，决定一个滚动单位需滚动多少像素
        strength = 100

        # 读取子控件的移动动画目标值
        target = self.widget_scroll_animation.target()

        # 根据滚动方向，目标值加或减滚动强度，并更新目标值
        target[1] += strength if event.angleDelta().y() > 0 else -strength
        target[1] = min(0, max(self.height() - self.attachment_.height(), target[1]))  # 防止滚出限制范围
        self.widget_scroll_animation.setTarget(target)


        # 计算滚动条的目标位置，修复了滚动条位置小于零
        scrollable_height = self.attachment_.height() - self.height()
        if scrollable_height > 0:
            process = -target[1] / scrollable_height
            scroll_bar_vertical_target_y = int(process * (self.height() - self.scroll_bar_vertical.height()))
        else:
            scroll_bar_vertical_target_y = 0  # 内容不需要滚动时,滚动条位置设为 0

        # 以下为源代码
        # 计算滚动条的目标位置
        # process = -target[1] / (self.attachment_.height() - self.height())
        # scroll_bar_vertical_target_y = int(process * (self.height() - self.scroll_bar_vertical.height()))

        # 如果竖直方向滚动条可见，尝试启动动画
        if self.scroll_bar_vertical.isVisible():
            self.scroll_bar_vertical.moveTo(0, scroll_bar_vertical_target_y)
            self.widget_scroll_animation.try_to_start()
            event.accept()