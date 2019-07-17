from baselib.utils import base_util as bu


def add_authorization():
    from baselib.security.credentialmanager import CredentialManager
    homedir = "C:/users/{}".format(bu.current_user())
    configdir = "{}/repos/gdimindialocal/baselib/database".format(
        homedir
    )
    configfile = "{}/credentials.cfg".format(configdir)
    try:
        credman = CredentialManager(
            configfile=configfile
        )
        credman.add_credential(
            sectionname="BLOSSOM_DATABASE",
            host_name='gimblossomsql.southcentralus.cloudapp.azure.com',
            passphrase='This is my message',
            database='BlossomUAT',
            user='blossomadmin',
            password='B100$0m1234$',
            dbtype='MSSQLServer',
            protocol='Server Authentication'
        )
    except IOError as e:
        print(e.message)


def get_authorization():
    from baselib.security.credentialmanager import CredentialManager
    homedir = "C:/users/{}".format(bu.current_user())
    configdir = "{}/repos/gdimindialocal/baselib/database".format(
        homedir
    )
    configfile = "{}/credentials.cfg".format(configdir)
    passphrase = 'This is my message'
    try:
        credman = CredentialManager(
            configfile=configfile
        )
        config = credman.get_credential(sectionname="BLOSSOM_DATABASE",
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


add_authorization()
# get_authorization()
