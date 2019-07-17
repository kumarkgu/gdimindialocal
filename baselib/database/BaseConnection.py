import os
from baselib.utils import base_util as bu
from baselib.utils.Logger import Logger
try:
    from .CredentialManager import CredentialManager
except ImportError:
    from baselib.database.CredentialManager import CredentialManager
# from . import CredentialManager as cm


class BaseConnection:
    """
    Base class for connection
    """
    _NO_MONGO_CONN = "Connection Name: {} defined is not a connection to " \
                     "Mongo DB.{}Check the name and try again"
    _NO_MSSQL_CONN = "Connection Name: {} defined is not a connection to " \
                     "MS SQL Server.{}Check the name and try again"

    _KEY_NAME = "Name"
    _KEY_TYPE = "Type"
    _USER_NAME = "User Name"
    _PASS_WORD = "Pass Word"
    _SERVER = "Server"
    _PORT_NUMBER = "Port Number"
    _PROTOCOL = "Connection Protocol"
    _CRED_OWNER = "Credential Owner"
    _AUTHORIZED_USER = "Authorized User"
    _DB_TYPE = "Database Type"
    _SSL_CONNECTION = "SSL Connection"
    _SSL_CERTIFICATION = "SSL Certification"
    _DB_NAME = "Database Name"
    _MODULE_NAME = "Module Name"
    _CRED_KEYWORD = {
        "MongoDB": {
            _USER_NAME: {
                _KEY_NAME: "user",
                _KEY_TYPE: "optional"
            },
            _PASS_WORD: {
                _KEY_NAME: "password",
                _KEY_TYPE: "optional"
            },
            _SERVER: {
                _KEY_NAME: "server",
                _KEY_TYPE: "mandatory"
            },
            _PORT_NUMBER: {
                _KEY_NAME: "port",
                _KEY_TYPE: "mandatory"
            },
            _PROTOCOL: {
                _KEY_NAME: "protocol",
                _KEY_TYPE: "optional"
            },
            _CRED_OWNER: {
                _KEY_NAME: "owner",
                _KEY_TYPE: "optional"
            },
            _AUTHORIZED_USER: {
                _KEY_NAME: "authorized_user",
                _KEY_TYPE: "optional"
            },
            _DB_TYPE: {
                _KEY_NAME: "dbtype",
                _KEY_TYPE: "mandatory"
            },
            _DB_NAME: {
                _KEY_NAME: "database",
                _KEY_TYPE: "mandatory"
            },
            _SSL_CONNECTION: {
                _KEY_NAME: "ssl_connection",
                _KEY_TYPE: "optional"
            },
            _SSL_CERTIFICATION: {
                _KEY_NAME: "ssl_certification",
                _KEY_TYPE: "optional"
            }
        },
        "MSSQLServer": {
            _USER_NAME: {
                _KEY_NAME: "user",
                _KEY_TYPE: "optional"
            },
            _PASS_WORD: {
                _KEY_NAME: "password",
                _KEY_TYPE: "optional"
            },
            _SERVER: {
                _KEY_NAME: "server",
                _KEY_TYPE: "mandatory"
            },
            _DB_NAME: {
                _KEY_NAME: "database",
                _KEY_TYPE: "mandatory"
            },
            _PORT_NUMBER: {
                _KEY_NAME: "port",
                _KEY_TYPE: "optional"
            },
            _CRED_OWNER: {
                _KEY_NAME: "owner",
                _KEY_TYPE: "optional"
            },
            _PROTOCOL: {
                _KEY_NAME: "protocol",
                _KEY_TYPE: "optional"
            },
            _AUTHORIZED_USER: {
                _KEY_NAME: "authorized_user",
                _KEY_TYPE: "optional"
            },
            _DB_TYPE: {
                _KEY_NAME: "dbtype",
                _KEY_TYPE: "mandatory"
            },
            _MODULE_NAME: {
                _KEY_NAME: "module",
                _KEY_TYPE: "optional"
            }
        }
    }

    def __init__(self, config=None, log=None):
        if config is None:
            self.configfile = self._get_config_file()
        self.log = log if log else Logger("DatabaseConnection").getlog()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _get_config_file(self):
        return "{}{}{}".format(
            os.path.dirname(__file__),
            bu.get_path_separator(),
            "password.cfg"
        )

    def get_config_details(self, sectionname, passphrase):
        try:
            credential = CredentialManager(self.configfile)
            config = credential.get_credential(sectionname, passphrase)
        except ValueError:
            raise
        return config

    def get_detail(self):
        return self.configfile, self.configfile
