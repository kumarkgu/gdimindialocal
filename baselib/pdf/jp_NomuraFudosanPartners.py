import re
import csv
from baselib.pdf.jp_base_process import JapanBasePDF
from baselib.utils import fileobjects as fo
from baselib.utils import csv_process as cp


class NomuraFudosanPartners(JapanBasePDF):
    def __init__(self, tabuladir=None, tabulajarfile=None, xpdfdir=None,
                 processdir=None, tempname="temp", outname="output", auditfile = None, dqoutdir = None):
        super(NomuraFudosanPartners, self).__init__(
            xpdfdir=xpdfdir, tabuladir=tabuladir, tabulajarfile=tabulajarfile,
            processdir=processdir, tempname=tempname, outname=outname,
            auditfile=auditfile
        )
        self.begin = '面 積'
        self.end = None
        self.pivotcolumn = None
        self.regexppivot = None #re.compile("^\([A-Za-z]*[0-9]*[0-9]\)", re.ASCII)
        self.runtype = 'lattice'
        self.addressindex = 4

    def _set_header(self, currline, prevline=None):
        templine = currline
        if not prevline:
            return templine
        try:
            #combine 面 積(m2) and 面 積(坪)
            if templine[5] == '坪':
                prevline.insert(6, prevline[5] +"("+ templine[5]+")")
                prevline[5] = prevline[5] + "("+ templine[4] + ")"
            elif templine[6] == '坪':
                prevline.insert(6, prevline[5] + "(" + templine[6] + ")")
                prevline[5] = prevline[5] + "(" + templine[5] + ")"
            #split 所在地;交通
            prevline.insert(3, prevline[2].split(";")[1])
            prevline[2] = prevline[2].split(";")[0]
            #Split ビル名;(構造/規模)
            prevline.insert(2,prevline[1].split(";")[1])
            prevline[1] = prevline[1].split(";")[0]
            #add Unit Comment
            prevline.insert(3, "UnitComment")


            for index in range(0, len(prevline)):
                if index + 1 > len(templine):
                    templine.insert(index,"")
                #split "担 当 ・ 備 考"
                if prevline[index] == "担 当 ・ 備 考":
                    templine[index] = prevline[index].split(" ・ ")[0]
                    templine.insert(index + 1,  'TEL')
                    templine.insert(index + 2,  prevline[index].split(" ・ ")[1])
                    break
                templine[index] = prevline[index]
            return templine
        except IndexError:
            raise
            #pass

    @staticmethod
    def _set_record( currline, prevline):
        templine = currline

        # to make columns aligns using position of 竣工年月
        if not re.search('\d年\d+月', templine[3]):
            if re.search('\d年\d+月', templine[2]):
                templine.insert(0, "")
            else:
                for index in range(0, 4):
                    if templine[index] != "":
                        templine.insert(index,"")

        #split 所在地 and 交 通
        if ";" not in templine[2] and templine[2] != "":
            templine[2] = templine[2] + ";"
        templine.insert(3, ";".join(templine[2].split(";")[1:]))
        templine[2] = templine[2].split(";")[0]

        #split ビル名 and (構造/規模)
        if ";" not in templine[1] and templine[1] != "":
            templine[1] = templine[1] + ";"
        templine.insert(2,";".join(templine[1].split(";")[1:]))
        templine[1] = templine[1].split(";")[0]

        #split Unitcomment
        if "★" in templine[2]:
            templine.insert(3, templine[2].split("★")[1])
            templine[2] = templine[2].split("★")[0]
        else: templine.insert(3, "")

        # split "担 当 ・ 備 考"
        if len(templine) >= 19 and "TEL" in templine[18]:
            templine.insert(19, ";".join(templine[18].split("TEL")[1:]))
            templine[18] = templine[18].split("TEL")[0]
        else: templine.insert(19,"")

        if len(templine) >= 19 and ";" in templine[19]:
            templine.insert(20, ";".join(templine[19].split(";")[1:]))
            templine[19] = templine[19].split(";")[0]
        else: templine.insert(20,"")

        #if there is no tel in "担 当 ・ 備 考"
        if len(templine) >= 19 and ";" in templine[18].rstrip(";"):
            templine[20] = ";".join(templine[18].split(";")[1:])
            templine[18] = templine[18].split(";")[0]

        #autofile the content
        for index in [0,1,2,4,5,6,16,17,18,19,20]:
            if index == 0 and templine[index] != "":
                break
            elif index == 1 and templine[index] != "":
                templine[0] = prevline[0]
                break
            elif prevline[index] != "" and templine[index] == "":
                templine[index] = prevline[index]

        for index in [10,11,12,13]:
            if templine[index] == "〃":
                templine[index] = prevline[index]
        return templine

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
                    if lineno < 2:
                        outline = self._set_header(outline, prevline=prevline)
                    if lineno == 1:
                        #print(outline)
                        writer.writerow(outline)
                    # remove all blank lines from content
                    if outline[4] == "":
                        continue;
                    if lineno > 1:
                        outline = self._set_record(outline,prevline)
                        outline[addressindex] = cp.addxform(outline[addressindex])
                        #print(outline)
                        writer.writerow(outline)
                    lineno += 1
                    prevline = outline
        except:
            raise
        finally:
            w_fileno.close()

    def process_pdf(self, pdffile, skippage ):
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
                    pivotregexp=self.regexppivot, ignorecounter=0,
                    multipage=True, fileno=filecounter, headercol = 2,
                )
                filecounter += 1
        except Exception:
            raise
        finally:
            tempfileno.close()
        self._process_csv(tempout, outfile, self.addressindex)
        self.dq_check(auditfile=self.auditfile, pdffile=pdffile, outfile=outfile, auditout=dqout)

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