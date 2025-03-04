import cv2
import pytesseract
from PIL import Image


def extract_text_from_image(image_path):
    
    image = cv2.imread(image_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    processed_image_path = "processed_image.png"
    cv2.imwrite(processed_image_path, gray)

    text = pytesseract.image_to_string(Image.open(processed_image_path))

    return text

image_path = "C:/Users/sksan/Downloads/ex1.jpeg" 
extracted_text = extract_text_from_image(image_path)
print("Extracted Text:", extracted_text)
