import copy


class DictOps:
    def __init__(self, clist=None, cdict=None, default=None):
        self.clist = clist
        self.cdict = cdict
        self.default = default

    def reset_list(self, clist):
        self.clist = clist

    def reset_dict(self, cdict):
        self.cdict = cdict

    def reset_defval(self, defval):
        self.default = defval

    @staticmethod
    def _setkeyvalue_cols(cdict, defval, cols, dtype="String"):
        retdict = cdict
        for col in cols:
            if col not in cdict:
                continue
            try:
                if not cdict[col]:
                    raise ValueError
                value = cdict[col]
            except ValueError:
                value = [defval] if dtype.lower() == "list" else defval
            retdict[col] = value
        return retdict

    @staticmethod
    def _setkeyvalue_all(cdict, defval, dtype="String"):
        retdict = {}
        for key in cdict:
            try:
                try:
                    value = cdict[key]
                except KeyError or ValueError:
                    raise ValueError
            except ValueError:
                value = [defval] if dtype.lower() == "list" else defval
            retdict[key] = value
        return retdict

    def _setdictdefault(self, cdict, defval, cols=None, dtype="String"):
        if cols:
            return self._setkeyvalue_cols(cdict, defval=defval, cols=cols,
                                          dtype=dtype)
        else:
            return self._setkeyvalue_all(cdict, defval=defval, dtype=dtype)

    def fillarrayofdict(self, cols=None, dtype="String"):
        retlist = []
        for tdict in self.clist:
            retlist.append(
                self._setdictdefault(
                    cdict=tdict, defval=self.default, cols=cols, dtype=dtype
                )
            )
        return retlist



