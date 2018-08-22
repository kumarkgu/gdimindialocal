import re
import os
import glob
import csv
from bs4 import BeautifulSoup
from base.pdf import xpdf as xpdf
from base.pdf import tabula as tabula
from base.utils import fileobjects as fo


class JapanBasePDF:
    def __init__(self, xpdfdir=None, tabuladir=None, tabulajarfile=None,
                 processdir=None, tempname="temp", outname="output"):
        self.tabdir = tabuladir
        self.tabjarfile = tabulajarfile
        self.xpdfdir = xpdfdir
        self.processdir = processdir
        self.tempdir = "{}/{}".format(processdir, tempname)
        self.outdir = "{}/{}".format(processdir, outname)
        self.htmldir = "{}/html".format(processdir)
        self.regfile = re.compile(r'page(\d+)\.html')
        self.pxreg = re.compile(r'\D*(\d+)px', re.IGNORECASE)
        self.xpdf = xpdf.XpdfPdfProcess(utilpath=xpdfdir)
        self.tabula = tabula.TabulaPDF(tabuladir=tabuladir,
                                       tabulajarfile=tabulajarfile)

    def _exec_xpdf_pdftohtml(self, pdffile, htmldir):
        self.xpdf.pdf_to_html(pdffile, htmldir=htmldir)

    def _exec_tabula(self, pdffile, outfile, boundary=None, pageno=None,
                     runtype="lattice"):
        pages = 'all' if not pageno else pageno
        self.tabula.execute_tabula(
            pageno=pages,
            boundary=boundary,
            outfile=outfile,
            pdffile=pdffile,
            runtype=runtype
        )

    def _get_html_files(self, htmldir):
        templist = []
        filelist = []
        for file in glob.glob("{}/page*.html".format(htmldir)):
            basename = os.path.basename(file)
            regmatch = self.regfile.search(basename)
            if regmatch:
                templist.append(int(regmatch.group(1)))
        templist.sort()
        for fnumber in templist:
            filelist.append(
                "{0}/page{1}.html".format(htmldir, str(fnumber))
            )
        return filelist

    @staticmethod
    def _get_top_position(divs, regexp):
        posn = 0
        for keyval in divs["style"].split(";"):
            key = keyval.strip().split(":")
            if key[0] == "top":
                regmatch = regexp.search(key[1])
                if regmatch:
                    posn = regmatch.group(1)
                    break
        return posn

    def _get_topbottom_coord(self, filename, parser=None, begin=None, end=None):
        bsoup = BeautifulSoup(open(filename, encoding='utf-8'), parser)
        beginposn = 0
        endposn = 0
        regmatch = self.regfile.search(filename)
        filenumber = regmatch.group(1)
        alldivs = bsoup.findAll('div', {'class': 'txt'})
        flag = 0
        for divs in alldivs:
            currtext = divs.getText()
            if begin and begin != "":
                flag = 1
            if end and end != "":
                flag += 10
            currposn = int(self._get_top_position(divs, self.pxreg))
            if flag > 0:
                if flag == 1 or flag == 11:
                    if currtext == begin:
                        beginposn = currposn
                    if flag == 1:
                        endposn = currposn if currposn > endposn else endposn
                if flag == 10 or flag == 11:
                    if currtext == end:
                        endposn = currposn
                    if flag == 10:
                        beginposn = currposn if currposn < beginposn else beginposn
                if flag == 11:
                    if beginposn > 0 and endposn > 0:
                        break
            else:
                beginposn = currposn if currposn < beginposn else beginposn
                endposn = currposn if currposn > endposn else endposn
        beginposn = beginposn - 5
        endposn = endposn + 35 if flag == 1 else endposn + 1
        return beginposn, endposn, filenumber

    @staticmethod
    def refill_csv(infile, outfile, ignorefirst=True):
        linecounter = 1
        outcsv = open(outfile, 'wt', encoding='utf-8', newline="")
        writer = csv.writer(outcsv, delimiter=",")
        prevline = []
        with open(infile, 'rt', encoding='utf-8') as incsv:
            reader = csv.reader(incsv, dialect='excel')
            for line in reader:
                outline = [field for field in line]
                if linecounter == 1:
                    linecounter += 1
                    if not ignorefirst:
                        writer.writerow(outline)
                    continue
                try:
                    for posn in range(0, len(outline)):
                        if outline[posn] == "":
                            outline[posn] = prevline[posn]
                        else:
                            if posn == 0:
                                outline[posn] = outline[posn].split(";")[0]
                except IndexError:
                    pass
                prevline = outline
                writer.writerow(outline)
                linecounter += 1
            outcsv.close()

    def build_directory(self, tempdir, outputdir):
        fo.create_dir(tempdir)
        fo.create_dir(outputdir)

    def preprocess_pdf(self, pdffile, html_dir=None):
        if not html_dir:
            htmldir = "{}/html".format(os.path.dirname(pdffile))
        else:
            htmldir = html_dir
        fo.remove_dir(htmldir)
        self._exec_xpdf_pdftohtml(pdffile=pdffile, htmldir=htmldir)
        filelist = self._get_html_files(htmldir=htmldir)
        return filelist

    def process_pdf_tab(self, pdffile, htmlfile, outfile, begin, end, **kwargs):
        topposn, bottomposn, pageno = self._get_topbottom_coord(
            htmlfile,
            "html.parser",
            begin=begin,
            end=end
        )
        xycoord = "{},{},{},{}".format(
            str(topposn),
            str(kwargs.get('left', 2)),
            str(bottomposn),
            str(kwargs.get('right', 1450))
            #str(kwargs.get('right', 850))
        )
        self._exec_tabula(pdffile=pdffile, outfile=outfile, boundary=xycoord,
                          pageno=pageno,
                          runtype=kwargs.get('runtype', 'lattice'))

