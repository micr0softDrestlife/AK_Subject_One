#  Author: micr0softDrestlife
import os
import re
from datetime import datetime


def prepare_ocr_cache_dir(base_dir):
    """准备 OCR 文本缓存目录，失败时返回 None。"""
    if not base_dir:
        return None
    try:
        os.makedirs(base_dir, exist_ok=True)
        return base_dir
    except Exception:
        return None


def persist_ocr_text(cache_dir, ocr_text):
    """将 OCR 原文落盘，便于界面展示和 AI 提示词分流。"""
    if not ocr_text or not cache_dir:
        return None
    try:
        stamp = datetime.now().strftime("%m-%d-%H-%M-%S-%f")
        path = os.path.join(cache_dir, f"ocr_{stamp}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(str(ocr_text))
        return path
    except Exception as e:
        print(f"OCR文本写入临时文件失败: {e}")
        return None


def load_ocr_text(path, fallback=""):
    """读取 OCR 临时文件文本，失败时回退到 fallback。"""
    if not path:
        return fallback
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"OCR临时文件读取失败: {e}")
        return fallback


def build_ai_prompt_from_ocr(ocr_text):
    """将 OCR 文本规范化为 AI 提示词，减少无效换行。"""
    if not ocr_text:
        return ""

    lines = [line.strip() for line in str(ocr_text).splitlines() if line.strip()]
    if not lines:
        return ""

    # 题面被切成很多短行时，压平成空格分隔，避免大量换行干扰模型理解。
    if len(lines) >= 6:
        return re.sub(r"\s+", " ", " ".join(lines)).strip()

    # 行数较少时保留结构，但去掉多余空白。
    return "\n".join(lines)
