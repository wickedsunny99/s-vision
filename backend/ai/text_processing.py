import io

import pytesseract
from PIL import Image


class TextProcessor:
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"  # Update path

    def extract_text(self, image_bytes):
        try:
            img = Image.open(io.BytesIO(image_bytes))
            return pytesseract.image_to_string(img)
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""
