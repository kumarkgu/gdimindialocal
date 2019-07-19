import re
import csv
from jobs.japan.base.jp_base_process import JapanBasePDF
from baselib.utils import fileobjects as fo
from baselib.csvops import csv_process as cp


class XymaxED(JapanBasePDF):
    def __init__(self, tabuladir=None, tabulajarfile=None, xpdfdir=None,
                 processdir=None, tempname="temp", outname="output", auditfile = None, dqoutdir = None):
        super(XymaxED, self).__init__(
            xpdfdir=xpdfdir, tabuladir=tabuladir, tabulajarfile=tabulajarfile,
            processdir=processdir, tempname=tempname, outname=outname,
            auditfile=auditfile
        )
        self.begin = 'エリア'
        self.end = '凡例'
        self.pivotcolumn = 6
        self.regexppivot = re.compile('[A-Za-z]*[0-9]+[,]*[0-9]*F|^M\d|^\d*-;\d*\d$', re.ASCII)
        self.runtype = 'lattice'
        self.addressindex = 2

    @staticmethod
    def _set_header(currline, prevline=None):
        templine = currline
        if not prevline:
            return templine
        else:
            #print(prevline)
            #insert 共益費 into header
            for index in range(0, len(templine)):
                if templine[index] != "":
                    prevline.insert(index + 2, templine[index])
            #split header by ";"
            for index in range(1, len(prevline) + 3):
                if ";" in prevline[index]:
                    #print(prevline[index])
                    prevline.insert(index + 1, prevline[index].split(";")[1])
                    prevline[index] = prevline[index].split(";")[0]

            return prevline
        #except IndexError:
            #pass

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

            #inset blank column for building record without 竣工年 or 規模
            if prevline[4] != "" and prevline[5] in ("New","") :
                if not re.search('\d年', prevline[4]):
                    prevline.insert(5,"")
                    prevline[5] = prevline[4]
                    prevline[4] = ""
                else:
                    prevline.insert(5, "")

            # auto file first 6 columns for lines without 物 件 名 称
            if prevprevline:
               for index in range(0, 6):
                   if index == 1 and prevline[index] != "":
                       break
                   if prevprevline[index] != "" and prevline[index] == "":
                       prevline[index] = prevprevline[index]
            return prevline

    def _process_csv(self, infile, outfile, addressindex):
        w_fileno = open(outfile, 'wt', encoding='utf-8', newline="")
        writer = csv.writer(w_fileno, delimiter=",")
        prevline = None
        prevprevline = None
        try:
            with open(infile, 'rt', encoding='utf-8') as r_fileno:
                reader = csv.reader(r_fileno, dialect='excel')
                lineno = 0
                for line in reader:
                    outline = [field.replace("\n", ";").rstrip() for field in line]
                    #print('no = '+ str(lineno))
                    #print(outline)
                    #print(prevline)
                    #print(prevprevline)
                    if lineno < 2:
                        outline = self._set_header(outline, prevline = prevline)
                    if lineno == 1:
                        writer.writerow(outline)
                    if lineno > 1:
                        outline = self._set_record(outline, prevline = prevline, prevprevline = prevprevline)
                        #output the combine lines with 共益費 only
                        if outline[0] != "" and len(outline) > 14:
                            outline[addressindex] = cp.addxform(outline[addressindex])
                            writer.writerow(outline)
                    lineno += 1
                    prevprevline = prevline
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
        dqout = "{}/dq.xlsx".format(
            self.dqoutdir,
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
                    pivotregexp=self.regexppivot, ignorecounter=2,
                    multipage=True, fileno=filecounter, headercol = 2,
                )
                filecounter += 1
        except Exception:
            raise
        finally:
            tempfileno.close()
        self._process_csv(tempout, outfile, self.addressindex)
        self.dq_check(auditfile=self.auditfile, pdffile=pdffile, outfile=outfile, auditout=dqout)
