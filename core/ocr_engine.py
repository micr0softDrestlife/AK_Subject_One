#  Author: micr0softDrestlife
import pytesseract
from PIL import Image
import cv2
import numpy as np


class OCREngine:
    def __init__(self, tesseract_path=None):
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

    def _to_pil(self, image_array):
        """Convert numpy array or PIL Image to a PIL Image instance without altering pixels."""
        if isinstance(image_array, Image.Image):
            return image_array

        arr = np.asarray(image_array)
        # If it's a 3-channel image assume it's already RGB
        if arr.ndim == 3 and arr.shape[2] == 3:
            arr = arr.astype('uint8')
            return Image.fromarray(arr)
        # single channel or other
        return Image.fromarray(arr)

    def extract_text(self, image_array):
        """直接从图像中提取文字，不做预处理以最大程度保留原始信息。"""
        try:
            pil_image = self._to_pil(image_array)
            tesseract_config = '--oem 1 --psm 6'
            text = pytesseract.image_to_string(
                pil_image,
                lang='chi_sim+eng',
                config=tesseract_config
            )
            return text.strip()
        except Exception as e:
            print(f"OCR识别错误: {e}")
            return ""

    def extract_text_split(self, image_array):
        """将图像按竖直中线分割，先对左半部分OCR，再对右半部分OCR，按左右顺序合并返回结果。"""
        try:
            pil = self._to_pil(image_array)
            w, h = pil.size
            mid = w // 2

            left = pil.crop((0, 0, mid, h))
            right = pil.crop((mid, 0, w, h))

            left_text = self.extract_text(left)
            right_text = self.extract_text(right)

            # 合并左右识别结果，保留空格或换行以帮助后续处理
            if left_text and right_text:
                return left_text + '\n' + right_text
            return (left_text or '') + (('\n' + right_text) if right_text else '')
        except Exception as e:
            print(f"分屏OCR错误: {e}")
            return ""