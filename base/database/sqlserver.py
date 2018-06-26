import pyodbc
import pypyodbc
import os
import pandas as pd
try:
    from .BaseConnection import BaseConnection
except:
    from base.database.BaseConnection import BaseConnection


class SQLServer(BaseConnection):
    def __init__(self, module=None, log=None):
        super(SQLServer, self).__init__(log=log)
        self.conn = None
        self.module = module
        self.driver = 'SQL Server'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

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

    def _get_connection(self, sectionname, passphrase=None):
        if self.conn is not None:
            return
        config = self.get_config_details(sectionname, passphrase)
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

    def connect(self, sectionname, passphrase=None):
        self._get_connection(sectionname, passphrase)
        return self.conn

    def disconnect(self):
        if self.conn is not None:
            self.log.info("Disconnecting From Database")
            self.conn.close()
            self.conn = None

    def run_query(self, query, sectionname, passphrase=None):
        conn = self.connect(sectionname=sectionname, passphrase=passphrase)
        cursor = conn.cursor()
        query = self._clean_query(query=query)
        self.log.info("Executing Query: {}".format(query))
        result = cursor.execute(query)
        cursor.commit()
        cursor.close()
        return result

    def sql_to_df(self, query, sectionname, passphrase=None):
        conn = self.connect(sectionname=sectionname, passphrase=passphrase)
        query = self._clean_query(query=query)
        self.log.info("Executing Query: {}".format(query))
        data = pd.read_sql(query, conn)
        return data
