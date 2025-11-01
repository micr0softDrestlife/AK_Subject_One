#  Author: micr0softDrestlife
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow
from gui.tray_icon import TrayIcon
from core.ocr_engine import OCREngine
from core.ai_client import get_ai_client
from core.screenshot import ScreenshotManager
from config.settings import AppConfig

class OCRAIApplication:
    def __init__(self):
        self.config = AppConfig()
        self.setup_components()
    
    def setup_components(self):
        """初始化各个组件"""
        # 初始化核心组件
        self.ocr_engine = OCREngine(self.config.TESSERACT_PATH)# 初始化OCR引擎，传入tesseract路径
        # create AI client according to configured provider (ollama/qianwen/...)
        self.ai_client = get_ai_client(self.config)
        self.screenshot_manager = ScreenshotManager()
        
        # 初始化GUI, 传入配置以便MainWindow可以根据DEBUG等选项调整行为
        self.main_window = MainWindow(
            self.ocr_engine,
            self.ai_client,
            self.screenshot_manager,
            self.config
        )
        
        # 初始化托盘图标
        self.tray_icon = TrayIcon(self)
    
    def show(self):
        """显示主窗口"""
        self.main_window.root.deiconify()
        self.main_window.root.lift()
        self.main_window.root.focus_force()
    
    def quit(self):
        """退出应用"""
        if self.main_window:
            self.main_window.root.quit()
    
    def run(self):
        """运行应用"""
        # 启动托盘图标
        self.tray_icon.setup_tray()
        self.tray_icon.run()
        
        # 启动主窗口（可选隐藏启动）
        # self.main_window.root.withdraw()  # 隐藏启动
        
        # 运行主循环
        self.main_window.run()

if __name__ == "__main__":
    app = OCRAIApplication()
    app.run()