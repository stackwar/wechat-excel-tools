# 微信搜索 + Excel 回写

从 Excel 读取关键词，通过键鼠模拟在微信桌面端逐个搜索并截图，将状态、摘要、截图回写到同一 Excel。

## 功能特性

- 批量搜索：按 Excel 行逐个执行微信搜索
- 自动截图：搜索后自动截取指定区域并嵌入 Excel
- 断点续跑：已成功的行自动跳过，中断后重跑不会重复
- 跨平台：macOS / Windows 均可运行
- 可打包：支持 PyInstaller 打包为单文件 exe 分发

## 合规声明

微信无官方个人号自动化接口。本工具使用 `pyautogui` 模拟快捷键与输入，可能违反腾讯用户协议，请自行评估合规风险，仅限个人学习与内部效率场景。

## 环境要求

- Python 3.10+
- macOS / Windows

## 安装

```bash
cd wechat-excel-automation
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 配置

复制 `config.example.yaml` 为 `config.yaml`：

```bash
cp config.example.yaml config.yaml
```

关键配置项：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `excel_path` | Excel 路径，留空则用脚本目录下的 `search_list.xlsx` | `""` |
| `sheet_name` | 工作表名 | `搜索列表` |
| `hotkeys.open_search` | 打开搜索的快捷键 | `command+f`（Windows 改为 `ctrl+f`） |
| `automation.step_delay_sec` | 每步间隔秒数 | `0.8` |
| `automation.after_search_wait_sec` | 搜索后等待截图的秒数 | `1.5` |
| `automation.capture_region` | 截图区域 `[left, top, width, height]`，null 为全屏 | `null` |

## 准备 Excel

表头格式（第一行）：

| 关键词 | 状态 | 结果摘要 | 截图 |
|--------|------|----------|------|
| 某群名或联系人 | | | |

生成空白模板：

```bash
python create_template.py
```

## 运行

1. 登录微信，打开主窗口
2. 执行脚本：

```bash
python main.py --countdown 5
```

3. 倒计时内将鼠标移到微信窗口内，倒计时结束后不要操作键鼠

参数说明：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-c / --config` | 配置文件路径 | 自动查找同目录 `config.yaml` |
| `--countdown` | 开始前倒计时秒数 | `5` |

## 打包为 Windows EXE

### 方式一：本地打包（需 Windows 环境）

```bash
pip install pyinstaller
pyinstaller --onefile --name wechat-search --hidden-import=yaml main.py
```

产物在 `dist/wechat-search.exe`。

### 方式二：GitHub Actions 自动构建

项目已包含 `.github/workflows/build-windows.yml`，推送 tag 即可触发：

```bash
git tag v1.0
git push --tags
```

构建完成后在 GitHub Actions 页面下载产物。也可在 Actions 页面手动点击 "Run workflow" 触发。

### 分发结构

将以下文件放在同一目录交付给用户：

```
wechat-search/
├── wechat-search.exe
├── config.yaml          # 用户按需修改
├── search_list.xlsx     # 填入关键词
└── output/              # 运行后自动生成
    └── screenshots/
```

## macOS 权限

首次运行可能需要在「系统设置 → 隐私与安全性」中授权：

- 辅助功能（键鼠控制）
- 屏幕录制（截图）

为终端或打包后的 app 勾选对应权限。

## 中文关键词

非 ASCII 关键词通过剪贴板粘贴输入。macOS 可能弹出剪贴板访问授权提示，请允许。

## 目录结构

| 文件 | 说明 |
|------|------|
| `main.py` | 入口：加载配置、遍历关键词、调度搜索与回写 |
| `automation.py` | 键鼠自动化：快捷键、输入、截图 |
| `excel_io.py` | Excel 读写：读取关键词、写状态、嵌入截图 |
| `create_template.py` | 生成空白 Excel 模板 |
| `config.example.yaml` | 配置文件样例 |
| `requirements.txt` | Python 依赖 |
| `.github/workflows/build-windows.yml` | GitHub Actions 自动打包 |
