from typing import Pattern


def isgregex(string):
    try:
        assert isinstance(string, Pattern)
        return True
    except AssertionError:
        return False


def isint(string):
    try:
        assert isinstance(string, int)
        return True
    except AssertionError:
        return False


def return_type(string):
    if isint(string):
        return "Int"
    elif isgregex(string):
        return "Pattern"
    else:
        return "String"


def return_list(userobject):
    try:
        assert isinstance(userobject, list)
        return userobject
    except AssertionError:
        return [userobject]

