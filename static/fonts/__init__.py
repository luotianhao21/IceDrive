import os
from siui.gui import SiFont
from PyQt5.QtGui import QFont, QFontDatabase

current_module_path = os.path.dirname(os.path.abspath(__file__))

class GlobalFontSize:
    S = 14
    M = 20
    L = 24
    XL = 32

class GlobalFontWeight:
    LIGHT = QFont.Weight.Light
    NORMAL = QFont.Weight.Normal
    MEDIUM = QFont.Weight.Medium
    DEMI_BOLD = QFont.Weight.DemiBold
    BOLD = QFont.Weight.Bold

def get_font(font_file_name, font_size, font_weight) -> SiFont:
    """
    获取字体实例的函数，加载指定路径下的字体文件，并返回一个 SiFont 实例\n
    :param font_file_name: 字体文件名，需放置在当前模块路径下
    :param font_size: 字体大小，建议使用 GlobalFontSize 中的预设值
    :param font_weight: 字体粗细，建议使用 QFont.Weight 中的预设值
    :return:
    """
    font_path = str(os.path.join(current_module_path, font_file_name))
    font_id = QFontDatabase.addApplicationFont(font_path)

    if font_id == -1:
        raise Exception(f"Failed to load font: {font_file_name}")

    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

    return SiFont.getFont(families=[font_family], size=font_size, weight=font_weight)

class IceDriveFont:
    # 本Font调用的多为vivoSans字体
    class vivoSans:
        # 变成函数，使用的时候再调用，不要自动执行
        @staticmethod
        def Light(font_size: int = GlobalFontSize.S):
            return get_font("vivoSans/vivoSansGlobal-Light.ttf", font_size, GlobalFontWeight.LIGHT)

        @staticmethod
        def Regular(font_size: int = GlobalFontSize.S):
            return get_font("vivoSans/vivoSansGlobal-Regular.ttf", font_size, GlobalFontWeight.NORMAL)

        @staticmethod
        def Heavy(font_size: int = GlobalFontSize.S):
            return get_font("vivoSans/vivoSansGlobal-Heavy.ttf", font_size, GlobalFontWeight.BOLD)

        @staticmethod
        def Bold(font_size: int = GlobalFontSize.S):
            return get_font("vivoSans/vivoSansGlobal-Bold.ttf", font_size, GlobalFontWeight.BOLD)

        @staticmethod
        def ExtraBold(font_size: int = GlobalFontSize.S):
            return get_font("vivoSans/vivoSansGlobal-Extrabold.ttf", font_size, GlobalFontWeight.BOLD)

        @staticmethod
        def DemiBold(font_size: int = GlobalFontSize.S):
            return get_font("vivoSans/vivoSansGlobal-Demibold.ttf", font_size, GlobalFontWeight.DEMI_BOLD)

    class Others:
        @staticmethod
        def YouSheBiaoTiHei(font_size: int = GlobalFontSize.S):
            return get_font("Others/YouSheBiaoTiHei.ttf", font_size, GlobalFontWeight.NORMAL)

        @staticmethod
        def AaJianHaoTi(font_size: int = GlobalFontSize.S):
            return get_font("Others/AaJianHaoTi.ttf", font_size, GlobalFontWeight.NORMAL)