import sys
import os
import functools

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


def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))


def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)


def get_rattr(obj, schema):
    attrlist = {}
    singleval = ["scalar", "value", "string", "number"]
    try:
        for key, value in schema.items():
            if value["Type"].lower() in singleval:
                attrlist[key] = rgetattr(obj, value["Attribute"])
            else:
                listdetail = []
                for items in rgetattr(obj, value["Attribute"]):
                    listdetail.append(get_rattr(items, value["Subattribute"]))
                attrlist[key] = listdetail
        return attrlist
    except AttributeError as aerr:
        print(aerr)


def repeat_string(string, repeat=1, until=True):
    _repeat = 1 if repeat > 0 else 0
    if until:
        return (string * (repeat // len(string) + _repeat))[:repeat]
    else:
        return string * repeat
