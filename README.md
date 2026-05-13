# 微信搜索 + Excel 回写（示例工具）

## 功能概述

1. 在指定目录（默认同脚本目录）维护 `search_list.xlsx`，表头需包含「关键词」列（可在 `config.yaml` 改列名）。
2. 运行 `python main.py`：按行读取关键词，通过**系统级键盘快捷键**在微信中触发搜索并截图，将**状态、结果摘要、截图**写回 Excel。
3. 运行前请**登录微信**并打开主窗口；倒计时期间切换到微信，倒计时结束后**不要操作键鼠**。

## 重要说明（合规与稳定性）

- 微信**无官方个人号自动化接口**。本工具使用 `pyautogui` 模拟快捷键与输入，可能违反腾讯用户协议，请自行评估合规风险，仅限个人学习与内部效率场景。
- 不同微信版本、系统语言、显示缩放、窗口布局会导致**同一套快捷键/流程失效**，必须在 `config.yaml` 中按你的环境调参，必要时自行改 `automation.py`（例如增加固定坐标点击、图像模板匹配等）。

## 环境

- Python 3.10+（建议）
- macOS / Windows

```bash
cd tools/wechat-excel-automation
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 配置文件

复制 `config.example.yaml` 为 `config.yaml`（或改用 `config.json`）。

- **Windows** 请将 `hotkeys.open_search` 改为 `ctrl+f`（若你的微信搜索快捷键不同，以实际为准）。
- **capture_region**：建议填写 `[left, top, width, height]` 只截微信窗口区域，避免全屏图过大；可用系统截图工具查看坐标估算。
- **excel_path**：留空则使用脚本目录下的 `search_list.xlsx`。

## 准备 Excel

表头示例（第一行）：

| 关键词 | 状态 | 结果摘要 | 截图 |
|--------|------|----------|------|
| 测试联系人 | | | |

生成空模板：

```bash
python create_template.py
```

## 运行

1. 打开微信主界面。
2. 执行：

```bash
python main.py --countdown 5
```

倒计时内切换到微信；结束后脚本会逐行搜索并保存 Excel。

## 打包为可执行文件

使用 [PyInstaller](https://pyinstaller.org/)：

```bash
pip install pyinstaller
pyinstaller --onefile --name wechat-excel-search main.py
```

- Windows 产物在 `dist/wechat-excel-search.exe`。
- macOS 产物在 `dist/wechat-excel-search`；首次可能需在「隐私与安全性」中允许辅助功能/录屏权限（系统设置里为终端或该 app 勾选）。

请将 `config.yaml`、`search_list.xlsx` 与可执行文件放在同一目录分发（或让用户通过 `excel_path` 指到维护目录）。

## 中文关键词与剪贴板

非英文关键词通过剪贴板粘贴。macOS 可能弹出「是否允许访问剪贴板」授权，请允许终端或打包后的 app。

## 目录结构

| 文件 | 说明 |
|------|------|
| `main.py` | 入口 |
| `excel_io.py` | Excel 读写与嵌入图片 |
| `automation.py` | 截图与搜索键序 |
| `create_template.py` | 生成示例 xlsx |
| `config.example.yaml` | 配置样例 |
