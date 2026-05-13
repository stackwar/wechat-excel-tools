"""生成 search_list.xlsx 模板到脚本目录。"""

import sys
from pathlib import Path

from openpyxl import Workbook


def main() -> None:
    if getattr(sys, 'frozen', False):
        root = Path(sys.executable).resolve().parent
    else:
        root = Path(__file__).resolve().parent
    path = root / 'search_list.xlsx'
    wb = Workbook()
    ws = wb.active
    ws.title = '搜索列表'
    ws.append(['关键词', '状态', '结果摘要', '截图'])
    ws.append(['示例：某群名或联系人', '', '', ''])
    wb.save(path)
    print(f'已生成: {path}')


if __name__ == '__main__':
    main()
