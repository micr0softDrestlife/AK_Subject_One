#  Author: micr0softDrestlife
import tkinter as tk
from tkinter import ttk


class PanelControlsMixin:
    def create_switch(self, parent=None):
        """创建滑动开关。可指定父容器 parent（默认为 root）。"""
        if parent is None:
            parent = self.root
        switch_frame = tk.Frame(
            parent, bg="#f3f5f9"
        )  # 创建一个框架用于放置开关，Frame是tkinter的容器控件，绑定parent
        switch_frame.pack(
            pady=6, anchor="w", padx=6
        )  # pack用于布局，anchor用于对齐方式，padx/pady用于内边距

        self.switch_state = False
        self.switch_var = tk.StringVar(value="Off")  # StringVar用于动态更新标签文字

        # 开关背景
        self.switch_canvas = tk.Canvas(
            switch_frame, width=60, height=30, bg="white"
        )  # Canvas用于绘制图形
        self.switch_canvas.pack()

        # 绘制初始状态（Off）
        self.draw_switch()

        # 绑定点击事件
        self.switch_canvas.bind("<Button-1>", self.toggle_switch)
        # Button-1表示鼠标左键点击事件，绑定toggle_switch方法，bind用于事件绑定，绑定那块区域

        # 状态文字
        self.switch_label = tk.Label(
            switch_frame, textvariable=self.switch_var, bg="#f3f5f9", fg="#334155"
        )  # 为框架绑定标签显示开关状态
        self.switch_label.pack(side=tk.LEFT, padx=6)  # 设置标签位置
        # 保存 switch_frame 以便在折叠时管理
        self._switch_frame = switch_frame

    def create_simplify_switch(self, parent=None):
        """创建用于控制AI简化模式的滑动开关。开启时会在调用AI时附加系统提示。"""
        if parent is None:
            parent = self.root
        frame = tk.Frame(parent, bg="#f3f5f9")
        frame.pack(pady=6, anchor="w", padx=6)

        self.simplify_state = False
        self.simplify_var = tk.StringVar(value="Off")

        # 开关画布
        self.simplify_canvas = tk.Canvas(frame, width=60, height=30, bg="white")
        self.simplify_canvas.pack(side=tk.LEFT)
        # 初始绘制
        self.draw_simplify()
        self.simplify_canvas.bind("<Button-1>", self.toggle_simplify)

        # 标签
        self.simplify_label = tk.Label(
            frame, textvariable=self.simplify_var, bg="#f3f5f9", fg="#334155"
        )
        self.simplify_label.pack(side=tk.LEFT, padx=6)

        # 保存 frame
        self._simplify_frame = frame

    def create_confirm_switch(self, parent=None):
        """创建用于控制是否需要手动确认OCR文本再发送给AI的滑动开关。"""
        if parent is None:
            parent = self.root
        frame = tk.Frame(parent, bg="#f3f5f9")
        frame.pack(pady=6, anchor="w", padx=6)

        self.confirm_state = False
        self.confirm_var = tk.StringVar(value="Off")

        # 开关画布
        self.confirm_canvas = tk.Canvas(frame, width=60, height=30, bg="white")
        self.confirm_canvas.pack(side=tk.LEFT)
        # 初始绘制
        self.draw_confirm()
        self.confirm_canvas.bind("<Button-1>", self.toggle_confirm)

        # 标签
        self.confirm_label = tk.Label(
            frame, textvariable=self.confirm_var, bg="#f3f5f9", fg="#334155"
        )
        self.confirm_label.pack(side=tk.LEFT, padx=6)

        # 保存 frame
        self._confirm_frame = frame

    def create_split_switch(self, parent=None):
        """创建用于控制是否按左右分屏分别识别的滑动开关。开启时会对左右两半分别OCR并合并结果。"""
        if parent is None:
            parent = self.root
        frame = tk.Frame(parent, bg="#f3f5f9")
        frame.pack(pady=6, anchor="w", padx=6)

        self.split_state = False
        self.split_var = tk.StringVar(value="Off")

        # 开关画布
        self.split_canvas = tk.Canvas(frame, width=60, height=30, bg="white")
        self.split_canvas.pack(side=tk.LEFT)
        # 初始绘制
        self.draw_split()
        self.split_canvas.bind("<Button-1>", self.toggle_split)

        # 标签
        self.split_label = tk.Label(
            frame, textvariable=self.split_var, bg="#f3f5f9", fg="#334155"
        )
        self.split_label.pack(side=tk.LEFT, padx=6)

        # 保存 frame
        self._split_frame = frame

    def draw_split(self):
        """绘制左右分屏开关状态"""
        try:
            self.split_canvas.delete("all")
        except Exception:
            return

        self.split_var.set("左右分屏")

        if self.split_state:
            self.split_canvas.create_rectangle(
                0, 0, 60, 30, fill="green", outline="black"
            )
            self.split_canvas.create_oval(30, 0, 60, 30, fill="white", outline="black")
        else:
            self.split_canvas.create_rectangle(
                0, 0, 60, 30, fill="gray", outline="black"
            )
            self.split_canvas.create_oval(0, 0, 30, 30, fill="white", outline="black")

    def toggle_split(self, event):
        """切换左右分屏开关"""
        self.split_state = not getattr(self, "split_state", False)
        self.draw_split()

    def draw_confirm(self):
        """绘制手动确认开关状态"""
        try:
            self.confirm_canvas.delete("all")
        except Exception:
            return

        self.confirm_var.set("修改模式")

        if self.confirm_state:
            self.confirm_canvas.create_rectangle(
                0, 0, 60, 30, fill="green", outline="black"
            )
            self.confirm_canvas.create_oval(
                30, 0, 60, 30, fill="white", outline="black"
            )
            # self.confirm_var.set('On')
        else:
            self.confirm_canvas.create_rectangle(
                0, 0, 60, 30, fill="gray", outline="black"
            )
            self.confirm_canvas.create_oval(0, 0, 30, 30, fill="white", outline="black")
            # self.confirm_var.set('Off')

    def toggle_confirm(self, event):
        """切换手动确认开关"""
        self.confirm_state = not getattr(self, "confirm_state", False)
        self.draw_confirm()
        # if turning off, hide any OK button and clear waiting flag
        if not self.confirm_state:
            try:
                if hasattr(self, "ok_btn"):
                    try:
                        self.ok_btn.place_forget()
                    except Exception:
                        pass
                self.waiting_for_confirm = False
            except Exception:
                pass

    def create_speed_slider(self, parent=None):
        """创建OCR速度滑块，用于在速度和精度之间切换"""
        if parent is None:
            parent = self.root

        frame = tk.Frame(parent, bg="#f3f5f9")
        frame.pack(pady=6, anchor="w", padx=6, fill=tk.X)

        # 标签
        tk.Label(frame, text="OCR速度:", bg="#f3f5f9", fg="#334155").pack(side=tk.LEFT)

        # 速度模式映射: 滑块值 -> 模式名
        self._speed_modes_map = {0: "fast", 1: "balanced", 2: "accurate"}
        self._speed_labels = {0: "⚡极速", 1: "⚖️平衡", 2: "🎯精确"}

        # 当前速度值（记录上一次的值，避免重复触发）
        self.speed_var = tk.IntVar(value=0)  # 默认极速模式
        self._last_speed_value = 0

        # 速度显示标签
        self.speed_display = tk.Label(
            frame, text=self._speed_labels[0], width=8, bg="#f3f5f9", fg="#334155"
        )
        self.speed_display.pack(side=tk.RIGHT, padx=(6, 0))

        # 滑块
        self.speed_slider = ttk.Scale(
            frame,
            from_=0,
            to=2,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            command=self._on_speed_change,
            length=150,
        )
        self.speed_slider.pack(side=tk.LEFT, padx=6, fill=tk.X, expand=True)

        # 保存frame
        self._speed_frame = frame

    def _on_speed_change(self, value):
        """速度滑块值改变时的回调"""
        # 将浮点值四舍五入为整数
        int_value = round(float(value))

        # 只有当值真正改变时才处理
        if int_value == self._last_speed_value:
            return

        self._last_speed_value = int_value

        # 更新滑块位置（吸附到整数位置）
        self.speed_var.set(int_value)

        # 更新显示标签
        self.speed_display.config(text=self._speed_labels.get(int_value, ""))

        # 更新OCR引擎的速度模式
        mode = self._speed_modes_map.get(int_value, "fast")
        try:
            self.ocr_engine.set_speed_mode(mode)
            # 更新状态栏
            mode_info = self.ocr_engine.get_speed_modes().get(mode, {})
            self.status_var.set(
                f"OCR模式: {mode_info.get('name', mode)} - {mode_info.get('description', '')}"
            )
        except Exception as e:
            print(f"切换OCR速度模式失败: {e}")

    def draw_simplify(self):
        """绘制简化模式开关状态"""
        try:
            self.simplify_canvas.delete("all")
        except Exception:
            return

        self.simplify_var.set("简化模式")

        if self.simplify_state:
            self.simplify_canvas.create_rectangle(
                0, 0, 60, 30, fill="green", outline="black"
            )
            self.simplify_canvas.create_oval(
                30, 0, 60, 30, fill="white", outline="black"
            )
            # self.simplify_var.set('On')
        else:
            self.simplify_canvas.create_rectangle(
                0, 0, 60, 30, fill="gray", outline="black"
            )
            self.simplify_canvas.create_oval(
                0, 0, 30, 30, fill="white", outline="black"
            )
            # self.simplify_var.set('Off')

    def toggle_simplify(self, event):
        """切换简化模式开关"""
        self.simplify_state = not getattr(self, "simplify_state", False)
        self.draw_simplify()

    def draw_switch(self):
        """绘制开关状态"""
        self.switch_canvas.delete("all")

        self.switch_var.set("开始答题")

        if self.switch_state:
            # 开状态 - 绿色
            self.switch_canvas.create_rectangle(
                0, 0, 60, 30, fill="green", outline="black"
            )  # 绘制矩形作为开关背景
            self.switch_canvas.create_oval(
                30, 0, 60, 30, fill="white", outline="black"
            )  # 绘制圆形作为开关按钮
            # self.switch_var.set("On")
            if hasattr(self, "solve_btn"):
                self.solve_btn.config(state="normal")  # 启用Solve按钮
        else:
            # 关状态 - 灰色
            self.switch_canvas.create_rectangle(
                0, 0, 60, 30, fill="gray", outline="black"
            )
            self.switch_canvas.create_oval(0, 0, 30, 30, fill="white", outline="black")
            # self.switch_var.set("Off")
            if hasattr(self, "solve_btn"):
                self.solve_btn.config(state="disabled")

    def toggle_switch(self, event):
        """切换开关状态"""
        self.switch_state = not self.switch_state
        self.draw_switch()

    def _toggle_controls(self):
        """折叠/展开控件面板主体"""
        if getattr(self, "_controls_expanded", True):
            # 隐藏主体
            try:
                self.controls_body.pack_forget()
            except Exception:
                pass
            self._toggle_btn.config(text="+")
            self._controls_expanded = False
        else:
            # 展开主体
            try:
                self.controls_body.pack(fill=tk.X)
            except Exception:
                pass
            self._toggle_btn.config(text="−")
            self._controls_expanded = True
