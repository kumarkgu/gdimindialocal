import os
import shutil
import glob
from baselib.utils import fileobjects as fo
from baselib.utils import Logger as lo


class JapanProcess:
    def __init__(self, rawdir, processdir=None, xpdfdir=None, tabuladir=None,
                 tabulajarfile=None, auditfile = None, **kwargs):
        self.rawdir = rawdir
        self.processdir = processdir
        self.xpdfdir = xpdfdir
        self.tabuladir = tabuladir
        self.tabulajar = tabulajarfile
        self.auditfile = auditfile
        self.processname = kwargs.get('processname', 'japan')
        self.dates = kwargs.get('dates', os.path.basename(rawdir))
        self.tempname = kwargs.get('tempname', "temp/{}".format(self.dates))
        self.outputname = kwargs.get('outname', "output/{}".format(self.dates))
        self.dqname = kwargs.get('dqtname', "{}/dq".format(self.outputname))
        self.archivename = kwargs.get(
            'archivename', "archive/{}".format(self.dates)
        )
        self.filetype = {
            #"Xymax": 0,
            "XymaxED": 0,
            "XymaxKansai":0,
            #"Nissay": 0,
            "MFBM": 0,
            "MitsuiFudosan": 0,
            "NoumuraFudongsanPartner": 0,
            "Apple":0,
            "CRE":0,
            "PureJapan":0,
        }
        self.log = kwargs.get('log', self._set_logger())

    def _set_logger(self):
        return lo.Logger(self.processname).getlog()

    def create_base_directory(self):
        self.log.info(
            "..Creating Process Directory: {}".format(self.processdir)
        )
        fo.create_dir(self.processdir)
        self.log.info(
            "..Creating Temporary Directory: {}/{}".format(
                self.processdir, self.tempname
            )
        )

        fo.create_dir("{}/{}".format(self.processdir, self.tempname))
        self.log.info(
            "..Creating Output Directory: {}/{}".format(
                self.processdir, self.outputname
            )
        )

        if os.path.exists("{}/{}".format(self.processdir, self.dqname)):
            shutil.rmtree("{}/{}".format(self.processdir, self.dqname))
        fo.create_dir("{}/{}".format(self.processdir, self.dqname))
        self.log.info(
            "..Creating dq Directory: {}/{}".format(
                self.processdir, self.dqname
            )
        )

        fo.create_dir("{}/{}".format(self.processdir, self.outputname))
        self.log.info(
            "..Creating Archive Directory: {}/{}".format(
                self.processdir, self.archivename
            )
        )
        fo.create_dir("{}/{}".format(self.processdir, self.archivename))


    def create_object(self, objectname):
        return objectname(
            tabuladir=self.tabuladir, tabulajarfile=self.tabulajar,
            xpdfdir=self.xpdfdir, processdir=self.processdir,
            tempname=self.tempname, outname=self.outputname,
            auditfile= self.auditfile,
        )

    def process_files(self):
        self.log.info("Creating Base Directories")
        self.create_base_directory()
        for pdffile in glob.glob("{}/*.pdf".format(self.rawdir)):
            basepdf = os.path.basename(pdffile)
            self.log.info("Processing File: {}".format(basepdf))
            keyname = ""
            keyvalue = 0
            fileprocess = False
            for key, value in self.filetype.items():
                #print(key)
                if basepdf.lower().find(key.lower()) >= 0:
                    keyname = key
                    keyvalue = value
                    break
            if keyname == "XymaxED":
                if keyvalue == 0:
                    from jobs.japan.base.jp_xymaxED import XymaxED
                    o_xymaxED = self.create_object(XymaxED)
                    self.filetype["XymaxED"] = 1
                o_xymaxED.process_pdf(pdffile=pdffile, skippage = 1)
                fileprocess = True
            if keyname == "XymaxKansai":
                if keyvalue == 0:
                    from jobs.japan.base.jp_xymaxKansai import XymaxKansai
                    o_xymaxKansai = self.create_object(XymaxKansai)
                    self.filetype["XymaxKansai"] = 1
                o_xymaxKansai.process_pdf(pdffile=pdffile, skippage=0)
                fileprocess = True
            # elif keyname == "Xymax":
            #     if keyvalue == 0:
            #         from baselib.pdf.jp_xymax import Xymax
            #         o_xymax = self.create_object(Xymax)
            #         self.filetype["Xymax"] = 1
            #     o_xymax.process_pdf(pdffile=pdffile)
            #     fileprocess = True
            elif keyname == "MFBM":
                if keyvalue == 0:
                    from jobs.japan.base.jp_mfbm import MFBMFile
                    o_mfbm = self.create_object(MFBMFile)
                    self.filetype["MFBM"] = 1
                o_mfbm.process_pdf(pdffile=pdffile)
                fileprocess = True
            elif keyname == 'Nissay':
                if keyvalue == 0:
                    from jobs.japan.base.jp_Nissay import Nissay
                    o_nissay = self.create_object(Nissay)
                    self.filetype["Nissay"] = 1
                o_nissay.process_pdf(pdffile= pdffile, skippage = 1)
                fileprocess = True
            elif keyname == 'MitsuiFudosan':
                if keyvalue == 0:
                    from jobs.japan.base.jp_MitsuiFudosan import MitsuiFudosan
                    o_MitsuiFudosan = self.create_object(MitsuiFudosan)
                    self.filetype["MitsuiFudosan"] = 1
                o_MitsuiFudosan.process_pdf(pdffile= pdffile)
                fileprocess = True
            elif keyname in ('NomuraFudosanPartners'):
                if keyvalue == 0:
                    from jobs.japan.base.jp_NomuraFudosanPartners import NomuraFudosanPartners
                    o_NomuraFudosanPartners = self.create_object(NomuraFudosanPartners)
                    self.filetype["NomuraFudosanPartners"] = 1
                o_NomuraFudosanPartners.process_pdf(pdffile= pdffile, skippage = 2)
                fileprocess = True
            elif keyname in ('Apple'):
                if keyvalue == 0:
                    from jobs.japan.base.jp_apple import Apple
                    o_Apple = self.create_object(Apple)
                    self.filetype["Apple"] = 1
                o_Apple.process_pdf(pdffile= pdffile)
                fileprocess = True
            elif keyname in ('CRE'):
                if keyvalue == 0:
                    from jobs.japan.base.jp_cre import CRE
                    o_CRE = self.create_object(CRE)
                    self.filetype["CRE"] = 1
                o_CRE.process_pdf(pdffile= pdffile)
                fileprocess = True
            elif keyname in ('PureJapan'):
                if keyvalue == 0:
                    from jobs.japan.base.jp_PureJapan import PureJapan
                    o_PureJapan = self.create_object(PureJapan)
                    self.filetype["PureJapan"] = 1
                o_PureJapan.process_pdf(pdffile=pdffile)
                fileprocess = True
            else:
                pass
            if fileprocess:
                self.log.info("..Moving File to Archive Directory")
                fo.move_file(
                    pdffile,
                    "{}/{}".format(self.processdir, self.archivename)
                )
