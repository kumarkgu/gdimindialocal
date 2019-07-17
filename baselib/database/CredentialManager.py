import configparser
import os
from baselib.utils import security as sec
from baselib.utils import base_util as bu
from baselib.utils import objects as ob
try:
    from .UserAuthorization import UserAuthorization
except ImportError:
    from baselib.database.UserAuthorization import UserAuthorization
# from . import UserAuthorization as ua


class CredentialManager:
    _SECTION_NO_EXIST = "Section: {} does not exists in the password file{}" + \
                        "Please add a section or change values and try again"
    _USER_NOT_UPD_AUTH = "User: {} is not authorized to update the " \
                         "access list for{}configuration: {}"
    _BLANK_USER_LIST = "User List: cannot contain blank value{}" + \
                       "Please input correct value and try again"
    _USER_NOT_ACC_AUTH = "User: {} is not Authorized to access the " \
                         "configuration {}file to get server credentials for " \
                         "Environment: {}"
    _AUTH_FILE_NOT_EXIST = "User Authentication File: {} does not exists.{}" \
                           "Either it has been deleted or no users have been " \
                           "authorized to access credentials"
    _USER_NOT_EXIST = "Users specified in to remove access from section: {}" \
                      "does not exists in access list"
    _FILE_NOT_TRUE = "File: {} cannot be created or accessed.{}" \
                     "Possible case:{}" \
                     "1. It is a directory already available{}" \
                     "2. It is already an object in the System"

    def __init__(self, configfile, listsep=';;;'):
        self.configfile = configfile
        self.curruser = bu.current_user()
        self.authfile = self._get_auth_file(configfile)
        self.listsep = listsep

    def _get_auth_file(self, configfile):
        return "{}{}{}".format(
            os.path.dirname(configfile),
            bu.get_path_separator(),
            "userauth.cfg"
        )

    def _get_config(self, sectionname):
        config = configparser.ConfigParser()
        config.read(self.configfile)
        try:
            config = config[sectionname]
            retdict = dict(config.items())
        except configparser.NoSectionError:
            raise configparser.NoSectionError(sectionname)
        return retdict

    def _merge_config(self, sectionname, sections, runmethod='new'):
        config = configparser.ConfigParser()
        fileexistflag = 1
        sectionexistflag = 1
        try:
            with open(self.configfile) as cfgfile:
                config.read_file(cfgfile)
        except IOError:
            fileexistflag = 0
            sectionexistflag = 0
        # Now check if section exists
        if fileexistflag == 1:
            try:
                config = config[sectionname]
            except configparser.NoSectionError:
                sectionexistflag = 0
            except KeyError:
                sectionexistflag = 0
            if sectionexistflag == 0:
                for section in config.sections():
                    config.remove_section(section)
        else:
            sectionexistflag = 0
        if runmethod.upper() == 'NEW':
            if sectionexistflag == 1:
                raise configparser.DuplicateSectionError(sectionname)
            else:
                config.add_section(sectionname)
                for key, value in sections.items():
                    config.set(sectionname, key, value)
        elif runmethod.upper() == 'UPDATE':
            if fileexistflag == 0:
                raise IOError
            if sectionexistflag == 0:
                raise configparser.NoSectionError(sectionname)
            else:
                for key, value in sections.items():
                    config.set(sectionname, key, value)
        modeflag = 'w' if fileexistflag == 0 else 'a'
        with open(self.configfile, modeflag) as cfgfile:
            config.write(cfgfile)

    def _get_owner_list(self, owners, passphrase):
        ownerlist = []
        for owner in owners.split(self.listsep):
            ownerlist.append(sec.decrypt(passphrase, owner))
        return ownerlist

    def _add_authorization(self, section, authlist):
        if authlist is not None:
            userlist = authlist.split(';')
            authorization = UserAuthorization(self.authfile)
            authorization.add_user_authorization(section, userlist)

    def _get_authorization(self, section):
        check = False
        if section is not None:
            authorization = UserAuthorization(self.authfile)
            check = authorization.check_user_authorized(section)
        return check

    def _remove_authorization(self, section, authlist):
        if authlist is not None:
            userlist = authlist.split(';')
            authorization = UserAuthorization(self.authfile)
            authorization.remove_user_from_section(section, userlist)

    def add_credential(self, sectionname, host_name, passphrase, **kwargs):
        """
            :param sectionname: The section header which is to be added to the
                             config file
            :param host_name: Server Name/Host Name
            :param passphrase: Passphrase which is used for encrypting and
                               decrypting
            :param kwargs: Set of keywords and values which are system dependant
            :return: Nothing
        """
        from functools import reduce
        config = {'server': host_name}
        # Now generate the key, and then encrypt the password
        numberflag = 0
        if kwargs:
            for key, value in kwargs.items():
                if key.upper() == 'AUTHORIZED_USERS' or \
                   key.upper() == 'CURRENT_USER':
                    continue
                if key.upper() == "USER":
                    numberflag += 1
                if key.upper() == "PASSWORD":
                    numberflag += 10
                config[key.lower()] = (str(value) if ob.isint(value) else value)
        if numberflag == 0 or numberflag == 10:
            config['user'] = 'None'
            config['password'] = 'None'
        elif numberflag == 1:
            config['password'] = 'None'
        else:
            config['password'] = sec.encrypt(passphrase,
                                             str(config['password']))
            if 'owner' in config:
                config['owner'] = reduce(
                    lambda x, y: x + self.listsep + y,
                    list(map(
                        lambda x: sec.encrypt(passphrase, x),
                        config['owner'].split(';')
                    )))
            else:
                config['owner'] = sec.encrypt(passphrase, self.curruser)

        if 'dbtype' not in config:
            config['dbtype'] = 'MSSQLServer'
        if numberflag == 0 or numberflag == 1 or numberflag == 10:
            config['protocol'] = 'Windows Authentication'
            if 'owner' in config:
                del config['owner']
        else:
            config['protocol'] = 'Server Authentication'

        try:
            self._merge_config(sectionname, config)
        except IOError:
            raise IOError(
                self._FILE_NOT_TRUE.format(
                    self.configfile,
                    os.linesep,
                    os.linesep,
                    os.linesep
                )
            )
        except configparser.DuplicateSectionError:
            raise
        except configparser.NoSectionError:
            raise
        if kwargs:
            for key, value in kwargs.items():
                if (key.upper() == 'AUTHORIZED_USERS' and
                   value.strip != ""):
                    self._add_authorization(sectionname, value)

    def get_credential(self, sectionname, passphrase=None):
        try:
            config = self._get_config(sectionname)
        except configparser.NoSectionError:
            raise
        # First check if user is authorized to use and get details
        if config['protocol'] == 'Windows Authentication':
            if config["user"] == 'None':
                del config["user"]
            if config["password"] == "None":
                del config["password"]
            return config
        config["owner"] = self._get_owner_list(config["owner"], passphrase)
        if (False if self.curruser.upper() in list(map(lambda x: x.upper(),
                                                       config["owner"])
                                                   ) else True):
            try:
                isauthorized = self._get_authorization(sectionname)
                if not isauthorized:
                    raise ValueError(
                        self._USER_NOT_ACC_AUTH.format(
                            self.curruser,
                            os.linesep,
                            sectionname
                        )
                    )
            except ValueError:
                raise
            except FileNotFoundError:
                raise
        config["password"] = sec.decrypt(passphrase, config["password"])
        return config

    def add_access(self, sectionname, userlist, passphrase):
        if userlist.strip() == "":
            raise ValueError(self._BLANK_USER_LIST.format(os.linesep))
        try:
            config = self._get_config(sectionname)
        except configparser.NoSectionError:
            raise
        except KeyError:
            raise ValueError(
                self._SECTION_NO_EXIST.format(
                    sectionname,
                    os.linesep
                )
            )
        # First check if user is authorized to use and get details
        config["owner"] = self._get_owner_list(config["owner"], passphrase)
        if (False if self.curruser.upper() in list(map(lambda x: x.upper(),
                                                       config["owner"])
                                                   ) else True):
            raise ValueError(
                self._USER_NOT_UPD_AUTH.format(
                    self.curruser,
                    os.linesep,
                    sectionname
                )
            )
        self._add_authorization(sectionname, userlist)

    def remove_access(self, sectionname, userlist, passphrase):
        if userlist.strip() == "":
            raise ValueError(self._BLANK_USER_LIST.format(os.linesep))
        try:
            config = self._get_config(sectionname)
        except configparser.NoSectionError:
            raise
        except KeyError:
            raise ValueError(
                self._SECTION_NO_EXIST.format(
                    sectionname,
                    os.linesep
                )
            )
        # First check if user is authorized to use and get details
        config["owner"] = self._get_owner_list(config["owner"], passphrase)
        if (False if self.curruser.upper() in list(map(lambda x: x.upper(),
                                                       config["owner"])
                                                   ) else True):
            raise ValueError(
                self._USER_NOT_UPD_AUTH.format(
                    self.curruser,
                    os.linesep,
                    sectionname
                )
            )
        self._remove_authorization(sectionname, userlist)
