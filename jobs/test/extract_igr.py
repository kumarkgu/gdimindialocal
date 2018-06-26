import os
import re
import shutil
from typing import Pattern

from base.pdf import xpdf as pdf
from base.utils import Logger as lo
from base.utils import base_util as bu
from base.utils import excelprocess as ep
from base.utils import fileobjects as fo


# "/Documents/JLL/Projects/Research/IGR/process"
class ProcessIgr:
    def __init__(self, log=None, homepath=None, projpath=None, utilpath=None,
                 boxpath=None, sectionmatch=None, headermap=None):
        self.currentuser = bu.current_user()
        self.homepath = self._set_home_path(homepath=homepath)
        self.toppath = os.path.join(self.homepath, projpath)
        self.sectionmatch = sectionmatch
        self.headermap = headermap
        pathvar = utilpath if utilpath else os.path.join(
            self.homepath,
            "Softwares/xpdf/bin64"
        )
        self.xpdf = pdf.XpdfPdfProcess(pathvar)
        self.boxpath = boxpath if boxpath else os.path.join(
            self.homepath,
            "/Box Sync/ResearchData/IGRData/Unprocessed"
        )
        (
            self.temppath, self.logpath, self.rawpath,self.procpath,
            self.errorpath
        ) = self._set_paths()
        self.log = log
        self.fileobjects = fo.FileProcess()
        self._set_regex_patterns()

    def _set_home_path(self, homepath=None):
        return homepath if homepath else "C:/Users/{}".format(self.currentuser)

    def _set_paths(self):
        return (
            self.homepath + "/temp/igr",
            os.path.join(self.toppath, "log"),
            os.path.join(self.toppath, "rawfiles"),
            os.path.join(self.toppath, "processed"),
            os.path.join(self.toppath, "errorfiles")
        )

    def _set_regex_patterns(self):
        __lbegin = ["Type of document (Title)", "Type of document", "Article",
                    "Title"]
        __lignore = ["https://", "Index-II"]
        self._re_empty = re.compile(r'^\s*$')
        self._re_header = re.compile(r'^(\s*\()(\d+)(\)\s*)(\S*.*)')

        # Set Ignore patterns
        self.ignore_pats = []
        for __vpattern in __lignore:
            self.ignore_pats.append(
                re.compile(
                    r"\s*" + re.escape(__vpattern) + r"\s*"
                )
            )

        # From where the section starts
        self.section_pats = [
            re.compile(r'(^\s*Name.*Village\s*)(:)(\s*\S+.*\s*)',
                       re.IGNORECASE),
            re.compile(r'(^\s*\(*Village\s*Name\)*\s*)(:)(\s*\S+.*\s*)',
                       re.IGNORECASE)
        ]

        # Other headers
        self.header_pats = [
            re.compile(r'(\s*Details\s+taken.*\s*)(:*)([^:]*)',
                       re.IGNORECASE),
            re.compile(r'(\s*Selected.*stamp\s*)(:*)([^:]*)',
                       re.IGNORECASE)
        ]

        # Beginning of the patterns
        self.begin_pats = []
        for __vpattern in __lbegin:
            self.begin_pats.append(
                re.compile(
                    r"(\(*\d*\)*\s*)(\(*" + re.escape(__vpattern) +
                    r"\)*\s*)(\S+.*)",
                    re.IGNORECASE
                )
            )

        self.alternate_begin_pats = [
            re.compile(
                r'(\(\d\)\s*)(\S+.*)', re.IGNORECASE
            )
        ]

        # End of the section
        self.section_end_pats = [
            re.compile(r'^\s*\(14\)\s*', re.IGNORECASE),
            re.compile(r'^\s*Remarks\s*', re.IGNORECASE)
        ]

        self.building_name_header = [
            re.compile(r'.*Land measuring\s*.*portal.*home.*', re.IGNORECASE),
            re.compile(r'.*Property.*Description.*')
        ]

        self.building_name_pats = [
            re.compile(r'(Name of the Building\s*:*\s*)([^,]+)', re.IGNORECASE),
            re.compile(r'(Name of Building\s*:*\s*)([^,]+)', re.IGNORECASE),
            re.compile(r'(Building Name\s*:*\s*)([^,]+)', re.IGNORECASE)
        ]

        self._re_multi_space = re.compile(r'\s+')
        self._re_digit_paran = re.compile(r'^\d\)')
        self._re_head_paran = re.compile(
            r'^[\s*\(\)]+([^\s\(\)].*[^\s\(\)])[\s\(\)]*$'
        )

    def initial_prepare(self):
        # Create directories
        self.fileobjects.create_dir(self.toppath)
        self.fileobjects.create_dir(self.temppath)
        self.fileobjects.create_dir(self.logpath)
        self.fileobjects.create_dir(self.rawpath)
        self.fileobjects.create_dir(self.procpath)
        self.log.info("Copying the Files from Box to Local Location")
        __asrcdir = self.fileobjects.get_subdirectory(self.boxpath)
        for __vsrc in __asrcdir:
            __vsrcdir = os.path.join(self.boxpath, __vsrc)
            __vdstdir = os.path.join(self.rawpath, __vsrc)
            self.log.info("..Directory: {}".format(__vsrcdir))
            if os.path.isdir(__vdstdir):
                self.fileobjects.remove_dir(__vdstdir)
            try:
                shutil.copytree(__vsrcdir, __vdstdir)
            except Exception as e:
                self.log.info("ERROR: {}".format(str(e)))
                raise

    def _clean_string(self, string, additional_clean=False, header=False):
        try:
            string = string.strip()
            # string = re.sub(r'\s+', ' ', string)
            string = self._re_multi_space.sub(' ', string)
            if additional_clean:
                # string = re.sub(r'^\d\)', '', string)
                string = self._re_digit_paran.sub('', string)
                string = string.strip()
            if header:
                # __vmat = re.search(self._re_header, string)
                __vmat = self._re_header.search(string)
                if __vmat:
                    __vstart = __vmat.start(4)
                    string = self._get_header(
                        __vmat.group(2),
                        string[__vstart:]
                    )
                string = string.strip(',_-: /\\')
                __omatch = self._re_head_paran.search(string)
                if __omatch:
                    string = __omatch.group(1)
            return string
        except AttributeError:
            return None

    def _get_last_empty(self, string, position):
        __vtemp = string[0:position]
        __vposn = __vtemp.rfind(" ")
        # This checks if this is stand alone
        __vtemp = string[position:].strip()
        if __vtemp:
            return __vposn + 1
        else:
            return position

    def _get_header(self, indexnumber, string):
        __vstring = string.strip()
        if __vstring:
            return string
        else:
            for key, value in self.sectionmatch.items():
                if key == indexnumber:
                    __vstring = value
                    break
            return __vstring

    def _get_temp_file(self, filename):
        __vbase = os.path.basename(filename)
        __vwoext = __vbase.rsplit('.', 1)[0]
        return os.path.join(
            os.path.dirname(filename),
            __vwoext + ".txt"
        )

    def _check_empty_ignore(self, line):
        # if re.match(self._re_empty, line):
        if self._re_empty.match(line):
            return True
        for __opattern in self.ignore_pats:
            # if re.search(__opattern, line):
            if __opattern.search(line):
                return True
        return False

    def _match_data(self, data, string):
        try:
            assert isinstance(string, Pattern)
            if string.search(data):
                return True
        except AssertionError:
            if data == string:
                return True
        return False

    def _get_modified_head(self, head):
        try:
            for __vkey, __lvalue in self.headermap.items():
                try:
                    assert isinstance(__lvalue, list)
                    for __vvalue in __lvalue:
                        if self._match_data(head, __vvalue):
                            return __vkey
                except AssertionError:
                    if self._match_data(head, __lvalue):
                        return __vkey
        except AttributeError:
            pass
        return head

    def _set_head_data(self, head, data, datadict, additional_clean=False):
        __vhead = self._clean_string(string=head, header=True,
                                     additional_clean=additional_clean)
        __vdata = self._clean_string(string=data,
                                     additional_clean=additional_clean)
        __vhead = self._get_modified_head(__vhead)
        if head:
            # if __vhead == "Date of 14/02/2018 submission":
            #     __vdata = "Test"
            datadict[__vhead] = __vdata
            __lbuilding = []
            for __opattern in self.building_name_header:
                __vmatch = __opattern.search(__vhead)
                if __vmatch:
                    for __obuildpat in self.building_name_pats:
                        for __odatapat in __obuildpat.finditer(__vdata):
                            __lbuilding.append(__odatapat.group(2))
                    break
            if len(__lbuilding) > 0:
                datadict["Building Name"] = ", ".join(__lbuilding)

    def _process_text_file(self, filename):
        self.log.info("    ....Checking if PDF is unreadable")
        __vboolean = self.xpdf.is_unreadable_pdf(filename=filename)
        if __vboolean:
            return None
        self.log.info("    ....Reading and converting file to text")
        self.xpdf.pdf_to_text(filename=filename, outformat="table")
        __vtext = self._get_temp_file(filename=filename)
        self.log.info("    ....Reading converted text file")
        __vlineno = 0
        __vflag = 0
        __vtextpos = 0
        __vmainsecflag = 0
        __dfile = {}
        __vhead = None
        __vdata = None
        with open(__vtext, 'r') as infile:
            for __vline in infile:
                __vboolean = self._check_empty_ignore(__vline)
                if __vboolean:
                    continue
                if __vmainsecflag == 0:
                    __vsec = None
                    for __opattern in self.section_pats:
                        __vsec = __opattern.search(__vline)
                        if __vsec:
                            break
                    if __vsec:
                        __vmainsecflag = 1
                        __vhead = __vsec.group(1)
                        __vdata = __vsec.group(3)
                        self._set_head_data(
                            head=__vhead, data=__vdata, datadict=__dfile,
                            additional_clean=True
                        )
                        __vlineno += 1
                    continue
                if __vmainsecflag == 0:
                    continue
                __vcurrpos = self._get_last_empty(__vline, __vtextpos)
                if __vtextpos > 0:
                    __vmat = self._re_header.search(__vline)
                    if __vmat:
                        self._set_head_data(
                            head=__vhead, data=__vdata, datadict=__dfile
                        )
                        if __vflag == 1:
                            __vflag = 2
                        __vhead = __vline[0:__vcurrpos]
                        __vdata = __vline[__vcurrpos:]
                    else:
                        __vmatch = 0
                        for __opattern in self.header_pats:
                            __vmat = __opattern.search(__vline)
                            if __vmat:
                                self._set_head_data(
                                    head=__vhead, data=__vdata, datadict=__dfile
                                )
                                __vhead = __vline[0:__vcurrpos]
                                __vdata = __vline[__vcurrpos:]
                                __vmatch = 1
                                break
                        if __vmatch == 0:
                            __vhead += " " + __vline[0:__vcurrpos]
                            __vdata += " " + __vline[__vcurrpos:]
                else:
                    for __opattern in self.begin_pats:
                        __vmat = __opattern.search(__vline)
                        if __vmat:
                            __vtextpos = __vmat.start(3)
                            __vhead = __vmat.group(2)
                            __vdata = __vmat.group(3)
                            __vflag = 1
                            break
                    if __vflag == 0:
                        for __opattern in self.alternate_begin_pats:
                            __vmat = __opattern.search(__vline)
                            if __vmat:
                                __vtextpos = __vmat.start(2)
                                __vhead = ""
                                __vdata = __vmat.group(2)
                                __vflag = 1
                                break
        self._set_head_data(
            head=__vhead, data=__vdata, datadict=__dfile
        )
        os.remove(__vtext)
        return __dfile

    def _process_error_path(self, dirpath=None, village=None, filename=None):
        __vdirectory = os.path.join(dirpath, village)
        self.fileobjects.create_dir(__vdirectory)
        return os.path.join(__vdirectory, filename)

    def _process_file(self, filename, directory=None, mode=None):
        __vhtmlpath = os.path.join(self.temppath, "html")
        __vbase = os.path.basename(filename)
        # __vfile = os.path.join(self.temppath, __vbase)
        self.log.info("....Processing File: {}".format(filename))
        self.fileobjects.remove_dir(__vhtmlpath)
        self.fileobjects.copy_file(filename, self.temppath)
        __vcopyfile = os.path.join(self.temppath, os.path.basename(filename))
        __ddata = None
        if mode == "pdftotext":
            try:
                __ddata = self._process_text_file(filename=__vcopyfile)
            except Exception:
                pass
        if __ddata:
            self.log.info("    ....Successfully read file. Cleaning up")
            __vfinaldir = self._process_error_path(
                dirpath=self.procpath, village=directory, filename=__vbase
            )
            shutil.move(filename, __vfinaldir)
            os.remove(__vcopyfile)
            return __ddata
        else:
            self.log.info(
                "    ....Warning: Cannot read PDF file. Possible Text language"
                " not supported")
            __vfinaldir = self._process_error_path(
                dirpath=self.errorpath, village=directory, filename=__vbase
            )
            shutil.move(filename, __vfinaldir)
            os.remove(__vcopyfile)
            return None

    def wrap_process_files(self, mode=None, outputfile=None, errorfile=None,
                           foldername=None, filename=None):
        self.log.info("Started Processing Files")
        if foldername:
            __asubdirs = [foldername]
        else:
            __asubdirs = self.fileobjects.get_subdirectory(self.rawpath)
        if not __asubdirs:
            return False
        __vmode = "pdftotext" if not mode else mode
        __ldata = []
        __owserror = ep.ExcelWorkBook(errorfile, "Error")
        __owsoutput = ep.ExcelWorkBook(outputfile, "Output")
        try:
            for __vd in __asubdirs:
                __vdirec = self.rawpath + "/" + __vd
                self.log.info("..Processing Directory: {}".format(__vdirec))
                if filename:
                    __afiles = [
                        "{0}/{1}/{2}.pdf".format(
                            self.rawpath, foldername, filename
                        )
                    ]
                else:
                    __afiles = self.fileobjects.get_files(__vdirec, full=True)
                for __vfile in __afiles:
                    __ddata = self._process_file(
                        filename=__vfile, directory=__vd, mode=__vmode
                    )
                    __vbase = os.path.basename(__vfile)
                    __vwoext = __vbase.rsplit('.', 1)[0]
                    __lfiledetail = "_".join(__vwoext.split(".")).split("_")
                    if __ddata:
                        __ddata["CTSNo"] = __lfiledetail[1]
                        __ddata["Year"] = __lfiledetail[0][-4:]
                        __ddata["DocumentNo"] = "_".join(__lfiledetail[2:])
                        __ddata["Village"] = __vd
                        __ldata.append(__ddata)
                    else:
                        __ddata = {
                            "CTSNo": __lfiledetail[1],
                            "Year": __lfiledetail[0][-4:],
                            "DocumentNo": "_".join(__lfiledetail[2:]),
                            "Village": __vd
                        }
                        __lerror = __owserror.get_excel_columns([__ddata])
                        __owserror.append_to_ws(__lerror)
                if len(__ldata) > 0:
                    self.log.info("    ....Writing To Excel Sheet")
                    __ldata = __owsoutput.get_excel_columns(__ldata)
                    __owsoutput.append_to_ws(__ldata)
                    __ldata = []
                self.log.info("....Deleting Directory")
                self.fileobjects.remove_dir(__vdirec)
        except Exception as e:
            self.log.info("ERROR: {}".format(str(e)))
        self.log.info("Saving Excel File(s)")
        __owsoutput.save_wb_objects(outputfile)
        __owserror.save_wb_objects(errorfile)


vprojpath = "Documents/JLL/Projects/Research/IGR/process"
vtopfile = "C:/Users/gunjan.kumar/{}".format(vprojpath)
log = lo.Logger("Research IGR Data").getlog()
dsection = {
    "1": "Type of document",
    "2": "Reward",
    "3": "Quotation (details of the lease in relation to the lease, "
         "that the sergeant should specify)",
    "4": "Land measuring, portals and home number (if any)",
    "5": "area",
    "6": "When the levy or connection is given.",
    "9": "Date of the date of the document",
    "10": "The date of registration of the document",
    "11": "serial numbers, volumes and pages",
    "12": "Stamp duty as per market price",
    "13": "Registration Fee as per marketable",
    "14": "Remarks"
}

dmapcolumn = {
    "DocumentType": ["Type of document", "Article", "Title",
                     "Type of document (Title)"],
    "Village Name": ["Name of the village", "Village Name"],
    "Filing Number": ["serial numbers, volumes and pages",
                      "Registration Number / Year",
                      "Registration Number/Year",
                      "Filing No."],
    "Registration Date": ["The date of registration of the document",
                          "Date of Registartion", "Date of filing"],
    "Submission Date": ["Date of the date of the document",
                        "Date of submission", "Date of Execution"],
    "Stamp Duty": [re.compile(r'^Stamp Duty', re.IGNORECASE)],
    "Registration Fee": [re.compile(r'^Registration Fee', re.IGNORECASE)],
    "Area": [re.compile(r'^Area', re.IGNORECASE)],
    "Remarks": [re.compile(r'^Remark', re.IGNORECASE)]
}

oigr = ProcessIgr(log=log, projpath=vprojpath, sectionmatch=dsection,
                  headermap=dmapcolumn)
vfolder = ""
# oigr.initial_prepare()
voutputfile = "{0}/igrdata{1}.xlsx".format(vtopfile, vfolder)
verrorfile = "{0}/igrerror{1}.xlsx".format(vtopfile, vfolder)
oigr.wrap_process_files(outputfile=voutputfile, errorfile=verrorfile)
# oigr.wrap_process_files(outputfile=voutputfile, errorfile=verrorfile,
#                         foldername="Thane", filename="IGR2018_1_3150")



# from base.utils import mailops as mo
# import re
from base.utils import Logger as lo
from base.utils import base_util as bu
from base.websuite import setbrowser as sb
from base.image import imagetxt as it
# from selenium.common.exceptions import NoSuchElementException
# from PIL import Image
# from io import BytesIO
# import base64
# from base.image.imagetxt import ReadImage
# from base.image import imageprocess as ip

# log = lo.Logger("Research IGR Data").getlog()
#
# _DRIVER_PATH = "C:\\Users\\gunjan.kumar\\Documents\\Drivers"
# _CHROME_DRIVER = "chromedriver.exe"
# _IE_DRIVER = "IEDriverServer.exe"
# _BASE_DIR = "C:\\Users\\gunjan.kumar\\Documents\\JLL\\Projects\\Research\\IGR"
# _TEMP_DIR = _BASE_DIR + "\\temp"
# _WEB_SITE = "https://esearchigr.maharashtra.gov.in/testingesearch/Login.aspx"
# _PATH_SEP = bu.get_path_separator()
# _SLEEP_TIME = 2
# _OCR_PATH = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"
#
#
# def _image_to_text(filename):
#     __oocr = it.ReadImage(_OCR_PATH)
#     __vvalue = __oocr.read_image(filename)
#     return __vvalue
#
#
# def _process_initial_page(browser, tempfile):
#     __vuser = input("Enter Username to connect to the site: ")
#     __vpass = input("Enter password for the user on the site: ")
#     __vtry = 1
#     while __vtry < 4:
#         browser.inputdata("txtUserid", __vuser)
#         browser.inputdata("txtPswd", __vpass)
#         browser.take_screenshot("img", imagefile=tempfile, itemno=1,
#                                 xcorr=219, ycorr=84, widthcorr=30,
#                                 heightcorr=10)
#         __vcaptcha = _image_to_text(tempfile)
#         browser.inputdata("txtcaptcha", __vcaptcha)
#         __vtry += 1
#
#
# def process_igr(website, inputfile, outputfile, driver_path=_DRIVER_PATH,
#                 default_driver="Chrome", chromedriver=_CHROME_DRIVER,
#                 iedriver=_IE_DRIVER, pathsep=_PATH_SEP, sleeptime=_SLEEP_TIME
#                 ):
#     try:
#         __obrowse = sb.BrowserOperation(
#             driverdir=driver_path,
#             chromerdriver=chromedriver,
#             pathsep=pathsep
#         )
#         __obrowse.start_webpage(website, sleeptime=sleeptime)
#         # Now fill in the user name and password
#     except:
#         log.info("ERROR: This is the error")
