from baselib.utils import objects as objs
import pandas as pd
import win32com.client
import time


class ExcelOps:
    def __init__(self):
        pass

    @staticmethod
    def refresh_ext_data(xlfile, sleeptime=5):
        xlapp = win32com.client.DispatchEx("Excel.Application")
        xlwb = xlapp.Workbooks.Open(xlfile)
        xlwb.RefreshAll()
        time.sleep(sleeptime)
        xlwb.Save()
        xlapp.Quit()

    @staticmethod
    def read_excel_to_df(filename, sheets=None):
        retdict = {}
        if sheets:
            sheets = objs.return_list(sheets)
            for sheet in sheets:
                retdict[sheet] = pd.read_excel(filename, sheet_name=sheet)
        else:
            retdict = pd.read_excel(filename, sheet_name=None)
        return retdict

