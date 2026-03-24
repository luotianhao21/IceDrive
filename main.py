# main.py
import sys
from PyQt5.QtWidgets import QApplication

import siui
from siui.core import SiGlobal, SiColor
from static import icons
from app import IceDriveApp  # 从独立文件导入IceDriveApp

# 仅在主进程执行一次图标注册（避免循环引用重复执行）
if __name__ == "__main__":
    # 载入图标
    siui.core.globals.SiGlobal.siui.loadIcons(
        icons.IconDictionary(color=SiGlobal.siui.colors.fromToken(SiColor.SVG_NORMAL)).icons
    )

    # 添加自定义图标
    baqian_custom_icons = icons.IceDriveCustomIconDictionary()
    SiGlobal.siui.iconpack.append_class(baqian_custom_icons.icons_class)
    for key, data in baqian_custom_icons.icons.items():
        SiGlobal.siui.iconpack.append(key, data, baqian_custom_icons.icons_class)

    # 启动应用
    app = QApplication(sys.argv)
    ice_drive_window = IceDriveApp()
    ice_drive_window.show()
    sys.exit(app.exec_())