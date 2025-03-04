import cv2
from PIL import Image
import pytesseract
import numpy as np
from typing import Dict, Any
from patterns import PATTERNS  # Import the pattern extraction logic

def preprocess_image(image_path: str) -> Any:
    """Loads and preprocesses an image for OCR."""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding for better OCR accuracy
    processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY, 11, 2)
    
    # Denoise image
    processed = cv2.fastNlMeansDenoising(processed, h=30)
    
    return processed

def extract_text_from_image(image_path: str) -> str:
    """Extracts text from a preprocessed image using Tesseract OCR."""
    processed_image = preprocess_image(image_path)
    text = pytesseract.image_to_string(processed_image, config='--psm 6')
    return text

def apply_patterns(text: str) -> Dict[str, Any]:
    """Applies regex patterns to extract structured data from text."""
    extracted_data = {}
    
    for pattern in PATTERNS:
        match = pattern.regex.search(text)
        if match:
            extracted_data[pattern.name] = pattern.parser(match)
    
    return extracted_data

if __name__ == "__main__":
    image_path = "D:\\Claims App\\ex2.jpeg"  # Replace with the actual image path
    extracted_text = extract_text_from_image(image_path)
    structured_data = apply_patterns(extracted_text)
    
    print("Extracted Data:", structured_data)
