from bs4 import BeautifulSoup
from base.utils import tdim_string as ts
from base.utils import fileobjects as fo
from base.pdf import xpdf as xpdf
import re
import glob
import os


class IgrPdfCommonProcessing:
    def __init__(self, defsectionname=None, headermap=None, allheaders=None,
                 ishtml=False, regexpclass=None):
        self.ishtml = ishtml
        self.regex = regexpclass
        self.defsectionname = defsectionname
        self.headermap = headermap
        self.allheaders = allheaders

    @staticmethod
    def _get_key_value(valuedict, posn):
        posnvalue = ts.lpad(posn, 3, "0")
        for key, value in valuedict.items():
            if posnvalue == key.split(":")[0]:
                return [value, key.split(":")[1].lstrip("0")]

    def check_section_match(self, string):
        for pattern in self.regex.sectionstart:
            posn = "1" if self.ishtml else "1,3"
            retdict = ts.match_return_string(data=string, string=pattern,
                                             position=posn)
            if retdict:
                retvalue = [v for k, v in sorted(retdict.items())]
                retvalue = retvalue[0] if len(retvalue) == 1 else retvalue
                return retvalue
        return None

    def _check_begin_title(self, string, posn, allpatterns):
        flag = False
        data = None
        textposition = None
        head = ""
        l_place = [int(x) for x in posn.split(",")]
        for pattern in allpatterns:
            retdict = ts.match_return_string(data=string, string=pattern,
                                             position=posn)
            if retdict:
                flag = True
                if len(l_place) > 1:
                    head = self._get_key_value(retdict, l_place[0])[0]
                if not self.ishtml:
                    t_list = self._get_key_value(retdict, l_place[1])
                    textposition = t_list[1]
                    data = t_list[0]
                return [flag, head, data, textposition]
        return [flag]

    def check_begin(self, string):
        posn = "2"
        posn = "2,3".format(posn) if not self.ishtml else posn
        l_return = self._check_begin_title(string=string, posn=posn)
        if not l_return[0]:
            posn = "2"
            l_return = self._check_begin_title(string=string, posn=posn)
        if self.ishtml:
            return [l_return[0], l_return[1]]
        else:
            return [l_return[0], l_return[1], l_return[2], l_return[3]]

    def get_header(self, indexnumber, string):
        t_string = string.strip()
        if t_string:
            return string
        else:
            for key, value in self.defsectionname.items():
                if key == indexnumber:
                    t_string = value
                    break
            return t_string

    def clean_header(self, header, additional_clean=False):
        if not ts.isenglish(header):
            header = ts.extract_english(header)
        try:
            if additional_clean:
                header = self.regex.digitparan.sub('', header)
                header = header.strip()
            match = self.regex.header.search(header)
            if match:
                startposn = match.start(4)
                header = self.get_header(match.group(2), header[startposn:])
            header = ts.clean_string(header, multispace=self.regex.multispace)
            match = self.regex.headparan.search(header)
            if match:
                header = match.group(1)
            return header
        except AttributeError:
            return None

    def clean_data(self, data, additional_clean=False):
        data = ts.clean_string(data)
        if additional_clean:
            data = self.regex.digitparan.sub('', data)
            data = data.strip()
        return data

    def modify_header_name(self, header):
        try:
            for key, value in self.headermap.items():
                try:
                    assert isinstance(value, list)
                    for t_value in value:
                        if ts.match_string(header, t_value):
                            return key
                except AssertionError:
                    if ts.match_string(header, value):
                        return key
        except AttributeError:
            pass
        return header

    def get_building_name(self, header, value, datadict):
        building = []
        for pattern in self.regex.buildingheader:
            match = pattern.search(header)
            if match:
                for buildpattern in self.regex.buildingname:
                    for builddata in buildpattern.finditer(value):
                        building.append(builddata.group(2))
                break
        if len(building) > 0:
            datadict["Building Name"] = ", ".join(building)

    def check_header(self, string):
        match = self.regex.header.search(string)
        if match:
            return True
        for pattern in self.regex.other_header:
            match = pattern.search(string)
            if match:
                return True
        return False

    def check_multiple_head(self, header):
        data = self.regex.multihead.findall(header)
        if len(data) > 1:
            return True
        return False

    def set_head_data(self, header, value, datadict, additional_clean=False):
        if self.check_multiple_head(header=header):
            raise xpdf.PDFManualProcess(
                "PDF needs Manual Process"
            )
        header = self.clean_header(header, additional_clean=additional_clean)
        value = self.clean_data(value, additional_clean=additional_clean)
        header = self.modify_header_name(header)
        header = ts.initial_captial(header)
        if header:
            datadict[header] = value
            self.get_building_name(header, value, datadict)

    def empty_ignore_string(self, string):
        if self.regex.empty.match(string):
            return True
        for pattern in self.regex.ignore:
            match = pattern.search(string)
            if match:
                return True
        return False

    def check_readable_pdf(self, pdfclass, pdffile):
        return not pdfclass.is_unreadable_pdf(pdffile)

    def copy_to_temp(self, pdffile, temppath):
        fo.copy_file(pdffile, temppath)
        filename = os.path.join(temppath, os.path.basename(pdffile))
        return filename


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

    def _fill_key_value(self, line, key, odict):
        for keys in line["style"].split(";"):
            vallist = keys.strip().split(":")
            if vallist[0] == key:
                odict[key] = vallist[1]
                break
        return odict

    def _get_key_value(self, line, key):
        for keys in line["style"].split(";"):
            vallist = keys.strip().split(":")
            if vallist[0] == key:
                return vallist[1]
        return None

    def _check_header_cont(self, tdict, headfont=None, headleft=None):
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


class XPdfText:
    def __init__(self, utilpath, pdffile=None, textfile=None, regexpclass=None,
                 defsectionname=None, headermap=None, allheaders=None, log=None
                 ):
        self.xpdf = xpdf.XpdfPdfProcess(utilpath=utilpath, log=log)
        self.pdffile = pdffile
        self.textfile = textfile
        self.igr = IgrPdfCommonProcessing(
            defsectionname=defsectionname,
            headermap=headermap,
            ishtml=False,
            allheaders=allheaders,
            regexpclass=regexpclass
        )

    def reset_file(self, pdffile=None, textfile=None):
        self.pdffile = pdffile if pdffile else self.pdffile
        self.textfile = textfile if textfile else self .textfile

    def _get_last_empty(self, string, position):
        tempvalue = string[0:position]
        posn = tempvalue.rfind(" ")
        tempvalue = string[position:].strip()
        if tempvalue:
            return posn + 1
        else:
            return position

    def _get_temp_file(self, filename):
        basefile = os.path.basename(filename)
        filewoextn = basefile.rsplit('.', 1)[0]
        return os.path.join(
            os.path.dirname(filename),
            "{}.txt".format(filewoextn)
        )

    def process_text_file(self, textfile=None):
        datadict = {}
        if textfile:
            self.reset_file(textfile=textfile)
        mainsecflag = 0
        textposition = 0
        head = None
        data = None
        with open(textfile, 'r') as infile:
            for line in infile:
                if self.igr.empty_ignore_string(line):
                    continue
                if mainsecflag == 0:
                    templist = self.igr.check_section_match(line)
                    if templist:
                        self.igr.set_head_data(
                            templist[0], templist[1], datadict
                        )
                        mainsecflag = 1
                        continue
                if mainsecflag == 0:
                    continue
                currposn = self._get_last_empty(line, textposition)
                if textposition > 0:
                    if self.igr.check_header(line):
                        self.igr.set_head_data(
                            header=head, value=data, datadict=datadict
                        )
                        head = line[0:currposn]
                        data = line[currposn:]
                    else:
                        head += " {}".format(line[0:currposn].strip())
                        data += " {}".format(line[currposn:].strip())
                else:
                    templist = self.igr.check_begin(line)
                    if templist[0]:
                        head = templist[1]
                        data = templist[2]
                        textposition = templist[3]
        self.igr.set_head_data(
            header=head, value=data, datadict=datadict
        )
        return datadict

    def process(self, pdffile, temppath):
        if not self.igr.check_readable_pdf(self.xpdf, pdffile):
            raise xpdf.PDFUnreadableFont(
                "PDF: {} is unreadable".format(pdffile)
            )
        #  Copy the file to the temp directory
        tempfile = self.igr.copy_to_temp(pdffile, temppath)
        textfile = self._get_temp_file(tempfile)
        fo.remove_file(textfile)
        self.reset_file(pdffile=tempfile, textfile=textfile)
        self.xpdf.pdf_to_text(tempfile, outformat="table")
        try:
            datadict = self.process_text_file(textfile)
            fo.remove_file(textfile)
            fo.remove_file(tempfile)
        except xpdf.PDFManualProcess as pmp:
            fo.remove_file(textfile)
            raise xpdf.PDFManualProcess(
                "Switch mode for PDF: {}".format(pdffile)
            )
        except Exception as e:
            fo.remove_file(textfile)
            fo.remove_file(tempfile)
            raise
        return datadict


    # def check_section_match(self, string):
    #     for pattern in self.regex.sectionstart:
    #         match = pattern.search(string)
    #         if match:
    #             if self.ishtml:
    #                 return match.group(1)
    #             else:
    #                 return [match.group(1), match.group(3)]
    #     return None

    # def check_begin(self, string):
    #     flag = 0
    #     head = string
    #     data = ""
    #     textposition = 0
    #     for pattern in self.regex.title:
    #         match = pattern.search(string)
    #         if match:
    #             flag = 1
    #             head = match.group(2)
    #             if not self.ishtml:
    #                 textposition = match.start(3)
    #                 data = match.group(3)
    #             break
    #     if flag == 0:
    #         for pattern in self.regex.alternatebegin:
    #             match = pattern.search(string)
    #             if match:
    #                 flag = 1
    #                 head = ""
    #                 if not self.ishtml:
    #                     textposition = match.start(2)
    #                     data = match.group(2)
    #                 break
    #     if self.ishtml:
    #         return [True if flag == 1 else False, head]
    #     else:
    #         return [True if flag == 1 else False,
    #                 head, data, textposition]

