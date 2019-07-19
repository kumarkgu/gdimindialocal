import os
import urllib
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from baselib.utils import Logger as lo

class tosql():

    def __init__(self, processdir = None, yearmonth = None,auditfile = None, **kwargs):
        self.outdir = "{}/output/{}".format(processdir, yearmonth)
        self.auditfile = auditfile
        self.processname = kwargs.get('processname', 'japan')
        self.log = kwargs.get('log', self._set_logger())
        self.entities = ["Property", "Availability", "Owner", "Contact"]


    def _set_logger(self):
        return lo.Logger(self.processname).getlog()

    @staticmethod
    def sql_engine():
        _DRIVER = "SQL Server"
        _SERVER = "USLILVMGDIM01.DelphiPrd.Am.JonesLangLaSalle.com\INST01"
        _DB = "GDIMRegAPAC"
        _UID = ""
        _PSW = ""

        connstr = "DRIVER={};SERVER={};DATABASE={};UID={};PWD={};".format(_DRIVER, _SERVER, _DB, _UID, _PSW)
        connstr = urllib.parse.quote_plus(connstr)
        new_con = 'mssql+pyodbc:///?odbc_connect={}'.format(connstr)
        engine = create_engine(new_con)
        return engine

    @staticmethod
    def csv_to_df(csvpath):
        header = pd.read_csv(csvpath
                             ,error_bad_lines=False
                             ,sep=","
                             ,index_col=False
                             ,encoding="utf-8"
                             ,nrows=0)
        df = pd.read_csv(csvpath
                         ,error_bad_lines=False
                         ,sep=","
                         ,index_col=False
                         ,encoding="utf-8"
                         ,skiprows=1
                         ,names=header.columns)
        df.columns = df.columns.str.replace(" ", "")
        return df

    @staticmethod
    def mapping_to_df(mappingpath, entity, fudosan):
        df = pd.read_excel(mappingpath, sheetname=entity)
        df.columns = df.columns.str.replace(" ", "")
        out_df = None
        if fudosan in df.columns:
            out_df = df[["Field", fudosan]].dropna(subset=[fudosan])
        return out_df


    def df_remap(self, outdir, mappingpath, filename, entity):
        _now = datetime.now()
        _fudosan = filename.split("_")[0]
        _recievedate = filename.split("_")[1].replace(".csv", "")
        _csvpath = "{}/{}".format(outdir, filename)
        df = self.csv_to_df(_csvpath)

        _mapping = self.mapping_to_df(mappingpath, entity=entity, fudosan=_fudosan)

        if _mapping is None:
            return None

        out_df = pd.DataFrame(columns=_mapping["Field"], index=df.index)

        for index, row in _mapping.iterrows():
            if row[_fudosan] == "<Date run the process>":
                out_df[row["Field"]] = _now
            elif row[_fudosan] == "<Suffix date on the file name>":
                out_df[row["Field"]] = _recievedate
            elif "\"" in row[_fudosan]:
                out_df[row["Field"]] = row[_fudosan].replace("\"", "")
            else:
                out_df[row["Field"]] = df[row[_fudosan]]
        return out_df.drop_duplicates()


    def df_to_sql(self, df, entity):
        _engine = self.sql_engine()
        _schema = "JPN_IT_3S"
        _table = "ml_tbl_PDF" + entity

        if _engine.dialect.has_table(_engine, tablename=_table, schema=_schema):
            df.to_sql(name=_table, con=_engine, if_exists='append', schema=_schema, index=False)
        else:
            print("Please use baselib/pdf/Sqlquery to create the " + entity + " sql table first")

    def csv_to_sql(self):
        for file in os.listdir(self.outdir):
            filename = os.fsdecode(file)
            if filename.endswith(".csv") and "_" in filename:
                for entity in self.entities:
                    self.log.info(
                        "..[To SQL] - Uploading " + filename + " to " + entity + " SQL Table."
                    )
                    df = self.df_remap(self.outdir, self.auditfile, filename, entity)
                    if df is not None:
                        self.df_to_sql(df, entity)

# df = df_remap(outdir, mappingpath, filename, entity)
# df_to_sql(df, entity)
