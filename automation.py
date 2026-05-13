"""
跨平台简单自动化：键盘输入 + 截图。

说明：微信桌面版无官方自动化接口，不同版本/语言/缩放下界面不同。
本模块只提供「通用键鼠」能力；具体键序请在 config 里按你的客户端调整。
"""

from __future__ import annotations

import platform
import time
from pathlib import Path

import pyautogui
import pyperclip

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


def sleep_sec(sec: float) -> None:
    time.sleep(max(0.0, sec))


def screenshot_region(
    region: tuple[int, int, int, int] | None,
    save_path: Path,
) -> Path:
    """
    region: (left, top, width, height)，None 表示全屏。
    """
    save_path.parent.mkdir(parents=True, exist_ok=True)
    if region is None:
        im = pyautogui.screenshot()
    else:
        im = pyautogui.screenshot(region=region)
    im.save(str(save_path))
    return save_path


def hotkey_from_string(spec: str) -> list[str]:
    """
    例如 "command+f" / "ctrl+f" -> pyautogui.hotkey 参数列表。
    在 macOS 上使用 command，在 Windows 上使用 ctrl。
    """
    raw = [p.strip().lower() for p in spec.split('+') if p.strip()]
    out: list[str] = []
    is_mac = platform.system() == 'Darwin'
    for p in raw:
        if p in ('cmd', 'command', 'win', 'meta', 'super'):
            out.append('command' if is_mac else 'ctrl')
        elif p == 'ctrl':
            out.append('ctrl')
        elif p == 'alt':
            out.append('alt')
        elif p == 'shift':
            out.append('shift')
        else:
            out.append(p)
    return out


def search_keyword_typing(
    keyword: str,
    *,
    step_delay: float,
    after_search_wait: float,
    open_search_hotkey: str,
) -> None:
    """
    默认流程：请先手动点开微信主窗口，并确保「打开搜索」快捷键可用。

    1) 发送打开搜索快捷键
    2) 全选、输入关键词、回车
    """
    keys = hotkey_from_string(open_search_hotkey)
    sleep_sec(step_delay)
    pyautogui.click()
    sleep_sec(0.3)
    pyautogui.hotkey(*keys)
    sleep_sec(step_delay)
    if platform.system() == 'Darwin':
        pyautogui.hotkey('command', 'a')
    else:
        pyautogui.hotkey('ctrl', 'a')
    sleep_sec(0.1)
    # typewrite 仅适合 ASCII；中文等用剪贴板粘贴（需系统允许 Python 访问剪贴板）
    if keyword.isascii():
        pyautogui.typewrite(keyword, interval=0.03)
    else:
        pyperclip.copy(keyword)
        if platform.system() == 'Darwin':
            pyautogui.hotkey('command', 'v')
        else:
            pyautogui.hotkey('ctrl', 'v')
    sleep_sec(after_search_wait)
