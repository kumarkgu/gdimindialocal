import cv2
import os
import pickle
import face_recognition as fr
from baselib.image.imagebase import imgbase as ib


class BaseFaceOperation:
    def __init__(self, imagefile=None, model=None, encodefile=None,
                 tolerance=None):
        self.imagefile = imagefile
        self.encodefile = encodefile
        self.model = model if model else "hog"
        self.imagebase = ib.ImageBase()
        self.tolerance = tolerance if tolerance else 0.6

    def read_image(self, imagefile=None):
        imagefile = imagefile if imagefile else self.imagefile
        image = self.imagebase.read_image(imagefile=imagefile)
        rgbdata = self.imagebase.convertcolor(image=image,
                                              colorcode=cv2.COLOR_BGR2RGB)
        return image, rgbdata

    def _face_locs(self, rgbdata):
        return fr.face_locations(img=rgbdata, model=self.model)

    @staticmethod
    def _face_encode(rgbdata, locations):
        return fr.face_encodings(face_image=rgbdata,
                                 known_face_locations=locations)

    @staticmethod
    def get_names(filename):
        name = filename.split(os.path.sep)[-1]
        name = os.path.splitext(name)[0]
        name = name.replace("_", " ")
        return name

    def encode_face(self, rgbdata):
        locs = self._face_locs(rgbdata=rgbdata)
        encodings = self._face_encode(rgbdata=rgbdata, locations=locs)
        return locs, encodings

    def write_data(self, encodefile=None, encodes=None, names=None):
        if encodefile is None:
            encodefile = self.outpath
        data = {"encodings": encodes, "names": names}
        fileno = open(encodefile, "wb")
        fileno.write(pickle.dumps(data))
        fileno.close()

    def read_data(self, encodefile=None):
        encodefile = encodefile if encodefile else self.encodefile
        data = pickle.loads(open(encodefile, "rb").read())
        return data

    @staticmethod
    def _get_name(matches, data):
        matchidxs = [i for (i, b) in enumerate(matches) if b]
        counts = {}
        for i in matchidxs:
            name = data["names"][i]
            counts[name] = counts.get(name, 0) + 1
        name = max(counts, key=counts.get)
        return name

    def match_face(self, encodings, data):
        names = []
        for encode in encodings:
            matches = fr.compare_faces(known_face_encodings=data["encodings"],
                                       face_encoding_to_check=encode,
                                       tolerance=self.tolerance)
            name = "Unknown"
            if True in matches:
                name = self._get_name(matches=matches, data=data)
            names.append(name)
        return names
