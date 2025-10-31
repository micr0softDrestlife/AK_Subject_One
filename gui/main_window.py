#  Author: micr0softDrestlife
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from PIL import Image, ImageTk
import io

class MainWindow:
    def __init__(self, ocr_engine, ai_client, screenshot_manager, config):
        self.ocr_engine = ocr_engine
        self.ai_client = ai_client
        self.screenshot_manager = screenshot_manager
        self.config = config
        self.debug = getattr(config, 'DEBUG', False)

        # keep a reference to the preview image to avoid GC
        self._preview_photo = None

        self.create_window()
    
    def create_window(self):
        """创建主窗口"""
        self.root = tk.Tk()# 创建主窗口，Tk是tkinter的主窗口类
        self.root.title("OCR AI Tool")
        self.root.geometry("400x500")# 设置窗口大小
        self.root.attributes('-alpha', 0.9)# 设置窗口透明度

        # 窗口始终置顶（除非最小化或窗口被关闭）
        try:
            self.root.attributes('-topmost', True)
        except Exception:
            pass
        # 监听最小化/还原事件，最小化时取消置顶，恢复时再次置顶
        self.root.bind('<Unmap>', self._on_unmap)
        self.root.bind('<Map>', self._on_map)
        
        
        
        # 折叠式控件面板（可以折叠以节省空间），包含区域选择、开关、预览等
        self.controls_frame = tk.Frame(self.root)

        header = tk.Frame(self.controls_frame)
        header.pack(fill=tk.X)
        self._controls_expanded = True
        self._toggle_btn = tk.Button(header, text='−', width=2, command=self._toggle_controls)
        self._toggle_btn.pack(side=tk.LEFT, padx=(5, 2), pady=5)
        tk.Label(header, text='工具面板').pack(side=tk.LEFT, padx=4)

        # 折叠面板的主体
        self.controls_body = tk.Frame(self.controls_frame)
        self.controls_body.pack(fill=tk.X)

        # 创建区域选择按钮（放入controls_body），并在右侧增加一个“关闭”按钮以移除选区边框
        region_frame = tk.Frame(self.controls_body)
        region_frame.pack(pady=6, anchor='w', padx=6)

        self.region_btn = ttk.Button(
            region_frame,
            text="选择识别区域",
            command=self.select_region
        )
        self.region_btn.pack(side=tk.LEFT)

        # 关闭选区边框的按钮，初始禁用
        self.close_region_btn = ttk.Button(
            region_frame,
            text="关闭",
            command=self.close_region,
            state='disabled'
        )
        self.close_region_btn.pack(side=tk.LEFT, padx=(6, 0))

        # 创建滑动开关（放入controls_body）
        self.create_switch(parent=self.controls_body)

        # 创建简化模式开关（放入controls_body）
        self.create_simplify_switch(parent=self.controls_body)

        # 显示选定区域
        self.region_label = tk.Label(self.controls_body, text="未选择区域", wraplength=360)
        self.region_label.pack(pady=5, anchor='w', padx=6)

        # 区域预览（用于持久显示所选区域）
        preview_frame = tk.LabelFrame(self.controls_body, text="选定区域预览")
        preview_frame.pack(pady=5, padx=6, fill=tk.X)
        self.preview_canvas = tk.Canvas(preview_frame, width=320, height=120, bg='black')
        self.preview_canvas.pack(padx=5, pady=5)

        # 结果显示区域
        self.create_result_area()

        self.controls_frame.pack(fill=tk.X, pady=(5, 0))

        # 创建Solve按钮（保持可见，不折叠）
        self.solve_btn = ttk.Button(
            self.root,
            text="Solve",
            command=self.solve,
            state='disabled'
        )
        self.solve_btn.pack(pady=10)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_switch(self, parent=None):
        """创建滑动开关。可指定父容器 parent（默认为 root）。"""
        if parent is None:
            parent = self.root
        switch_frame = tk.Frame(parent)# 创建一个框架用于放置开关，Frame是tkinter的容器控件，绑定parent
        switch_frame.pack(pady=6, anchor='w', padx=6)
        
        self.switch_state = False
        self.switch_var = tk.StringVar(value="Off")# StringVar用于动态更新标签文字
        
        # 开关背景
        self.switch_canvas = tk.Canvas(switch_frame, width=60, height=30, bg='white')# Canvas用于绘制图形
        self.switch_canvas.pack()
        
        # 绘制初始状态（Off）
        self.draw_switch()
        
        # 绑定点击事件
        self.switch_canvas.bind('<Button-1>', self.toggle_switch)
        # Button-1表示鼠标左键点击事件，绑定toggle_switch方法，bind用于事件绑定，绑定那块区域
        
        # 状态文字
        self.switch_label = tk.Label(switch_frame, textvariable=self.switch_var)# 为框架绑定标签显示开关状态
        self.switch_label.pack()
        # 保存 switch_frame 以便在折叠时管理
        self._switch_frame = switch_frame

    def create_simplify_switch(self, parent=None):
        """创建用于控制AI简化模式的滑动开关。开启时会在调用AI时附加系统提示。"""
        if parent is None:
            parent = self.root
        frame = tk.Frame(parent)
        frame.pack(pady=6, anchor='w', padx=6)

        self.simplify_state = False
        self.simplify_var = tk.StringVar(value="Off")

        # 开关画布
        self.simplify_canvas = tk.Canvas(frame, width=60, height=30, bg='white')
        self.simplify_canvas.pack(side=tk.LEFT)
        # 初始绘制
        self.draw_simplify()
        self.simplify_canvas.bind('<Button-1>', self.toggle_simplify)

        # 标签
        self.simplify_label = tk.Label(frame, textvariable=self.simplify_var)
        self.simplify_label.pack(side=tk.LEFT, padx=6)

        # 保存 frame
        self._simplify_frame = frame

    def draw_simplify(self):
        """绘制简化模式开关状态"""
        try:
            self.simplify_canvas.delete('all')
        except Exception:
            return

        if self.simplify_state:
            self.simplify_canvas.create_rectangle(0, 0, 60, 30, fill='green', outline='black')
            self.simplify_canvas.create_oval(30, 0, 60, 30, fill='white', outline='black')
            self.simplify_var.set('On')
        else:
            self.simplify_canvas.create_rectangle(0, 0, 60, 30, fill='gray', outline='black')
            self.simplify_canvas.create_oval(0, 0, 30, 30, fill='white', outline='black')
            self.simplify_var.set('Off')

    def toggle_simplify(self, event):
        """切换简化模式开关"""
        self.simplify_state = not getattr(self, 'simplify_state', False)
        self.draw_simplify()
    
    def draw_switch(self):
        """绘制开关状态"""
        self.switch_canvas.delete("all")
        
        if self.switch_state:
            # 开状态 - 绿色
            self.switch_canvas.create_rectangle(0, 0, 60, 30, fill='green', outline='black')# 绘制矩形作为开关背景
            self.switch_canvas.create_oval(30, 0, 60, 30, fill='white', outline='black')# 绘制圆形作为开关按钮
            self.switch_var.set("On")
            if hasattr(self, 'solve_btn'):
                self.solve_btn.config(state='normal')# 启用Solve按钮
        else:
            # 关状态 - 灰色
            self.switch_canvas.create_rectangle(0, 0, 60, 30, fill='gray', outline='black')
            self.switch_canvas.create_oval(0, 0, 30, 30, fill='white', outline='black')
            self.switch_var.set("Off")
            if hasattr(self, 'solve_btn'):
                self.solve_btn.config(state='disabled')
    
    def toggle_switch(self, event):
        """切换开关状态"""
        self.switch_state = not self.switch_state
        self.draw_switch()

    def _toggle_controls(self):
        """折叠/展开控件面板主体"""
        if getattr(self, '_controls_expanded', True):
            # 隐藏主体
            try:
                self.controls_body.pack_forget()
            except Exception:
                pass
            self._toggle_btn.config(text='+')
            self._controls_expanded = False
        else:
            # 展开主体
            try:
                self.controls_body.pack(fill=tk.X)
            except Exception:
                pass
            self._toggle_btn.config(text='−')
            self._controls_expanded = True

    def _on_unmap(self, event):
        """窗口最小化时取消置顶"""
        try:
            if self.root.state() == 'iconic':
                self.root.attributes('-topmost', False)
        except Exception:
            pass

    def _on_map(self, event):
        """窗口还原时再次置顶"""
        try:
            if self.root.state() != 'iconic':
                self.root.attributes('-topmost', True)
        except Exception:
            pass
    
    def select_region(self):
        """选择识别区域"""
        from gui.region_selector import RegionSelector
        
        def on_region_selected(region):
            if region:
                self.screenshot_manager.set_region(region)
                self.region_label.config(text=f"已选择区域: {region}")
                # 尝试捕获并显示选区预览
                img = self.screenshot_manager.capture_region()
                if img is not None:
                    self.update_preview(img)
                # enable solve when region selected
                self.solve_btn.config(state='normal' if self.switch_state else 'disabled')
                # 显示屏幕上的选区边框以便观察
                try:
                    self._create_region_overlay(region)
                    # 启用关闭按钮
                    self.close_region_btn.config(state='normal')
                except Exception:
                    pass

        # 最小化主窗口临时（使用 iconify 而不是 withdraw 防止任务栏图标消失）
        try:
            self.root.iconify()
        except Exception:
            # fallback to withdraw if iconify not available
            try:
                self.root.withdraw()
            except Exception:
                pass

        selector = RegionSelector(on_region_selected)
        selector.start_selection()

        # 重新显示主窗口并置顶
        try:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
        except Exception:
            pass
    
    def create_result_area(self):
        """创建结果显示区域"""
        result_frame = tk.LabelFrame(self.root, text="AI回复")
        result_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.result_text = scrolledtext.ScrolledText(
            result_frame, 
            wrap=tk.WORD,
            height=10
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def solve(self):
        """执行OCR和AI处理"""
        if not self.switch_state:
            return
        # 每次solve前清空结果区域以保持简洁（若result_text不存在则忽略）
        try:
            self.result_text.delete('1.0', tk.END)
        except Exception:
            pass

        # 在新线程中执行，避免界面冻结
        thread = threading.Thread(target=self._solve_thread)
        thread.daemon = True
        thread.start()
    
    def _solve_thread(self):
        """处理线程"""
        self.status_var.set("正在处理...")
        
        try:
            # 截图
            screenshot = self.screenshot_manager.capture_region()
            if screenshot is None:
                self.result_text.insert(tk.END, "错误: 未选择区域\n")
                return
            
            # OCR识别
            ocr_text = self.ocr_engine.extract_text(screenshot)
            if not ocr_text:
                self.root.after(0, lambda: self.result_text.insert(tk.END, "OCR未识别到文字\n"))
                return

            # 若开启debug则输出OCR原文，默认不打印到结果区域
            if self.debug:
                self.root.after(0, lambda: self.result_text.insert(tk.END, f"识别文字: {ocr_text}\n\n正在调用AI...\n"))
            else:
                # 仍在结果区显示正在调用AI的状态行
                self.root.after(0, lambda: self.result_text.insert(tk.END, "正在调用AI...\n"))

            # 如果简化模式开启，传入重要的 system prompt 指示 AI 只返回简短答案
            system_prompt = None
            if getattr(self, 'simplify_state', False):
                system_prompt = "快速回答下面问题，不需要任何解释"

            ai_response = self.ai_client.generate_response(ocr_text, system_prompt=system_prompt)

            # 更新界面
            self.root.after(0, lambda: self.display_result(ocr_text, ai_response))
            
        except Exception as e:
            self.root.after(0, lambda: self.result_text.insert(tk.END, f"处理错误: {str(e)}\n"))
        finally:
            self.root.after(0, lambda: self.status_var.set("就绪"))
    
    def display_result(self, ocr_text, ai_response):
        """显示结果"""
        self.result_text.insert(tk.END, f"AI回复:\n{ai_response}\n{'='*50}\n")
        self.result_text.see(tk.END)

    def update_preview(self, image_array):
        """在preview_canvas中显示所选区域的缩略图，并绘制边框以便观察"""
        try:
            if not hasattr(image_array, 'shape'):
                return
            # 转为PIL Image
            pil = Image.fromarray(image_array)
            # 缩放以适配canvas
            canvas_w = int(self.preview_canvas['width'])
            canvas_h = int(self.preview_canvas['height'])
            pil.thumbnail((canvas_w, canvas_h), Image.LANCZOS)
            self._preview_photo = ImageTk.PhotoImage(pil)
            self.preview_canvas.delete('all')
            self.preview_canvas.create_image(canvas_w//2, canvas_h//2, image=self._preview_photo)
            # 绘制红色边框以示意
            self.preview_canvas.create_rectangle(2, 2, canvas_w-2, canvas_h-2, outline='red', width=2)
        except Exception as e:
            print('update_preview 错误:', e)
    
    def _create_region_overlay(self, region):
        """在屏幕上创建一个无窗口装饰的透明覆盖，仅显示选区边框，直到用户点击关闭。"""
        # 清除已有覆盖
        try:
            if hasattr(self, 'region_overlay') and self.region_overlay:
                try:
                    self.region_overlay.destroy()
                except Exception:
                    pass
                self.region_overlay = None
        except Exception:
            self.region_overlay = None

        if not region:
            return

        x1, y1, x2, y2 = region
        x1, x2 = int(min(x1, x2)), int(max(x1, x2))
        y1, y2 = int(min(y1, y2)), int(max(y1, y2))
        w = max(1, x2 - x1)
        h = max(1, y2 - y1)

        # 创建覆层窗口
        overlay = tk.Toplevel(self.root)
        overlay.overrideredirect(True)
        try:
            overlay.attributes('-topmost', True)
        except Exception:
            pass

        # Try to make the background transparent on Windows by using a transparentcolor key
        transparent_color = 'white'
        try:
            overlay.config(bg=transparent_color)
            # set geometry to match region
            overlay.geometry(f"{w}x{h}+{x1}+{y1}")
            # Make the chosen bg color transparent (works on Windows)
            overlay.wm_attributes('-transparentcolor', transparent_color)
        except Exception:
            # fallback: still set geometry
            overlay.geometry(f"{w}x{h}+{x1}+{y1}")

        canvas = tk.Canvas(overlay, width=w, height=h, highlightthickness=0, bg=transparent_color)
        canvas.pack(fill=tk.BOTH, expand=True)
        # Draw a red border inside the overlay
        canvas.create_rectangle(1, 1, w-2, h-2, outline='red', width=3)

        # keep reference
        self.region_overlay = overlay

    def close_region(self):
        """关闭用于观察的选区边框并清除选区，要求重新选择才能再次OCR"""
        try:
            if hasattr(self, 'region_overlay') and self.region_overlay:
                try:
                    self.region_overlay.destroy()
                except Exception:
                    pass
                self.region_overlay = None
        except Exception:
            pass

        # 清除选区
        try:
            self.screenshot_manager.set_region(None)
        except Exception:
            pass

        # 更新界面元素
        try:
            self.region_label.config(text="未选择区域")
            self.preview_canvas.delete('all')
            self.solve_btn.config(state='disabled')
            self.close_region_btn.config(state='disabled')
        except Exception:
            pass
    
    def run(self):
        """运行主循环"""
        self.root.mainloop()