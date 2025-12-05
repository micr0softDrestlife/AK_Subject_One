#  Author: micr0softDrestlife
# OCR Engine - 使用 PaddleOCR 进行文字识别

from PIL import Image
import numpy as np


# 速度模式配置
# 值越小速度越快但精度可能降低，值越大精度越高但速度越慢
SPEED_MODES = {
    'fast': {
        'name': '极速模式',
        'ocr_version': 'PP-OCRv4',  # mobile版本，最快
        'text_det_limit_side_len': 640,  # 较小的检测尺寸
        'description': '最快速度，适合简单文字'
    },
    'balanced': {
        'name': '平衡模式',
        'ocr_version': 'PP-OCRv4',  # mobile版本
        'text_det_limit_side_len': 960,  # 中等检测尺寸
        'description': '速度与精度平衡'
    },
    'accurate': {
        'name': '精确模式',
        'ocr_version': None,  # 使用默认server版本 (PP-OCRv5)
        'text_det_limit_side_len': 1280,  # 较大的检测尺寸
        'description': '最高精度，速度较慢'
    }
}


class OCREngine:
    """
    基于 PaddleOCR 的 OCR 引擎
    
    PaddleOCR 优势：
    - 中文识别准确率更高
    - 支持109种语言
    - 无需额外安装二进制文件，pip安装即可使用
    - 模型会自动下载并缓存到本地，支持离线使用
    
    速度模式：
    - fast: 极速模式，使用PP-OCRv4 mobile，约0.5秒
    - balanced: 平衡模式，使用PP-OCRv4 mobile，约1秒
    - accurate: 精确模式，使用PP-OCRv5 server，约8秒
    """
    
    def __init__(self, model_dir=None, use_gpu=False, lang='ch', speed_mode='fast'):
        """
        初始化 PaddleOCR 引擎
        
        Args:
            model_dir: 模型存储目录，为None时使用默认目录（~/.paddlex）
            use_gpu: 是否使用GPU加速（PaddleOCR 3.x 会自动检测）
            lang: 识别语言，'ch'为中英文混合，'en'为纯英文
            speed_mode: 速度模式，'fast'/'balanced'/'accurate'
        """
        self.model_dir = model_dir
        self.use_gpu = use_gpu
        self.lang = lang
        self._speed_mode = speed_mode
        self._ocr = None
        self._initialized = False
        self._current_mode = None  # 记录当前加载的模式
    
    @property
    def speed_mode(self):
        return self._speed_mode
    
    @speed_mode.setter
    def speed_mode(self, value):
        """设置速度模式，如果模式改变则重新初始化OCR"""
        if value not in SPEED_MODES:
            raise ValueError(f"无效的速度模式: {value}，可选: {list(SPEED_MODES.keys())}")
        if value != self._speed_mode:
            self._speed_mode = value
            self._initialized = False  # 标记需要重新初始化
            self._ocr = None
    
    def set_speed_mode(self, mode):
        """设置速度模式的方法（供外部调用）"""
        self.speed_mode = mode
        print(f"OCR速度模式已切换为: {SPEED_MODES[mode]['name']}")
    
    def get_speed_modes(self):
        """获取所有可用的速度模式"""
        return SPEED_MODES
    
    def _init_ocr(self):
        """延迟初始化 PaddleOCR，首次调用时加载模型"""
        if self._initialized and self._current_mode == self._speed_mode:
            return
        
        try:
            from paddleocr import PaddleOCR
            
            mode_config = SPEED_MODES.get(self._speed_mode, SPEED_MODES['fast'])
            
            # PaddleOCR 3.x 配置参数
            ocr_params = {
                'lang': self.lang,
                # 关闭不必要的预处理以加速
                'use_doc_orientation_classify': False,
                'use_doc_unwarping': False,
                'use_textline_orientation': False,
            }
            
            # 设置模型版本
            if mode_config['ocr_version']:
                ocr_params['ocr_version'] = mode_config['ocr_version']
            
            # 设置检测尺寸限制
            if mode_config['text_det_limit_side_len']:
                ocr_params['text_det_limit_side_len'] = mode_config['text_det_limit_side_len']
            
            self._ocr = PaddleOCR(**ocr_params)
            self._initialized = True
            self._current_mode = self._speed_mode
            print(f"PaddleOCR 引擎初始化成功 - {mode_config['name']}")
            
        except ImportError as e:
            raise ImportError(
                "PaddleOCR 未安装。请运行: pip install paddleocr paddlepaddle\n"
                f"错误详情: {e}"
            )
        except Exception as e:
            print(f"PaddleOCR 初始化错误: {e}")
            raise

    def _to_numpy(self, image_array):
        """
        将输入图像转换为numpy数组（BGR格式，PaddleOCR要求）
        
        Args:
            image_array: PIL Image 或 numpy array
            
        Returns:
            numpy array (BGR格式)
        """
        if isinstance(image_array, Image.Image):
            # PIL Image 转 numpy array
            img_array = np.array(image_array)
            # 如果是RGB，转换为BGR（PaddleOCR使用OpenCV的BGR格式）
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                img_array = img_array[:, :, ::-1]  # RGB to BGR
            return img_array
        
        arr = np.asarray(image_array)
        # 确保是uint8类型
        if arr.dtype != np.uint8:
            arr = arr.astype('uint8')
        return arr

    def _to_pil(self, image_array):
        """将输入图像转换为PIL Image（用于分割等操作）"""
        if isinstance(image_array, Image.Image):
            return image_array
        
        arr = np.asarray(image_array)
        if arr.ndim == 3 and arr.shape[2] == 3:
            arr = arr.astype('uint8')
            return Image.fromarray(arr)
        return Image.fromarray(arr)

    def extract_text(self, image_array):
        """
        从图像中提取文字
        
        Args:
            image_array: PIL Image 或 numpy array
            
        Returns:
            识别出的文字字符串
        """
        try:
            # 确保OCR引擎已初始化
            self._init_ocr()
            
            # 转换图像格式 - PaddleOCR 3.x 需要numpy数组
            img = self._to_numpy(image_array)
            
            # 执行OCR识别 - PaddleOCR 3.x 使用 predict 方法
            result = self._ocr.predict(img)
            
            # 解析结果
            if result is None or len(result) == 0:
                return ""
            
            # PaddleOCR 3.x 返回格式: [OCRResult对象]
            # 每个OCRResult包含 rec_texts, rec_scores, dt_polys 等属性
            text_lines = []
            for ocr_result in result:
                if hasattr(ocr_result, 'rec_texts'):
                    # 新版API
                    text_lines.extend(ocr_result.rec_texts)
                elif isinstance(ocr_result, dict) and 'rec_texts' in ocr_result:
                    text_lines.extend(ocr_result['rec_texts'])
                elif isinstance(ocr_result, list):
                    # 兼容旧版格式
                    for item in ocr_result:
                        if item and len(item) >= 2:
                            text_content = item[1][0] if isinstance(item[1], tuple) else item[1]
                            text_lines.append(str(text_content))
            
            return '\n'.join(text_lines)
            
        except Exception as e:
            print(f"OCR识别错误: {e}")
            import traceback
            traceback.print_exc()
            return ""

    def extract_text_split(self, image_array):
        """
        将图像按竖直中线分割，先对左半部分OCR，再对右半部分OCR，按左右顺序合并返回结果。
        
        适用于左右分屏的题目显示场景。
        
        Args:
            image_array: PIL Image 或 numpy array
            
        Returns:
            合并后的文字字符串
        """
        try:
            pil = self._to_pil(image_array)
            w, h = pil.size
            mid = w // 2

            # 分割图像
            left = pil.crop((0, 0, mid, h))
            right = pil.crop((mid, 0, w, h))

            # 分别识别
            left_text = self.extract_text(left)
            right_text = self.extract_text(right)

            # 合并结果
            if left_text and right_text:
                return left_text + '\n' + right_text
            return (left_text or '') + (('\n' + right_text) if right_text else '')
            
        except Exception as e:
            print(f"分屏OCR错误: {e}")
            return ""
    
    def extract_text_with_positions(self, image_array):
        """
        从图像中提取文字及其位置信息
        
        Args:
            image_array: PIL Image 或 numpy array
            
        Returns:
            list: 包含 (文字, 置信度, 边界框) 的列表
        """
        try:
            self._init_ocr()
            img = self._to_numpy(image_array)
            result = self._ocr.predict(img)
            
            if result is None or len(result) == 0:
                return []
            
            extracted = []
            for ocr_result in result:
                if hasattr(ocr_result, 'rec_texts'):
                    # PaddleOCR 3.x 格式
                    texts = ocr_result.rec_texts if ocr_result.rec_texts else []
                    scores = ocr_result.rec_scores if hasattr(ocr_result, 'rec_scores') else [1.0] * len(texts)
                    boxes = ocr_result.dt_polys if hasattr(ocr_result, 'dt_polys') else [None] * len(texts)
                    
                    for i, text in enumerate(texts):
                        extracted.append({
                            'text': text,
                            'confidence': scores[i] if i < len(scores) else 1.0,
                            'box': boxes[i].tolist() if i < len(boxes) and boxes[i] is not None else None
                        })
                elif isinstance(ocr_result, dict) and 'rec_texts' in ocr_result:
                    texts = ocr_result.get('rec_texts', [])
                    scores = ocr_result.get('rec_scores', [1.0] * len(texts))
                    boxes = ocr_result.get('dt_polys', [None] * len(texts))
                    
                    for i, text in enumerate(texts):
                        extracted.append({
                            'text': text,
                            'confidence': scores[i] if i < len(scores) else 1.0,
                            'box': boxes[i] if i < len(boxes) else None
                        })
            
            return extracted
            
        except Exception as e:
            print(f"OCR识别错误: {e}")
            return []