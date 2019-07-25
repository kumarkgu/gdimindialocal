from .baseface import BaseFaceOperation
import cv2


class RecogFace(BaseFaceOperation):
    def __init__(self, encodefile, checkfile=None, model=None, tolerance=None):
        self.model = model if model else "hog"
        if not checkfile:
            super(RecogFace, self).__init__(model=model, tolerance=tolerance,
                                            encodefile=encodefile)
        else:
            super(RecogFace, self).__init__(model=model, tolerance=tolerance,
                                            encodefile=encodefile,
                                            imagefile=checkfile)
        self.image = None
        # self.boxes = None
        self.rgbdata = None
        self.encodings = None

    def readimage(self, checkfile=None):
        if not checkfile:
            checkfile = self.imagefile
        image, rgbdata = self.read_image(imagefile=checkfile)
        self.rgbdata = rgbdata
        self.image = image
        return rgbdata

    def encode_image(self, rgbdata=None):
        if not rgbdata:
            rgbdata = self.rgbdata
        locs, encodings = self.encode_face(rgbdata=rgbdata)
        return locs, encodings

    @staticmethod
    def draw_box(locations, names, image):
        for ((top, right, bottom, left), name) in zip(locations, names):
            cv2.rectangle(img=image, pt1=(left, top), pt2=(right, bottom),
                          color=(0, 255, 0), thickness=2)
            yaxis = top - 15 if top > 15 else top + 15
            cv2.putText(img=image, text=name, org=(left, yaxis),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5,
                        color=(0, 255, 0), thickness=2)

    @staticmethod
    def show_image(image):
        cv2.imshow("Image", image)
        cv2.waitKey(0)

    # def match_face(self, data, encodings=None, image=None, boxes=None):
    #     names = []
    #     if not encodings:
    #         encodings = self.encodings
    #     for encoding in encodings:
    #         # matches = fr.compare_faces(data["encodings"], encoding)
    #         matches = fr.compare_faces(known_face_encodings=data["encodings"],
    #                                    face_encoding_to_check=encoding,
    #                                    tolerance=0.5)
    #         name = "Unknown"
    #         if True in matches:
    #             matchidxs = [i for (i, b) in enumerate(matches) if b]
    #             counts = {}
    #             for i in matchidxs:
    #                 name = data["names"][i]
    #                 counts[name] = counts.get(name, 0) + 1
    #             name = max(counts, key=counts.get)
    #         names.append(name)
    #     if not image:
    #         image = self.image
    #     if not boxes:
    #         boxes = self.boxes
    #     for ((top, right, bottom, left), name) in zip(boxes, names):
    #         # draw the predicted face name on the image
    #         cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
    #         y = top - 15 if top - 15 > 15 else top + 15
    #         cv2.putText(image, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
    #                     0.75, (0, 255, 0), 2)
    #     # show the output image
    #     cv2.imshow("Image", image)
    #     cv2.waitKey(0)
