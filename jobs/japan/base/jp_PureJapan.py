import re
import csv
from jobs.japan.base.jp_base_process import JapanBasePDF
from baselib.utils import fileobjects as fo
from baselib.csvops import csv_process as cp


class PureJapan(JapanBasePDF):
    def __init__(self, tabuladir=None, tabulajarfile=None, xpdfdir=None,
                 processdir=None, tempname="temp", outname="output", auditfile = None, dqoutdir = None):
        super(PureJapan, self).__init__(
            xpdfdir=xpdfdir, tabuladir=tabuladir, tabulajarfile=tabulajarfile,
            processdir=processdir, tempname=tempname, outname=outname,
            auditfile=auditfile
        )
        self.begin = None
        self.end = None
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
                    if (lineno > 0 and outline[0] != "物件名;所在地") or lineno == 0:
                        #split 8 columns
                        for i in [8,7,6,5,4,3,2,0]:
                            split = outline[i].split(";")
                            if lineno > 0:
                                # handle excpetion where more than 2 lines in 募集階
                                if i == 2 and outline[i].count(";") > 1:
                                    split[0] = re.search('(.+?階)', outline[i])[1]
                                    split[1] = outline[i].replace(split[0]+';','')
                                    del split[2:]
                                # handle excpetion where more than 2 lines in 構造; 規模; 竣⼯
                                if i == 8 and outline[i].count(";") > 2:
                                    #match the string till last 造
                                    split[0] = outline[i][0:outline[i].rfind(re.findall('(.?造)', outline[i])[-1]) + 2]
                                    split[1] = outline[i].replace(split[0]+';', '').split(";")[0]
                                    split[2] = outline[i].replace(split[0]+';', '').split(";")[1]
                                    del split[3:]
                                if outline[i].count(";") < 1:
                                    split.insert(1, '')
                            for j in range(1, len(split)):
                                outline.insert(i + j, split[j])
                            outline[i] = split[0]
                        if lineno == 0:
                            split = outline[9].split("/")
                            outline.insert(10, split[1])
                            outline[9] =  split[0]
                            outline[9] = split[0]
                            #overwrite the header names for 賃料坪単価(税別) and 共益費坪単価(税別)
                            outline[6] = '賃料' + outline[6]
                            outline[8] = '共益費' + outline[8]

                        writer.writerow(outline)
                    lineno += 1
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
        #self.dq_check(auditfile=self.auditfile , pdffile= pdffile, outfile= outfile, auditout = dqout)


