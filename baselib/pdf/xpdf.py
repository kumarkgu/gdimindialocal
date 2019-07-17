import subprocess
import re
import os
import shutil


class PDFException(Exception):
    pass


class PDFUnreadableFont(PDFException):
    def __init__(self, message, errno=-17201):
        self.message = message
        self.errono = errno
        super(PDFUnreadableFont, self).__init__(message, errno)


class PDFManualProcess(PDFException):
    def __init__(self, message, errno=-17202):
        self.message = message
        self.errono = errno
        super(PDFManualProcess, self).__init__(message, errno)


class XpdfPdfProcess:
    def __init__(self, utilpath, log=None):
        self.utilpath = utilpath
        self.log = log
        self.mode = None
        self.utility = None
        self.regspace = re.compile(r'\s+')

    def _set_utility(self, mode=None):
        self.mode = mode if mode else "totext"
        self.utility = "{0}/pdf{1}.exe".format(self.utilpath, self.mode)

    def execute_command(self, command):
        try:
            subprocess.call(command)
        except Exception as e:
            self.log.info(
                "ERROR: While executing command: {0}. Error: {1}".format(
                    command, str(e)
                )
            )
            raise

    def _set_corr_file(self, filename):
        if self.regspace.search(filename):
            return r'"%s"' % filename
        else:
            return filename

    def pdf_to_text(self, filename, outformat=None):
        paramoption = "{} -fixed 2".format(outformat) if outformat \
            else "table -fixed 2"
        self._set_utility()
        command = "{0} -q -{1} {2}".format(
            self.utility,
            paramoption,
            self._set_corr_file(filename=filename)
        )
        self.execute_command(command)

    def pdf_to_html(self, filename, htmldir=None):
        html_dir = htmldir if htmldir else "{0}/html".format(
            os.path.dirname(filename)
        )
        if os.path.isdir(html_dir):
            shutil.rmtree(html_dir, ignore_errors=True)
        self._set_utility("tohtml")
        command = "{0} -q {1} {2}".format(
            self.utility,
            self._set_corr_file(filename=filename),
            html_dir
        )
        self.execute_command(command)

    def pdf_to_png(self, filename, pngroot=None):
        imgroot = pngroot if pngroot else "{0}/{1}".format(
            os.path.dirname(filename), os.path.basename(filename)
        )
        if os.path.isfile(imgroot + ".png"):
            os.remove(imgroot + ".png")
        self._set_utility("topng")
        command = "{0} {1} {2}".format(
            self.utility,
            self._set_corr_file(filename=filename),
            imgroot
        )
        self.execute_command(command)

    def _pdf_get_fonts(self, filename):
        self._set_utility("fonts")
        command = "{0} {1}".format(
            self.utility,
            self._set_corr_file(filename=filename)
        )
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        return iter(proc.stdout.readline, b'')

    def is_unreadable_pdf(self, filename):
        lineno = 0
        totalno = 0
        regexp = re.compile(r'\[none\]')
        for fontline in self._pdf_get_fonts(filename=filename):
            lineno += 1
            currline = fontline.decode('utf-8').strip()
            if regexp.match(currline):
                totalno += 1
        if totalno == lineno - 2:
            return True
        else:
            return False
