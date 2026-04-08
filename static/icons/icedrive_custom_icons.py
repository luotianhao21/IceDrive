import os
import re

from PyQt5.QtGui import QColor

current_module_path = os.path.dirname(os.path.abspath(__file__))
data_file_path = os.path.join(current_module_path, './icedrive_custom_icons.dat')

def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

class IceDriveCustomIconDictionary:
    def __init__(self):
        # 自定义的为明文储存
        self.icons: dict[str, str] = {}
        self.icons_class = 'icedrive_custom_icon'

        with open(data_file_path, 'r', encoding='utf-8') as f:
            library = f.read()
            library_list = library.split('!!!')[1:] # 分割并去掉第一个空项
            name = []
            data = []
            for item in library_list:
                n, d = item.split('###')
                name.append(n)
                if 'fill' not in d:
                    d = d.replace('></path>', ' fill="<<<COLOR_CODE>>>"></path>')
                elif 'fill' in d and '<<<COLOR_CODE>>>' not in d:
                    d = re.sub(r'fill=".*?"', 'fill="<<<COLOR_CODE>>>"', d)
                data.append(d)
        self.icons: dict[str, str] = dict(zip(name, data))

    def get(self, name: str, color: str | QColor = QColor(255, 255, 255)) -> str:
        try:
            if isinstance(color, QColor):
                color = color.name()
            svg_data: str = self.icons[name]
            return svg_data.replace('<<<COLOR_CODE>>>', color)
        except Exception as e:
            print(f"Error getting icon {name}: {e}")
            return ''
if __name__ == "__main__":
    icon_dict = IceDriveCustomIconDictionary()