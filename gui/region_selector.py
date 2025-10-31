#  Author: micr0softDrestlife
import tkinter as tk
from tkinter import ttk
import pyautogui

class RegionSelector:
    def __init__(self, on_region_selected):
        self.on_region_selected = on_region_selected
        self.start_x = None
        self.start_y = None
        self.selector_window = None
        
    def start_selection(self):
        """开始区域选择"""
        # 创建全屏透明窗口用于区域选择
        self.selector_window = tk.Tk()
        self.selector_window.attributes('-fullscreen', True)
        self.selector_window.attributes('-alpha', 0.3)
        self.selector_window.configure(bg='gray')
        
        # 绑定鼠标事件
        self.selector_window.bind('<Button-1>', self.on_mouse_down)
        self.selector_window.bind('<B1-Motion>', self.on_mouse_drag)
        self.selector_window.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.selector_window.bind('<Escape>', self.cancel_selection)
        
        # 显示提示
        self.canvas = tk.Canvas(self.selector_window, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_text(
            pyautogui.size().width // 2, 
            pyautogui.size().height // 2,
            text="拖动选择区域，按ESC取消",
            fill="white",
            font=("Arial", 16)
        )
        
        self.selector_window.mainloop()
    
    def on_mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2
        )
    
    def on_mouse_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
    
    def on_mouse_up(self, event):
        end_x, end_y = event.x, event.y
        region = (self.start_x, self.start_y, end_x, end_y)
        self.selector_window.destroy()
        self.on_region_selected(region)
    
    def cancel_selection(self, event):
        self.selector_window.destroy()
        self.on_region_selected(None)