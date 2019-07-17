import re
from baselib.utils import stringops as ts


class Company:
    def __init__(self, company=None, **kwargs):
        self.company = company if company else None
        self.removelist = kwargs.get('remove', None)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _set_remove_list(self, removelist):
        self.removelist = removelist

    def _set_company(self, company):
        self.company = company

    def _reset_vars(self, company=None, removelist=None):
        if not company:
            self.company = company
        if not removelist:
            self.removelist = removelist

    @staticmethod
    def _strip_vars(string, removelist=None):
        if not removelist:
            return string

    @staticmethod
    def clean_company(company, removelist=None):
        t_company = ts.clean_string()
        pass
