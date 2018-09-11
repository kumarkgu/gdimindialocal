import os
from jobs.igr.igrpdf import IgrPdfCommonProcessing
from base.utils import fileobjects as fo
from base.pdf import xpdf


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

    @staticmethod
    def _get_last_empty(string, position):
        tempvalue = string[0:position]
        posn = tempvalue.rfind(" ")
        tempvalue = string[position:].strip()
        if tempvalue:
            return posn + 1
        else:
            return position

    @staticmethod
    def _get_temp_file(filename):
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
                            templist[0], templist[1], datadict,
                            additional_clean=True
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
                        textposition = int(templist[3])
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
        except xpdf.PDFManualProcess:
            fo.remove_file(textfile)
            raise xpdf.PDFManualProcess(
                "Switch mode for PDF: {}".format(pdffile)
            )
        except Exception:
            fo.remove_file(textfile)
            fo.remove_file(tempfile)
            raise
        return datadict
