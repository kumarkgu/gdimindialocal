import os
from base.pdf.japan import JapanProcess


def run_process(yearmonth):
    homedir = "C:/users/{}".format(os.getlogin())
    projectdir = "{}/Documents/JLL/Projects/JapanPdfToText/Files".format(
        homedir
    )
    rawdir = "{}/rawfiles/{}".format(projectdir, yearmonth)
    processdir = "{}/process".format(projectdir)
    xpdfdir = "{}/Softwares/xpdf/bin64".format(homedir)
    tabuladir = "{}/Softwares/Tabula/tabula-java".format(homedir)
    tabjarfile = "tabula-1.0.2-jar-with-dependencies.jar"
    oprocess = JapanProcess(rawdir=rawdir, processdir=processdir,
                            xpdfdir=xpdfdir, tabuladir=tabuladir,
                            tabulajarfile=tabjarfile)
    oprocess.process_files()


run_process("201801")
