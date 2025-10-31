import os
from dataclasses import dataclass
# dataclass可以自动为类生成特殊方法如 __init__ 和 __repr__，使代码更简洁易读
@dataclass
class AppConfig:
    # Ollama 配置
    OLLAMA_BASE_URL: str = "http://localhost:11434"# 为OLLAMA_BASE_URL设置了默认值和类型注解
    OLLAMA_MODEL: str = "qwen2.5-coder:7b"  # 或其他你安装的模型

    # OCR 配置
    # 将相对路径解析为项目内的绝对路径，避免不同工作目录导致找不到可执行文件
    TESSERACT_PATH: str = os.path.abspath(# abspath打印当前工作目录中文件的绝对路径
        os.path.join(os.path.dirname(__file__), '..', 'te_exe', 'tesseract.exe')
    )

    # 界面配置
    WINDOW_WIDTH: int = 400
    WINDOW_HEIGHT: int = 300
    WINDOW_ALPHA: float = 0.9

    # 热键配置
    SCREENSHOT_HOTKEY: str = 'ctrl+alt+r'
    # 调试模式：开启后会把OCR原始识别结果输出到结果显示区域，便于调试
    DEBUG: bool = True