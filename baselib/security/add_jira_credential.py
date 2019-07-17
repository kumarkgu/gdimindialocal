from baselib.security.credentialmanager import CredentialManager
from baselib.utils import fileobjects as fo
import os


def _get_config_file():
    # tdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tdir = os.path.dirname(os.path.abspath(__file__))
    tdir = "{}/config".format(tdir)
    if not os.path.isdir(tdir):
        fo.create_dir(tdir)
    return "{}/credentials.cfg".format(tdir)


def _get_passphrase():
    passphrase = input("Please enter passphrase: ")
    return passphrase


def _get_password():
    password = input("Please enter password to store: ")
    return password


def add_jira_credential(**kwargs):
    cfgfile = kwargs.get("configfile", _get_config_file())
    try:
        passphrase = kwargs.get("passphrase", None)
        if passphrase is None:
            passphrase = _get_passphrase()
        password = kwargs.get("password", None)
        auth_user = kwargs.get("authorized_users", None)
        if password is None:
            password = _get_password()
        credman = CredentialManager(configfile=cfgfile)
        if auth_user is None:
            credman.add_credential(
                sectionname=kwargs.get("sectionname"),
                host_name=kwargs.get("host_name"),
                passphrase=passphrase,
                project=kwargs.get("project"),
                user=kwargs.get("user"),
                password=password,
                dbtype=kwargs.get("dbtype"),
            )
        else:
            credman.add_credential(
                sectionname=kwargs.get("sectionname"),
                host_name=kwargs.get("host_name"),
                passphrase=passphrase,
                project=kwargs.get("project"),
                user=kwargs.get("user"),
                password=password,
                dbtype=kwargs.get("dbtype"),
                authorized_users=auth_user
            )
    except IOError as ex:
        print(ex.message)


def add_db_credential(**kwargs):
    cfgfile = kwargs.get("configfile", _get_config_file())
    try:
        credman = CredentialManager(configfile=cfgfile)
        passphrase = kwargs.get("passphrase", _get_passphrase())
        user = kwargs.get("user", None)
        auth_user = kwargs.get("authorized_users", None)
        if user:
            password = kwargs.get("password", None)
            if password is None:
                password = _get_password()
            if auth_user is None:
                credman.add_credential(
                    sectionname=kwargs.get("sectionname"),
                    host_name=kwargs.get("host_name"),
                    passphrase=passphrase,
                    user=user,
                    password=password,
                    dbtype=kwargs.get("dbtype", "MSSQLServer"),
                    database=kwargs.get("database")
                )
            else:
                credman.add_credential(
                    sectionname=kwargs.get("sectionname"),
                    host_name=kwargs.get("host_name"),
                    passphrase=passphrase,
                    user=user,
                    password=password,
                    dbtype=kwargs.get("dbtype", "MSSQLServer"),
                    database=kwargs.get("database"),
                    authorized_users=auth_user
                )
        else:
            if auth_user is None:
                credman.add_credential(
                    sectionname=kwargs.get("sectionname"),
                    host_name=kwargs.get("host_name"),
                    passphrase=passphrase,
                    dbtype=kwargs.get("dbtype", "MSSQLServer"),
                    database=kwargs.get("database")
                )
            else:
                credman.add_credential(
                    sectionname=kwargs.get("sectionname"),
                    host_name=kwargs.get("host_name"),
                    passphrase=passphrase,
                    dbtype=kwargs.get("dbtype", "MSSQLServer"),
                    database=kwargs.get("database"),
                    authorized_users = auth_user
                )
    except IOError as ex:
        print(ex.message)


def get_credential(**kwargs):
    configfile = kwargs.get("configfile", _get_config_file())
    passphrase = kwargs.get("passphrase", None)
    if passphrase is None:
        passphrase = _get_passphrase()
    sectionname = kwargs.get("sectionname")
    try:
        credman = CredentialManager(
            configfile=configfile
        )
        config = credman.get_credential(sectionname=sectionname,
                                        passphrase=passphrase)
        for key, value in config.items():
            print(
                "Key: {}. Value: {}".format(
                    key,
                    value
                )
            )
    except IOError as e:
        print(e.message)
