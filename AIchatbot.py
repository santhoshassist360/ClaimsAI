import cv2
import pytesseract
import numpy as np
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage

# Initialize FastAPI app
app = FastAPI()

# Initialize OpenAI Chat Model
chat_model = ChatOpenAI()

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

@app.post("/chat")
def chatbot_response(user_query: str):
    """Handles chatbot responses based on user queries."""
    try:
        response = chat_model([HumanMessage(content=user_query)])
        return {"response": response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    image_path = "receipt.jpg"  # Replace with the actual image path
    extracted_text = extract_text_from_image(image_path)
    structured_data = apply_patterns(extracted_text)
    
    print("Extracted Data:", structured_data)
