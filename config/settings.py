#  Author: micr0softDrestlife
import os
from dataclasses import dataclass
# dataclass可以自动为类生成特殊方法如 __init__ 和 __repr__，使代码更简洁易读
@dataclass
class AppConfig:
    """应用程序配置类，存储各种配置选项"""

    # AI 提供方配置：'ollama'/'qianwen'/'qianwen'/'deepseek'/'other'。
    ## 可缩写：'qw'/'ds'/'ot'
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
    QIANWEN_MODEL: str = "qwen3-max" # 推荐qwen-flash、qwen-plus、qwen3-max

    # Deepseek 相关配置
    DEEPSEEK_API_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_API_KEY: str = "sk-4f1acb71a56f4f0e9e3bd213f85e2f38"
    DEEPSEEK_MODEL: str = "deepseek-chat" # 默认使用v3-non-reasoner

    # 自定义相关配置
    OTHER_API_URL: str = ""
    OTHER_API_KEY: str = ""
    OTHER_MODEL: str = ""

    # OCR 配置 - PaddleOCR
    # PaddleOCR 模型会自动下载到 ~/.paddleocr/ 目录
    # 首次运行会自动下载模型（约100MB），之后支持离线使用
    # 如需自定义模型目录，可设置此路径（为None时使用默认目录）
    PADDLEOCR_MODEL_DIR: str = None  # 例如: os.path.join(os.path.dirname(__file__), '..', 'ocr_models')
    
    # 是否使用GPU加速（需要安装paddlepaddle-gpu）
    PADDLEOCR_USE_GPU: bool = False
    
    # OCR语言设置：'ch'=中英文混合, 'en'=纯英文, 'ch_sim'=简体中文
    PADDLEOCR_LANG: str = 'ch'
    
    # OCR速度模式：'fast'=极速, 'balanced'=平衡, 'accurate'=精确
    # fast: 约0.5秒，使用PP-OCRv4 mobile模型
    # balanced: 约1秒，使用PP-OCRv4 mobile模型（较大检测尺寸）
    # accurate: 约8秒，使用PP-OCRv5 server模型（最高精度）
    PADDLEOCR_SPEED_MODE: str = 'fast'

    # 界面配置
    WINDOW_WIDTH: int = 400
    WINDOW_HEIGHT: int = 300
    WINDOW_ALPHA: float = 0.9

    # 热键配置
    SCREENSHOT_HOTKEY: str = 'ctrl+alt+r'
    # 调试模式：开启后会把OCR原始识别结果输出到结果显示区域，便于调试
    DEBUG: bool = True
