import pandas as pd


class BlossomContacts:
    _SHEET_NAME = "BlossomContacts"
    _COMPANY_NAME = "CompanyName"
    _CONTACT_NAME = "ContactName"
    _CONTACT_EMAIL = "ContactEmail"
    _CONTACT_PHONE = "ContactPhone"
    _USER_NAME = "UserName"
    _CITY = "City"

    def __init__(self, inputfile, **kwargs):
        self.sheetname = kwargs.get('sheetname', self._SHEET_NAME)
        self.companyname = kwargs.get('companyname', self._COMPANY_NAME)
        self.contactname = kwargs.get('contactname', self._CONTACT_NAME)
        self.contactemail = kwargs.get('contactemail', self._CONTACT_EMAIL)
        self.contactphone = kwargs.get('contactphone', self._CONTACT_PHONE)
        self.username = kwargs.get('username', self._USER_NAME)
        self.city = kwargs.get('city', self._CITY)
        self.inputfile = inputfile
        self.outfile = None
        self.wsdata = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._save_outwb()

    def _save_outwb(self):
        if self.outfile:
            self.wsdata.save_wb_objects(self.outfile)

    def read_excel(self, inputfile=None):
        if inputfile:
            self.inputfile = inputfile
        df = pd.read_excel(self.inputfile, sheetname=self.sheetname)
        return df



