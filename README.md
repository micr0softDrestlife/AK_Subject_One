# AK_Subject_One

当前版本：`v4.1`

AK_Subject_One 是一个“截图 -> OCR -> AI 解题”的桌面工具，目标是在尽量不打断当前操作的前提下，快速完成识别与答题。

## 功能总览

- 完整链路：区域截图 -> OCR 识别 -> AI 解题 -> 结果展示。
- 全局快捷键：
  - `Shift+L`：无焦点触发解题链路。
  - `Shift+K`：切换简化模式。
  - `Shift+J`：切换已选区域边框样式（红/透明/黑/浅白）。
  - `Shift+H`：重选识别区域。
  - `Ctrl+Shift+H`：热切换重选模式（无焦点双击取点 <-> 有焦全屏双击取点）。
- 无焦点重选：通过全局鼠标监听双击取点（左上角 -> 右下角）。
- 有焦重选：全屏双击取点，并支持背景透明度配置。
- 模式开关：
  - 开始答题开关（总开关）
  - 简化模式（仅输出简短答案）
  - 左右分屏 OCR
  - 修改模式（OCR 文本先人工确认再发送）
- OCR 速度调节：`fast / balanced / accurate`。
- 语音播报：`VOICE=True` 时播报 AI 回复。
- OCR 文本分流：OCR 原文落盘缓存，UI 显示原文，AI 使用清洗后的文本。
- 工具面板折叠：减少 UI 占用。

## v4.1 重要更新

1. 新增配置项 `REGION_SELECTOR_ALPHA`。
- 用于调整“有焦全屏双击取点”时背景透明度。
- 支持范围 `0.05 ~ 1.0`，超界或非法值会自动钳制/回退。

2. 有焦取点流程支持配置透传。
- `MainWindow.select_region()` 从配置读取透明度并传给 `RegionSelector`。
- `RegionSelector` 不再写死透明度常量。

3. 文档升级与结构梳理。
- 版本升级到 `v4.1`。
- README 增补目录与关键文件职责说明。

## 安装与运行

```bash
git clone https://github.com/micr0softDrestlife/AK_Subject_One.git
cd AK_Subject_One
pip install -r requirements.txt
python main.py
```

## 配置说明

配置文件：`config/settings.py`

### 1) 快捷键相关

- `HOTKEY_SOLVE = "shift+l"`
- `HOTKEY_TOGGLE_SIMPLIFY = "shift+k"`
- `HOTKEY_CYCLE_BORDER_STYLE = "shift+j"`
- `HOTKEY_RESELECT_REGION = "shift+h"`
- `HOTKEY_TOGGLE_RESELECT_MODE = "ctrl+shift+h"`
- `HOTKEY_RESELECT_REGION_NOFOCUS = True`

### 2) UI 相关

- `WINDOW_WIDTH / WINDOW_HEIGHT / WINDOW_ALPHA`
- `REGION_SELECTOR_ALPHA`：有焦全屏双击取点背景透明度（`0.05 ~ 1.0`）

### 3) OCR 相关

- `PADDLEOCR_LANG`
- `PADDLEOCR_SPEED_MODE = "fast" | "balanced" | "accurate"`
- `PADDLEOCR_MODEL_DIR`

### 4) 语音与调试

- `VOICE = True | False`
- `DEBUG = True | False`

### 5) AI 提供方

- `AI_PROVIDER = "ollama" | "qw" | "ds" | "ot" | ...`
- 各 provider 对应的 URL / KEY / MODEL 参数在 `AppConfig` 中配置。

## PaddleOCR 离线说明

首次运行时，PaddleOCR 会自动下载模型到本机缓存目录（如 `~/.paddleocr/`），后续可离线使用。

## 项目结构（含目录/文件功能）

```text
AK_Subject_One/
├── main.py  （程序入口与组件装配（配置/OCR/AI/截图/GUI/托盘））
├── requirements.txt
├── README.md
├── config/ （集中管理应用配置）
│   └── settings.py  （集中定义 provider、OCR、UI、热键、语音参数）
├── core/   （OCR、AI、截图、语音等核心能力）
│   ├── ai_client.py  （AI 客户端工厂与多 provider 适配）
│   ├── ocr_engine.py  （PaddleOCR 初始化、速度模式切换、文本提取/分屏提取）
│   ├── screenshot.py  （选区归一化与区域截图）
│   └── voice.py  （异步语音播报（Windows 优先 `System.Speech`，失败回退 `pyttsx3`））
├── gui/    （主窗口、布局、事件、热键与选区工具）
│   ├── main_window.py  （主流程编排（截图 -> OCR -> AI）、全局热键回调、状态与线程协调）
│   ├── window_layout.py  （窗口布局构建器）
│   ├── window_events.py  （窗口事件绑定与置顶状态管理）
│   ├── panel_controls.py  （面板控件创建与开关绘制/切换逻辑）
│   ├── hotkey_utils.py  （热键规范化与映射构建）
│   ├── ocr_text_pipeline.py  （OCR 文本缓存、读取与 AI 提示词清洗）
│   ├── region_tools.py  （无焦点双击取点与选区边框覆盖工具）
│   ├── region_selector.py  （有焦全屏双击取点选择器（支持背景透明度配置））
│   └── tray_icon.py  （系统托盘菜单与显示/退出动作）
└── artifacts/ （运行时产物（如 OCR 缓存文本））
    └── ocr_cache/
```


## 历史版本

### v4.1

- 增加 `REGION_SELECTOR_ALPHA` 配置项。
- 有焦全屏双击取点背景透明度支持配置与范围校验。

### v4

- 快捷键默认迁移到 `Shift` 体系。
- 增加无焦点双击取点与重选模式热切换。
- 新增边框样式循环切换与透明边框模式。
  - 边框当前前覆盖层是 `topmost` 且 `-disabled`，通常不抢焦点，但不同系统/浏览器下不能 100% 保证。
  - 若要降低风险，建议切换到透明边框样式，此时会直接不创建覆盖层。
- OCR 文本缓存分流（UI 原文 / AI 清洗文本）。
- 语音播报更新与稳定性修复。
- GUI 拆分为布局/事件/面板与工具模块。

### v3

- OCR 从 Tesseract 迁移至 PaddleOCR。
- 中文识别准确率提升，支持模型缓存离线使用。
- 引入 OCR 速度三档。

### v2

- 增加更多模型提供方适配。
- 增加修改模式与界面优化。
