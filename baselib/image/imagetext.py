from baselib.utils import base_util as bu
from baselib.userexception import baserror as ce
import pytesseract as pyt
from PIL import Image
import os


class ReadImage:
    _OCR_NOT_FOUND = "OCR Command Not Found. Restart the process by" \
                     " providing OCR Path"

    def __init__(self, ocrpath=None):
        self.ocr = None
        self._set_ocrpath(ocrpath=ocrpath)
        pyt.pytesseract.tesseract_cmd = self.ocr

    def _set_ocrpath(self, ocrpath=None):
        ocrname = "tesseract.exe"
        paths = [
            "C:/Program Files (x86)/Tesseract-OCR",
            "C:/Users/{0}/Box Sync/CoEUtilities".format(bu.current_user())
        ]
        if os.path.isfile(ocrpath):
            self.ocr = ocrpath
        else:
            for path in paths:
                t_path = "{}/{}".format(path, ocrname)
                if os.path.isfile(t_path):
                    self.ocr = t_path
                    break
        if self.ocr is None:
            raise ce.CommandNotFound(
                ReadImage._OCR_NOT_FOUND
            )

    @staticmethod
    def read_image(filename):
        ocrtext = pyt.image_to_string(Image.open(filename))
        return ocrtext

