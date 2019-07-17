import re
import datetime
from baselib.utils import stringops as sops


class DateOperations:
    _MONTH_MAP = {
        "01": "Jan",
        "02": "Feb",
        "03": "Mar",
        "04": "Apr",
        "05": "May",
        "06": "Jun",
        "07": "Jul",
        "08": "Aug",
        "09": "Sep",
        "10": "Oct",
        "11": "Nov",
        "12": "Dec"
    }

    def __init__(self):
        self.regexdate = {
            "date_ddmm": re.compile(r"(\d+)[-.\s]+(\d+)\s*$"),
            "date_ddmmyy": re.compile(r"(\d+)[-.]+(\d+)[-.]+(\d+)"),
            "date_ddmonyy": re.compile(r"(\d+)(th)*[-.]*([A-Za-z]+)[-.]*(\d+)"),
            "date_ddmon": re.compile(r"(\d+)(th)*[-.\s]*([A-Za-z]+)\s*")
        }

    @staticmethod
    def name_number(string, montomm=False):
        if not montomm:
            string = sops.lpad(string=string, length=2, char="0")
        for key, value in DateOperations._MONTH_MAP.items():
            if montomm:
                if value.lower() == string.lower():
                    return key
            else:
                if key == string:
                    return value
        return None

    @staticmethod
    def yy_to_yyyy(string):
        retval = string.strip()
        if len(retval) == 2:
            year = int(retval)
            prepend = "20" if year < 50 else "19"
            retval = "{}{}".format(prepend, retval)
        return retval

    def date_ddmmyy(self, regmatch):
        if regmatch:
            day = sops.lpad(string=regmatch.group(1), length=2, char="0")
            month = sops.lpad(string=regmatch.group(2), length=2, char="0")
            year = self.yy_to_yyyy(regmatch.group(3))
            retdate = "{0}-{1}-{2}".format(year, month, day)
        else:
            retdate = None
        return retdate

    def date_ddmonyy(self, regmatch):
        if regmatch:
            day = sops.lpad(string=regmatch.group(1), length=2, char="0")
            month = self.name_number(string=regmatch.group(3), montomm=True)
            year = self.yy_to_yyyy(regmatch.group(4))
            retdate = "{0}-{1}-{2}".format(year, month, day)
        else:
            retdate = None
        return retdate

    @staticmethod
    def date_ddmm(regmatch):
        if regmatch:
            day = sops.lpad(string=regmatch.group(1), length=2, char="0")
            month = sops.lpad(string=regmatch.group(2), length=2, char="0")
            year = datetime.datetime.now().strftime("%Y")
            retdate = "{0}-{1}-{2}".format(year, month, day)
        else:
            retdate = None
        return retdate

    def date_ddmon(self, regmatch):
        if regmatch:
            day = sops.lpad(string=regmatch.group(1), length=2, char="0")
            month = self.name_number(string=regmatch.group(3), montomm=True)
            year = datetime.datetime.now().strftime("%Y")
            retdate = "{0}-{1}-{2}".format(year, month, day)
        else:
            retdate = None
        return retdate

    @staticmethod
    def dateformat(indate, informat="%Y-%m-%d", outformat="%d-%b-%Y",
                   isucase=False):
        mydate = datetime.datetime.strptime(indate, informat)
        retdate = mydate.strftime(outformat)
        if isucase:
            return retdate.upper()
        else:
            return retdate

    def normalify_date(self, string, outformat=None, isucase=False):
        dtstring = None
        outformat = outformat if outformat else "%d-%b-%Y"
        funclist = sorted(list(self.regexdate.keys()), reverse=True)
        # for funcname, regex in self.regexdate.items():
        for funcname in funclist:
            regex = self.regexdate[funcname]
            regmatch = regex.match(string)
            if regmatch:
                func = getattr(self, funcname)
                dtstring = func(regmatch)
                break
        if dtstring is None:
            return None
        else:
            return self.dateformat(dtstring, outformat=outformat,
                                   isucase=isucase)

    @staticmethod
    def currdate(oformat=None):
        if oformat is not None:
            return datetime.datetime.now().strftime(oformat)
        else:
            return datetime.datetime.now()

    @staticmethod
    def comparedate(strdate1, strdate2, infrmt1="%Y-%m%d", infrmt2="%Y-%m%d"):
        try:
            assert isinstance(strdate1, datetime.datetime)
            date1 = strdate1
        except AssertionError:
            try:
                assert isinstance(strdate1, datetime.time)
                date1 = datetime.datetime(2019, 1, 1)
            except AssertionError:
                date1 = datetime.datetime.strptime(strdate1, infrmt1)
        try:
            assert isinstance(strdate2, datetime.datetime)
            date2 = strdate2
        except AssertionError:
            try:
                assert isinstance(strdate2, datetime.time)
                date2 = datetime.datetime(2019, 1, 1)
            except AssertionError:
                date2 = datetime.datetime.strptime(strdate2, infrmt2)
        if date2 >= date1:
            return True
        else:
            return False


class TimeConversion:
    def __init__(self):
        self.regextimedf = re.compile(r"(\s*\d+)(\s*\D*\s*)", re.IGNORECASE)
        self.timemap = self._time_map()
        self.regtimefill = re.compile(r"xx", re.IGNORECASE)

    def _time_map(self):
        t_map = dict({
            "sec": {
                "Variable": ["s", "ss", "sec"],
                "Function": "time_to_seconds",
                "Format": "00:00:XX"
            },
            "min": {
                "Variable": ["m", "mi", "min"],
                "Function": "time_to_minutes",
                "Format": "00:XX:00"
            },
            "hour": {
                "Variable": ["h", "hh", "hour"],
                "Function": "time_to_hours",
                "Format": "XX:00:00"
            },
        })
        return t_map

    @staticmethod
    def time_to_seconds(timestr):
        ftr = [3600, 60, 1]
        timesec = sum(
            [a * b for a,b in zip(ftr, [int(i) for i in timestr.split(":")])]
        )
        return timesec

    @staticmethod
    def time_to_minutes(timestr):
        ftr = [60, 1, 1/60]
        timemin = round(sum(
            [a * b for a, b in zip(ftr, [int(i) for i in timestr.split(":")])]
        ), 3)
        return timemin

    @staticmethod
    def time_to_hour(timestr):
        ftr = [1, 1/60, 1/3600]
        timehour = round(sum(
            [a * b for a, b in zip(ftr, [int(i) for i in timestr.split(":")])]
        ), 3)
        return timehour

    def timedifftotime (self, timediff, convertto="ss"):
        regmatch = self.regextimedf.match(timediff)
        if not regmatch:
            raise Exception("Time Specified is not a valid Time Format")
        tperiod = regmatch.group(1).strip()
        tperiod = sops.lpad(tperiod, 2, "0")
        pertype = regmatch.group(2).strip().lower()
        pertype = "min" if not pertype or pertype == "" else pertype
        convertto = convertto.lower()
        t_time = None
        func = None
        for key, value in self.timemap.items():
            if pertype in value["Variable"]:
                if convertto in value["Variable"]:
                    return tperiod
                t_time = self.regtimefill.sub(tperiod, value["Format"])
                break
        if t_time is None:
            raise Exception("Undefined Time Type: {}".format(pertype))
        for key, value in self.timemap.items():
            if convertto in value["Variable"]:
                func = getattr(self, value["Function"])
                break
        if func is None:
            raise Exception("Undefined Time Convert Type: {}".format(convertto))
        tconvert = func(t_time)
        return tconvert
