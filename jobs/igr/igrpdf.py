from base.utils import tdim_string as ts
from base.utils import fileobjects as fo
from base.pdf import xpdf as xpdf
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

    @staticmethod
    def check_readable_pdf(pdfclass, pdffile):
        return not pdfclass.is_unreadable_pdf(pdffile)

    @staticmethod
    def copy_to_temp(pdffile, temppath):
        fo.copy_file(pdffile, temppath)
        filename = os.path.join(temppath, os.path.basename(pdffile))
        return filename

    @staticmethod
    def _get_header(indexnumber, allsections, string):
        t_string = string.strip()
        if t_string:
            return string
        else:
            for key, value in allsections.items():
                if key == indexnumber:
                    t_string = ts.extract_string(value)
                    # t_string = value
                    break
            return t_string

    @staticmethod
    def _modify_header_name(header, allheaders):
        try:
            for key, value in allheaders.items():
                try:
                    assert isinstance(value, list)
                    for t_value in value:
                        if ts.match_string(string=header, matchpat=t_value):
                            return key
                except AssertionError:
                    if ts.match_string(string=header, matchpat=value):
                        return key
        except AttributeError:
            pass
        return header

    @staticmethod
    def _check_multiple_head(header, multihead):
        data = multihead.findall(header)
        if len(data) > 1:
            return True
        return False

    def _check_begin_title(self, string, posn, allpatterns):
        flag = False
        data = None
        textposition = None
        head = ""
        l_place = [int(x) for x in posn.split(",")]
        for pattern in allpatterns:
            retdict = ts.match_return_string(string=string, matchpat=pattern,
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

    def _clean_data(self, data, additional_clean=False):
        data = ts.clean_string(data)
        if additional_clean:
            data = self.regex.digitparan.sub('', data)
            data = data.strip()
        return data

    def check_section_match(self, string):
        for pattern in self.regex.sectionstart:
            posn = "1" if self.ishtml else "1,3"
            retdict = ts.match_return_string(string=string, matchpat=pattern,
                                             position=posn)
            if retdict:
                retvalue = [v for k, v in sorted(retdict.items())]
                retvalue = retvalue[0] if len(retvalue) == 1 else retvalue
                return retvalue
        return None

    def check_begin(self, string):
        posn = "2"
        posn = "2,3".format(posn) if not self.ishtml else posn
        l_return = self._check_begin_title(string=string, posn=posn,
                                           allpatterns=self.regex.title)
        if not l_return[0]:
            posn = "2"
            l_return = self._check_begin_title(
                string=string,
                posn=posn,
                allpatterns=self.regex.alternatebegin
            )
        if self.ishtml:
            return [l_return[0], l_return[1]]
        else:
            return [l_return[0], l_return[1], l_return[2], l_return[3]]

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
                header = self._get_header(match.group(2), self.defsectionname,
                                          header[startposn:])
            header = ts.clean_string(header, multispace=self.regex.multispace)
            match = self.regex.headparan.search(header)
            if match:
                header = match.group(1)
            return header
        except AttributeError:
            return None

    def get_building_name(self, header, value, datadict):
        building = []
        for pattern in self.regex.buildingheader:
            match = ts.match_string(string=header, matchpat=pattern)
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

    def set_head_data(self, header, value, datadict, additional_clean=False):
        if self._check_multiple_head(header=header,
                                     multihead=self.regex.multihead):
            raise xpdf.PDFManualProcess(
                "PDF needs Manual Process"
            )
        header = self.clean_header(header, additional_clean=additional_clean)
        value = self._clean_data(value, additional_clean=additional_clean)
        header = self._modify_header_name(header, self.headermap)
        header = ts.initial_captial(header)
        if header:
            datadict[header] = value
            self.get_building_name(header, value, datadict)

    def empty_ignore_string(self, string):
        if self.regex.empty.match(string):
            return True
        for pattern in self.regex.ignore:
            if ts.match_string(string=string, matchpat=pattern):
                return True
        return False


# def modify_header_name(self, header):
#     try:
#         for key, value in self.headermap.items():
#             try:
#                 assert isinstance(value, list)
#                 for t_value in value:
#                     if ts.match_string(header, t_value):
#                         return key
#             except AssertionError:
#                 if ts.match_string(header, value):
#                     return key
#     except AttributeError:
#         pass
#     return header

# def get_header(self, indexnumber, string):
#     t_string = string.strip()
#     if t_string:
#         return string
#     else:
#         for key, value in self.defsectionname.items():
#             if key == indexnumber:
#                 t_string = value
#                 break
#         return t_string

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
