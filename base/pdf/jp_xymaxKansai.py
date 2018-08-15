import re
import csv
from base.pdf.jp_base_process import JapanBasePDF
from base.utils import fileobjects as fo
from base.utils import csv_process as cp


class XymaxKansai(JapanBasePDF):
    def __init__(self, tabuladir=None, tabulajarfile=None, xpdfdir=None,
                 processdir=None, tempname="temp", outname="output"):
        super(XymaxKansai, self).__init__(
            xpdfdir=xpdfdir, tabuladir=tabuladir, tabulajarfile=tabulajarfile,
            processdir=processdir, tempname=tempname, outname=outname
        )
        self.begin = '種類'
        self.end = None
        self.pivotcolumn = 3
        self.regexppivot = re.compile('満室|', re.ASCII)
        self.runtype = 'lattice'

    @staticmethod
    def _set_record(currline, prevline,prevprevline ):
        templine = currline
        if len([field for field in templine if field != ""]) != 1:
            return templine
        else:
            # split column by ";"
            for index in [12, 3, 1]:
                if ";" in prevline[index]:
                    prevline.insert(index + 1, prevline[index].split(";")[1])
                    prevline[index] = prevline[index].split(";")[0]
                if prevline[index] == "":
                    prevline.insert(index, "")
            # insert 共益費 into column
            for index in range(0, len(templine)):
                if templine[index] != "":
                    prevline.insert(11, templine[index])
            #only keep one エリア value
            if ";" in prevline[0]:
                prevline[0] = prevline[0].split(";")[0]

            # auto file first 6 columns for lines without 物 件 名 称
            if prevprevline and prevline[2] == "":
                for index in range(0 , 6):
                    if prevprevline[index] != "" and prevline[index] == "":
                        prevline[index] = prevprevline[index]
            return prevline

    def _process_csv(self, infile, outfile):
        w_fileno = open(outfile, 'wt', encoding='utf-8', newline="")
        writer = csv.writer(w_fileno, delimiter=",")
        prevline = None
        try:
            with open(infile, 'rt', encoding='utf-8') as r_fileno:
                reader = csv.reader(r_fileno, dialect='excel')
                lineno = 0
                for line in reader:
                    outline = [field.replace("\n", ";").rstrip() for field in line]
                    print('no = '+ str(lineno))
                    print(outline)
                    print(prevline)
                    writer.writerow(outline)
                    lineno += 1
                    prevline = outline
        except:
            raise
        finally:
            w_fileno.close()

    def process_pdf(self, pdffile, skippage):
        basefile = fo.get_base_filename(pdffile)
        outfile = "{}/{}.csv".format(
            self.outdir,
            basefile
        )
        tempout = "{}/{}.csv".format(
            self.tempdir,
            basefile
        )
        filelist = self.preprocess_pdf(pdffile=pdffile, html_dir=self.htmldir)
        filecounter = 1
        tempfileno = open(tempout, 'wt', encoding='utf-8', newline="")
        tempwriter = csv.writer(tempfileno, delimiter=",")
        try:
            for htmlfile in filelist:
                if int(str(fo.get_base_filename(htmlfile)).replace("page","")) <= skippage:
                    continue;
                tempfile = "{0}/{1}_temp.csv".format(
                    self.tempdir,
                    fo.get_base_filename(htmlfile)
                )
                self.process_pdf_tab(
                    pdffile=pdffile, htmlfile=htmlfile, outfile=tempfile,
                    begin=self.begin, end=self.end, runtype = self.runtype
                )
                cp.arrange_csv(
                    tempfile, outfile=tempwriter, pivotcol=self.pivotcolumn,
                    pivotregexp=self.regexppivot, ignorecounter=1,
                    multipage=True, fileno=filecounter, headercol = 2,
                )
                filecounter += 1
        except Exception:
            raise
        finally:
            tempfileno.close()
        self._process_csv(tempout, outfile)
