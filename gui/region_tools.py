#  Author: micr0softDrestlife
import tkinter as tk


class NoFocusRegionPicker:
    """无焦点双击取点器：第一次点记录左上角，第二次点记录右下角。"""

    def __init__(
        self, mouse_module, on_first_point=None, on_region=None, on_error=None
    ):
        self.mouse_module = mouse_module
        self.on_first_point = on_first_point
        self.on_region = on_region
        self.on_error = on_error
        self.listener = None
        self.points = []

    def stop(self):
        try:
            if self.listener:
                self.listener.stop()
        except Exception:
            pass
        self.listener = None
        self.points = []

    def start(self):
        if self.mouse_module is None:
            raise RuntimeError("未检测到鼠标监听模块")

        self.stop()
        self.points = []

        def on_click(x, y, button, pressed):
            try:
                if not pressed:
                    return
                if button != self.mouse_module.Button.left:
                    return

                point = (int(x), int(y))
                self.points.append(point)
                if len(self.points) == 1:
                    if callable(self.on_first_point):
                        self.on_first_point(point)
                    return

                p1, p2 = self.points[0], self.points[1]
                region = (p1[0], p1[1], p2[0], p2[1])
                if callable(self.on_region):
                    self.on_region(region, p1, p2)
                self.stop()
                return False
            except Exception as e:
                if callable(self.on_error):
                    self.on_error(e)
                self.stop()

        self.listener = self.mouse_module.Listener(on_click=on_click)
        self.listener.start()


def destroy_region_overlay(overlay):
    """销毁现有选区边框覆盖层。"""
    if not overlay:
        return None
    try:
        overlay.destroy()
    except Exception:
        pass
    return None


def create_region_overlay(root, region, border_style, border_width, split_state=False):
    """创建选区边框覆盖层，返回 overlay 对象或 None。"""
    if not region:
        return None

    x1, y1, x2, y2 = region
    x1, x2 = int(min(x1, x2)), int(max(x1, x2))
    y1, y2 = int(min(y1, y2)), int(max(y1, y2))
    w = max(1, x2 - x1)
    h = max(1, y2 - y1)
    border_color = border_style.get("color", "")
    line_width = max(1, int(border_width))

    # 透明样式：不创建覆盖边框，避免覆盖层拦截交互。
    if not border_color:
        return None

    overlay = tk.Toplevel(root)
    overlay.overrideredirect(True)
    try:
        overlay.attributes("-topmost", True)
    except Exception:
        pass
    try:
        overlay.attributes("-disabled", True)
    except Exception:
        pass

    transparent_color = "white"
    try:
        overlay.config(bg=transparent_color)
        overlay.geometry(f"{w}x{h}+{x1}+{y1}")
        overlay.wm_attributes("-transparentcolor", transparent_color)
    except Exception:
        overlay.geometry(f"{w}x{h}+{x1}+{y1}")

    canvas = tk.Canvas(
        overlay, width=w, height=h, highlightthickness=0, bg=transparent_color
    )
    canvas.pack(fill=tk.BOTH, expand=True)
    canvas.create_rectangle(1, 1, w - 2, h - 2, outline=border_color, width=line_width)

    if split_state:
        cx = w // 2
        canvas.create_line(cx, 1, cx, h - 1, fill=border_color, width=line_width)

    return overlay
