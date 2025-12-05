### AK_Subject_One
- 该工具使用 **PaddleOCR** 进行OCR识别，相比Tesseract具有更高的中文识别准确率
- PaddleOCR模型会自动下载，之后支持**完全离线**使用
- 本工具用于对截图进行OCR并将OCR结果传输给大模型
- 默认模型供应商为Ollama，默认模型为qwen2.5-coder:7b，需要确保安装了ollama且有该模型
- 可自行配置所需大模型供应商，自带千问与deepseek相关API设置，配置后无需安装ollama
- 功能：
    - 开始答题：solve开始答题
    - 简化模式：只输出答案
    - 左右分屏：进行分屏OCR
    - 修改模式：对OCR结果进行修改
    - **OCR速度调节**：三档可调（极速/平衡/精确）
- OCRdebug功能
- 非必要组件折叠功能

#### Install
```text
git clone https://github.com/micr0softDrestlife/AK_Subject_One.git

pip install -r requirements.txt

python main.py
```

#### PaddleOCR 离线部署说明
首次运行时，PaddleOCR会自动下载模型文件到 `~/.paddleocr/` 目录：
- 检测模型 (det)
- 识别模型 (rec)  
- 方向分类模型 (cls)

#### Use
- 在setting.py文件中配置相关大模型供应商的API_KEY即可

#### 项目结构
```bash
ocr_ai_tool/
├── main.py              # 主程序入口
├── gui/
│   ├── tray_icon.py     # 系统托盘图标
│   ├── main_window.py   # 主浮动窗口
│   └── region_selector.py # 区域选择器
├── core/
│   ├── ocr_engine.py    # OCR识别模块
│   ├── ai_client.py     # Ollama API客户端
│   └── screenshot.py    # 截图功能
├── config/
│   └── settings.py      # 配置文件
```

#### v3
- **重大更新：从Tesseract迁移到PaddleOCR**
- 中文OCR识别准确率显著提升
- 无需安装Tesseract二进制文件
- 支持离线使用（模型自动缓存）
- **新增OCR速度滑块**：
  - ⚡极速模式：约0.5秒（PP-OCRv4 mobile）
  - ⚖️平衡模式：约1秒
  - 🎯精确模式：约8秒（PP-OCRv5 server，最高精度）

#### v2
- 完善了部分模型供应商
- 增加了修改模式
- 进行了页面美化
- 打包了相关的python库依赖