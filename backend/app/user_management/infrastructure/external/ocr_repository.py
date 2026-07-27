import pytesseract
from pytesseract import Output
import cv2
import numpy as np
from abc import ABC, abstractmethod
import logging
import os
from pathlib import Path
from typing import Optional, Tuple
import re
from user_management.infrastructure.config.settings import get_settings
logger = logging.getLogger(__name__)
from user_management.application.services.ocr_service import IOCRService
from user_management.application.exceptions.exception import UserNotFoundException,OCRScanFailedException,InvalidImageError

class OCRRepository(IOCRService):
    def __init__(self):
        self.settings = get_settings()
        self._set_tesseract_path()
        self._validate_tesseract_installed()
    def _set_tesseract_path(self) -> None:

        tesseract_path = self.settings.TESSERACT_PATH
        
        if tesseract_path and os.path.exists(tesseract_path):
            pytesseract.pytesseract.pytesseract_cmd = tesseract_path
            logger.info(f"Tesseract path set to: {tesseract_path}")
        else:
            logger.warning(f"Tesseract path not found: {tesseract_path}")
            logger.info("Trying system default Tesseract location...")
    
    def _validate_tesseract_installed(self) -> None:
        
        try:
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version: {version}")
        except pytesseract.TesseractNotFoundError:
            logger.error("Tesseract OCR not installed or not found in PATH")
            raise OCRScanFailedException(
                "Tesseract OCR engine not installed. "
                "Please install: https://github.com/UB-Mannheim/tesseract/wiki"
            )
    
            
    def extract_student_id_from_card(self, image_path: str) -> str:
        
        try:
            # Step 1: Validate image file
            self._validate_image_file(image_path)
            
            # Step 2: Load image
            image = self._load_image(image_path)
            
            # Step 3: Preprocess image for better OCR accuracy
            processed_image = self._preprocess_image(image)
            
            # Step 4: Extract text using Tesseract
            extracted_text = self._extract_text_from_image(processed_image)
            
            logger.debug(f"Extracted raw text: {extracted_text}")
            
            # Step 5: Parse and extract student ID
            student_id = self._parse_student_id(extracted_text)
            
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
    
    
    def _extract_text_from_image(self, image: np.ndarray) -> str:
        
        try:
            # Extract text with high PSM (Page Segmentation Mode)
            # PSM 6 = Assume a single uniform block of text
            config = '--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789'
            
            text = pytesseract.image_to_string(image, config=config)
            
            return text.strip()
        
        except Exception as e:
            raise OCRScanFailedException(f"Tesseract OCR failed: {str(e)}")
    

    
    def _parse_student_id(self, text: str) -> Optional[str]:
       
        if not text:
            return None
        
        # Remove whitespace
        text = text.replace('\n', ' ').replace('\r', '')
        
        logger.debug(f"Parsing text for student ID: {text[:100]}...")
        
        # Pattern 1: Look for "ID:" or "No:" or "NUM:" followed by numbers
        patterns = [
            r'(?:ID|No|NUM|STUDENT)[:\s]+(\d{6})',  # ID: 20210001
            r'(\d{6})',  
            r'Registration[:\s]+(\d{6,10})',
            r'(?:رقم الترسيم|رقم التسجيل)[:\s]+(\d{6}'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Return first valid match
                student_id = matches[0]
                
                # Validate student ID format
                if self._validate_student_id_format(student_id):
                    return student_id
        
        # Pattern 2: Just look for any 6-digit number
        digits = re.findall(r'\d{6}', text)
        if digits:
            return digits[0]
        
        return None
    
    def _validate_student_id_format(self, student_id: str) -> bool:
        
        if not student_id or len(student_id) < 6:
            return False
        
        try:
            year_part = int(student_id[:4])
            
            
            if year_part < 2000 or year_part > 2099:
                return False
            
            # Check rest are digits
            int(student_id)
            
            return True
        except ValueError:
            return False