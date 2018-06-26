from base.utils import base_util as bu


def add_authorization():
    from base.database.CredentialManager import CredentialManager
    homedir = "C:/users/{}".format(bu.current_user())
    configdir = "{}/codes/python/gdim/Projects/local/base/database".format(
        homedir
    )
    configfile = "{}/password.cfg".format(configdir)
    try:
        credman = CredentialManager(
            configfile=configfile
        )
        credman.add_credential(
            sectionname="DEVELOPMENT_SQL",
            host_name='USVDCVMSQL21.DelphiPrd.Am.JonesLangLaSalle.com\SQL2014',
            passphrase='This is my message',
            database='GDIMRegApac',
            user='EDWAPACUser_RW',
            password='EDw@pacRead&write',
            dbtype='MSSQLServer',
            protocol='Server Authentication'
        )
    except IOError as e:
        print(e.message)


def get_authorization():
    from base.database.CredentialManager import CredentialManager
    homedir = "C:/users/{}".format(bu.current_user())
    configdir = "{}/codes/python/gdim/Projects/local/base/database".format(
        homedir
    )
    configfile = "{}/password.cfg".format(configdir)
    passphrase = 'This is my message'
    try:
        credman = CredentialManager(
            configfile=configfile
        )
        config = credman.get_credential(sectionname="DEVELOPMENT_SQL",
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


# add_authorization()
get_authorization()
