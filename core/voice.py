#  Author: micr0softDrestlife
import base64
import os
import queue
import re
import subprocess
import threading


class VoiceOutput:
    """稳定的异步语音播报器。Windows 下优先使用 System.Speech。"""

    def __init__(self, enabled=False, max_chars=180):
        self.enabled = bool(enabled)
        self.max_chars = max(40, int(max_chars))
        self._queue = queue.Queue()
        self._thread = None
        self._running = False
        self._lock = threading.Lock()
        self._windows_backend = os.name == "nt"

        if self.enabled:
            self._start_worker()

    def _start_worker(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def _normalize_text(self, text):
        if text is None:
            return ""
        normalized = re.sub(r"\s+", " ", str(text)).strip()
        if len(normalized) > self.max_chars:
            normalized = normalized[: self.max_chars]
        return normalized

    def _speak_windows(self, text):
        payload = base64.b64encode(text.encode("utf-8")).decode("ascii")
        cmd = (
            "$b='" + payload + "';"
            "$t=[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($b));"
            "Add-Type -AssemblyName System.Speech;"
            "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
            "$s.Speak($t);"
            "$s.Dispose();"
        )
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd],
                check=True,
                timeout=90,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except Exception as e:
            print(f"Windows语音播报失败: {e}")
            return False

    def _speak_pyttsx3(self, text):
        try:
            import pyttsx3

            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            engine.stop()
            return True
        except Exception as e:
            print(f"pyttsx3播报失败: {e}")
            return False

    def _worker(self):
        while self._running:
            try:
                text = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue

            if text is None:
                break

            with self._lock:
                ok = False
                if self._windows_backend:
                    ok = self._speak_windows(text)
                if not ok:
                    self._speak_pyttsx3(text)

        self._running = False

    def speak(self, text):
        """异步播报文本。新任务会覆盖未播报的旧任务。"""
        if not self.enabled:
            return

        normalized = self._normalize_text(text)
        if not normalized:
            return

        if not self._running:
            self._start_worker()

        # 只保留最新的待播报内容，避免队列积压造成“似乎不播报”
        try:
            while True:
                self._queue.get_nowait()
        except queue.Empty:
            pass

        self._queue.put(normalized)

    def shutdown(self):
        """停止播报线程。"""
        if not self._running:
            return
        self.enabled = False
        self._running = False
        self._queue.put(None)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
