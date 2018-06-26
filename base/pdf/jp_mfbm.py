import re
import csv
from base.pdf.jp_base_process import JapanBasePDF
from base.utils import fileobjects as fo
from base.utils import csv_process as cp


class MFBMFile(JapanBasePDF):
    def __init__(self, tabuladir=None, tabulajarfile=None, xpdfdir=None,
                 processdir=None, tempname="temp", outname="output"):
        super(MFBMFile, self).__init__(
            xpdfdir=xpdfdir, tabuladir=tabuladir, tabulajarfile=tabulajarfile,
            processdir=processdir, tempname=tempname, outname=outname
        )
        self.begin = '賃料 共益費 時間内'
        self.end = None
        self.pivotcolumn = 6
        self.regexppivot = re.compile('[A-Za-z]*[0-9]+[,]*[0-9]*F', re.ASCII)

    @staticmethod
    def _set_header(currline, prevline=None):
        templine = currline
        if not prevline:
            return templine
        try:
            for index in range(0, len(templine)):
                if index == 0:
                    templine[index] = "BuildingName"
                elif index == 1:
                    templine[index] = "BuildingAddress"
                else:
                    templine[index] = prevline[index] + " " + templine[index]
        except IndexError:
            pass
        templine.insert(0, "PerfectureName")
        templine.insert(1, "Location")
        return templine

    @staticmethod
    def _set_record(currline, prevline, perfecture=None, location=None):
        templine = currline
        templine.insert(0, perfecture)
        templine.insert(1, location)
        if not prevline:
            return templine
        try:
            for index in range(0, len(templine)):
                if templine[index] == "":
                    templine[index] = prevline[index]
        except IndexError:
            pass
        return templine

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
                for line in reader:
                    outline = [field.replace("\n", ";").rstrip() for field in line]
                    if lineno < 2:
                        outline = self._set_header(outline, prevline=prevline)
                    else:
                        if lineno == 2:
                            writer.writerow(prevline)
                            prevline = None
                        currname = outline[0] if self._check_pref_location(
                            currline=outline
                        ) else ""
                        if currname != "" and prevname != "":
                            perfecture = prevname
                            location = currname
                        elif prevname != "":
                            location = prevname
                        if currname == "":
                            if prevname == "":
                                writer.writerow(prevline)
                                templine = prevline
                            else:
                                templine = None
                            outline = self._set_record(outline, templine,
                                                       perfecture=perfecture,
                                                       location=location)
                            # writer.writerow(prevline)
                        else:
                            if prevname == "" and (prevline is not None):
                                writer.writerow(prevline)
                    lineno += 1
                    prevline = outline
                    prevname = currname
                writer.writerow(prevline)
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
        filelist = self.preprocess_pdf(pdffile=pdffile, html_dir=self.htmldir)
        filecounter = 1
        try:
            for htmlfile in filelist:
                tempfile = "{0}/{1}_temp.csv".format(
                    self.tempdir,
                    fo.get_base_filename(htmlfile)
                )
                self.process_pdf_tab(
                    pdffile=pdffile, htmlfile=htmlfile, outfile=tempfile,
                    begin=self.begin, end=self.end, runtype='stream'
                )
                self._process_csv(tempfile, outfile)
                filecounter += 1
        except Exception:
            raise

# # Headers
# # - Building Name
# # - Address
# # - 竣工年月 (Completion Date)
# # - 階数 (Rank)
# # - 階 (Floor)
# # - 用途 (Use)
# # - 面積 m2 (Area)
# # - 面積坪 (Area Tsoubo)
# # - 共用 負担 (Shared Burdn)
# # - 貸付予定日 (Scheduled Date of Loan)
# # - 賃料（円/坪） (Rent Yen/Tsoubo)
# # - 共益費（円/坪） (Common Service Fee (Yen/tsoubo))
# # - 時間内空調費 (Air Conditioning cost within time)
# # - 敷金 (Security Deposit)
# # - 担当者 (Person in charge)
# # - ℡ (Telephone)
# # - 備考 (Remarks)


