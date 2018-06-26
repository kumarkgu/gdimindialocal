import sys
import os
try:
    import pwd
except ImportError:
    import getpass
    pwd = None


# Get the path separator as it varies from system to system
def get_path_separator():
    pathsep = "/"
    if sys.platform == "linux" or sys.platform == "linux2":
        pathsep = "/"
    elif sys.platform == "win32":
        pathsep = "\\"
    elif sys.platform == "cygwin":
        pathsep = "/"
    elif sys.platform == "darwin":
        pathsep = "/"
    return pathsep


# Get the current user name
def current_user():
    if pwd:
        return pwd.getpwuid(os.geteuid()).pw_name
    else:
        return getpass.getuser()


def delete_dict_keys(dictname, deletekeys=None):
    delkeys = []
    if not deletekeys:
        for keys in dictname:
            delkeys.append(keys)
    else:
        delkeys = deletekeys
    try:
        for keys in delkeys:
            if keys in dictname:
                del dictname[keys]
    except Exception:
        pass
    return dictname
