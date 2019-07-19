class SPCoEError(Exception):
    pass


class InvalidHeaderDataFormat(SPCoEError):
    def __init__(self, message, errno=-19001):
        self.message = message
        self.errono = errno
        super(InvalidHeaderDataFormat, self).__init__(message, errno)


class NoUserNamePassword(SPCoEError):
    def __init__(self, message, errno=-19002):
        self.message = message
        self.errono = errno
        super(NoUserNamePassword, self).__init__(message, errno)
