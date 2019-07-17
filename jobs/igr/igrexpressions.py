import re
from baselib.database.sqlserver import SQLServer
from baselib.utils.Logger import Logger


class IGRExpressions:
    _TABLE_NAME = 'GDIMRegApac.IND_LA.PDF_Expressions'

    def __init__(self, conn_name, ishtml=False, passphrase=None,
                 log=None, isothers=False):
        self.log = log if log else Logger("IGR Process").getlog()
        self.proctype = "HTML" if ishtml else "Text"
        self.ishtml = ishtml
        self.conn_name = conn_name
        self.passphrase = passphrase
        self.query = """
            SELECT
                ProcessType,
                Expression,
                IsRegExp
            FROM
                {0}
            WHERE
                ModuleName = 'IGR'      AND
                CountryName = 'India'   AND
                SubModuleName = '{1}'   AND
                ProcessType =   CASE
                                    WHEN '{2}' = '' THEN ProcessType
                                    ELSE '{2}'
                                END     AND
                EndDate = '9999-12-31'
            ORDER BY
                ProcessType,
                OrderNumber
        """

        self.digitparan = None
        self.empty = None
        self.header = None
        self.headparan = None
        self.multihead = None
        self.multispace = None
        self.villagename = None

        self.alternatebegin = None
        self.title = None
        self.dataend = None
        self.ignore = None
        self.other_header = None
        self.sectionstart = None

        self.headermap = None
        self.headerorder = None
        self.buildingheader = None
        self.buildingcolumnname = None
        self.buildingname = None
        self.errorheader = None
        self.defsectionname = None

        self._set_base_regexp(isothers=isothers)
        self._set_all_expressions(isothers=isothers)

    def _set_base_regexp(self, isothers=False):
        if isothers:
            self.digitparan = re.compile(r'^\d\)')
            self.empty = re.compile(r'^\s*$')
            self.header = re.compile(r'^(\s*\()(\d+)(\)\s*)(\S*.*)')
            self.headparan = re.compile(
                r'^[\s*()]+([^\s()].*[^\s()])[\s()]*$'
            )
            self.multihead = re.compile(r'\s*\((\d+)\)\s*')
            self.multispace = re.compile(r'\s+')
            self.villagename = re.compile(r'\s*\d*\)*\s*(\D*)')

    @staticmethod
    def _get_expressions(dbhandler, submodule, basequery=None,
                         tablename=None, conn_name=None, passphrase=None):
        secdict = {}
        proctype = ""
        query = basequery.format(
            tablename,
            submodule,
            proctype
        )
        rawdf = dbhandler.sql_to_df(
            query,
            conn_name,
            passphrase
        )
        if rawdf.empty:
            return secdict
        for index, rows in rawdf.iterrows():
            key = rows['ProcessType']
            if not (key in secdict):
                secdict[key] = []
            if rows['IsRegExp'] == 1:
                secdict[key].append(
                    re.compile(rows['Expression'], re.IGNORECASE)
                )
            else:
                secdict[key].append(rows['Expression'])
        return secdict

    @staticmethod
    def _get_process_data(datadict, proctype=None):
        allproctype = "All"
        proctype = proctype if proctype else allproctype
        if proctype in datadict:
            return datadict[proctype]
        elif allproctype in datadict:
            return datadict[allproctype]
        return datadict

    def _set_all_expressions(self, isothers=False):
        allsubtypes = [
            "Alternate Begin",
            "Begin",
            "Data End",
            "Ignore",
            "Other Header",
            "Section Begin"
        ]
        with SQLServer(log=self.log) as dbhandler:
            for subtype in allsubtypes:
                self.log.info("Getting Detail For: {}".format(subtype))
                tempdata = self._get_expressions(
                    dbhandler=dbhandler,
                    submodule=subtype,
                    basequery=self.query,
                    tablename=self._TABLE_NAME,
                    conn_name=self.conn_name,
                    passphrase=self.passphrase
                )
                if subtype == "Alternate Begin":
                    self.alternatebegin = self._get_process_data(tempdata,
                                                                 self.proctype)
                elif subtype == "Begin":
                    self.title = self._get_process_data(tempdata, self.proctype)
                elif subtype == "Data End":
                    self.dataend = self._get_process_data(tempdata,
                                                          self.proctype)
                elif subtype == "Ignore":
                    self.ignore = self._get_process_data(tempdata,
                                                         self.proctype)
                elif subtype == "Other Header":
                    self.other_header = self._get_process_data(tempdata,
                                                               self.proctype)
                elif subtype == "Section Begin":
                    self.sectionstart = self._get_process_data(tempdata,
                                                               self.proctype)
            if isothers:
                subtype = "Column Mapping"
                self.log.info("Getting Detail For: {}".format(subtype))
                self.headermap = self._get_expressions(
                    dbhandler=dbhandler,
                    submodule=subtype,
                    basequery=self.query,
                    tablename=self._TABLE_NAME,
                    conn_name=self.conn_name,
                    passphrase=self.passphrase
                )

                subtype = "Column Header Order"
                self.log.info("Getting Detail For: {}".format(subtype))
                self.headerorder = self._get_expressions(
                    dbhandler=dbhandler,
                    submodule=subtype,
                    basequery=self.query,
                    tablename=self._TABLE_NAME,
                    conn_name=self.conn_name,
                    passphrase=self.passphrase
                )[subtype]

                subtype = "Building Header"
                self.log.info("Getting Detail For: {}".format(subtype))
                tempdata = self._get_expressions(
                    dbhandler=dbhandler,
                    submodule=subtype,
                    basequery=self.query,
                    tablename=self._TABLE_NAME,
                    conn_name=self.conn_name,
                    passphrase=self.passphrase
                )
                for key, value in tempdata.items():
                    self.buildingheader = value
                    self.buildingcolumnname = key
                    break

                subtype = self.buildingcolumnname
                self.log.info("Getting Detail For: {}".format(subtype))
                self.buildingname = self._get_expressions(
                    dbhandler=dbhandler,
                    submodule=subtype,
                    basequery=self.query,
                    tablename=self._TABLE_NAME,
                    conn_name=self.conn_name,
                    passphrase=self.passphrase
                )[subtype]

                subtype = "Error Header"
                self.log.info("Getting Detail For: {}".format(subtype))
                self.errorheader = self._get_expressions(
                    dbhandler=dbhandler,
                    submodule=subtype,
                    basequery=self.query,
                    tablename=self._TABLE_NAME,
                    conn_name=self.conn_name,
                    passphrase=self.passphrase
                )

                subtype = "Default Section Name"
                self.log.info("Getting Detail For: {}".format(subtype))
                tempdata = self._get_expressions(
                    dbhandler=dbhandler,
                    submodule=subtype,
                    basequery=self.query,
                    tablename=self._TABLE_NAME,
                    conn_name=self.conn_name,
                    passphrase=self.passphrase
                )
                self.defsectionname = {}
                for key, value in tempdata.items():
                    self.defsectionname[key] = "".join(value).strip()
