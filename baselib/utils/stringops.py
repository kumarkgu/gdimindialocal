from unidecode import unidecode
from typing import Pattern
import re
import string as strn


def clean_string(string, replace=None, multispace=None,
                 replacement=None, ifstrip=False):
    multispace = multispace if multispace else re.compile(r'\s+')
    replace = replace if replace else ",_-: /\\"
    # string = string.strip(replace)
    if replacement is not None:
        rplchar = "".join([replacement for x in range(0, len(replace))])
        tab = str.maketrans(replace, rplchar)
    else:
        tab = str.maketrans(dict.fromkeys(replace))
    string = string.translate(tab)
    string = multispace.sub(' ', string)
    if ifstrip:
        string = string.strip()
    return string


def clean_query(query, replstr=" "):
    query = query.replace('\n', ' ')
    query = query.replace('\r', ' ')
    query = re.sub(r"\s+", replstr, query)
    return query.strip()


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


def split_string(string, sep=None, prename=None, postname=None):
    prename = "" if prename is None else prename
    sep = "," if sep is None else sep
    postname = "" if postname is None else postname
    tname = ["{0}{1}{2}".format(prename, x.strip(), postname)
             for x in string.split(sep)]
    return tname


def stringyfy_string(string, sep=None, prename=None, postname=None):
    prename = "" if prename is None else prename
    sep = "," if sep is None else sep
    postname = "" if postname is None else postname
    tname = ["'{0}{1}{2}'".format(prename, x.strip(), postname)
             for x in string.split(sep)]
    return sep.join(tname)


def middle_string(string):
    regexp = re.compile(r"([{(\[\"'])(.*)([})\]\"'])")
    regmatch = regexp.match(string)
    retstring = string
    if regmatch:
        retstring = regmatch.group(2)
    return retstring


def listify_data(data, islist=False, issplit=False, sep=","):
    if islist:
        try:
            assert isinstance(data, list)
            return data
        except AssertionError:
            if issplit:
                t_list = split_string(data, sep=sep)
                return t_list
            else:
                return [data]
    else:
        return data


class StripComments:
    _LITERAL_1 = r"('[^\n\r']*')"
    _LITERAL_2 = r'("[^\n\r"]*")'
    _MULTILINE_1 = r"(/(?!\\)\*[\s\S]*?\*(?!\\)/)"
    _SINGLELINE1 = r"(--[^\n\r]*$)"
    _SINGLELINE2 = r"(//[^\n\r]*$)"
    _SINGLELINE3 = r"(#[^\n\r]*$)"

    def __init__(self, lang='SQL'):
        self.language = lang
        self.languagefunc = {
            "sql": "_sqlserver_regex",
            "c++": "_cplusplus_regex"
        }
        self.regmulti = None
        self.regsingle = None
        self.number = None
        self._get_regex(lang=lang)

    def _get_regex(self, lang):
        match = 0
        for key, value in self.languagefunc.items():
            if key.lower() == lang.lower():
                funcname = getattr(StripComments, value)
                retval = funcname()
                self.number = retval[0]
                strlit = retval[1]
                if retval[2]:
                    self.regsingle = re.compile(strlit + r"|" + retval[2],
                                                re.IGNORECASE)
                if retval[3]:
                    self.regmulti = re.compile(strlit + r"|" + retval[3],
                                               re.IGNORECASE|re.MULTILINE)
                match = 1
                break
        if match == 0:
            raise KeyError("Language: {} specified is not defined".format(lang))

    @staticmethod
    def _sqlserver_regex():
        return [1, StripComments._LITERAL_1, StripComments._SINGLELINE1,
                StripComments._MULTILINE_1]

    @staticmethod
    def _cplusplus_regex():
        strlit = StripComments._LITERAL_2 + r"|" + StripComments._LITERAL_1
        return [2, strlit, StripComments._SINGLELINE2,
                StripComments._MULTILINE_1]

    @staticmethod
    def _python_regex():
        strlit = StripComments._LITERAL_2 + r"|" + StripComments._LITERAL_1
        return [1, strlit, StripComments._SINGLELINE3]

    @staticmethod
    def _remove_string(string, regex):
        for grep in regex.findall(string=string):
            string = string.replace(grep[1], '')
        return string

    def remove_string(self, string, regex, sep="\n", method=None):
        if not method:
            string = self._remove_string(string=string, regex=regex)
        else:
            strlist = listify_data(string, islist=True, issplit=True, sep=sep)
            retlist = []
            for strline in strlist:
                retlist.append(self._remove_string(string=strline, regex=regex))
            string = "\n".join(retlist)
        return string
