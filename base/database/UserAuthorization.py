import os
from base.utils import base_util as bu
from base.utils import security as sec


class UserAuthorization:
    _AUTH_FILE_NOT_EXIST = "User Authentication File: {} does not exists.{}" \
                           "Either it has been deleted or no users have been " \
                           "authorized to access credentials"
    _USER_NOT_EXIST = "Users specified in to remove access from section: {}" \
                      "does not exists in access list"

    def __init__(self, authfile):
        self.authfile = authfile
        self.curruser = bu.current_user()

    def _get_auth_userlist(self, section=None):
        userlist = []
        try:
            with open(self.authfile, 'r') as filenum:
                for line in filenum:
                    line = line.strip()
                    if section is None:
                        userlist.append(line)
                        continue
                    if line.startswith('#'):
                        continue
                    section = line[:line.find("=")].strip()
                    if section.upper() != section.upper():
                        continue
                    else:
                        userlist.append(
                            line[line.find("=") + 1:].lstrip())
        except FileNotFoundError:
            pass
        return userlist

    def _write_to_authfile(self, writelist, section=None, mode='a+'):
        with open(self.authfile, mode) as filenum:
            for line in writelist:
                # Now if section is None, it means we have to write the whole
                # line
                if section is None:
                    filenum.write("{}{}".format(line, os.linesep))
                else:
                    filenum.write(
                        "{}={}{}".format(
                            section,
                            sec.encrypt_password(line.upper),
                            os.linesep
                        )
                    )

    def check_user_authorized(self, section):
        check = False
        try:
            with open(self.authfile, 'r') as auth_file:
                for line in auth_file:
                    line = line.lstrip()
                    if line.startswith('#'):
                        continue
                    t_section = line[:line.find("=")].strip()
                    if t_section.upper() != section.upper():
                        continue
                    user = line[line.find("=") + 1:].strip()
                    if (sec.verify_password("ALL", user) or
                        sec.verify_password(self.curruser.upper(),
                                            user)):
                        check = True
                        break
        except FileNotFoundError:
            raise FileNotFoundError(self._AUTH_FILE_NOT_EXIST.format(
                self.authfile,
                os.linesep)
            )
        return check

    def add_user_authorization(self, section, userlist):
        alluserlist = self._get_auth_userlist(section)
        addlist = []
        for user in userlist:
            for userhash in alluserlist:
                if userhash.strip() == "":
                    continue
                if sec.verify_password(user, userhash):
                    continue
            addlist.append(user)
        if len(addlist) > 0:
            self._write_to_authfile(addlist, section)

    def remove_user_from_section(self, section, authlist):
        userlist = self._get_auth_userlist()
        newlist = []
        templist = authlist
        counter = 0
        for item in userlist:
            if item.strip() == "":
                continue
            if item.startswith("#") or \
               item[:item.find("=")].strip().upper() != section.upper():
                newlist.append(item)
            else:
                if len(templist) == 0:
                    continue
                match = ""
                for user in templist:
                    if sec.verify_password(
                            user.upper(),
                            item[item.find("=") + 1:].strip()
                    ):
                        match = user
                        counter += 1
                        break
                if match == "":
                    newlist.append(item)
                else:
                    templist.remove(match)
        if counter == 0:
            raise ValueError(self._USER_NOT_EXIST.format(section))
        self._write_to_authfile(newlist, None, 'w')

