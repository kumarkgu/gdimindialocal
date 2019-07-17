import os
from baselib.utils import fileobjects as fo


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


@checkdir
def copy_tree(source, destination, log=None):
    for dirs in [source, destination]:
        print("Processing: {}".format(dirs))
        allsubs = fo.get_subdirectory(dirs)
        for subdir in allsubs:
            print("....Subdirectory: {}".format(subdir))

source = "C:/Users/gunjan.kumar/Box Sync/ResearchData/IGRData/Unprocessed"
target = "C:/Users/gunjan.kumar/Documents/JLL/Projects/Research/IGR/process/processed"
copy_tree(source=source, destination=target)

