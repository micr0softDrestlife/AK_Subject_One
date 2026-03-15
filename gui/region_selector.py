#  Author: micr0softDrestlife
import tkinter as tk

import pyautogui


class RegionSelector:
    def __init__(self, on_region_selected, overlay_alpha=0.3):
        self.on_region_selected = on_region_selected
        self.start_x = None
        self.start_y = None
        self.selector_window = None
        self.canvas = None
        self.tip_id = None
        self._first_point = None
        try:
            alpha = float(overlay_alpha)
        except Exception:
            alpha = 0.3
        if alpha != alpha:  # NaN
            alpha = 0.3
        self.overlay_alpha = min(1.0, max(0.05, alpha))

    def start_selection(self):
        """开始区域选择（有焦全屏双击取点）。"""
        self._first_point = None
        self.start_x = None
        self.start_y = None

        # 创建全屏透明窗口用于区域选择
        self.selector_window = tk.Tk()
        self.selector_window.attributes("-fullscreen", True)
        self.selector_window.attributes("-alpha", self.overlay_alpha)
        self.selector_window.configure(bg="gray")

        # 绑定鼠标事件
        self.selector_window.bind("<Button-1>", self.on_click)
        self.selector_window.bind("<Escape>", self.cancel_selection)

        # 显示提示
        self.canvas = tk.Canvas(self.selector_window, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.tip_id = self.canvas.create_text(
            pyautogui.size().width // 2,
            pyautogui.size().height // 2,
            text="点击左上角，再点击右下角（按 ESC 取消）",
            fill="white",
            font=("Arial", 16),
        )

        self.selector_window.mainloop()

    def on_click(self, event):
        point = (int(event.x), int(event.y))

        if self._first_point is None:
            self._first_point = point
            self.start_x, self.start_y = point
            self.canvas.create_oval(
                point[0] - 4,
                point[1] - 4,
                point[0] + 4,
                point[1] + 4,
                outline="red",
                fill="red",
            )
            self.canvas.itemconfig(
                self.tip_id, text=f"已记录左上角: {point}，请点击右下角"
            )
            return

        end_x, end_y = point
        self.canvas.create_oval(
            end_x - 4, end_y - 4, end_x + 4, end_y + 4, outline="red", fill="red"
        )
        self.canvas.create_rectangle(
            self.start_x, self.start_y, end_x, end_y, outline="red", width=1
        )
        region = (self.start_x, self.start_y, end_x, end_y)
        self.selector_window.destroy()
        self.on_region_selected(region)

    def cancel_selection(self, event):
        self.selector_window.destroy()
        self.on_region_selected(None)
