import os
from base.utils import base_util as bu
from base.utils import Logger as lo
from base.utils import fileobjects as fo


class RunProcess:
    def __init__(self, processname, homepath=None, projpath=None, utilpath=None,
                 sourcepath=None, log=None):
        self.processname = processname
        self.currentuser = bu.current_user()
        self.homepath = self._set_home_path(homepath=homepath)
        self.toppath = os.path.join(self.homepath, projpath)
        self.sourcepath = sourcepath if sourcepath else os.path.join(
            self.homepath,
            "/Box Sync/{0}/Unprocessed".format(self.processname)
        )
        (
            self.temppath, self.logpath, self.rawpath, self.procpath,
            self.errorpath
        ) = self._set_paths()
        self.log = lo.Logger(self.processname).getlog() if not log else log
        self.utilpath = utilpath if utilpath else os.path.join(
            self.homepath,
            "Softwares"
        )

    def _set_home_path(self, homepath=None):
        return homepath if homepath else "C:/Users/{}".format(self.currentuser)

    def _set_paths(self):
        return (
            "{0}/temp/{1}".format(
                self.homepath,
                self.processname
            ),
            os.path.join(self.toppath, "log"),
            os.path.join(self.toppath, "rawfiles"),
            os.path.join(self.toppath, "processed"),
            os.path.join(self.toppath, "errorfiles")
        )

    def build_process_directory(self, basedir=False, logdir=False, rawdir=False,
                                processdir=False, errordir=False, tempdir=False
                                ):
        if basedir:
            fo.create_dir(self.toppath)
        if logdir:
            fo.create_dir(self.logpath)
        if tempdir:
            fo.create_dir(self.temppath)
        if rawdir:
            fo.create_dir(self.rawpath)
        if processdir:
            fo.create_dir(self.procpath)
        if errordir:
            fo.create_dir(self.errorpath)

    def copy_rawfiles(self, sourcefiles=True):
        if not sourcefiles:
            return
        fo.copy_tree_1level(self.sourcepath, self.rawpath)

    def get_subdirectory(self, directory):
        return fo.get_subdirectory(directory)

    def get_files(self, directory, full=False):
        return fo.get_files(dirname=directory, full=full)

    def create_dir(self, dirname):
        fo.create_dir(dirname=dirname)

    def remove_dir(self, dirname):
        fo.remove_dir(dirname=dirname)
