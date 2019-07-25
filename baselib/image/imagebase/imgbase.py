import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import base64
import urllib.parse as url
import urllib.request as req
from baselib.userexception import baserror as ie


class ImageBase:
    def __init__(self, imagefile=None):
        self.imagefile = imagefile

    def _reset_image_file(self, imagefile):
        self.imagefile = imagefile

    @staticmethod
    def _check_if_url(path):
        return url.urlparse(path).scheme in ('http', 'https')

    @staticmethod
    def read_url(urlpath):
        response = req.urlopen(urlpath)
        image = np.asarray(bytearray(response.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return image

    @staticmethod
    def read_file(imagefile):
        return cv2.imread(imagefile)

    @staticmethod
    def convertcolor(image, colorcode=None):
        return cv2.cvtColor(image, colorcode)

    def read_image(self, imagefile=None):
        try:
            if imagefile:
                self._reset_image_file(imagefile=imagefile)
            if self._check_if_url(self.imagefile):
                image = self.read_url(self.imagefile)
            else:
                image = self.read_file(self.imagefile)
            if image is None:
                raise ValueError
        except ValueError:
            raise ie.FileNotReadErr(
                "File: {} cannot be read".format(self.imagefile)
            )
        return image

    def convert_to_greyscale(self, outfile=None, imagefile=None, image=None):
        try:
            if image is None:
                image = self.read_image(imagefile=imagefile)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        except ie.FileNotReadErr:
            raise
        except Exception:
            raise
        if outfile:
            cv2.imwrite(outfile, image)
            return None
        else:
            return image

    @staticmethod
    def inverse_image(image):
        return cv2.bitwise_not(image)

    @staticmethod
    def write_to_file(image, outfile=None):
        if outfile:
            cv2.imwrite(outfile, image)


def convert_to_greyscale(filename, outfile=None):
    objimage = cv2.imread(filename)
    objimage = cv2.cvtColor(objimage, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(outfile, objimage)


def save_image(image, filepath):
    image.save(filepath)


def crop_image(image, box):
    return image.crop(box)


def read_image_base64(image):
    objimage = Image.open(BytesIO(base64.b64decode(image)))
    return objimage


def image_crop_save_base64(image, **kwargs):
    objimage = read_image_base64(image)
    if kwargs["box"]:
        objimage = crop_image(objimage, kwargs["box"])
    if kwargs["filepath"]:
        save_image(objimage, kwargs["filepath"])
    return objimage
