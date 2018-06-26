import os
import glob
from base.utils import fileobjects as fo
from base.utils import Logger as lo


class JapanProcess:
    def __init__(self, rawdir, processdir=None, xpdfdir=None, tabuladir=None,
                 tabulajarfile=None, **kwargs):
        self.rawdir = rawdir
        self.processdir = processdir
        self.xpdfdir = xpdfdir
        self.tabuladir = tabuladir
        self.tabulajar = tabulajarfile
        self.processname = kwargs.get('processname', 'japan')
        self.dates = kwargs.get('dates', os.path.basename(rawdir))
        self.tempname = kwargs.get('tempname', "temp/{}".format(self.dates))
        self.outputname = kwargs.get('outname', "output/{}".format(self.dates))
        self.archivename = kwargs.get(
            'archivename', "archive/{}".format(self.dates)
        )
        self.filetype = {
            "Xymax": 0,
            "Nihon_Seimei": 0,
            "MFBM": 0
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
                if basepdf.lower().find(key.lower()) >= 0:
                    keyname = key
                    keyvalue = value
                    break
            if keyname == "Xymax":
                if keyvalue == 0:
                    from base.pdf.jp_xymax import Xymax
                    o_xymax = self.create_object(Xymax)
                    self.filetype["Xymax"] = 1
                o_xymax.process_pdf(pdffile=pdffile)
                fileprocess = True
            elif keyname == "MFBM":
                if keyvalue == 0:
                    from base.pdf.jp_mfbm import MFBMFile
                    o_mfbm = self.create_object(MFBMFile)
                    self.filetype["MFBM"] = 1
                o_mfbm.process_pdf(pdffile=pdffile)
                fileprocess = True
            else:
                pass
            if fileprocess:
                self.log.info("..Moving File to Archive Directory")
                fo.move_file(
                    pdffile,
                    "{}/{}".format(self.processdir, self.archivename)
                )
