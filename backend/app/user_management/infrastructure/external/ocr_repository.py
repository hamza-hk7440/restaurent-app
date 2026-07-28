import pytesseract
from pytesseract import Output
import cv2
import numpy as np
from abc import ABC, abstractmethod
import logging
import os
import shutil
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
import re
from user_management.infrastructure.config.settings import get_settings
logger = logging.getLogger(__name__)
from user_management.application.services.ocr_service import IOCRService
from user_management.application.exceptions.exception import UserNotFoundException,OCRScanFailedException,InvalidImageError

class OCRRepository(IOCRService):
    def __init__(self):
        self.settings = get_settings()
        self._set_tesseract_path()
    def _set_tesseract_path(self) -> None:
        candidates = []

        configured_path = getattr(self.settings, "TESSERACT_PATH", None)
        if configured_path:
            candidates.append(configured_path)

        candidates.extend(
            [
                r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
                r"C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe",
                "tesseract",
            ]
        )

        for candidate in candidates:
            expanded_candidate = os.path.expandvars(os.path.expanduser(candidate))

            if expanded_candidate == "tesseract":
                resolved = shutil.which("tesseract")
                if resolved:
                    pytesseract.pytesseract.tesseract_cmd = resolved
                    logger.info(f"Tesseract path resolved from PATH: {resolved}")
                    return
                continue

            if os.path.exists(expanded_candidate):
                pytesseract.pytesseract.tesseract_cmd = expanded_candidate
                logger.info(f"Tesseract path set to: {expanded_candidate}")
                return

            logger.warning(f"Tesseract candidate not found: {expanded_candidate}")

        logger.warning(
            "Tesseract executable could not be resolved. "
            f"Configured value={configured_path!r}, current_cmd={getattr(pytesseract.pytesseract, 'tesseract_cmd', None)!r}"
        )
    
    def _validate_tesseract_installed(self) -> None:
        
        try:
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version: {version}")
        except pytesseract.TesseractNotFoundError:
            logger.error(
                "Tesseract OCR not found. "
                f"Configured path: {self.settings.TESSERACT_PATH!r}. "
                f"Current command: {getattr(pytesseract.pytesseract, 'tesseract_cmd', None)!r}"
            )
            logger.error("Tesseract OCR not installed or not found in PATH")
            raise OCRScanFailedException(
                "Tesseract OCR engine not installed. "
                "Please install: https://github.com/UB-Mannheim/tesseract/wiki"
            )
    
            
    def extract_student_id_from_card(self, image_path: str) -> str:
        
        try:
            self._validate_tesseract_installed()
            # Step 1: Validate image file
            self._validate_image_file(image_path)
            
            # Step 2: Load image
            image = self._load_image(image_path)
            
            # Step 3: Preprocess image for better OCR accuracy
            processed_image = self._preprocess_image(image)
            
            # Step 4: Extract text using Tesseract across multiple orientations
            extracted_text = ""
            student_id = None
            for label, candidate_image in self._generate_ocr_candidates(processed_image):
                extracted_text, words = self._extract_text_and_words(candidate_image)
                logger.debug(f"OCR extracted text ({label}) full: {extracted_text!r}")
                logger.debug(f"Extracted raw text ({label}): {extracted_text}")

                student_id = self._parse_student_id(extracted_text, words)
                if student_id:
                    logger.info(f"Student ID extracted using orientation: {label}")
                    break
            
            if not student_id:
                raise UserNotFoundException(
                    "Could not extract valid student ID from image. "
                    "Please ensure the ID card is clear and legible."
                )
            
            logger.info(f"Successfully extracted student ID: {student_id}")
            return student_id
        
        except (InvalidImageError, UserNotFoundException):
            raise
        except Exception as e:
            logger.error(f"Error extracting student ID: {str(e)}")
            raise OCRScanFailedException(f"OCR processing failed: {str(e)}")
    
    
    def _validate_image_file(self, image_path: str) -> None:

        if not os.path.exists(image_path):
            raise InvalidImageError(f"Image file not found: {image_path}")
        
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        file_ext = Path(image_path).suffix.lower()
        
        if file_ext not in valid_extensions:
            raise InvalidImageError(
                f"Invalid image format: {file_ext}. "
                f"Supported formats: {', '.join(valid_extensions)}"
            )
        
        file_size = os.path.getsize(image_path)
        max_size = 10 * 1024 * 1024  # 10MB
        
        if file_size > max_size:
            raise InvalidImageError(
                f"Image file too large: {file_size / 1024 / 1024:.2f}MB. "
                f"Maximum size: 10MB"
            )
    
    def _load_image(self, image_path: str) -> np.ndarray:
        
        image = cv2.imread(image_path)
        
        if image is None:
            raise InvalidImageError(f"Failed to load image: {image_path}")
        
        logger.debug(f"Image loaded: shape={image.shape}, dtype={image.dtype}")
        return image

    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Step 2: Apply denoising (reduces noise in image)
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        
        # Step 3: Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        # Improves contrast for better text visibility
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Step 4: Apply thresholding (converts to black and white)
        # Otsu's thresholding automatically finds best threshold
        _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Step 5: Apply morphological operations
        # Dilate expands white regions, erode shrinks them
        # Helps connect broken text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        # Step 6: Resize if image too small (OCR works better on larger images)
        height, width = morph.shape
        if width < 300 or height < 200:
            scale = max(300 / width, 200 / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            morph = cv2.resize(morph, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        logger.debug(f"Image preprocessed: shape={morph.shape}")
        return morph

    def _generate_ocr_candidates(self, image: np.ndarray):
        yield "original", image
        yield "rotated_90_cw", cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        yield "rotated_90_ccw", cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        yield "rotated_180", cv2.rotate(image, cv2.ROTATE_180)
        height, width = image.shape[:2]
        crops = {
            "bottom_half": image[height // 2 :, :],
            "bottom_left_quarter": image[height // 2 :, : width // 2],
            "bottom_right_quarter": image[height // 2 :, width // 2 :],
            "center_band": image[height // 4 : (3 * height) // 4, :],
        }
        for label, crop in crops.items():
            if crop.size:
                yield label, crop
    
    
    def _extract_text_and_words(self, image: np.ndarray) -> tuple[str, list[dict[str, Any]]]:
        
        try:
            # Extract full text and word boxes so we can find a 6-digit number
            # near the registration label even if OCR is noisy.
            config = '--psm 11 --oem 3'
            
            text = pytesseract.image_to_string(image, config=config)
            data = pytesseract.image_to_data(image, config=config, output_type=Output.DICT)
            words: list[dict[str, Any]] = []
            for i, raw_text in enumerate(data.get("text", [])):
                cleaned = (raw_text or "").strip()
                if not cleaned:
                    continue
                conf_raw = data.get("conf", ["-1"])[i]
                try:
                    confidence = float(conf_raw)
                except (TypeError, ValueError):
                    confidence = -1.0
                words.append(
                    {
                        "text": cleaned,
                        "left": int(data.get("left", [0])[i]),
                        "top": int(data.get("top", [0])[i]),
                        "width": int(data.get("width", [0])[i]),
                        "height": int(data.get("height", [0])[i]),
                        "conf": confidence,
                    }
                )
            
            return text.strip(), words
        
        except Exception as e:
            raise OCRScanFailedException(f"Tesseract OCR failed: {str(e)}")
    

    
    def _parse_student_id(self, text: str, words: Optional[List[Dict[str, Any]]] = None) -> Optional[str]:
       
        if not text:
            return None
        
        # Remove whitespace
        text = text.replace('\n', ' ').replace('\r', '')
        
        logger.debug(f"Parsing text for student ID: {text[:100]}...")
        
        # Pattern 1: Only accept a 6-digit number after the Arabic labels.
        patterns = [
            r'(?:رقم\s*الت[رسش]يم|رقم\s*التسجيل)[:\s#\-]*([0-9]{6})',
            r'(?:رقم\s*الت[رسش]يم|رقم\s*التسجيل)[^\d]{0,30}([0-9]{6})',
        ]

        for pattern in patterns:
            try:
                matches = re.findall(pattern, text, re.IGNORECASE)
            except re.error as e:
                logger.error(f"Invalid OCR regex pattern {pattern!r}: {e}")
                continue

            if matches:
                student_id = matches[0]

                if self._is_plausible_student_id(student_id):
                    return student_id

        if words:
            label_words = []
            for word in words:
                normalized = self._normalize_ocr_text(word["text"])
                if self._matches_registration_label(normalized):
                    label_words.append(word)

            if label_words:
                for label_word in label_words:
                    candidate = self._find_nearest_six_digit_number(words, label_word)
                    if candidate:
                        return candidate

        return None

    def _find_nearest_six_digit_number(self, words: List[Dict[str, Any]], label_word: Dict[str, Any]) -> Optional[str]:
        label_x = label_word["left"]
        label_y = label_word["top"]

        best_candidate = None
        best_score = None

        for word in words:
            candidate_text = self._normalize_ocr_text(word["text"])
            if not re.fullmatch(r"\d{6}", candidate_text):
                continue
            if not self._is_plausible_student_id(candidate_text):
                continue

            dx = abs(word["left"] - label_x)
            dy = abs(word["top"] - label_y)
            score = (dy * 3) + dx

            if best_score is None or score < best_score:
                best_score = score
                best_candidate = candidate_text

        return best_candidate

    def _normalize_ocr_text(self, text: str) -> str:
        text = text or ""
        text = text.strip().lower()
        text = text.replace("0", "o")
        text = text.replace("1", "l")
        text = text.replace("5", "s")
        text = text.replace("7", "t")
        text = re.sub(r"[^a-z\u0600-\u06ff]+", "", text)
        return text

    def _matches_registration_label(self, normalized_text: str) -> bool:
        if not normalized_text:
            return False

        label_patterns = [
            r"رقمالترسيم",
            r"رقمالتسجيل",
            r"نقم\w*الترسيم",
            r"نقم\w*التسجيل",
            r"num",
            r"cin",
            r"registration",
        ]

        return any(re.search(pattern, normalized_text) for pattern in label_patterns)
    
    def _is_plausible_student_id(self, student_id: str) -> bool:
        if not student_id or not student_id.isdigit():
            return False

        if len(student_id) != 6:
            return False

        # Reject academic-year-like values such as 202520 or 202526.
        if student_id.startswith("2025") or student_id.startswith("2026"):
            return False

        # Reject obvious barcode or document noise.
        if student_id in {"970770", "9707707", "202520", "202526"}:
            return False

        return True
