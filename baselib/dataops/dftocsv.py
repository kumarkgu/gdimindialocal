import pandas as pd
from baselib.utils import objects as objs


class DFToCSV:
    def __init__(self, **kwargs):
        self.datetimeformat = None
        self.dateformat = None
        self.separator = None
        self.header = None
        # self.line_terminator = None
        self._setcsvprop(**kwargs)

    def _setcsvprop(self, **kwargs):
        dtfmt = "%d-%b-%Y %H:%M:%S"
        # dfmt = dtfmt[:dtfmt.find(" ")].strip()
        self.datetimeformat = kwargs.get("datetimeformat", dtfmt)
        self.dateformat = kwargs.get("dateformat", dtfmt)
        self.separator = kwargs.get("separator", ",")
        self.header = kwargs.get("header", True)

    def savetocsv(self, filename, dfs, cols=None, index_header=None,
                  index=True):
        filename = objs.return_list(filename)
        dfs = objs.return_list(dfs)
        for idx, df in enumerate(dfs):
            t_fname = filename[idx]
            if cols:
                if index:
                    df.to_csv(t_fname, sep=self.separator,
                              columns=cols, header=self.header,
                              date_format=self.dateformat,
                              index_label=index_header)
                else:
                    df.to_csv(t_fname, sep=self.separator,
                              columns=cols, header=self.header,
                              date_format=self.dateformat,
                              index=index)
            else:
                if index:
                    df.to_csv(t_fname, sep=self.separator,
                              header=self.header, date_format=self.dateformat,
                              index_label=index_header)
                else:
                    df.to_csv(t_fname, sep=self.separator,
                              header=self.header, date_format=self.dateformat,
                              index=index)

    @staticmethod
    def readcsv(csvfile, **kwargs):
        return pd.read_csv(csvfile, **kwargs)
