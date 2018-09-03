import os
import shutil


def checkfile(func):
    def inner(path):
        if os.path.isfile(path):
            return func(path)
        else:
            raise OSError
    return inner


def checkdir(func):
    def check(*args, **kwargs):
        for dir in args:
            if not os.path.isdir(dir):
                raise OSError("Directory: {} does not exists".format(dir))
        for key, value in kwargs.items():
            if not os.path.isdir(value):
                raise OSError("Directory: {} does not exists".format(value))
        return func(*args, **kwargs)
    return check


def create_dir(dirname):
    os.makedirs(dirname, exist_ok=True)


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


def copy_file(sourcefile, destination):
    try:
        shutil.copy2(sourcefile, destination)
    except FileNotFoundError:
        create_dir(destination)
        shutil.copy2(sourcefile, destination)


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
def copy_tree_1level(source, destination, log=None):
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
