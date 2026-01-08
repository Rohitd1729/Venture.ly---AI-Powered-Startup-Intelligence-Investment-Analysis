
import sys
import os
import pytesseract
from PIL import Image

def test_ocr_setup():
    print("Testing OCR Setup...")
    
    # Check Tesseract Path
    tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if os.path.exists(tesseract_cmd):
        print(f"Tesseract found at: {tesseract_cmd}")
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    else:
        print("Tesseract not found at default location.")
        return
    
    try:
        # Create a simple image with text using PIL
        img = Image.new('RGB', (200, 100), color = (255, 255, 255))
        import PIL.ImageDraw as ImageDraw
        d = ImageDraw.Draw(img)
        d.text((10,10), "Hello World", fill=(0,0,0))
        
        # Run OCR
        text = pytesseract.image_to_string(img)
        print(f"OCR Result: '{text.strip()}'")
        
        if "Hello World" in text:
            print("OCR Verification SUCCESS!")
        else:
            print("OCR Verification FAILED: Text not matching.")
            
    except Exception as e:
        print(f"OCR Verification ERROR: {e}")

if __name__ == "__main__":
    test_ocr_setup()
