#  Author: micr0softDrestlife
import os
import threading
import tkinter as tk
from tkinter import scrolledtext

from gui.hotkey_utils import build_hotkey_map, normalize_hotkey
from gui.ocr_text_pipeline import (
    build_ai_prompt_from_ocr,
    load_ocr_text,
    persist_ocr_text,
    prepare_ocr_cache_dir,
)
from gui.panel_controls import PanelControlsMixin
from gui.region_tools import (
    NoFocusRegionPicker,
    create_region_overlay,
    destroy_region_overlay,
)
from gui.window_events import WindowEventsMixin
from gui.window_layout import WindowLayoutMixin

try:
    from pynput import keyboard as pynput_keyboard
except Exception:
    pynput_keyboard = None
try:
    from pynput import mouse as pynput_mouse
except Exception:
    pynput_mouse = None

try:
    from core.voice import VoiceOutput
except Exception:
    VoiceOutput = None


class MainWindow(WindowEventsMixin, WindowLayoutMixin, PanelControlsMixin):
    def __init__(self, ocr_engine, ai_client, screenshot_manager, config):
        self.ocr_engine = ocr_engine
        self.ai_client = ai_client
        self.screenshot_manager = screenshot_manager
        self.config = config
        self.debug = getattr(config, "DEBUG", False)
        self.hotkey = getattr(
            config, "HOTKEY_SOLVE", getattr(config, "SCREENSHOT_HOTKEY", "shift+l")
        )
        self.simplify_hotkey = getattr(config, "HOTKEY_TOGGLE_SIMPLIFY", "shift+k")
        self.border_cycle_hotkey = getattr(
            config, "HOTKEY_CYCLE_BORDER_STYLE", "shift+j"
        )
        self.reselect_hotkey = getattr(config, "HOTKEY_RESELECT_REGION", "shift+h")
        self.toggle_reselect_mode_hotkey = getattr(
            config, "HOTKEY_TOGGLE_RESELECT_MODE", "ctrl+shift+h"
        )
        # 兼容旧习惯：即便默认热键改为 Shift+H，仍允许 Ctrl+H 触发重选。
        self.legacy_reselect_hotkey = "ctrl+h"
        self.reselect_nofocus = bool(
            getattr(config, "HOTKEY_RESELECT_REGION_NOFOCUS", True)
        )
        self.voice_enabled = bool(getattr(config, "VOICE", False))

        # whether we are waiting for the user to confirm/edit OCR text before sending
        self.waiting_for_confirm = False
        self.processing = False

        # keep a reference to the preview image to avoid GC
        self._preview_photo = None
        self._hotkey_listener = None
        self._closed = False
        self._last_ocr_text_path = None
        self._region_picker = None
        self._border_styles = [
            {"name": "红色", "color": "red"},
            {"name": "透明", "color": ""},
            {"name": "黑色", "color": "black"},
            {"name": "浅白色", "color": "#f5f5f5"},
        ]
        self._border_style_index = 0
        self._border_line_width = 1
        self.region_overlay = None
        self.voice_output = (
            VoiceOutput(enabled=self.voice_enabled) if VoiceOutput else None
        )
        cache_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "artifacts", "ocr_cache")
        )
        self._ocr_cache_dir = prepare_ocr_cache_dir(cache_dir)

        self.create_window()
        self._setup_global_hotkey()

    def create_window(self):
        """创建主窗口"""
        self._build_window_layout()
        self._bind_window_events()

    def _normalize_hotkey(self, hotkey):
        """将配置热键转为 pynput 可识别格式。"""
        return normalize_hotkey(hotkey, default="<shift>+l")

    def _ready_status(self):
        return (
            f"就绪 | 解题快捷键: {str(self.hotkey).upper()} | "
            f"简化切换: {str(self.simplify_hotkey).upper()} | "
            f"边框切换: {str(self.border_cycle_hotkey).upper()} | "
            f"重选区域: {str(self.reselect_hotkey).upper()} | "
            f"重选模式: {str(self.toggle_reselect_mode_hotkey).upper()}"
        )

    def _set_local_hint(self, message):
        """更新仅本地状态提示条（不创建任何额外顶层窗口）。"""
        try:
            if hasattr(self, "local_hint_var"):
                self.local_hint_var.set(f"本地提示: {message}")
        except Exception:
            pass

    def _current_border_style(self):
        return self._border_styles[self._border_style_index % len(self._border_styles)]

    def _persist_ocr_text(self, ocr_text):
        """将 OCR 原文落盘，便于界面展示和 AI 提示词分流。"""
        path = persist_ocr_text(self._ocr_cache_dir, ocr_text)
        self._last_ocr_text_path = path
        return path

    def _load_ocr_text(self, path, fallback=""):
        """读取 OCR 临时文件文本，失败时回退到 fallback。"""
        return load_ocr_text(path, fallback=fallback)

    def _build_ai_prompt_from_ocr(self, ocr_text):
        """将 OCR 文本规范化为 AI 提示词，减少无效换行。"""
        return build_ai_prompt_from_ocr(ocr_text)

    def _setup_global_hotkey(self):
        """注册全局快捷键，支持无焦点触发答题流程。"""
        if pynput_keyboard is None:
            print("全局快捷键不可用: 未安装 pynput")
            return

        hotkey_map = build_hotkey_map(
            solve_hotkey=self.hotkey,
            simplify_hotkey=self.simplify_hotkey,
            border_hotkey=self.border_cycle_hotkey,
            reselect_hotkey=self.reselect_hotkey,
            legacy_reselect_hotkey=self.legacy_reselect_hotkey,
            callbacks={
                "solve": self._on_global_hotkey,
                "simplify": self._on_toggle_simplify_hotkey,
                "border": self._on_cycle_border_hotkey,
                "reselect": self._on_reselect_hotkey,
            },
            warn=print,
        )
        toggle_reselect_mode_expr = self._normalize_hotkey(
            self.toggle_reselect_mode_hotkey
        )
        if toggle_reselect_mode_expr not in hotkey_map:
            hotkey_map[toggle_reselect_mode_expr] = self._on_toggle_reselect_mode_hotkey
        else:
            print(
                "警告: 重选模式切换快捷键重复"
                f"({self.toggle_reselect_mode_hotkey})，已忽略该快捷键注册"
            )

        try:
            self._hotkey_listener = pynput_keyboard.GlobalHotKeys(hotkey_map)
            self._hotkey_listener.start()
        except Exception as e:
            print(
                "注册全局快捷键失败("
                f"解题={self.hotkey}, 简化={self.simplify_hotkey}, "
                f"边框={self.border_cycle_hotkey}, 重选={self.reselect_hotkey}): {e}"
            )

    def _on_global_hotkey(self):
        """全局快捷键回调（非主线程），转到 Tk 主线程执行。"""
        try:
            self.root.after(0, lambda: self.solve(force=True))
        except Exception:
            pass

    def _on_toggle_simplify_hotkey(self):
        """简化模式快捷键回调（非主线程），转到 Tk 主线程执行。"""
        try:
            self.root.after(0, self._toggle_simplify_from_hotkey)
        except Exception:
            pass

    def _toggle_simplify_from_hotkey(self):
        self.simplify_state = not getattr(self, "simplify_state", False)
        self.draw_simplify()
        self.status_var.set(f"简化模式: {'开启' if self.simplify_state else '关闭'}")

    def _on_cycle_border_hotkey(self):
        """边框样式快捷键回调（非主线程），转到 Tk 主线程执行。"""
        try:
            self.root.after(0, self._cycle_border_style)
        except Exception:
            pass

    def _cycle_border_style(self):
        self._border_style_index = (self._border_style_index + 1) % len(
            self._border_styles
        )
        style = self._current_border_style()
        self.status_var.set(f"边框样式: {style['name']}")
        selected_region = getattr(self.screenshot_manager, "selected_region", None)
        if selected_region:
            self._create_region_overlay(selected_region)

    def _on_reselect_hotkey(self):
        """重选区域快捷键回调（非主线程），转到 Tk 主线程执行。"""
        try:
            self.root.after(0, self._reselect_region_from_hotkey)
        except Exception:
            pass

    def _on_toggle_reselect_mode_hotkey(self):
        """重选模式切换快捷键回调（非主线程），转到 Tk 主线程执行。"""
        try:
            self.root.after(0, self._toggle_reselect_mode_from_hotkey)
        except Exception:
            pass

    def _toggle_reselect_mode_from_hotkey(self):
        self.reselect_nofocus = not bool(self.reselect_nofocus)
        try:
            setattr(
                self.config, "HOTKEY_RESELECT_REGION_NOFOCUS", self.reselect_nofocus
            )
        except Exception:
            pass

        # 切换模式时终止当前取点监听，避免中间态混淆。
        self._stop_region_pick_listener()
        mode_label = "无焦点双击取点" if self.reselect_nofocus else "有焦全屏双击取点"
        self.status_var.set(f"重选模式: {mode_label}")
        self._set_local_hint(f"重选模式已切换为：{mode_label}")

    def _on_close(self):
        """窗口关闭时释放资源。"""
        self.shutdown()
        try:
            self.root.quit()
        except Exception:
            pass

    def shutdown(self):
        """释放全局热键与语音资源。"""
        if self._closed:
            return
        self._closed = True

        try:
            if self._hotkey_listener:
                self._hotkey_listener.stop()
        except Exception:
            pass

        try:
            if self.voice_output:
                self.voice_output.shutdown()
        except Exception:
            pass
        self._stop_region_pick_listener()

    def _stop_region_pick_listener(self):
        if self._region_picker:
            try:
                self._region_picker.stop()
            except Exception:
                pass
        self._region_picker = None

    def _apply_selected_region(self, region):
        if not region:
            return
        self.screenshot_manager.set_region(region)
        self.region_label.config(text=f"已选择区域: {region}")
        self.solve_btn.config(state="normal" if self.switch_state else "disabled")
        self._set_local_hint(f"已更新识别区域 {region}")
        try:
            self._create_region_overlay(region)
            self.close_region_btn.config(state="normal")
        except Exception:
            pass

    def _reselect_region_from_hotkey(self):
        if self.reselect_nofocus and pynput_mouse is not None:
            self._start_nofocus_region_pick()
            return
        if self.reselect_nofocus and pynput_mouse is None:
            self.status_var.set("无焦点重选不可用，自动切换为有焦双击取点")
            self._set_local_hint("未检测到鼠标监听能力，回退为有焦双击取点")
        self.select_region(keep_focus=False)

    def _start_nofocus_region_pick(self):
        self._stop_region_pick_listener()
        self.status_var.set(
            "无焦点重选区域: 请依次点击左上角和右下角（可能触发网页点击）"
        )
        self._set_local_hint("无焦点取点中：先点左上角，再点右下角")

        def on_first_point(point):
            self.root.after(
                0,
                lambda p=point: self.status_var.set(
                    f"无焦点重选区域: 第一取点 {p}，请点击右下角"
                ),
            )
            self.root.after(
                0, lambda p=point: self._set_local_hint(f"第一取点成功 {p}")
            )

        def on_region(region, p1, p2):
            self.root.after(0, lambda r=region: self._apply_selected_region(r))
            self.root.after(0, lambda: self.status_var.set("无焦点重选区域完成"))
            self.root.after(
                0,
                lambda start=p1, end=p2: self._set_local_hint(
                    f"双击取点完成 {start} -> {end}"
                ),
            )
            self.root.after(0, self._stop_region_pick_listener)

        def on_error(error):
            error_text = str(error)
            self.root.after(
                0, lambda err=error_text: self.status_var.set(f"无焦点重选失败: {err}")
            )
            self.root.after(
                0, lambda err=error_text: self._set_local_hint(f"无焦点重选失败: {err}")
            )
            self.root.after(0, self._stop_region_pick_listener)

        try:
            self._region_picker = NoFocusRegionPicker(
                mouse_module=pynput_mouse,
                on_first_point=on_first_point,
                on_region=on_region,
                on_error=on_error,
            )
            self._region_picker.start()
        except Exception as e:
            self.status_var.set(f"启动无焦点重选失败: {e}")
            self._set_local_hint(f"启动无焦点重选失败: {e}")

    def select_region(self, keep_focus=True):
        """选择识别区域（有焦模式，会弹出全屏选择窗口）"""
        from gui.region_selector import RegionSelector

        self._stop_region_pick_listener()

        def on_region_selected(region):
            self._apply_selected_region(region)

        try:
            self.root.iconify()
        except Exception:
            try:
                self.root.withdraw()
            except Exception:
                pass

        selector_alpha = getattr(self.config, "REGION_SELECTOR_ALPHA", 0.3)
        selector = RegionSelector(on_region_selected, overlay_alpha=selector_alpha)
        selector.start_selection()

        if keep_focus:
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
            result_frame, wrap=tk.WORD, height=10
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # OK 按钮，用于在手动确认模式下把编辑后的 OCR 文本发送到 AI
        self.ok_btn = tk.Button(
            result_frame,
            text="✔",
            bg="green",
            fg="white",
            command=self._on_confirm_send,
        )
        # 隐藏，按需 place 到 result_text 的右下角
        try:
            self.ok_btn.place_forget()
        except Exception:
            pass

    def solve(self, force=False):
        """执行OCR和AI处理"""
        if not force and not self.switch_state:
            return

        if self.waiting_for_confirm:
            try:
                self.status_var.set("请先确认当前OCR文本")
            except Exception:
                pass
            return

        if self.processing:
            try:
                self.status_var.set("正在处理上一题，请稍候...")
            except Exception:
                pass
            return

        self.processing = True
        # 每次solve前清空结果区域以保持简洁（若result_text不存在则忽略）
        try:
            self.result_text.delete("1.0", tk.END)
        except Exception:
            pass

        # 在新线程中执行，避免界面冻结
        thread = threading.Thread(target=self._solve_thread)
        thread.daemon = True
        thread.start()

    def _solve_thread(self):
        """处理线程"""
        self.root.after(0, lambda: self.status_var.set("正在处理..."))

        try:
            # 截图
            screenshot = self.screenshot_manager.capture_region()
            if screenshot is None:
                self.root.after(
                    0, lambda: self.result_text.insert(tk.END, "错误: 未选择区域\n")
                )
                return

            # OCR识别（支持左右分屏模式）
            if getattr(self, "split_state", False):
                try:
                    ocr_text = self.ocr_engine.extract_text_split(screenshot)
                except Exception:
                    # fallback to normal extraction on error
                    ocr_text = self.ocr_engine.extract_text(screenshot)
            else:
                ocr_text = self.ocr_engine.extract_text(screenshot)
            if not ocr_text:
                self.root.after(
                    0, lambda: self.result_text.insert(tk.END, "OCR未识别到文字\n")
                )
                return

            ocr_text_path = self._persist_ocr_text(ocr_text)
            ocr_text_for_ui = self._load_ocr_text(ocr_text_path, fallback=ocr_text)
            ai_prompt = self._build_ai_prompt_from_ocr(
                self._load_ocr_text(ocr_text_path, fallback=ocr_text)
            )
            if not ai_prompt:
                self.root.after(
                    0, lambda: self.result_text.insert(tk.END, "OCR文本清洗后为空\n")
                )
                return

            # 若开启debug则输出OCR原文，默认不打印到结果区域
            if self.debug:
                self.root.after(
                    0,
                    lambda: self.result_text.insert(
                        tk.END,
                        f"识别文字: {ocr_text_for_ui}\n"
                        f"OCR临时文件: {ocr_text_path}\n\n正在调用AI...\n",
                    ),
                )
            else:
                # 仍在结果区显示正在调用AI的状态行
                self.root.after(
                    0, lambda: self.result_text.insert(tk.END, "正在调用AI...\n")
                )

            # 如果简化模式开启，传入重要的 system prompt 指示 AI 只返回简短答案
            system_prompt = None
            if getattr(self, "simplify_state", False):
                system_prompt = "快速回答下面问题，不需要任何解释"
            # 如果手动确认模式开启，则将OCR结果放入可编辑的结果框并显示OK按钮，等待用户确认后再发送
            if getattr(self, "confirm_state", False):

                def prepare_for_confirm():
                    try:
                        self.result_text.delete("1.0", tk.END)
                    except Exception:
                        pass
                    self.result_text.insert(tk.END, ocr_text_for_ui)
                    # place OK 按钮在结果框右下角
                    try:
                        self.ok_btn.place(
                            in_=self.result_text,
                            relx=1.0,
                            rely=1.0,
                            x=-10,
                            y=-10,
                            anchor="se",
                        )
                        self.ok_btn.lift()
                    except Exception:
                        pass
                    self.waiting_for_confirm = True
                    self.status_var.set("等待确认并点击 OK 发送")

                self.root.after(0, prepare_for_confirm)
                return

            ai_response = self.ai_client.generate_response(
                ai_prompt, system_prompt=system_prompt
            )

            # 更新界面
            self.root.after(0, lambda: self.display_result(ai_prompt, ai_response))

        except Exception as e:
            self.root.after(
                0, lambda: self.result_text.insert(tk.END, f"处理错误: {str(e)}\n")
            )
        finally:
            self.root.after(0, self._finish_processing)

    def _finish_processing(self):
        """线程结束后的统一收尾。"""
        self.processing = False
        if not self.waiting_for_confirm:
            self.status_var.set(self._ready_status())

    def display_result(self, ocr_text, ai_response):
        """显示结果"""
        self.result_text.insert(tk.END, f"\n\nAI回复:\n{ai_response}\n{'=' * 50}\n")
        self.result_text.see(tk.END)
        if self.voice_enabled and self.voice_output:
            self.voice_output.speak(ai_response)

    def _on_confirm_send(self):
        """当用户点击 OK 时，将编辑后的文本发送给 AI 并显示回复"""
        if not getattr(self, "waiting_for_confirm", False):
            return

        prompt = None
        try:
            prompt = self.result_text.get("1.0", tk.END).strip()
        except Exception:
            prompt = None

        if not prompt:
            # nothing to send
            try:
                self.status_var.set("没有可发送的文本")
            except Exception:
                pass
            return

        # hide OK button and clear waiting flag
        try:
            self.ok_btn.place_forget()
        except Exception:
            pass
        self.waiting_for_confirm = False
        self.processing = True

        # start thread to call AI so UI doesn't block
        thread = threading.Thread(target=self._confirm_send_thread, args=(prompt,))
        thread.daemon = True
        thread.start()

    def _confirm_send_thread(self, prompt):
        """线程：调用AI并将结果回填界面"""
        try:
            self.root.after(0, lambda: self.status_var.set("正在调用AI..."))
            system_prompt = None
            if getattr(self, "simplify_state", False):
                system_prompt = "快速回答下面问题，不需要任何解释"

            ai_response = self.ai_client.generate_response(
                prompt, system_prompt=system_prompt
            )
            self.root.after(0, lambda: self.display_result(prompt, ai_response))
        except Exception as e:
            self.root.after(
                0, lambda: self.result_text.insert(tk.END, f"处理错误: {str(e)}\n")
            )
        finally:
            self.root.after(0, self._finish_processing)

    def update_preview(self, image_array):
        """选区预览功能已移除。"""
        return

    def _create_region_overlay(self, region):
        """在屏幕上创建一个无窗口装饰的透明覆盖，仅显示选区边框，直到用户点击关闭。"""
        self.region_overlay = destroy_region_overlay(self.region_overlay)

        if not region:
            return

        border_style = self._current_border_style()
        self.region_overlay = create_region_overlay(
            root=self.root,
            region=region,
            border_style=border_style,
            border_width=self._border_line_width,
            split_state=getattr(self, "split_state", False),
        )

    def close_region(self):
        """关闭用于观察的选区边框并清除选区，要求重新选择才能再次OCR"""
        self._stop_region_pick_listener()
        self.region_overlay = destroy_region_overlay(self.region_overlay)

        # 清除选区
        try:
            self.screenshot_manager.set_region(None)
        except Exception:
            pass

        # 更新界面元素
        try:
            self.region_label.config(text="未选择区域")
            self.solve_btn.config(state="disabled")
            self.close_region_btn.config(state="disabled")
        except Exception:
            pass

    def run(self):
        """运行主循环"""
        try:
            self.root.mainloop()
        finally:
            self.shutdown()
