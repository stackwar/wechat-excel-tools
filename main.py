"""
从 Excel 读取关键词，调用系统级键鼠在微信中搜索并截图，回写到同一 Excel。

运行前：
1. 安装依赖：pip install -r requirements.txt
2. 复制 config.example.yaml 为 config.yaml（可选）
3. 登录微信，打开主界面，运行本脚本后不要操作鼠标键盘

打包：
  Windows: pyinstaller --onefile main.py
  macOS:   pyinstaller --onefile main.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from automation import screenshot_region, search_keyword_typing, sleep_sec
from excel_io import (
    embed_screenshot,
    ensure_output_dir,
    load_rows,
    resolve_excel_path,
    save_workbook,
    write_status,
)


def _deep_merge_defaults(defaults: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
    out = dict(defaults)
    for k, v in data.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = {**out[k], **v}  # type: ignore[arg-type]
        else:
            out[k] = v
    return out


def _load_config(path: Path | None) -> dict[str, Any]:
    defaults: dict[str, Any] = {
        'excel_path': '',
        'sheet_name': '搜索列表',
        'columns': {
            'keyword': '关键词',
            'status': '状态',
            'result': '结果摘要',
            'screenshot': '截图',
        },
        'automation': {
            'step_delay_sec': 0.8,
            'after_search_wait_sec': 1.5,
            'capture_region': None,
        },
        'hotkeys': {
            'open_search': 'command+f',
        },
    }
    if path is None or not path.is_file():
        return defaults
    suffix = path.suffix.lower()
    if suffix in ('.yaml', '.yml'):
        try:
            import yaml  # type: ignore
        except ImportError:
            print('未安装 PyYAML，请执行: pip install pyyaml 或改用 JSON 配置', file=sys.stderr)
            return defaults
        with path.open('r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        merged = _deep_merge_defaults(defaults, data)
        return merged
    if suffix == '.json':
        import json

        with path.open('r', encoding='utf-8') as f:
            data = json.load(f)
        return _deep_merge_defaults(defaults, data)
    print(f'不支持的配置文件后缀: {path}', file=sys.stderr)
    return defaults


def _region_from_config(val: Any) -> tuple[int, int, int, int] | None:
    if val is None:
        return None
    if isinstance(val, (list, tuple)) and len(val) == 4:
        return int(val[0]), int(val[1]), int(val[2]), int(val[3])
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description='微信搜索 + Excel 回写（键鼠自动化）')
    parser.add_argument(
        '-c',
        '--config',
        type=Path,
        default=None,
        help='配置文件路径（YAML 或 JSON），默认同目录 config.yaml / config.json',
    )
    parser.add_argument(
        '--countdown',
        type=int,
        default=5,
        help='开始前倒计时秒数，便于切换到微信窗口',
    )
    args = parser.parse_args()

    if getattr(sys, 'frozen', False):
        base = Path(sys.executable).resolve().parent
    else:
        base = Path(__file__).resolve().parent
    cfg_path = args.config
    if cfg_path is None:
        for name in ('config.yaml', 'config.yml', 'config.json'):
            p = base / name
            if p.is_file():
                cfg_path = p
                break

    cfg = _load_config(cfg_path)
    excel_path = resolve_excel_path(cfg.get('excel_path') or '')
    sheet_name = str(cfg.get('sheet_name') or '搜索列表')
    cols = cfg.get('columns') or {}
    col_kw = str(cols.get('keyword') or '关键词')
    col_status = str(cols.get('status') or '状态')
    col_result = str(cols.get('result') or '结果摘要')
    col_shot = str(cols.get('screenshot') or '截图')

    auto = cfg.get('automation') or {}
    step_delay = float(auto.get('step_delay_sec', 0.8))
    after_search = float(auto.get('after_search_wait_sec', 1.5))
    region = _region_from_config(auto.get('capture_region'))

    hotkeys = cfg.get('hotkeys') or {}
    open_search = str(hotkeys.get('open_search') or 'command+f')

    print(f'Excel: {excel_path}')
    print('即将开始：请切换到微信主窗口。倒计时结束后不要触碰鼠标键盘。')
    for i in range(max(0, args.countdown), 0, -1):
        print(f'  {i} ...')
        sleep_sec(1.0)

    ws, rows, headers = load_rows(excel_path, sheet_name, col_kw)
    print(f'共读取到 {len(rows)} 行关键词。')
    shot_dir = ensure_output_dir()

    first_run = True
    for item in rows:
        row = int(item['_row'])
        keyword = str(item['keyword'])

        # 跳过已成功的行
        if col_status in headers:
            existing = ws.cell(row=row, column=headers[col_status]).value
            if existing and str(existing).strip() == '成功':
                print(f'行 {row} 关键词「{keyword}」已成功，跳过。')
                continue

        shot_path = shot_dir / f'row_{row}.png'
        try:
            search_keyword_typing(
                keyword,
                step_delay=step_delay * 2 if first_run else step_delay,
                after_search_wait=after_search,
                open_search_hotkey=open_search,
            )
            first_run = False
            screenshot_region(region, shot_path)
            write_status(ws, row, headers, col_status, col_result, '成功', f'已搜索: {keyword}')
            embed_screenshot(ws, row, headers, col_shot, shot_path)
        except Exception as e:  # noqa: BLE001
            write_status(ws, row, headers, col_status, col_result, '失败', str(e))
        save_workbook(ws, excel_path)
        print(f'行 {row} 关键词「{keyword}」已处理并保存。')

    print('全部完成。')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
