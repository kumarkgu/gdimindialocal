import re
import os
from pymongo import MongoClient
try:
    from .BaseConnection import BaseConnection
except ImportError:
    from base.database.BaseConnection import BaseConnection
# from . import BaseConnection as bc


class MongoDBConn(BaseConnection):
    def __init__(self):
        super(MongoDBConn, self).__init__()
        self.mongodb = None
        self.client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def _prepare_uri(self, config):
        uri = "mongodb://"
        credential = self._CRED_KEYWORD["MongoDB"]
        try:
            if config[credential[self._USER_NAME][self._KEY_NAME]]:
                uri += config[credential[self._USER_NAME][self._KEY_NAME]]
                if config[credential[self._PASS_WORD][self._KEY_NAME]]:
                    uri += ":{}@".format(
                        config[credential[self._PASS_WORD][self._KEY_NAME]]
                    )
        except KeyError:
            pass
        try:
            if config[credential[self._SERVER][self._KEY_NAME]]:
                uri += config[credential[self._SERVER][self._KEY_NAME]]
        except KeyError:
            pass
        try:
            if config[credential[self._PORT_NUMBER][self._KEY_NAME]]:
                uri += ":{}".format(
                    config[credential[self._PORT_NUMBER][self._KEY_NAME]]
                )
        except KeyError:
            pass
        uri += "/"
        match = 0
        try:
            if config[credential[self._DB_NAME][self._KEY_NAME]]:
                uri += config[credential[self._DB_NAME][self._KEY_NAME]]
                tempstring = config[credential[self._DB_NAME][self._KEY_NAME]]
                if re.match(r'.*\?.*', tempstring):
                    uri += "&"
                    match = 1
        except KeyError:
            pass

        if match == 0:
            uri += "?"

        try:
            if config[
                credential[self._SSL_CONNECTION][self._KEY_NAME]
            ].lower() == "true":
                uri += "ssl=true&ssl_cert_reqs=CERT_NONE"
        except KeyError:
            pass
        # # End Change: 001-1
        return uri

    def _get_connection(self, sectionname, passphrase=None):
        config = self.get_config_details(sectionname, passphrase)
        try:
            if config['dbtype'].upper() != 'MONGODB':
                raise ValueError(
                    self._NO_MONGO_CONN.format(sectionname, os.linesep)
                )
            if self.mongodb:
                return
            # Now prepare uri for connecting to mongodb
            uri = self._prepare_uri(config)
            self.client = MongoClient(uri)
            try:
                # self.mongodb = self.client.get_default_database()
                self.mongodb = self.client.get_database()
            except Exception:
                self.client.close()
                del self.client
                raise
        except ValueError:
            raise

    def disconnect(self):
        if not self.client and not self.mongodb:
            return
        if self.mongodb:
            self.client.close()
            del self.client
            del self.mongodb

    def connect(self, sectionname, passphrase=None):
        self._get_connection(sectionname, passphrase)
        return self.mongodb, self.client


# def myconnect():
#     sectionname = "HawkMongoDBDev"
#     passphrase = "This is my message"
#     mongo = MongoDBConn()
#     (mongodb, mongoclient) = mongo.connect(sectionname=sectionname,
#                                            passphrase=passphrase)
#
#
# myconnect()
