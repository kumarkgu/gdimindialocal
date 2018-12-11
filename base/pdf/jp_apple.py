import re
import csv
from base.pdf.jp_base_process import JapanBasePDF
from base.utils import fileobjects as fo
from base.utils import csv_process as cp

class Apple(JapanBasePDF):
    def __init__(self, tabuladir=None, tabulajarfile=None, xpdfdir=None,
                 processdir=None, tempname="temp", outname="output", auditfile = None, dqoutdir = None):
        super(Apple, self).__init__(
            xpdfdir=xpdfdir, tabuladir=tabuladir, tabulajarfile=tabulajarfile,
            processdir=processdir, tempname=tempname, outname=outname,
            auditfile=auditfile
        )
        self.begin = None
        self.end = None
        self.pivotcolumn = None
        self.regexppivot = None
        self.runtype = 'lattice'

    @staticmethod
    def _set_record(currline):
        templine = [None] *len(currline)
        nextline = [None] *len(currline)
        for i in range(0, len(currline)):
            if ";" in currline[i]:
                split = currline[i].split(";")
                templine[i] = split[0]
                nextline[i] = ";".join(split[1:])
            else:
                templine[i] = currline[i]
                nextline[i] = currline[i]
        return templine, nextline

    def _process_csv(self, infile, outfile):
        w_fileno_resi = open(outfile.replace("Apple","AppleResi"), "wt", encoding="utf-8", newline="")
        writer_resi = csv.writer(w_fileno_resi, delimiter=",")
        w_fileno_retail = open(outfile.replace("Apple","AppleRetail"), "wt", encoding="utf-8", newline="")
        writer_retail = csv.writer(w_fileno_retail, delimiter=",")
        w_fileno = w_fileno_resi
        writer = writer_resi
        prevline = None
        try:
            with open(infile, 'rt', encoding='utf-8') as r_fileno:
                reader = csv.reader(r_fileno, dialect='excel')
                currline = None
                for line in reader:
                    outline = [field.replace("\n", ";").rstrip() for field in line]
                    if len(outline) < 2 or (not re.search("^\d$", outline[0]) and outline[0] != "No"):
                        continue
                    else:
                        #split tabless into Residence and retail
                        if outline[1].replace(" ","") == "ビル名":
                            w_fileno.close()
                            writer = writer_retail
                            w_fileno = w_fileno_retail
                        #split rows with ";"
                        if outline[0] != "No":
                            if ";" in outline[4]:
                                currline = outline
                                for i in range(0, outline[4].count(";")):
                                    prevline, currline = self._set_record(currline)
                                    #Write lines within the semicolon line
                                    writer.writerow(prevline)
                            elif currline:
                                #Write last line of the semicolon line
                                writer.writerow(currline)
                                # Write first line after line with semicolon
                                writer.writerow(outline)
                                currline = None
                            else:
                                #Writ first line
                                writer.writerow(outline)
                        else:
                            #Write Title
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
        self.dq_check(auditfile=self.auditfile, pdffile=pdffile.replace("Apple","AppleResi"), outfile=outfile.replace("Apple","AppleResi"), auditout=dqout)
        self.dq_check(auditfile=self.auditfile, pdffile=pdffile.replace("Apple","AppleRetail"), outfile=outfile.replace("Apple","AppleRetail"), auditout=dqout)




