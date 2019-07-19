import re
import csv
from jobs.japan.base.jp_base_process import JapanBasePDF
from baselib.utils import fileobjects as fo
from baselib.csvops import csv_process as cp


class Xymax(JapanBasePDF):
    def __init__(self, tabuladir=None, tabulajarfile=None, xpdfdir=None,
                 processdir=None, tempname="temp", outname="output", auditfile = None, dqoutdir = None):
        super(Xymax, self).__init__(
            xpdfdir=xpdfdir, tabuladir=tabuladir, tabulajarfile=tabulajarfile,
            processdir=processdir, tempname=tempname, outname=outname, auditfile = auditfile
        )
        self.begin = 'エリア'
        self.end = '凡例'
        self.pivotcolumn = 6
        self.regexppivot = re.compile('[A-Za-z]*[0-9]+[,]*[0-9]*F', re.ASCII)

    def process_pdf(self, pdffile):
        basefile = fo.get_base_filename(pdffile)
        outfile = "{}/{}.csv".format(
            self.outdir,
            basefile
        )
        tempout = "{}/{}.csv".format(
            self.tempdir,
            basefile
        )
        dqout = "{}/dq.xlsx".format(
            self.dqoutdir,
        )
        filelist = self.preprocess_pdf(pdffile=pdffile, html_dir=self.htmldir)
        filecounter = 1
        tempfileno = open(tempout, 'wt', encoding='utf-8', newline="")
        tempwriter = csv.writer(tempfileno, delimiter=",")
        try:
            for htmlfile in filelist:
                tempfile = "{0}/{1}_temp.csv".format(
                    self.tempdir,
                    fo.get_base_filename(htmlfile)
                )
                self.process_pdf_tab(
                    pdffile=pdffile, htmlfile=htmlfile, outfile=tempfile,
                    begin=self.begin, end=self.end
                )
                cp.arrange_csv(
                    tempfile, outfile=tempwriter, pivotcol=self.pivotcolumn,
                    pivotregexp=self.regexppivot, ignorecounter=1,
                    multipage=True, fileno=filecounter
                )
                filecounter += 1
        except Exception:
            raise
        finally:
            tempfileno.close()
        self.refill_csv(infile=tempout, outfile=outfile, ignorefirst=False)
        self.dq_check(auditfile=self.auditfile, pdffile=pdffile, outfile=outfile, auditout=dqout)
