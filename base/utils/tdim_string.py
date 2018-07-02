from unidecode import unidecode
from typing import Pattern
import re
import string as strn


def clean_string(string, replace=None, multispace=None):
    multispace = multispace if multispace else re.compile(r'\s+')
    string = multispace.sub(' ', string)
    replace = replace if replace else ",_-: /\\"
    string = string.strip(replace)
    string = string.strip()
    return string


def isenglish(string):
    try:
        string.encode('ascii')
    except UnicodeEncodeError:
        return False
    else:
        return True


def translate_english(string):
    return unidecode(str(string))


def extract_english(string, asciireg=None):
    asciireg = asciireg if asciireg else re.compile(r'[^\x00-\x7F]+')
    string = asciireg.sub('', string)
    return string.strip()


def match_string(string, matchpat):
    try:
        assert isinstance(matchpat, Pattern)
        if matchpat.search(string):
            return True
    except AssertionError:
        if string == matchpat:
            return True
    else:
        return False


def match_return_string(string, matchpat, **kwargs):
    try:
        assert isinstance(matchpat, Pattern)
        posn = kwargs.get('position', None)
        match = matchpat.search(string)
        if match:
            if posn is None:
                return match.group(0)
            else:
                matchdict = {}
                try:
                    for curval in posn.split(","):
                        intval = int(curval)
                        key = "{}:{}".format(
                            lpad(curval, 3, "0"),
                            lpad(match.start(intval), 5, "0")
                        )
                        matchdict[key] = match.group(intval)
                except IndexError:
                    pass
                return matchdict
    except AssertionError:
        if string == matchpat:
            return string
    else:
        return None


def initial_captial(string):
    return strn.capwords(string)


def lpad(string, length, char=" "):
    return str(string).rjust(length, char)


def rpad(string, length, char=" "):
    return str(string).ljust(length, char)


def extract_string(string, matchpat=None, grpnumber=None):
    try:
        assert isinstance(string, Pattern)
        t_group = grpnumber if grpnumber else 1
        match = matchpat.search(string)
        if match:
            return match.group(t_group)
    except AssertionError:
        return string
    return None
