#  Author: micr0softDrestlife


class WindowEventsMixin:
    """窗口事件绑定器：只负责绑定与窗口置顶状态管理。"""

    def _bind_window_events(self):
        # 窗口始终置顶（除非最小化或窗口被关闭）
        try:
            self.root.attributes("-topmost", True)
        except Exception:
            pass

        # 监听最小化/还原事件，最小化时取消置顶，恢复时再次置顶
        self.root.bind("<Unmap>", self._on_unmap)
        self.root.bind("<Map>", self._on_map)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_unmap(self, event):
        """窗口最小化时取消置顶"""
        try:
            if self.root.state() == "iconic":
                self.root.attributes("-topmost", False)
        except Exception:
            pass

    def _on_map(self, event):
        """窗口还原时再次置顶"""
        try:
            if self.root.state() != "iconic":
                self.root.attributes("-topmost", True)
        except Exception:
            pass
