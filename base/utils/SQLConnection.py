import pyodbc
import sys


class MSSqlConnection:
    def __init__(self, server, database=None, user=None, password=None):
        self.server = server
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.cursor = None

    def connect(self, log=None):
        if self.conn is None:
            connstr = 'DRIVER={SQL Server};SERVER=%s' % self.server
            connmessage = connstr
            if self.database:
                connstr += ';DATABASE={}'.format(self.database)
                connmessage += ';DATABASE={}'.format(self.database)
            if self.user and self.password:
                connstr += ';UID={};PWD={}'.format(self.user, self.password)
                connmessage += ';UID={};PWD=****'.format(self.user)
            if log:
                log.info("Connecting to {}".format(connmessage))
            else:
                print("Connecting to {}".format(connmessage))
            try:
                self.conn = pyodbc.connect(connstr)
                self.cursor = self.conn.cursor()
                if log:
                    log.info("SQL Connection Established")
                else:
                    print("SQL Connection Established")
            except Exception as err:
                if log:
                    log.info("***ERROR***: SQL Connection Failed")
                    log.info(err)
                else:
                    print("***ERROR***: SQL Connection Failed")
                    print(err)
                sys.exit(1)

    def disconnect(self, log=None):
        if self.cursor is not None:
            self.cursor = None
        if self.conn is not None:
            self.conn.close()
            if log:
                log.info("SQL Connection Closed")
            else:
                print("SQL Connection Closed")
            self.conn = None
