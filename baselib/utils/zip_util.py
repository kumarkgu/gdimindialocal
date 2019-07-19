# ##############################################################################
# # Name       : create_client_database.py
# # Date       : 24-May-2019
# # Created By : Gunjan Kumar
# # Description: This file is used to do operation on zip file
# ##############################################################################
# # Change Log :
# # S.  Changed     Changed  Change
# # No. Date        By       Description
# # --- ----------- -------- ---------------------------------------------------
# # 001 24-May-2019 Gunjan K . Initial Creation of code
# ##############################################################################
import zipfile
import os
from baselib.utils import Logger
from baselib.utils import stringops as sops


class ZipOperation:
    def __init__(self, log=None):
        self.log = Logger.Logger("Zip File").getlog() if not log else log

    @staticmethod
    def _iterate_members(members, sep=","):
        try:
            assert isinstance(members, list)
            return members
        except AssertionError:
            try:
                assert isinstance(members, dict)
                return members
            except AssertionError:
                return sops.listify_data(members, islist=True, issplit=True,
                                         sep=sep)

    def extract_files(self, zfile, tempdir=None, members=None):
        self.log.info("Processing ZIP File: {}".format(zfile))
        if not tempdir:
            tempdir = os.path.dirname(zfile)
        if members:
            members = self._iterate_members(members)
        retval = 0
        with zipfile.ZipFile(zfile, mode='r') as zipf:
            self.log.info(
                "..Extracting ZIP File to directory: {}".format(tempdir)
            )
            try:
                zipf.extractall(path=tempdir, members=members)
                retval = 1
            except KeyError:
                mesg = "Member File does not exists in ZIP File"
                self.log.info("..Member File does not exist in ZIP File")
        return retval
