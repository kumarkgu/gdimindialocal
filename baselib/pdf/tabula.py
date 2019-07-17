import subprocess


class TabulaPDF:
    def __init__(self, tabuladir=None, tabulajarfile=None):
        self.tabdir = tabuladir
        self.tabjarfile = tabulajarfile
        # self.tabulacmnd = self._set_tabula_command()

    def _set_tabula_command(self, runtype="lattice"):
        if runtype == "stream":
            return "java -Dfile.encoding=UTF-8 -jar {0}/{1} -t -p {2} -a {3}" \
                   " -i -f CSV -o {4} {5}"
        else:
            return "java -Dfile.encoding=UTF-8 -jar {0}/{1} -l -p {2} -a {3}" \
                   " -i -f CSV -o {4} {5}"

    def execute_tabula(self, pageno='all', boundary=None, outfile=None,
                       pdffile=None, runtype="lattice"):
        command = self._set_tabula_command(runtype=runtype).format(
            self.tabdir,
            self.tabjarfile,
            pageno,
            boundary,
            outfile,
            pdffile
        )
        try:
            subprocess.call(command)
        except Exception as e:
            raise
