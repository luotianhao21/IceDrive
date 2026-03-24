import os
import re

current_module_path = os.path.dirname(os.path.abspath(__file__))
data_file_path = os.path.join(current_module_path, './icedrive_custom_icons.dat')

class IceDriveCustomIconDictionary:
    def __init__(self):
        # 自定义的为明文储存
        self.icons = {}
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
        self.icons = dict(zip(name, data))

if __name__ == "__main__":
    icon_dict = IceDriveCustomIconDictionary()