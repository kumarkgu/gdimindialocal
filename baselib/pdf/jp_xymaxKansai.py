import re
import csv
from baselib.pdf.jp_base_process import JapanBasePDF
from baselib.utils import fileobjects as fo
from baselib.utils import csv_process as cp


class XymaxKansai(JapanBasePDF):
    def __init__(self, tabuladir=None, tabulajarfile=None, xpdfdir=None,
                 processdir=None, tempname="temp", outname="output", auditfile = None, dqoutdir = None):
        super(XymaxKansai, self).__init__(
            xpdfdir=xpdfdir, tabuladir=tabuladir, tabulajarfile=tabulajarfile,
            processdir=processdir, tempname=tempname, outname=outname,
            auditfile=auditfile
        )
        self.begin = '種類'
        self.end = None
        self.pivotcolumn = 5
        self.regexppivot = re.compile("[A-Za-z]*[0-9]+[,]*[0-9]*F|^\d\d\d$|^満室$|^満車$|^必要な坪数をリクエストください。$|^単独棟$", re.ASCII)
        self.runtype = 'lattice'
        self.addressindex = 4

    @staticmethod
    def _set_header(currline):
        templine = currline
        try:
            for index in range(0, len(templine)):
                if index == 1:
                    templine[index] = templine[index] + ""
                templine[index] = templine[index].replace(";","")
        except IndexError:
            pass
        templine.insert(1, "Location")
        templine.insert(4, "Address")
        return templine

    @staticmethod
    def _set_record(currline, prevline):
        templine = currline
        insertstart = 0
        if prevline is None:
            return templine
        try:
            # In some page, only one area under  エリア
            if any(str in templine[1] for str in ("PM", "リーシング")):
                templine[0] = templine[1]
                templine[1] = templine[2]
                templine[2] = "-"
            # In some page, only one area under  エリア, and no 種類
            if templine[0] == "" and templine[1] == "" and templine[2] != "":
                templine[0] = "-"
                templine[1] = templine[2]
                templine[2] = "-"
            #if 満室 or 必要な坪数をリクエストください。, need to insert 7 blank value to make columns align
            if "必要な坪数をリクエストください。" in templine[4]:
                templine = templine[:5] + ["", "", "", "", "", "", ""] + templine[5:]
            #split Address and ビル名
            if ";" in templine[3]:
                templine.insert(4, ";".join(templine[3].split(";")[1:]))
                templine[3] = templine[3].split(";")[0]
            else: templine.insert(4, "")
            #Only keep one location name
            if ";" in templine[1]:
                templine[1] = templine[1].split(";")[0]

            for index in range (0, len(templine)):
                if templine[index] == "即入居可能" and index != 8:
                    for i in range(0, 8 - index):
                        templine.insert(index, "")

                if re.search(("^空.*台$|^なし$"), templine[index]) and index != 12:
                    for i in range(0, 12 - index):
                        templine.insert(index, "")

                if any(templine[index] == str for str in ("個別", "セントラル", "併用","設置なし")):
                     if index < 14:
                         #if previous line is contact number
                         if ";" in templine[index - 1]:
                             if templine[index - 2] != "満室":
                                 insertstart = index - 2
                             else: insertstart = index - 1
                         else: insertstart = index
                         for i in range(0, 14 - index):
                             templine.insert(insertstart, "")
                     if index > 14:
                         for i in range(14, index):
                             del templine[i -1]
                             templine.insert(len(templine), "")

                #Autofill data from previous line
                if index in [0,1,2,3,4,12,13]:
                    if templine[index] == "" and prevline[index] != "":
                        templine[index] = prevline[index]
                        #print(index)
                        #print(templine[index])

            #print(templine)

            if templine[7] == '' and templine[5] not in ("満室","満車","必要な坪数をリクエストください。") :
                templine[7] = prevline[7]

            return templine[:21]
        except IndexError:
            pass

        #個別, セントラル, 併用
        #応相談
        #即入居可能


    def _process_csv(self, infile, outfile, addressindex):
        w_fileno = open(outfile, 'wt', encoding='utf-8', newline="")
        writer = csv.writer(w_fileno, delimiter=",")
        prevline = None
        try:
            with open(infile, 'rt', encoding='utf-8') as r_fileno:
                reader = csv.reader(r_fileno, dialect='excel')
                lineno = 0
                for line in reader:
                    outline = [field.replace("\n", ";").rstrip() for field in line]
                    #print('no = '+ str(lineno))
                    #print(outline)
                    #print(prevline)
                    if lineno < 2 and outline[0] == "種類":
                        outline = self._set_header(outline)
                        writer.writerow(outline)
                        prevline = outline
                    elif lineno > 0 and len(outline) > 10 and outline[0] not in ("種類","エリア") and outline[4] != "":
                        outline = self._set_record(outline,prevline)
                        outline[addressindex] = cp.addxform(outline[addressindex])
                        writer.writerow(outline)
                        prevline = outline
                    lineno += 1
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
                    pivotregexp=self.regexppivot, ignorecounter=1,
                    multipage=True, fileno=filecounter, headercol = 0,
                )
                filecounter += 1
        except Exception:
            raise
        finally:
            tempfileno.close()
        self._process_csv(tempout, outfile, self.addressindex)
        self.dq_check(auditfile=self.auditfile, pdffile=pdffile, outfile=outfile, auditout=dqout)
