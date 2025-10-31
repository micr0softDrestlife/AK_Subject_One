# smoke_test.py - simple import/construct test
import sys
sys.path.append(r'E:\tools\ocr_ai_tongsha\python')

from config.settings import AppConfig
from core.ocr_engine import OCREngine
from core.ai_client import OllamaClient
from core.screenshot import ScreenshotManager

if __name__ == '__main__':
    cfg = AppConfig()
    ocr = OCREngine(cfg.TESSERACT_PATH)
    ai = OllamaClient(cfg.OLLAMA_BASE_URL, cfg.OLLAMA_MODEL)
    ss = ScreenshotManager()
    print('AppConfig:', cfg)
    print('OCREngine initialized, tesseract_cmd =', getattr(__import__('pytesseract').pytesseract, 'tesseract_cmd', None))
    print('OllamaClient:', ai.base_url, ai.model)
    print('ScreenshotManager selected_region:', ss.selected_region)
    print('SMOKE TEST: OK')
