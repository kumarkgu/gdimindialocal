import pytesseract as pyt
from PIL import Image

class ReadImage:
    def __init__(self, ocrpath):
        self.ocr = ocrpath
        pyt.pytesseract.tesseract_cmd = self.ocr

    def read_image(self, filename):
        __vtext = pyt.image_to_string(Image.open(filename))
        return __vtext

