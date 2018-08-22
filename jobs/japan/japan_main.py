import os
from base.pdf.japan import JapanProcess


def run_process(yearmonth):

    homedir = "C:/users/{}".format(os.getlogin())
    projectdir = "{}/Documents/JLL/Projects/JapanPdfToText/Files".format(
        homedir
    )
    rawdir = "{}/rawfiles/{}".format(projectdir, yearmonth)
    processdir = "{}/process".format(projectdir)
    xpdfdir = "{}/Softwares/xpdf/bin64".format(projectdir)
    tabuladir = "{}/Softwares/Tabula/tabula-java".format(projectdir)
    dqdir = "{}/dq".format(projectdir)
    tabjarfile = "tabula-1.0.2-jar-with-dependencies.jar"
    auditfile = "csv_dq.xlsx"
    oprocess = JapanProcess(rawdir=rawdir, processdir=processdir,
                            xpdfdir=xpdfdir, tabuladir=tabuladir,
                            tabulajarfile=tabjarfile, dqdir=dqdir,
                            auditfile=auditfile)
    oprocess.process_files()

run_process("201805")
