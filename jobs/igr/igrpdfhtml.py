import re
import glob
import os
from bs4 import BeautifulSoup
from jobs.igr.igrpdf import IgrPdfCommonProcessing
from base.utils import tdim_string as ts
from base.utils import fileobjects as fo
from base.pdf import xpdf


class XPdfHtml:
    def __init__(self, utilpath, pdffile=None, htmldir=None, headermap=None,
                 defsectionname=None, allheaders=None, regexpclass=None,
                 log=None):
        self.xpdf = xpdf.XpdfPdfProcess(utilpath=utilpath, log=log)
        self.pdffile = pdffile
        self.filereg = re.compile(r'page(\d+)\.html')
        self.pxreg = re.compile(r'\D*(\d+)px', re.IGNORECASE)
        self.igr = IgrPdfCommonProcessing(
            defsectionname=defsectionname,
            headermap=headermap,
            ishtml=True,
            allheaders=allheaders,
            regexpclass=regexpclass
        )
        self.htmldir = htmldir

    def reset_filedir(self, pdffile=None, htmldir=None):
        self.pdffile = pdffile if pdffile else self.pdffile
        self.htmldir = htmldir if htmldir else self.htmldir

    def _get_html_files(self):
        templist = []
        filelist = []
        for files in glob.glob(self.htmldir + "/page*.html"):
            basefile = os.path.basename(files)
            match = self.filereg.search(basefile)
            if match:
                templist.append(int(match.group(1)))
        templist.sort()
        for currnumber in templist:
            filelist.append(
                "{0}/page{1}.html".format(self.htmldir, str(currnumber))
            )
        return filelist

    @staticmethod
    def _fill_key_value(line, key, odict):
        for keys in line["style"].split(";"):
            vallist = keys.strip().split(":")
            if vallist[0] == key:
                odict[key] = vallist[1]
                break
        return odict

    @staticmethod
    def _get_key_value(line, key):
        for keys in line["style"].split(";"):
            vallist = keys.strip().split(":")
            if vallist[0] == key:
                return vallist[1]
        return None

    @staticmethod
    def _check_header_cont(tdict, headfont=None, headleft=None):
        if headfont and headfont != "":
            if tdict["font-size"] == headfont:
                if headleft and headleft != "":
                    if tdict["left"] == headleft:
                        return True
                else:
                    return True
        return False

    def sort_files_data(self, files, parser):
        keys = ["top", "left"]
        filedict = {}
        for filename in files:
            soup = BeautifulSoup(open(filename, encoding='utf-8'), parser)
            alldivs = soup.findAll('div', {'class': 'txt'})
            match = self.filereg.search(filename)
            if match:
                filenumber = match.group(1).rjust(3, "0")
                for t_div in alldivs:
                    key = filenumber
                    for t_key in keys:
                        value = self._get_key_value(t_div, t_key)
                        match = self.pxreg.search(value)
                        value = match.group(1) if match else "0"
                        key += value.rjust(5, "0")
                    filedict[key] = t_div
        return filedict

    def process_html_file(self, htmldir=None, parser=None):
        datadict = {}
        if htmldir:
            self.reset_filedir(htmldir=htmldir)
        filelist = self._get_html_files()
        parser = parser if parser else 'html.parser'
        sectionflag = 0
        headersection = 0
        datasection = 0
        headerfont = ""
        headerleft = ""
        data = None
        head = None
        filedata = self.sort_files_data(filelist, parser=parser)
        # for t_file in filelist:
        #     soup = BeautifulSoup(open(t_file, encoding='utf-8'), parser)
        #     alldivs = soup.findAll('div', {'class': 'txt'})
        #     for t_divs in alldivs:
        for t_key, t_divs in sorted(filedata.items()):
            # t_dict = {}
            # self._fill_key_value(t_divs, "left", t_dict)
            t_dict = {"left": t_key[8:]}
            allspan = t_divs.findAll('span')
            for currspan in allspan:
                self._fill_key_value(currspan, "font-size", t_dict)
                t_dict["value"] = currspan.string.strip()
                if self.igr.empty_ignore_string(t_dict["value"]):
                    continue
                if sectionflag == 0:
                    head = self.igr.check_section_match(t_dict["value"])
                    if head:
                        head = self.igr.clean_header(
                            head, additional_clean=True
                        )
                        sectionflag = 1
                        continue
                if sectionflag == 0:
                    continue
                if sectionflag == 1:
                    self.igr.set_head_data(
                        head, t_dict["value"], datadict, True
                    )
                    head = ""
                    sectionflag = 2
                elif sectionflag == 2:
                    tempvalue = t_dict["value"]
                    if not ts.isenglish(t_dict["value"]):
                        engdata = ts.extract_english(t_dict["value"])
                    else:
                        engdata = t_dict["value"]
                    if len(engdata) <= 0:
                        continue
                    if headersection == 0 and datasection == 0:
                        beginlist = self.igr.check_begin(engdata)
                        if not beginlist[0]:
                            continue
                        head = beginlist[1]
                        headerfont = t_dict["font-size"]
                        headerleft = t_dict["left"]
                        headersection = 1
                    else:
                        if self.igr.check_header(engdata):
                            self.igr.set_head_data(
                                head, data, datadict
                            )
                            headerfont = t_dict["font-size"]
                            headerleft = t_dict["left"]
                            head = engdata
                            data = ""
                            headersection = 1
                            datasection = 0
                        else:
                            if self._check_header_cont(t_dict, headerfont,
                                                       headerleft):
                                head += " " + engdata
                                headersection = 1
                                datasection = 0
                            else:
                                if datasection == 0:
                                    data = tempvalue
                                else:
                                    data += " " + tempvalue
                                headersection = 0
                                datasection = 1
        self.igr.set_head_data(
            head, data, datadict
        )
        return datadict

    def process(self, pdffile, temppath):
        if not self.igr.check_readable_pdf(self.xpdf, pdffile):
            raise xpdf.PDFUnreadableFont(
                "PDF: {} is unreadable".format(pdffile)
            )
        #  Copy the file to the temp directory
        tempfile = self.igr.copy_to_temp(pdffile, temppath)
        dirname = os.path.dirname(tempfile)
        htmldir = os.path.join(dirname, "html")
        fo.remove_dir(htmldir)
        self.reset_filedir(pdffile=tempfile, htmldir=htmldir)
        try:
            self.xpdf.pdf_to_html(tempfile, htmldir=htmldir)
            datadict = self.process_html_file(htmldir)
            fo.remove_dir(htmldir)
            fo.remove_file(tempfile)
        except Exception as e:
            fo.remove_dir(htmldir)
            fo.remove_file(tempfile)
            raise e
        return datadict
