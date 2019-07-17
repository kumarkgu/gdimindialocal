import pyodbc
import pypyodbc
import os
import pandas as pd
import datetime
from urllib.parse import quote_plus
from .baseconnection import BaseConnection
import sqlalchemy


class SQLServer(BaseConnection):
    def __init__(self, module=None, log=None):
        super(SQLServer, self).__init__(log=log)
        self.conn = None
        self.engine = None
        self.module = module
        self.driver = 'SQL Server'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        self.close_engine()

    def _get_conn_string(self, config):
        connstring = "DRIVER={%s}" % self.driver
        credential = self._CRED_KEYWORD["MSSQLServer"]
        try:
            module = config[credential[self._MODULE_NAME][self._KEY_NAME]]
        except KeyError:
            module = 'pyodbc'
        connstring += ";SERVER={}".format(
            config[credential[self._SERVER][self._KEY_NAME]]
        )
        msgstring = connstring
        try:
            tempstr = credential[self._DB_NAME][self._KEY_NAME]
            if config[tempstr]:
                connstring += ";DATABASE={}".format(
                    config[tempstr]
                )
                msgstring = connstring
            tempstr = credential[self._PROTOCOL][self._KEY_NAME]
            userkey = credential[self._USER_NAME][self._KEY_NAME]
            if config[tempstr]:
                protocol = config[tempstr]
            else:
                if config[userkey] and config[userkey].upper() != "NONE":
                    protocol = "Server Authentication"
                else:
                    protocol = "Windows Authentication"
            if protocol == "Server Authentication":
                if not config[userkey] or config[userkey].upper() == "NONE":
                    raise IndexError
                connstring += ";UID={}".format(config[userkey])
                passkey = credential[self._PASS_WORD][self._KEY_NAME]
                if config[passkey]:
                    msgstring = "{};PWD={}".format(connstring, "*****")
                    connstring += ";PWD={}".format(config[passkey])
            else:
                connstring += ";Trusted_Connection=yes"
                msgstring = connstring
        except IndexError:
            raise
        except KeyError:
            pass
        return [connstring, msgstring, module]

    def _get_module(self, config, credential):
        try:
            module = config[credential[self._MODULE_NAME][self._KEY_NAME]]
        except KeyError:
            module = "pyodbc"
        return module

    def _get_driver(self, driver=None):
        driver = self.driver if not driver else "SQL Server Native Client 10.0"
        return driver

    @staticmethod
    def _get_quote_string(config, **kwargs):
        protocol = kwargs.get("protocol", None)
        dbname = kwargs.get("dbname", None)
        user = kwargs.get("user", None)
        passwd = kwargs.get("passwd", None)
        connstr = "DRIVER={%s}" % kwargs.get("driver")
        connstr += ";SERVER={}".format(config[kwargs.get("server")])
        msgstr = connstr
        try:
            if dbname and config[dbname]:
                connstr += ";DATABASE={}".format(config[dbname])
                msgstr = connstr
            if protocol in config and config[protocol]:
                t_auth = config[protocol]
            else:
                if user and config[user] and config[user].upper() != "NONE":
                    t_auth = "Server Authentication"
                else:
                    t_auth = "Windows Authentication"
            if t_auth == "Server Authentication":
                if not config[user] or config[user].upper() == "NONE":
                    raise IndexError
                connstr += ";UID={}".format(config[user])
                if passwd and config[passwd]:
                    msgstr = "{};PWD={}".format(connstr, "*****")
                    connstr += ";PWD={}".format(config[passwd])
            else:
                connstr += ";Trusted_Connection=yes"
                msgstr = connstr
        except IndexError:
            raise
        except KeyError:
            pass
        return [connstr, msgstr]

    def _build_list_args(self, credential, driver=None):
        keydict = dict({
            self._SERVER: "server",
            self._PROTOCOL: "protocol",
            self._DB_NAME: "dbname",
            self._USER_NAME: "user",
            self._PASS_WORD: "passwd"
        })
        retdict = dict({"driver": self._get_driver(driver=driver)})
        for key, value in keydict.items():
            retdict[value] = credential[key][self._KEY_NAME]
        return retdict

    def _build_alchemy_string(self, config):
        credential = self._CRED_KEYWORD["MSSQLServer"]
        module = self._get_module(config=config, credential=credential)
        argdict = self._build_list_args(credential, driver="New")
        t_string = self._get_quote_string(config=config, **argdict)
        self.log.info("Connecting String: {}".format(t_string[1]))
        params = quote_plus(t_string[0])
        t_str = "mssql+{}".format(module)
        t_str += ":///?odbc_connect=%s" % params
        self.engine = sqlalchemy.create_engine(t_str)

    def alchemy_engine(self, sectionname, passphrase, newdbname=None,
                       resetdbname=False):
        if not resetdbname and self.engine is not None:
            return
        else:
            config = self.get_config_details(sectionname, passphrase)
            if self.engine is not None:
                self.close_engine()
            creds = self._CRED_KEYWORD["MSSQLServer"]
            if resetdbname and newdbname is not None:
                config[creds[self._DB_NAME][self._KEY_NAME]] = newdbname
            try:
                if config['dbtype'].upper() != 'MSSQLSERVER':
                    raise ValueError(
                        self._NO_MSSQL_CONN.format(sectionname, os.linesep)
                    )
                self._build_alchemy_string(config)
            except ValueError:
                raise

    def _get_connection(self, sectionname, passphrase=None,
                        newdbname=None, resetdbname=False):
        if not resetdbname and self.conn is not None:
            return
        else:
            config = self.get_config_details(sectionname, passphrase)
            if self.conn is not None:
                self.disconnect()
            credential = self._CRED_KEYWORD["MSSQLServer"]
            config[credential[self._DB_NAME][self._KEY_NAME]] = newdbname
        try:
            if config['dbtype'].upper() != 'MSSQLSERVER':
                raise ValueError(
                    self._NO_MSSQL_CONN.format(sectionname, os.linesep)
                )
            returnval = self._get_conn_string(config=config)
            self.log.info("Connecting: {}".format(returnval[1]))
            if returnval[2] == "pypyodbc":
                self.conn = pypyodbc.connect(returnval[0])
            else:
                self.conn = pyodbc.connect(returnval[0])
        except ValueError:
            raise

    @staticmethod
    def _clean_query(query):
        query = query.strip()
        query = query.replace("\n", " ")
        query = query.replace("\r", " ")
        query = " ".join(query.split())
        return query

    def reconnect(self, sectionname, dbname, passphrase=None):
        self._get_connection(sectionname, passphrase,
                             newdbname=dbname, resetdbname=True)
        return self.conn

    def connect(self, sectionname, passphrase=None):
        self._get_connection(sectionname, passphrase)
        return self.conn

    def disconnect(self):
        if self.conn is not None:
            self.log.info("Disconnecting From Database")
            self.conn.close()
            self.conn = None

    def close_engine(self):
        if self.engine is not None:
            self.log.info("Resetting Alchemy Engine")
            self.engine = None

    def run_query(self, query, sectionname=None, passphrase=None, iscommit=True,
                  iffetch=False, params=None):
        conn = self.connect(sectionname=sectionname, passphrase=passphrase)
        cursor = conn.cursor()
        query = self._clean_query(query=query)
        self.log.info("Executing Query: {}".format(query))
        if params:
            result = cursor.execute(query, params)
        else:
            result = cursor.execute(query)
        if iffetch:
            result = []
            while True:
                row = cursor.fetchone()
                if row is None:
                    break
                result.append(row)
        if iscommit:
            cursor.commit()
        cursor.close()
        return result

    def sql_to_df(self, query, sectionname, passphrase=None, dbname=None,
                  loginfo=True):
        if dbname is None:
            conn = self.connect(sectionname=sectionname, passphrase=passphrase)
        else:
            conn = self.reconnect(sectionname=sectionname,
                                  passphrase=passphrase, dbname=dbname)
        query = self._clean_query(query=query)
        if loginfo:
            self.log.info("Executing Query: {}".format(query))
        data = pd.read_sql(query, conn)
        return data

    def sql_to_df_timed(self, query, sectionname, passphrase=None):
        conn = self.connect(sectionname=sectionname, passphrase=passphrase)
        query = self._clean_query(query=query)
        self.log.info("Executing Query: {}".format(query))
        starttime = datetime.datetime.now()
        data = pd.read_sql(query, conn)
        endtime = datetime.datetime.now()
        deltatime = endtime - starttime
        return [data, starttime, endtime, deltatime]

    @staticmethod
    def sql_df_to_sql(df, table, sectionname, schema=None,
                      if_exists="append"):
        try:
            assert isinstance(df, pd.DataFrame)
        except AssertionError:
            raise Exception("Data provided is not of Dataframe")
