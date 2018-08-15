import re
import csv
from base.pdf.jp_base_process import JapanBasePDF
from base.utils import fileobjects as fo
from base.utils import csv_process as cp


class MitsuiFudosan(JapanBasePDF):
    def __init__(self, tabuladir=None, tabulajarfile=None, xpdfdir=None,
                 processdir=None, tempname="temp", outname="output"):
        super(MitsuiFudosan, self).__init__(
            xpdfdir=xpdfdir, tabuladir=tabuladir, tabulajarfile=tabulajarfile,
            processdir=processdir, tempname=tempname, outname=outname
        )
        self.begin = '時間'
        self.end = None
        self.pivotcolumn = None
        self.regexppivot = None #re.compile("^\([A-Za-z]*[0-9]*[0-9]\)", re.ASCII)
        self.runtype = 'stream'

    def _set_header(self, currline, prevline=None, prevprevline=None):
        templine = currline
        if not prevline:
            return templine
        try:
            if not prevprevline:
                for index in range(0, len(templine)):
                    templine[index] = prevline[index] + templine[index]
                return templine
            else:
                for index in range(0, len(templine)):
                    if index == 0:
                        templine[index] = "ビル名称"
                    elif index == 1:
                        templine[index] = "転貸方式"
                    elif index == 2:
                        templine[index] = "Address"
                    else:
                        templine[index] = prevline[index] + templine[index]
                templine.insert(0, "PerfectureName")
                templine.insert(1, "Location")
                templine.insert(5, templine[5].split(" ")[1])
                templine[5] = templine[5].split(" ")[0]
                del templine[7] # del empty column between 階数 and 室
                return templine
        except IndexError:
            pass

    @staticmethod
    def _check_pref_location(currline):
        counter = 0
        for field in currline:
            if field != "":
                counter += 1
            if counter > 1:
                break
        isperflocation = True if counter == 1 else False
        return isperflocation

    @staticmethod
    def _check_short_line(currline):
        counter = 0
        for field in currline:
            if field != "":
                counter += 1
            if counter > 3:
                break
        isshortline = True if counter == 2 else False
        return isshortline

    def _set_record(self, currline, prevline):
        templine = currline
        # to make columns aligns
        if len(templine) < 18 and templine[7] !="": # len(templine) < 18 -> Missing 転貸方式 in some page, templine[7] !="" -> 用 契途 約 & 面積(m2) in same cell
            templine.insert(1, "")
        #split 階数 from 竣工年月
        if " " in templine[3]:
            templine[4] = templine[3].split(" ")[1]
            templine[3] = templine[3].split(" ")[0]
        #split 面積(m2) from 用 契途 約
        if templine[7] == "" and templine[6] != "":
            templine[7] = templine[6].split(" ")[2]
            templine[6] = templine[6].split(" ")[0] + templine[6].split(" ")[1]
        #split TEL from 担当者
        if " " in templine[15]:
            templine[16] = templine[15].split(" ")[1]
            templine[15] = templine[15].split(" ")[0]
        #handel short lines, e.g. line "A=WEST棟、B=EAST棟"
        if self._check_short_line(prevline):
            templine[0] = prevline[0]
            templine[1] = prevline[1]
        # auto fill building name and address
        if not self._check_short_line(templine):
            for index in [0, 2]:
                if templine[index] in ("", "新") and prevline[index] != "新":
                    templine[index] = prevline[index]
        return templine

    def _process_csv(self, infile, outfile):
        w_fileno = open(outfile, 'wt', encoding='utf-8', newline="")
        writer = csv.writer(w_fileno, delimiter=",")
        prevline = None
        prevprevline = None
        perfecture = None
        location = None
        try:
            with open(infile, 'rt', encoding='utf-8') as r_fileno:
                reader = csv.reader(r_fileno, dialect='excel')
                lineno = 0
                for line in reader:
                    outline = [field.replace("\n", ";").rstrip() for field in line]
                    if "営業中物件一覧" in outline or '三井不動産ビルマネジメント株式会社' in outline:
                        break
                    print('no = '+ str(lineno))
                    if lineno < 3:
                        outline = self._set_header(outline, prevline=prevline, prevprevline = prevprevline)
                    print(outline)
                    if lineno == 3:
                        writer.writerow(prevline)
                    if lineno > 3:
                        print(self._check_pref_location(outline))
                        print(self._check_pref_location(prevline))
                        if '合   計' in outline or "".join(outline[0:6]) == "": #remove "合   計" line and page line
                            continue
                        if self._check_pref_location(outline) and self._check_pref_location(prevline):
                            perfecture = prevline[0]
                            location = outline[0]
                        elif self._check_pref_location(outline) and not self._check_pref_location(prevline):
                            location = outline[0]
                        elif not self._check_pref_location(outline):
                            print(self._check_short_line(outline))
                            outline = self._set_record(outline, prevline)
                            if not self._check_short_line(outline):
                                writer.writerow([perfecture, location]+outline)
                    print('perfecture =' + str(perfecture))
                    print('location =' + str(location))
                    lineno += 1
                    prevprevline = prevline
                    prevline = outline
        except:
            raise
        finally:
            w_fileno.close()

    def process_pdf(self, pdffile, ):
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
        print(filelist)
        filecounter = 1
        tempfileno = open(tempout, 'wt', encoding='utf-8', newline="")
        tempwriter = csv.writer(tempfileno, delimiter=",")
        try:
            for htmlfile in filelist:
                print(htmlfile)
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
                    multipage=True, fileno=filecounter, headercol = 3,
                )
                filecounter += 1
        except Exception:
            raise
        finally:
            tempfileno.close()
        self._process_csv(tempout, outfile)

# - ビル名称
# - 竣工
# - 所在地
# - 最寄駅
# - フロア
# - 面積 (m2)
# - 面積 (坪)
# - 入居時期
# - 備考
# - 担当者
# - 連絡先TEL