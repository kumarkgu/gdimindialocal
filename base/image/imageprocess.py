import numpy as np
import cv2
from base.image.imagebase import imageerror as ie
from base.image.imagebase.imagebase import ImageBase


class ProcessImage(ImageBase):
    def __init__(self, imagefile=None):
        super(ProcessImage, self).__init__(imagefile=imagefile)

    @staticmethod
    def rotateandscale(image, scale=1.0, angle=30):
        (height, width) = image.shape[:2]
        (center_x, center_y) = (width // 2, height // 2)
        median = cv2.getRotationMatrix2D((center_x, center_y), -angle,
                                         scale=scale)
        cos = np.abs(median[0, 0])
        sin = np.abs(median[0, 1])
        new_width = int((height * sin) + (width * cos))
        new_height = int((height * cos) + (width * sin))
        median[0, 2] += (new_width / 2) - center_x
        median[1, 2] += (new_height / 2) - center_y
        return cv2.warpAffine(image, median, (new_width, new_height),
                              flags=cv2.INTER_CUBIC,
                              borderMode=cv2.BORDER_REPLICATE)

    @staticmethod
    def _calculate_blur(image):
        return cv2.Laplacian(image, cv2.CV_64F).var()

    @staticmethod
    def show_image(imagelist, waittime=0):
        for key, value in imagelist.items():
            cv2.imshow("{}:".format(key), value)
        cv2.waitKey(waittime)

    @staticmethod
    def resize_image(image, dimension=None, scale=None, interpolation=None,
                     xwidth=None, yheight=None):
        def _get_interpolation(pscale):
            if pscale >= 1:
                t_inter = interpolation if interpolation else cv2.INTER_CUBIC
            else:
                t_inter = interpolation if interpolation else cv2.INTER_AREA
            return t_inter
        (height, width) = image.shape[:2]
        if scale:
            interpol = _get_interpolation(pscale=scale)
            t_dimension = (int(width * scale), int(height * scale))
        else:
            if xwidth:
                ratio = xwidth / width
                t_dimension = (xwidth, int(height * ratio))
            elif yheight:
                ratio = yheight / height
                t_dimension = (int(width * ratio), yheight)
            elif dimension:
                ratio = dimension[0] / width
                t_dimension = dimension
            else:
                return image
            interpol = _get_interpolation(ratio)
        return cv2.resize(image, t_dimension, interpol)

    def _read_image(self, image):
        image = self.imagefile if not image else image
        try:
            assert isinstance(image, np.ndarray)
        except AssertionError:
            try:
                assert isinstance(image, str)
                image = self.read_image(imagefile=image)
            except AssertionError:
                raise ie.ImageOrImageFileNotValidErr(
                    "Input: {} is neither a valid Image File or Image"
                    " Array".format(image)
                )
        except Exception:
            raise
        return image

    def convert_black_white(self, image=None):
        image = self._read_image(image=image)
        gray_image = self.convert_to_greyscale(image=image)
        (thresh, image_bw) = cv2.threshold(gray_image, 128, 255,
                                           cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        return image_bw

    def check_blurr(self, image, threshold=100):
        try:
            score = self._calculate_blur(image)
        except cv2.error as err:
            raise ie.ImageCV2Err(str(err))
        if score < threshold:
            raise ie.ImageBlurrErr(str(score))
        return 0

    def rotate_image(self, imagedata=None, **kwargs):
        image = self.imagefile if not imagedata else imagedata
        try:
            assert isinstance(image, np.ndarray)
        except AssertionError:
            try:
                assert isinstance(image, str)
                image = self.read_image(imagefile=image)
            except AssertionError:
                raise ie.ImageOrImageFileNotValidErr(
                    "Input: {} is neither a valid Image File or Image"
                    " Array".format(image)
                )
        except Exception:
            raise
        angle = kwargs.get("rotation", -30)
        scale = kwargs.get("scale", 1.0)
        rotated = self.rotateandscale(image=image, scale=scale, angle=angle)
        return rotated

    def correct_skew_image(self, imagedata=None, **kwargs):
        image = self._read_image(image=imagedata)
        gray_image = self.convert_to_greyscale(image=image)
        gray_image = self.inverse_image(gray_image)
        # set all foreground pixel to 255 and background to 0
        thresh = cv2.threshold(gray_image, 0, 255,
                               cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        coords = np.column_stack(np.where(thresh > 0))
        angle = cv2.minAreaRect(coords)[-1]
        angle = kwargs.get("rotation", -(90 + angle) if angle < -45 else -angle)
        angle = -angle
        scale = kwargs.get("scale", 1.0)
        if angle != 0:
            rotated = self.rotateandscale(image=image, scale=scale, angle=angle)
        else:
            rotated = image
        return rotated


def test_rotated(basepath, foldername, filename, extension, rotate=None):
    filepath = "{}/{}".format(basepath, foldername)
    file = "{}/{}.{}".format(filepath, filename, extension)
    outfile = "{}/rotate_{}.{}".format(filepath, filename, extension)
    oimage = ProcessImage(imagefile=file)
    if rotate:
        rotated = oimage.correct_skew_image(rotation=rotate)
    else:
        rotated = oimage.correct_skew_image()
    oimage.write_to_file(rotated, outfile=outfile)


def test_black_white(basepath, foldername, filename, extension):
    filepath = "{}/{}".format(basepath, foldername)
    file = "{}/{}.{}".format(filepath, filename, extension)
    outfile = "{}/rotate_{}.{}".format(filepath, filename, extension)
    oimage = ProcessImage(imagefile=file)
    black_white = oimage.convert_black_white()
    oimage.write_to_file(black_white, outfile=outfile)


vpath = "C:/Users/gunjan.kumar/Documents/JLL/Projects/Research/IGR/process"
vpath += "/challenges"
vextn = "png"
# vfile = "page1"

# Test rotation
print("Correcting Rotated Text")
vfolder = "test_rotation_angle"
vfile = "test_image_2"
test_rotated(vpath, vfolder, vfile, vextn)
#
# # Test 180 degree
# print("Correcting 90 degree rotated text")
# vfolder = "scanned_image_180/html"
# test_rotated(vpath, vfolder, vfile, vextn, 270)
#
#
# # Test colored image
# print("Converting Image to Black White")
# vfolder = "colored_image"
# test_black_white(vpath, vfolder, vfile, vextn)
