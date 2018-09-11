import os
# import re
import shutil
from datetime import datetime
from base.utils import excelprocess as ep
from base.utils.setprocesspath import RunProcess
from base.utils.Logger import Logger
from base.utils import base_util as bu
from jobs.igr import igrpdftext as iptext
from jobs.igr import igrpdfhtml as iphtml
from base.pdf import xpdf as xpdf
try:
    from .igrexpressions import IGRExpressions
except Exception:
    from jobs.igr.igrexpressions import IGRExpressions


class ProcessIgr(RunProcess):
    def __init__(self, processname, log=None, homepath=None, projpath=None,
                 utilpath=None, boxpath=None, conn_name=None, keymesg=None):
        super(ProcessIgr, self).__init__(
            processname=processname, projpath=projpath, utilpath=utilpath,
            sourcepath=boxpath, homepath=homepath, log=log
        )
        self.textregex = IGRExpressions(conn_name=conn_name, passphrase=keymesg,
                                        ishtml=False, log=log, isothers=True)
        self.htmlregex = IGRExpressions(conn_name=conn_name, passphrase=keymesg,
                                        ishtml=True, log=log, isothers=True)
        self.headermap = self.textregex.headermap
        self.allheaders = self.textregex.headerorder
        self.errorheader = self.textregex.errorheader
        self.defsectionname = self.textregex.defsectionname

    def build_initial(self, copyfrombase=False, basedir=False, logdir=False,
                      rawdir=False, processdir=False, errordir=False,
                      tempdir=False):
        self.build_process_directory(
            basedir=basedir, logdir=logdir, rawdir=rawdir, errordir=errordir,
            tempdir=tempdir, processdir=processdir
        )
        if copyfrombase:
            self.copy_rawfiles(sourcefiles=True)

    @staticmethod
    def add_fileinfo(file, directory, datadict=None, message=None):
        basename = os.path.basename(file)
        filewoextn = str(basename.rsplit('.', 1)[0])
        filedetail = "_".join(filewoextn.split(".")).split("_")
        datadict["CTSNo"] = filedetail[1]
        datadict["Year"] = filedetail[0][-4:]
        datadict["DocumentNo"] = "_".join(filedetail[2:])
        datadict["Village"] = directory
        if message:
            datadict["message"] = message

    @staticmethod
    def append_to_excel(worksheet, data, header=None):
        try:
            assert isinstance(data, list)
            output = worksheet.get_excel_columns(data=data, header=header)
        except AssertionError:
            output = worksheet.get_excel_columns(data=[data])
        worksheet.append_to_ws(output)

    def _get_final_path(self, dirpath=None, village=None, filename=None):
        filedirectory = os.path.join(dirpath, village)
        self.create_dir(filedirectory)
        return os.path.join(filedirectory, filename)

    def move_files(self, dirpath, village, filename):
        finaldirectory = self._get_final_path(
            dirpath=dirpath, village=village,
            filename=os.path.basename(filename)
        )
        shutil.move(filename, finaldirectory)
        # os.remove(filename)

    def process(self, folder=None, filename=None, outfile=None, errorfile=None,
                **kwargs):
        self.log.info("Started Processing Files")
        self.build_initial(
            copyfrombase=kwargs.get('copyfrombase', False),
            basedir=kwargs.get('basedir', False),
            rawdir=kwargs.get('rawdir', False),
            errordir=kwargs.get('errordir', False),
            tempdir=kwargs.get('tempdir', False),
            processdir=kwargs.get('processdir', False),
            logdir=kwargs.get('logdir', False)
        )
        if folder:
            subfolder = [folder]
        else:
            subfolder = self.get_subdirectory(self.rawpath)
        if not subfolder:
            return False
        # __vmode = kwargs.get('mode', "pdftotext")
        wsdata = ep.ExcelWorkBook(
            outfile, "Output", kwargs.get('exceloverwrite', False)
        )
        wserror = ep.ExcelWorkBook(
            errorfile, "Error", kwargs.get('exceloverwrite', False)
        )
        # Now initialize both html and text mode
        xpdftext = iptext.XPdfText(
            self.utilpath, regexpclass=self.textregex,
            defsectionname=self.defsectionname, headermap=self.headermap,
            allheaders=self.allheaders, log=self.log
        )
        xpdfhtml = iphtml.XPdfHtml(
            self.utilpath, defsectionname=self.defsectionname,
            headermap=self.headermap, allheaders=self.allheaders,
            regexpclass=self.htmlregex, log=self.log
        )
        for currfolder in subfolder:
            filedirectory = os.path.join(self.rawpath, currfolder)
            self.log.info("Processing Directory: {}".format(filedirectory))
            if filename:
                filelist = [
                    "{0}/{1}/{2}.pdf".format(
                        self.rawpath, folder, filename
                    )
                ]
            else:
                filelist = self.get_files(filedirectory, full=True)
            datalist = []
            for currfile in filelist:
                self.log.info("..Processing File: {}".format(currfile))
                counternumber = 0
                datadict = {}
                # If file has space then rename the file and process the same
                try:
                    datadict = xpdftext.process(currfile, self.temppath)
                except xpdf.PDFUnreadableFont:
                    errmsg = "....PDF: {} font is unreadable. Processing" \
                             " Next".format(currfile)
                    self.log.info(errmsg)
                    errmsg = "Font Unreadable"
                    counternumber = -1
                except xpdf.PDFManualProcess:
                    self.log.info(
                        "....PDF: {} cannot be read as Text. Switcing to "
                        "HTML processing".format(currfile)
                    )
                    counternumber = 1
                except Exception as e:
                    errmsg = "ERROR: Processing Next file. {}".format(str(e))
                    self.log.info(errmsg)
                    errmsg = str(e)
                    counternumber = -1
                if counternumber == 1:
                    try:
                        datadict = xpdfhtml.process(currfile, self.temppath)
                    except Exception as e:
                        errmsg = "....PDF: {0} cannot be processed. " \
                                 "Processing Next. Error: {1}".format(
                                    currfile,
                                    str(e)
                                 )
                        self.log.info(errmsg)
                        errmsg = str(e)
                        counternumber = -1
                if counternumber == -1:
                    datadict = {}
                    self.add_fileinfo(
                        currfile, currfolder, message=errmsg, datadict=datadict
                    )
                    self.append_to_excel(wserror, data=datadict,
                                         header=self.errorheader)
                    self.move_files(self.errorpath, currfolder, currfile)
                    continue
                self.add_fileinfo(
                    currfile, currfolder, datadict=datadict
                )
                self.log.info("....Appending the data to the list")
                datalist.append(datadict)
                self.log.info("....Moving File to the final directory")
                self.move_files(self.procpath, currfolder, currfile)
            if len(datalist) > 0:
                self.log.info("..Writing data to the excel file")
                self.append_to_excel(wsdata, datalist,
                                     header=self.allheaders)
            self.remove_dir(filedirectory)
        self.log.info(
            "Saving Excel File(s)=>{0}"
            "Output File: {1}{0}"
            "Error File: {2}".format(
                os.linesep,
                outfile,
                errorfile
            )
        )
        wsdata.save_wb_objects(outfile)
        wserror.save_wb_objects(errorfile)


def run_igr_process(folder=None, file=None):
    homedir = "C:/Users/{}".format(bu.current_user())
    processname = "IGR"
    log = Logger(processname).getlog()
    projpath = "{}/Documents/JLL/Projects/Research/IGR/process".format(homedir)
    utilpath = "{}/Softwares/xpdf/bin64".format(homedir)
    boxpath = "{}/Box Sync/ResearchData/IGRData/Unprocessed".format(homedir)
    foldername = folder
    filename = file
    currdatetime = datetime.now().strftime("%Y%m%d")
    dataexcel = "{0}/igrdata_{1}.xlsx".format(projpath, currdatetime)
    errorexcel = "{0}/igrdata_err_{1}.xlsx".format(projpath, currdatetime)
    connname = "DEVELOPMENT_SQL"
    keymesg = "This is my message"
    oprocess = ProcessIgr(
        processname=processname, log=log, projpath=projpath, utilpath=utilpath,
        boxpath=boxpath, homepath=homedir, conn_name=connname, keymesg=keymesg
    )
    oprocess.process(
        folder=foldername, filename=filename, outfile=dataexcel,
        errorfile=errorexcel
    )


run_igr_process(folder=None, file=None)

# dsection = {
#     "1": "Type of document",
#     "2": "Reward",
#     "3": "Quotation (details of the lease in relation to the lease, "
#          "that the sergeant should specify)",
#     "4": "Land measuring, portals and home number (if any)",
#     "5": "area",
#     "6": "When the levy or connection is given.",
#     "9": "Date of the date of the document",
#     "10": "The date of registration of the document",
#     "11": "serial numbers, volumes and pages",
#     "12": "Stamp duty as per market price",
#     "13": "Registration Fee as per marketable",
#     "14": "Remarks"
# }

# dmapcolumn = {
#     "Document Type": ["Type of", "Type of document", "Article", "Title",
#                       "Type of document (Title)"],
#     "Village Name": ["Name of the village", "Village Name"],
#     "Filing Number": ["serial numbers, volumes and pages",
#                       "Serial Numbers, Sections And Pages",
#                       "Registration Number / Year",
#                       "Registration Number/Year",
#                       "Filing No."],
#     "Filing Amount": ["Filing Amount", "Total Filing"],
#     "Registration Date": ["The date of registration of the document",
#                           "Date of Registartion", "Date of filing"],
#     "Submission Date": ["Date of the date of the document",
#                         "Date of submission", "Date of Execution"],
#     "Stamp Duty": [re.compile(r'^Stamp Duty', re.IGNORECASE)],
#     "Registration Fee": [re.compile(r'^Registration Fee', re.IGNORECASE)],
#     "Area": [re.compile(r'^Area', re.IGNORECASE)],
#     "Remarks": [re.compile(r'^Remark', re.IGNORECASE)]
# }

# lheader = [
#     "Year",
#     "Village",
#     "CTSNo",
#     "DocumentNo",
#     "Village Name",
#     "Document Type",
#     "Filing Number",
#     "Registration Date",
#     "Submission Date",
#     "Date Of Mortgage",
#     "Building Name",
#     "Property Description",
#     "Area",
#     "Stamp Duty",
#     "Filing Amount",
#     "Loan Amount",
#     "Quotation (details Of The Lease In Relation To The Lease, That The "
#     "Sergeant Should Specify)",
#     "Reward",
#     "Registration Fee",
#     "Deposit",
#     "Rent",
#     "When The Levy Or Connection Is Given.",
#     "Land Measuring, Portals And Home Number (if Any)",
#     "Name Or Address Of The Respondent, If The Decree Or Order Of The "
#     "Court",
#     "If The Name Of The Party To Which The Document Is Written / Written "
#     "Or The Order Or Order Of The Civil Court, The Name And Address Of "
#     "The Reply.",
#     "Licencee Name And Address",
#     "Licencsor Name And Address",
#     "Mortgagor",
#     "Mortgagee",
#     "Assesment Or Judi",
#     "Remarks",
#     "Details Taken For The Assessment",
#     "Selected Article On Stamp Duty"
# ]

# lerror = [
#     "Year",
#     "Village",
#     "CTSNo",
#     "DocumentNo",
#     "message"
# ]
