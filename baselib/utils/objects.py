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


def change_case(titem, ccase="Lower"):
    def _ccase(string, ccase="Lower"):
        if ccase.lower() == "lower":
            return string.lower().strip()
        else:
            return string.upper().strip()

    try:
        assert isinstance(titem, dict)
        ctype = "dict"
    except AssertionError:
        try:
            assert isinstance(titem, list)
            ctype = "list"
        except AssertionError:
            ctype = "string"
    if ctype == "dict":
        tobj = {_ccase(k, ccase): v for k, v in titem.items()}
    elif ctype == "list":
        tobj = [_ccase(x, ccase) for x in titem]
    else:
        tobj = _ccase(titem, ctype)
    return tobj
