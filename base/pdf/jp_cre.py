import re
import csv
from base.pdf.jp_base_process import JapanBasePDF
from base.utils import fileobjects as fo
from base.utils import csv_process as cp

class CRE(JapanBasePDF):
    def __init__(self, tabuladir=None, tabulajarfile=None, xpdfdir=None,
                 processdir=None, tempname="temp", outname="output", auditfile = None, dqoutdir = None):
        super(CRE, self).__init__(
            xpdfdir=xpdfdir, tabuladir=tabuladir, tabulajarfile=tabulajarfile,
            processdir=processdir, tempname=tempname, outname=outname,
            auditfile=auditfile
        )
        self.begin = "　　　倉 庫 物 件 情 報 （ 貸主 ）"
        self.end = "取引形態"
        self.pivotcolumn = None
        self.regexppivot = None
        self.runtype = 'lattice'

    def _process_csv(self, infile, outfile):
        w_fileno = open(outfile, "wt", encoding="utf-8", newline="")
        writer= csv.writer(w_fileno, delimiter=",")
        OwnerType = None
        location = None
        hasheadr = 0
        try:
            with open(infile, 'rt', encoding='utf-8') as r_fileno:
                reader = csv.reader(r_fileno, dialect='excel')
                lineno = 0
                for line in reader:
                    outline = [field.replace("\n", ";").rstrip() for field in line]
                    length = len(outline) - outline.count("")
                    #retain the location
                    if length == 1:
                        if outline[0] != "":
                            location = outline[0]
                        elif outline[1] != "":
                            location = outline[1]
                    # determine it's 貸主 or 媒介
                    elif length == 2:
                        if "貸主" in outline[1]:
                            OwnerType = "貸主"
                        elif "媒介" in outline[1]:
                            OwnerType = " 媒介"
                    #determine if it's the header
                    elif length > 2:
                        if hasheadr == 0:
                            if outline[0] == "No":
                                outline = ["OwnerType", "Location","New?"] + outline
                            elif outline[1] == "No":
                                outline = ["OwnerType", "Location", "New?"] + outline[1:]
                            writer.writerow(outline)
                            hasheadr = 1
                        elif outline[0] != "No" and  outline[1] != "No":
                            if outline[0] not in ("New", ""):
                                outline= [OwnerType, location,""] + outline
                            else:
                                outline = [OwnerType, location] + outline
                            writer.writerow(outline)
        except:
            raise
        finally:
            w_fileno.close()


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
        tempfileno = open(tempout, 'wt', encoding='utf-8', newline="")
        tempwriter = csv.writer(tempfileno, delimiter=",")
        filecounter = 1
        try:
            for htmlfile in filelist:
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
                    pivotregexp=self.regexppivot, ignorecounter=0,
                    multipage=True, fileno=filecounter, headercol = 0
                )
                filecounter += 1
        except Exception:
            raise
        finally:
            tempfileno.close()
        self._process_csv(tempout, outfile)
        self.dq_check(auditfile=self.auditfile , pdffile= pdffile, outfile= outfile, auditout = dqout)


