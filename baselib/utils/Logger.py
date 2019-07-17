import logging


class Logger:
    def __init__(self, appname):
        self.app = appname
        self.log = None
        self.handler = None
        self.formatter = None
        self._setlog()

    def _setlog(self):
        self.log = logging.getLogger(self.app)
        self.log.setLevel(logging.INFO)
        self.handler = logging.StreamHandler()
        self.handler.setLevel(logging.INFO)
        self.formatter = logging.Formatter(
            '%(asctime)s\t%(levelname)s - %(filename)s:%(lineno)s - %(message)s'
        )
        self.handler.setFormatter(self.formatter)
        self.log.addHandler(self.handler)

    def getlog(self):
        return self.log
