#  Author: micr0softDrestlife
import pytesseract
from PIL import Image
import cv2
import numpy as np


class OCREngine:
    def __init__(self, tesseract_path=None):
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

    def preprocess_image(self, image):
        """图像预处理提高OCR准确率

        Expects image as a NumPy array in RGB order (H, W, C) or a single-channel grayscale.
        """
        # Ensure numpy array
        img = np.asarray(image)

        # If color image in RGB, convert to gray
        if img.ndim == 3 and img.shape[2] == 3:
            # If image came from OpenCV it may be BGR; however we try to detect common cases.
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img
        # 如果分辨率较小，适当放大以提高识别率（针对长中文，放大有助于LSTM模型）
        h, w = gray.shape[:2]
        target_w = 1200
        if w < target_w:
            scale = target_w / float(w)
            new_w = int(w * scale)
            new_h = int(h * scale)
            gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

        # 降噪（保留边缘）
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)

        # 对比度受限自适应直方图均衡（CLAHE）提高局部对比度
        try:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            denoised = clahe.apply(denoised)
        except Exception:
            pass

        # 自适应阈值（对非均匀照明更稳健）
        try:
            binary = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 9
            )
        except Exception:
            _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 小的形态学操作去除噪点
        kernel = np.ones((2, 2), np.uint8)
        opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        return opened

    def extract_text(self, image_array, preprocess=True):
        """从图像中提取文字

        Accepts a NumPy image (RGB) or a PIL Image. Returns stripped text.
        """
        try:
            # If PIL Image, convert to numpy array
            if isinstance(image_array, Image.Image):
                arr = np.array(image_array)
            else:
                arr = np.asarray(image_array)

            # If image is in BGR (common from cv2), convert to RGB before PIL
            if arr.ndim == 3 and arr.shape[2] == 3:
                # Heuristic: many cv2 images are uint8; assume RGB order is desired by PIL. If colors look inverted, swap.
                # Convert array to uint8 explicitly
                arr = arr.astype('uint8')
                pil_image = Image.fromarray(arr)
            else:
                pil_image = Image.fromarray(arr)

            # Optionally preprocess via OpenCV (PIL -> numpy)
            if preprocess:
                proc = np.array(pil_image)
                proc = self.preprocess_image(proc)
                pil_image = Image.fromarray(proc)

            # OCR识别，针对长中文文本使用合适的psm/oem
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