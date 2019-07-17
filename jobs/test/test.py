import re
from baselib.utils.Logger import Logger

vline = "(13) Registration Fee as per 1000"
# # __ore = re.compile(r'(^\s+Name.*Village\s*)(:)(\s*\S+.*\s*)$',
#                         re.IGNORECASE)
# __vbegin = "Article"
# __vregex = r"(\(*\d*\)*\s*)(\(*" + re.escape(__vbegin) + r"\)*)(\s+\S+.*)"
# __ore = re.compile(__vregex, re.IGNORECASE)
# mat = re.search(__ore, vline)
# if mat:
#     print("Match")
#     print(mat.group(1))
#     print(mat.group(2))
#     print(mat.group(3))
# else:
#     print("Not Match")


def _get_clean_data(string):
    try:
        string = string.strip()
        string = re.sub(r'\s+', ' ', string)
        string = string.rstrip(':- ')
        return string
    except AttributeError:
        return None


def _get_last_postion(string, currposn):
    __vtemp = string[0:currposn]
    __vposn = __vtemp.rfind(" ")
    return __vposn + 1


def string_strip(string):
    __vstring = string.strip(',()_- ')
    print(__vstring)


def test_run():
    vfirst=vline[0:_get_last_postion(vline, 30)].strip()
    vsecond=vline[_get_last_postion(vline, 30):].strip()
    print("{}, {}".format(vfirst, vsecond))

    vstring = "1) Remarks"
    print(
        "{} : cleaned to : '{}'".format(
            vstring, _get_clean_data(vstring)
        )
    )

    vstring = "1) Remarks :"
    print(
        "{} : cleaned to : '{}'".format(
            vstring, _get_clean_data(vstring)
        )
    )

    vstring = "1) Remarks :-"
    print(
        "{} : cleaned to : '{}'".format(
            vstring, _get_clean_data(vstring)
        )
    )

    vstring = "1) Remarks :-::"
    print(
        "{} : cleaned to : '{}'".format(
            vstring, _get_clean_data(vstring)
        )
    )


def string_regex(string):
    __opattern = re.compile(r'^[\(\s*\)]+([^\s\(\)].*[^\s\(\)])[\s\(\)]*$')
    __omatch = __opattern.search(string)
    if __omatch:
        print(__omatch.group(1))

# # test_run()
# mystring = '()(Property Description)'
# # string_strip(mystring)
# string_regex(mystring)


def test_string(string):
    ore = re.compile(r'12ヶ.*', re.IGNORECASE)
    if ore.search(string):
        print(string)
        # print(digit)


def index_of_list(key, mylist):
    try:
        return mylist.index(key)
    except ValueError:
        return -1

# # test_string('12ヶ月')
# llist = ['Gunjan', 'Kumar', 'Avinash']
# print(index_of_list('Gunjan', llist))


def test(string):
    from baselib.utils import stringops as ts
    value = ts.translate_english(string)
    print(value)

# test('मेस􀅊स')


def test_suppress_error(utilpath=None, pdffile=None, htmldir=None):
    from baselib.pdf import xpdf
    __oxpdf = xpdf.XpdfPdfProcess(utilpath=utilpath)
    # __vboolean = __oxpdf.is_unreadable_pdf(pdffile)
    # print(__vboolean)
    __oxpdf.pdf_to_html(pdffile, htmldir=htmldir)


def test_regexpression():
    from jobs.igr.igrexpressions import IGRExpressions
    passphrase = "This is my message"
    dbname = "DEVELOPMENT_SQL"
    log = Logger("IGR Process").getlog()
    oexpression = IGRExpressions(sectionname=dbname, ishtml=False,
                                 passphrase=passphrase, log=log,
                                 isothers=True)
    # oexpression.test_print()
    print(oexpression.buildingheader)
    print(oexpression.defsectionname)


def test_string_match():
    from baselib.utils import stringops as ts
    strpattern = re.compile(r'(\s*\(*Village\s*Name\)*\s*)(:)(\s*\S+.*\s*)')
    # strpattern = re.compile(r'^\s*\(*(Village\s*Name)\)*\s*:\s*')
    # strpattern = "Village Name: Gunjan Kumar"
    mystring = "Village Name: Gunjan Kumar"
    retdict = ts.match_return_string(mystring, strpattern, position="1,3")
    if retdict is None:
        print("Not Matched")
    else:
        print(retdict)
        retvalue = [v for k, v, in sorted(retdict.items())]
        # retvalue = [v for k, v, in retdict.items()]
        # retdict = retdict[0] if len(retdict) == 1 else retdict
        print(retvalue)


def test_lpad():
    from baselib.utils import stringops as ts
    string = 555555555
    string = ts.lpad(string, 5, "0")
    print(string)


def test_string_1():
    key = "002:00130"
    print(key.split(":")[1].lstrip("0"))


def gdim_column(gdim_type, column=None, prefix='gdim', default=None):
    """Returns a column value."""
    column_name = '{}_{}'.format(prefix, gdim_type)
    column_name = column_name.lower()

    if column is not None:
        # remove pre-existing prefixed column value
        match = re.match(r'{}_\w+-(.*)'.format(prefix), column)
        if match:
            column = match.groups()[0]

        column_name += '-{}'.format(column)
    elif default is not None:
        column_name += '_{}'.format(default)
    return column_name


def test_regex_mrms(string=None):
    reg = re.compile(r'^\s*M[rs]\.?\s+.*', re.IGNORECASE)
    if reg.search(string):
        print("Pattern Match. True. String: {}".format(string))
    else:
        print("ERROR: Pattern Does not match. String: {}".format(string))


def test_regex_mr_s(string=None):
    # reg = re.compile(r'^\s*Mr[s]?\.?\s+.*', re.IGNORECASE)
    reg = re.compile(r'^\s*Mr[s]?\.?\s+.*', re.IGNORECASE)
    if reg.search(string):
        print("Pattern Match. True. String: {}".format(string))
    else:
        print("ERROR: Pattern Does not match. String: {}".format(string))


def test_regex_test(string=None):
    reg = re.compile(r'(?i)^(.*\s+TEST|TEST\s+.*|\s*TEST\s*)$')
    if reg.search(string):
        print("Pattern Match. True. String: {}".format(string))
    else:
        print("ERROR: Pattern Does not match. String: {}".format(string))


def test_regex_http(string=None):
    reg = re.compile(r'(?i)(.*http[s]?:\/\/.*)')
    if reg.search(string):
        print("Pattern Match. True. String: {}".format(string))
    else:
        print("ERROR: Pattern Does not match. String: {}".format(string))


def check_tilda_operator(string):
    if ~string.isnull():
        print("String is Not Null")
    else:
        print("String is null")


# heck_tilda_operator()
# check_tilda_operator()


test_regex_http('https://kemplaw.com.au/')
# test_regex_http('http://kemplaw.com.au/')
# test_regex_http('HTTPS://KEMPLAW.COM.AU.CASES/')
# test_regex_http('HTTP://kemplaw.com.au.CASE/')
# test_regex_test('R7 Test')

# test_regex_test('ITS Testing Services (M) Sdn Bhd')
# test_regex_test('Secret Company A (TEST) Secret Company A (TEST) Secret Company A (TEST) Secret Company A (TEST)')
# test_regex_test('Tescom Software Systems Testing Pte Ltd')
# test_regex_test('CRM Support Test Record for SSO CV')
# test_regex_test('ITS Testing Services (M) Sdn Bhd')
# test_regex_test('Test CHM Account')
# test_regex_test('Test')
# test_regex_test('CRM Support Test Record for SSO CV')

# gdim_column(gdim_type='copy', column='KnownAs')

# test_regex_mrms("My Name is Gunjan")
# test_regex_mrms("Mr Name is Kumar")
# test_regex_mrms("Mr. Name is Dot")
# test_regex_mrms("Ms Name is Miss")
# test_regex_mrms("Mr. Name is Miss Dot")

# test_regex_mr_s("Mr Name is Gunjan")
# test_regex_mr_s("Mr. Name is later dot")
# test_regex_mr_s("Mrs Name is Misses")
# test_regex_mr_s("Mrs. Name is dot after misses")


# vutil = "C:/Users/gunjan.kumar/Softwares/xpdf/bin64"
# vpdf = "C:/Users/gunjan.kumar/temp/igr/IGR2018_5_9.pdf"
# vhtml = "C:/Users/gunjan.kumar/temp/igr/html2"
# test_suppress_error(vutil, vpdf, vhtml)

# test_regexpression()
# test_string_match()
# test_lpad()
# test_string_1()