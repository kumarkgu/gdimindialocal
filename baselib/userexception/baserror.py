class BaseCOEErr(Exception):
    pass


class FileNotReadErr(BaseCOEErr):
    def __init__(self, message, errno=-16001):
        self.message = message
        self.errono = errno
        super(FileNotReadErr, self).__init__(message, errno)


class CommandNotFound(BaseCOEErr):
    def __init__(self, message, errno=-16002):
        self.message = message
        self.errono = errno
        super(CommandNotFound, self).__init__(message, errno)


# All Image Related Error
class BaseImageErr(BaseCOEErr):
    pass


class ImageCV2Err(BaseImageErr):
    def __init__(self, message, errno=-17002):
        self.message = message
        self.errono = errno
        super(ImageCV2Err, self).__init__(message, errno)


class ImageOrImageFileNotValidErr(BaseImageErr):
    def __init__(self, message, errno=-17003):
        self.message = message
        self.errono = errno
        super(ImageOrImageFileNotValidErr, self).__init__(message, errno)


class ImageBlurrErr(BaseImageErr):
    def __init__(self, message, errno=-17004):
        self.message = message
        self.errno = errno
        super(ImageBlurrErr, self).__init__(message, errno)
