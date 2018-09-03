import os
from base.pdf.japan import JapanProcess
from base.pdf.jp_tosql import tosql

def run_process(yearmonth, name):

    homedir = "C:/users/{}".format(os.getlogin())
    projectdir = "{}/Documents/JLL/Projects/JapanPdfToText/Files".format(
        homedir
    )
    rawdir = "{}/rawfiles/{}".format(projectdir, yearmonth)
    processdir = "{}/process".format(projectdir)
    xpdfdir = "{}/Softwares/xpdf/bin64".format(projectdir)
    tabuladir = "{}/Softwares/Tabula/tabula-java".format(projectdir)
    tabjarfile = "tabula-1.0.2-jar-with-dependencies.jar"
    auditfile = "{}/dq/csv_dq.xlsx".format(projectdir)

    if name == "PDF":
        oprocess = JapanProcess(rawdir=rawdir, processdir=processdir,
                                xpdfdir=xpdfdir, tabuladir=tabuladir,
                                tabulajarfile=tabjarfile, auditfile=auditfile, )
        oprocess.process_files()
    if name == "Upload":
        oprocess = tosql(processdir = processdir
                         ,auditfile = auditfile
                         ,yearmonth = yearmonth)
        oprocess.csv_to_sql()

run_process("201805", "Upload")
