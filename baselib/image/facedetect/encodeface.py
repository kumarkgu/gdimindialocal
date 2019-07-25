from .baseface import BaseFaceOperation


class EncodeFace(BaseFaceOperation):
    def __init__(self, encodefile, imagefile=None, model=None):
        self.model = model if model else "hog"
        if not imagefile:
            super(EncodeFace, self).__init__(model=model, encodefile=encodefile)
        else:
            super(EncodeFace, self).__init__(model=model, encodefile=encodefile,
                                             imagefile=imagefile
                                             )
        self.rgbdata = None
        self.knownencode = []
        self.knownname = []

    def readimage(self, imagefile=None):
        if not imagefile:
            imagefile = self.imagefile
        image, rgbdata = self.read_image(imagefile=imagefile)
        self.rgbdata = rgbdata
        return rgbdata

    def encode_image(self, rgbdata=None, imagefile=None):
        if rgbdata is None:
            rgbdata = self.rgbdata
        if imagefile is None:
            imagefile = self.imagefile
        name = self.get_names(imagefile)
        locs, encodings = self.encode_face(rgbdata=rgbdata)
        for encoding in encodings:
            self.knownencode.append(encoding)
            self.knownname.append(name)
