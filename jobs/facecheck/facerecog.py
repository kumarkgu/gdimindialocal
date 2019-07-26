from baselib.image.facedetect import encodeface as ef, recognizeface as rf
from baselib.utils import base_util as bu, fileobjects as fo
import os


class TestFace:
    def __init__(self, paths, checkfile=None, encimagefile=None, model=None,
                 encodefile=None, tolerance=None):
        self.paths = paths
        self.checkfile = checkfile
        self.encimagefile = encimagefile
        self.model = model if model else "hog"
        self.encodefile = encodefile
        self.tolerance = tolerance if tolerance else 0.6

    def encodeimage(self, imagefile=None):
        if not imagefile:
            imagefile = self.paths
            if self.encimagefile:
                imagefile = self.encimagefile
        else:
            if not (os.path.isfile(imagefile)):
                self.paths = imagefile
        extensions = ["*.jpg", "*.png", "*.bmp"]
        if not (os.path.isfile(imagefile)):
            allfiles = fo.get_all_files(self.paths, extensions=extensions)
        else:
            allfiles = [imagefile]
        efobj = ef.EncodeFace(encodefile=self.encodefile, model=self.model)
        for (idx, files) in enumerate(allfiles):
            print("[INFO] Processing Image: {}/{}".format(
                idx + 1,
                len(allfiles)
            ))
            image, rgbdata = efobj.read_image(imagefile=files)
            efobj.encode_image(rgbdata=rgbdata, imagefile=files)
        # efobj.write_data(encodefile=self.encodefile,
        #                  encodes=efobj.knownencode, names=efobj.knownname)
        efobj.append_data(encodefile=self.encodefile,
                          encodes=efobj.knownencode, names=efobj.knownname)

    def match_image(self, checkfile=None, encodefile=None, model=None,
                    tolerance=None, def_window=True):
        checkfile = checkfile if checkfile else self.checkfile
        encodefile = encodefile if encodefile else self.encodefile
        model = model if model else self.model
        tolerance = tolerance if tolerance else self.tolerance
        frobj = rf.RecogFace(encodefile=encodefile, checkfile=checkfile,
                             model=model, tolerance=tolerance)
        frobj.readimage()
        locs, encodes = frobj.encode_image()
        data = frobj.read_data()
        matches = frobj.match_face(encodings=encodes, data=data)
        frobj.draw_box(locations=locs, names=matches, image=frobj.image)
        frobj.show_image(frobj.image, def_window=def_window)


def main_run(process=None, model=None):
    model = model if model else "hog"
    home = "C:/Users/{}".format(bu.current_user())
    path = "{}/OneDrive - JLL/Office/CoE/projects/RED/Support/team".format(home)
    encodefile = "{}/encoded_file_{}.txt".format(path, model)
    objtest = TestFace(paths=path, model=model, encodefile=encodefile)
    if process == "encode":
        inputdir = "{}/{}".format(path, "source_pics")
        objtest.encodeimage(imagefile=inputdir)
    else:
        # checkimage = "{}/check_pics/{}".format(path, "TeamPicture.png")
        # checkimage = "{}/check_pics/{}".format(path, "Rashmi_Venkatesh.jpg")
        # checkimage = "{}/check_pics/{}".format(path, "Gunjan_Marriage.jpg")
        checkimage = "{}/check_pics/{}".format(path, "Gunjan_Family.jpg")
        objtest.match_image(checkfile=checkimage, tolerance=0.5)


if __name__ == "__main__":
    _process = "decode"
    # _process = "encode"
    _model = "hog"
    # _model = "cnn"
    main_run(process=_process, model=_model)
