import pystray
from PIL import Image, ImageDraw
import threading

class TrayIcon:
    def __init__(self, main_app):
        self.main_app = main_app
        self.icon = None
        
    def create_image(self):
        """创建托盘图标"""
        image = Image.new('RGB', (64, 64), color='white')
        dc = ImageDraw.Draw(image)
        dc.rectangle([16, 16, 48, 48], fill='blue')
        dc.text((20, 20), "AI", fill='white')
        return image
    
    def show_window(self, icon, item):
        """显示主窗口"""
        self.main_app.show()
    
    def quit_app(self, icon, item):
        """退出应用"""
        self.main_app.quit()
        icon.stop()
    
    def setup_tray(self):
        """设置系统托盘"""
        image = self.create_image()
        menu = pystray.Menu(
            pystray.MenuItem("显示窗口", self.show_window),
            pystray.MenuItem("退出", self.quit_app)
        )
        
        self.icon = pystray.Icon("ocr_ai_tool", image, "OCR AI Tool", menu)
    
    def run(self):
        """在单独线程中运行托盘图标"""
        thread = threading.Thread(target=self.icon.run, daemon=True)
        thread.start()