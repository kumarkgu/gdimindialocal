import os
import glob
from base.utils import fileobjects as fo
from base.utils import Logger as lo


class JapanProcess:
    def __init__(self, rawdir, processdir=None, xpdfdir=None, tabuladir=None,
                 tabulajarfile=None, dqdir=None, auditfile=None, **kwargs):
        self.rawdir = rawdir
        self.processdir = processdir
        self.xpdfdir = xpdfdir
        self.tabuladir = tabuladir
        self.tabulajar = tabulajarfile
        self.dqdir = dqdir
        self.auditfile = auditfile
        self.processname = kwargs.get('processname', 'japan')
        self.dates = kwargs.get('dates', os.path.basename(rawdir))
        self.tempname = kwargs.get('tempname', "temp/{}".format(self.dates))
        self.outputname = kwargs.get('outname', "output/{}".format(self.dates))
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
        fo.create_dir("{}/{}".format(self.processdir, self.outputname))
        self.log.info(
            "..Creating Output Directory: {}/{}".format(
                self.processdir, self.archivename
            )
        )
        fo.create_dir("{}/{}".format(self.processdir, self.archivename))

    def create_object(self, objectname):
        return objectname(
            tabuladir=self.tabuladir, tabulajarfile=self.tabulajar,
            xpdfdir=self.xpdfdir, processdir=self.processdir,
            tempname=self.tempname, outname=self.outputname
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
                print(key)
                if basepdf.lower().find(key.lower()) >= 0:
                    keyname = key
                    keyvalue = value
                    break
            if keyname == "XymaxED":
                if keyvalue == 0:
                    from base.pdf.jp_xymaxED import XymaxED
                    o_xymaxED = self.create_object(XymaxED)
                    self.filetype["XymaxED"] = 1
                o_xymaxED.process_pdf(pdffile=pdffile, skippage = 1)
                fileprocess = True
            if keyname == "XymaxKansai":
                if keyvalue == 0:
                    from base.pdf.jp_xymaxKansai import XymaxKansai
                    o_xymaxKansai = self.create_object(XymaxKansai)
                    self.filetype["XymaxKansai"] = 1
                o_xymaxKansai.process_pdf(pdffile=pdffile, skippage=0)
                fileprocess = True
            # elif keyname == "Xymax":
            #     if keyvalue == 0:
            #         from base.pdf.jp_xymax import Xymax
            #         o_xymax = self.create_object(Xymax)
            #         self.filetype["Xymax"] = 1
            #     o_xymax.process_pdf(pdffile=pdffile)
            #     fileprocess = True
            elif keyname == "MFBM":
                if keyvalue == 0:
                    from base.pdf.jp_mfbm import MFBMFile
                    o_mfbm = self.create_object(MFBMFile)
                    self.filetype["MFBM"] = 1
                o_mfbm.process_pdf(pdffile=pdffile)
                fileprocess = True
            elif keyname == 'Nissay':
                if keyvalue == 0:
                    from base.pdf.jp_Nissay import Nissay
                    o_nissay = self.create_object(Nissay)
                    self.filetype["Nissay"] = 1
                o_nissay.process_pdf(pdffile= pdffile, skippage = 1)
                fileprocess = True
            elif keyname == 'MitsuiFudosan':
                if keyvalue == 0:
                    from base.pdf.jp_MitsuiFudosan import MitsuiFudosan
                    o_MitsuiFudosan = self.create_object(MitsuiFudosan)
                    self.filetype["MitsuiFudosan"] = 1
                o_MitsuiFudosan.process_pdf(pdffile= pdffile)
                fileprocess = True
            elif keyname in ('NomuraFudosanPartners'):
                if keyvalue == 0:
                    from base.pdf.jp_NomuraFudosanPartners import NomuraFudosanPartners
                    o_NomuraFudosanPartners = self.create_object(NomuraFudosanPartners)
                    self.filetype["NomuraFudosanPartners"] = 1
                o_NomuraFudosanPartners.process_pdf(pdffile= pdffile, skippage = 2)
                fileprocess = True
            else:
                pass
            if fileprocess:
                self.log.info("..checking data quality against audit file:" + self.dqdir + self.auditfile)


                self.log.info("..Moving File to Archive Directory")
                fo.move_file(
                    pdffile,
                    "{}/{}".format(self.processdir, self.archivename)
                )
