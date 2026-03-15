#  Author: micr0softDrestlife
import tkinter as tk
from tkinter import ttk


class WindowLayoutMixin:
    """窗口布局构建器：只负责组件创建与摆放，不负责事件绑定。"""

    def _build_window_layout(self):
        self.root = tk.Tk()  # 创建主窗口，Tk是tkinter的主窗口类
        self.root.title("OCR AI Tool")
        width = max(int(getattr(self.config, "WINDOW_WIDTH", 420)), 420)
        height = max(int(getattr(self.config, "WINDOW_HEIGHT", 520)), 520)
        self.root.geometry(f"{width}x{height}")  # 设置窗口大小
        self.root.attributes(
            "-alpha", float(getattr(self.config, "WINDOW_ALPHA", 0.95))
        )
        self.root.configure(bg="#f3f5f9")
        try:
            style = ttk.Style(self.root)
            style.theme_use("clam")
            style.configure("TButton", padding=6)
        except Exception:
            pass

        # 折叠式控件面板（可以折叠以节省空间），包含区域选择、开关等
        self.controls_frame = tk.Frame(self.root, bg="#f3f5f9")

        header = tk.Frame(self.controls_frame, bg="#f3f5f9")
        header.pack(fill=tk.X)
        self._controls_expanded = True
        self._toggle_btn = tk.Button(
            header, text="−", width=2, command=self._toggle_controls
        )
        self._toggle_btn.pack(side=tk.LEFT, padx=(5, 2), pady=5)
        tk.Label(header, text="工具面板", bg="#f3f5f9", fg="#1f2937").pack(
            side=tk.LEFT, padx=4
        )

        # 折叠面板的主体
        self.controls_body = tk.Frame(self.controls_frame, bg="#f3f5f9")
        self.controls_body.pack(fill=tk.X)

        # 创建区域选择按钮（放入controls_body），并在右侧增加一个“关闭”按钮以移除选区边框
        region_frame = tk.Frame(self.controls_body, bg="#f3f5f9")
        region_frame.pack(pady=6, anchor="w", padx=6)

        self.region_btn = ttk.Button(
            region_frame, text="选择识别区域", command=self.select_region
        )
        self.region_btn.pack(side=tk.LEFT)

        # 关闭选区边框的按钮，初始禁用
        self.close_region_btn = ttk.Button(
            region_frame, text="关闭", command=self.close_region, state="disabled"
        )
        self.close_region_btn.pack(side=tk.LEFT, padx=(6, 0))

        # 创建滑动开关（放入controls_body）
        self.create_switch(parent=self.controls_body)

        # 创建简化模式开关（放入controls_body）
        self.create_simplify_switch(parent=self.controls_body)

        # 创建左右分屏开关（放入controls_body）
        self.create_split_switch(parent=self.controls_body)

        # 创建手动确认开关（开启后OCR结果需在界面内确认/修改再发送）
        self.create_confirm_switch(parent=self.controls_body)

        # 创建OCR速度滑块
        self.create_speed_slider(parent=self.controls_body)

        # 显示选定区域
        self.region_label = tk.Label(
            self.controls_body,
            text="未选择区域",
            wraplength=360,
            bg="#f3f5f9",
            fg="#334155",
        )
        self.region_label.pack(pady=5, anchor="w", padx=6)

        # 结果显示区域
        self.create_result_area()

        self.controls_frame.pack(fill=tk.X, pady=(5, 0))

        # 创建Solve按钮（保持可见，不折叠）
        self.solve_btn = ttk.Button(
            self.root, text="Solve", command=self.solve, state="disabled"
        )
        self.solve_btn.pack(pady=10)

        self.local_hint_var = tk.StringVar(value="本地提示: 就绪")
        local_hint = tk.Label(
            self.root,
            textvariable=self.local_hint_var,
            bg="#f3f5f9",
            fg="#4b5563",
            anchor="w",
        )
        local_hint.pack(fill=tk.X, padx=10, pady=(0, 4))

        # 状态栏
        self.status_var = tk.StringVar(value=self._ready_status())
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            bg="#e5e7eb",
            fg="#111827",
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
