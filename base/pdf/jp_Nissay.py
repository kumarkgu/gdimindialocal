import re
import csv
from base.pdf.jp_base_process import JapanBasePDF
from base.utils import fileobjects as fo
from base.utils import csv_process as cp


class Nissay(JapanBasePDF):
    def __init__(self, tabuladir=None, tabulajarfile=None, xpdfdir=None,
                 processdir=None, tempname="temp", outname="output"):
        super(Nissay, self).__init__(
            xpdfdir=xpdfdir, tabuladir=tabuladir, tabulajarfile=tabulajarfile,
            processdir=processdir, tempname=tempname, outname=outname
        )
        self.begin = 'ﾋﾞﾙ名称'
        self.end = '①賃料はご相談に応じます。'
        self.pivotcolumn = None
        self.regexppivot = None #re.compile("^\([A-Za-z]*[0-9]*[0-9]\)", re.ASCII)
        self.runtype = 'stream'


    @staticmethod
    def _set_header(currline, prevline=None):
        templine = currline
        if not prevline:
            return templine
        try:
            for index in range(0, len(prevline)):
                if prevline[index] == "面積":
                    prevline.insert(index+1, prevline[index] + templine[1])
                    prevline[index] = prevline[index] + templine[0]
                else:
                    prevline[index] = prevline[index]
        except IndexError:
            pass
        prevline.insert(0, "BuildingGroup")
        prevline.insert(1, "PerfectureName")
        return prevline

    @staticmethod

    def _set_record(currline, prevline, perfecture=None, buildinggroup=None):
        templine = currline[0:5] + currline[6].split(" ") + currline[7:]
        print(currline[0:5])
        templine.insert(0, buildinggroup)
        templine.insert(1, perfecture)
        # if not prevline:
        #     return templine
        # try:
        #     for index in range(0, len(templine)):
        #         if templine[index] == "":
        #             templine[index] = prevline[index]
        # except IndexError:
        #     pass
        return templine

    @staticmethod
    def _check_pref_location(currline):
        counter = 0
        for field in currline:
            if "●" in field:
                counter += 1
            if counter > 1:
                break
        isperflocation = True if counter == 1 else False
        return isperflocation

    @staticmethod
    def _check_building_name(currline):
        counter = 0
        for field in currline:
            if field != "" and "(" not in field and "●" not in field:
                counter += 1
            if counter > 1:
                break
        isbuildingname = True if counter == 1 else False
        return isbuildingname

    def _process_csv(self, infile, outfile):
        w_fileno = open(outfile, 'wt', encoding='utf-8', newline="")
        writer = csv.writer(w_fileno, delimiter=",")
        currname = ""
        prevname = "BEGIN"
        prevline = None
        try:
            with open(infile, 'rt', encoding='utf-8') as r_fileno:
                reader = csv.reader(r_fileno, dialect='excel')
                lineno = 0
                buildinggroup = 0
                perfecture = None
                for line in reader:
                    print(lineno)
                    outline = [field.replace("\n", ";").rstrip() for field in line]
                    print(outline)
                    if lineno < 2:
                        outline = [item for field in line for item in field.split()]
                        outline = self._set_header(outline, prevline=prevline)
                    else:
                        if lineno == 2:
                            writer.writerow(prevline)
                            prevline = None
                        currname = outline[0].replace("● ","") if self._check_pref_location(
                            currline=outline
                        ) else ""
                        print(currname)
                        if currname != "" and prevname != "":
                            perfecture = currname
                        if currname == "":
                            if "(" not in outline[0] and "●" not in outline[0] and " " not in outline[0]:
                                buildinggroup += 1
                                outline = outline[0].split(" ") + outline[1:]
                            else:
                                outline.insert(0, " ")
                            outline = self._set_record(outline, prevline,
                                                      perfecture=perfecture,
                                                      buildinggroup = buildinggroup)
                            writer.writerow(outline)
                    lineno += 1
                    prevline = outline
                    prevname = currname
                writer.writerow(prevline)
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
        print(filelist)
        filecounter = 1
        tempfileno = open(tempout, 'wt', encoding='utf-8', newline="")
        tempwriter = csv.writer(tempfileno, delimiter=",")
        try:
            for htmlfile in filelist:
                if fo.get_base_filename(htmlfile) == 'page'+str(skippage):
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
                    pivotregexp=self.regexppivot, ignorecounter=0,
                    multipage=True, fileno=filecounter, headercol = 4
                )
                filecounter += 1
        except Exception:
            raise
        finally:
            tempfileno.close()
        self._process_csv(tempout, outfile)
        #self.refill_csv(infile=tempout, outfile=outfile, ignorefirst=False)


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