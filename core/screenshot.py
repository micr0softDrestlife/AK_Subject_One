#  Author: micr0softDrestlife
import pyautogui
import numpy as np
from PIL import ImageGrab


class ScreenshotManager:
    def __init__(self):
        # selected_region stored as absolute screen coordinates (x1, y1, x2, y2)
        self.selected_region = None  # (x1, y1, x2, y2)

    def set_region(self, region):
        """设置截图区域。region can be (x1,y1,x2,y2) in selector window coords; we normalize to absolute screen coords."""
        if not region:
            self.selected_region = None
            return

        x1, y1, x2, y2 = region
        # Ensure integers and proper ordering，区域规范化
        x1, x2 = int(min(x1, x2)), int(max(x1, x2))
        y1, y2 = int(min(y1, y2)), int(max(y1, y2))

        # If coordinates were relative to a window, they should still match screen coordinates in our selector.
        self.selected_region = (x1, y1, x2, y2)

    def capture_region(self):
        """捕获选定区域的截图并返回 RGB numpy 数组"""
        if not self.selected_region:
            return None

        x1, y1, x2, y2 = self.selected_region

        try:
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))# 截取屏幕指定区域
            arr = np.array(screenshot)
            # PIL ImageGrab returns RGB by default; ensure dtype uint8
            if arr.dtype != np.uint8:
                arr = arr.astype('uint8')
            return arr
        except Exception as e:
            print(f"截图失败: {e}")
            return None