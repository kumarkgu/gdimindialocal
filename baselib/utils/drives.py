# ##############################################################################
# # Name       : drives
# # Date       : 27-May-2019
# # Created By : Gunjan Kumar
# # Description: This file is used to do drive operations in windows
# ##############################################################################
# # Change Log :
# # S.  Changed     Changed  Change
# # No. Date        By       Description
# # --- ----------- -------- ---------------------------------------------------
# # 001 27-May-2019 Gunjan K . Initial Creation of code
# ##############################################################################
import os
import win32api
import win32wnet
import win32netcon
from baselib.utils import Logger


class DriveOps:
    def __init__(self, log=None):
        self.log = Logger.Logger("Zip File").getlog() if not log else log

    @staticmethod
    def existing_drives():
        drives = win32api.GetLogicalDriveStrings()
        drives = [x[0].upper() for x in drives.split('\000') if x]
        return drives

    def next_drive_letter(self, existing=None):
        if not existing:
            existing = self.existing_drives()
        for drives in 'EFGHIJKLMNOPQRSTUVWXYZ':
            if drives not in existing:
                return "{}:".format(drives)

    def disconnect_drive(self, drive, force=False):
        if os.path.exists(drive):
            self.log.info("Drive: {} in use. Trying to Unmap..".format(drive))
            force = 0 if not force else 1
            try:
                win32wnet.WNetCancelConnection2(drive, 1, force)
                self.log.info("Drive: {} successfully unmapped".format(drive))
                return 1
            except:
                strmsg = "Unmapping failed. This may not be a network drive..."
                self.log.info(strmsg)
                return -1
        else:
            self.log.info("Drive: {} is already free".format(drive))
            return 0

    def _map_path(self, drive, path, user=None, password=None):
        if os.path.exists(path):
            self.log.info(
                "Path: {}. reachable. Mapping to drive".format(
                    path,
                    drive
                )
            )
            try:
                netres = win32wnet.NETRESOURCE()
                netres.lpLocalName = drive
                netres.lpRemoteName = path
                netres.dwType = win32netcon.RESOURCETYPE_DISK
                if user:
                    win32wnet.WNetAddConnection2(NetResource=netres,
                                                 Password=password,
                                                 UserName=user)
                else:
                    win32wnet.WNetAddConnection2(NetResource=netres)
            except:
                self.log.info("Unexpected error while mapping path")
                raise
                # return -1
            self.log.info("Mapping Successful")
            return 1
        else:
            self.log.info("Network Path Unrachable")
            return -1

    def map_drive(self, netpath, drive=None, user=None, passwd=None,
                  force=False, autodrive=True):
        self.log.info("Connecting to Path: {}".format(netpath))
        t_getdrlet = 0
        if drive:
            if os.path.exists(drive):
                self.log.info("Drive: {} is currently in use")
                if force:
                    retval = self.disconnect_drive(drive, force=True)
                    if retval == -1:
                        if autodrive:
                            t_getdrlet = 1
                        else:
                            return -1
                else:
                    if autodrive:
                        t_getdrlet = 1
                    else:
                        self.log.info("None Forcing. Will not unmap. Return...")
                        return -1
        else:
            t_getdrlet = 1
        if t_getdrlet == 1:
            drive = self.next_drive_letter()
        retval = self._map_path(drive=drive, path=netpath, user=user,
                                password=passwd)
        if retval == 1:
            self.log.info("Mapping Successful")
            return drive
        else:
            self.log.info("Mapping Unsuccessful")
            return -1
