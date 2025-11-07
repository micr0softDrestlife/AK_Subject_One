### AK_Subject_One
- 该工具使用tesseract进行OCR识别，因此需要将tesseract安装到te_exe或者手动更改tesseract路径
- 进行了tesseract打包，安装不是必要操作
- 默认模型供应商为Ollama，默认模型为qwen2.5-coder:7b，需要确保安装了ollama且有该模型
- 可自行配置所需大模型供应商，自带千问与deepseek相关API设置
- 功能：
    - 开始答题
    - 简化模式
    - 左右分屏
    - 修改模式
- OCRdebug功能
- 非必要组件折叠功能

#### Install
```text
git clone https://github.com/micr0softDrestlife/AK_Subject_One.git

pip install -r requirements.txt

python main.py
```
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

#### v2
- 完善了部分模型供应商
- 增加了修改模式
- 进行了页面美化
- 打包了相关的python库依赖