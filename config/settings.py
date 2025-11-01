#  Author: micr0softDrestlife
import os
from dataclasses import dataclass
# dataclass可以自动为类生成特殊方法如 __init__ 和 __repr__，使代码更简洁易读
@dataclass
class AppConfig:

    # AI 提供方配置：'ollama'/'qianwen'/'qianwen'/'deepseek'/''。
    ## 可缩写：'qw'/'ds'
    # 默认使用 Ollama 本地服务
    AI_PROVIDER: str = 'ds'
    
    # Ollama 配置
    ## 默认模型供应商与模型
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5-coder:7b"  

    # 千问 相关配置
    # qw模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    # 以下是北京地域base_url，如果使用新加坡地域的模型，需要将base_url替换为：https://dashscope-intl.aliyuncs.com/compatible-mode/v1
    QIANWEN_API_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1" 
    QIANWEN_API_KEY: str = ""
    QIANWEN_MODEL: str = "qwen-flash" # 推荐qwen-flash、qwen-plus、qwen3-max

    # Deepseek 相关配置
    DEEPSEEK_API_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_API_KEY: str = "sk-45840361708d45ee8905e2bcce6eee94"
    DEEPSEEK_MODEL: str = "deepseek-chat" # 默认使用v3-non-reasoner

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