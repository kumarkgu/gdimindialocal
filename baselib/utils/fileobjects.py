import os
import shutil
import glob
import datetime
import time
from baselib.utils import dateops as dops


def checkfile(func):
    def inner(path):
        if os.path.isfile(path):
            return func(path)
        else:
            raise OSError
    return inner


def checkdir(func):
    def check(*args, **kwargs):
        for t_dir in args:
            if not os.path.isdir(t_dir):
                raise OSError("Directory: {} does not exists".format(t_dir))
        for key, value in kwargs.items():
            if not os.path.isdir(value):
                raise OSError("Directory: {} does not exists".format(value))
        return func(*args, **kwargs)
    return check


def create_dir(dirname, exist_ok=True):
    os.makedirs(dirname, exist_ok=exist_ok)


def remove_dir(dirname):
    shutil.rmtree(dirname, ignore_errors=True)


def get_subdirectory(dirname, full=False):
    fullname = dirname + "/" if full else ""
    return [fullname + name for name in os.listdir(dirname)
            if os.path.isdir(os.path.join(dirname, name))]


def get_files(dirname, full=False):
    fullname = dirname + "/" if full else ""
    return [fullname + name for name in os.listdir(dirname)
            if os.path.isfile(os.path.join(dirname, name))]


def copy_file(sourcefile, destination, isdstfile=False):
    try:
        if not isdstfile:
            shutil.copy2(sourcefile, destination)
        else:
            shutil.copyfile(sourcefile, destination)
    except FileNotFoundError:
        if not isdstfile:
            create_dir(destination)
            shutil.copy2(sourcefile, destination)
        else:
            create_dir(os.path.dirname(destination))
            shutil.copyfile(sourcefile, destination)


def move_file(sourcefile, destination):
    try:
        shutil.move(sourcefile, destination)
    except FileNotFoundError:
        create_dir(destination)
        shutil.move(sourcefile, destination)
    except shutil.Error:
        pass


def isdirectory(dirname):
    return os.path.isdir(dirname)


def remove_file(filename):
    try:
        os.remove(filename)
    except OSError:
        pass


def get_base_filename(filename):
    basefile = os.path.basename(filename)
    filewoext = basefile.rsplit('.', 1)[0]
    return filewoext


@checkdir
def copy_tree_1level(source, destination):
    allsubdirs = get_subdirectory(source)
    create_dir(destination)
    for subdir in allsubdirs:
        sourcedir = os.path.join(source, subdir)
        targetdir = os.path.join(destination, subdir)
        if os.path.isdir(targetdir):
            remove_dir(targetdir)
        try:
            shutil.copytree(sourcedir, targetdir)
        except Exception as e:
            print("ERROR: {}".format(str(e)))
            raise


def get_file_lists(source, extn=None):
    filelist = []
    extension = "*." + extn if extn else "*.*"
    for filename in glob.glob(source + "/" + extension):
        filelist.append(filename)
    return filelist


def make_base_dir(filename, exist_ok=True):
    dirname = os.path.basename(filename)
    create_dir(dirname=dirname, exist_ok=exist_ok)


def file_stat(filename):
    (mode, ino, dev, nlink, uid, gid,
     size, atime, mtime, ctime) = os.stat(filename)
    retdict = dict({
        "mode": mode,
        "inode": ino,
        "device": dev,
        "hardlinks": nlink,
        "userid": uid,
        "groupid": gid,
        "filesize": size,
        "accesstime": atime,
        "modifiedtime": mtime,
        "createtime": ctime
    })
    return retdict


def file_last_dropped(dir, timediff=None):
    tmobj = dops.TimeConversion()
    timediff = timediff if timediff else "30min"
    agotime = tmobj.timedifftotime(timediff=timediff, convertto="sec")
    currtime = time.time()
    retlist = []
    for root, dirs, files in os.walk(dir):
        for fname in files:
            try:
                files = os.path.join(root, fname)
                if currtime - os.stat(files).st_mtime < agotime:
                    retlist.append(files)
            except FileNotFoundError:
                pass
    return retlist


def get_all_files(path, extensions=None):
    if extensions:
        try:
            assert isinstance(extensions, list)
        except AssertionError:
            raise AssertionError("File Extenions are not in a list")
    else:
        extensions = ["*.*"]
    allfiles = []
    for extension in extensions:
        allfiles.extend(glob.glob("{}/{}".format(path, extension)))
    return allfiles


class FileWatcher:
    def __init__(self, path, timetype=None, filename=None):
        self.path = path
        self.times = self._convert_time(timetype)
        pass

    @staticmethod
    def _convert_time(timetype=None):
        return 1

    def reset_vals(self):
        pass