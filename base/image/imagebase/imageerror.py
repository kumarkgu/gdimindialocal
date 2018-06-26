class BaseImageErr(Exception):
    pass


class ImageCV2Err(BaseImageErr):
    def __init__(self, message, errno=-16001):
        self.message = message
        self.errono = errno
        super(ImageFileNotReadErr, self).__init__(message, errno)


class ImageFileNotReadErr(BaseImageErr):
    def __init__(self, message, errno=-16002):
        self.message = message
        self.errono = errno
        super(ImageFileNotReadErr, self).__init__(message, errno)


class ImageOrImageFileNotValidErr(BaseImageErr):
    def __init__(self, message, errno=-16003):
        self.message = message
        self.errono = errno
        super(ImageOrImageFileNotValidErr, self).__init__(message, errno)


class ImageBlurrErr(BaseImageErr):
    def __init__(self, message, errno=-16004):
        self.message = message
        self.errno = errno
        super(ImageBlurrErr, self).__init__(message, errno)
