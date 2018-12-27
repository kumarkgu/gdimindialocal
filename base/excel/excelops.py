import win32com.client
import time


class XlsOperations:
    def __init__(self):
        pass

    @staticmethod
    def refresh_ext_data(excelfile):
        xlapp = win32com.client.DispatchEx("Excel.Application")
        xlwb = xlapp.Workbooks.Open(excelfile)
        xlwb.RefreshAll()
        time.sleep(5)
        xlwb.Save()
        xlwb.Quit()


