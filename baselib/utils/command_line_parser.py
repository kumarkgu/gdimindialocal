# ##############################################################################
# # Name       : commandline.py
# # Date       : 16-Feb-2018
# # Created By : Gunjan Kumar
# # Description: This file processes the command line arguments for the HAWK
# #              processes
# ##############################################################################
# # Change Log :
# # S.  Changed     Changed  Change
# # No. Date        By       Description
# # --- ----------- -------- ---------------------------------------------------
# # 001 16-Feb-2018 Gunjan K 1. Initial Creation of file
# ##############################################################################
import optparse
from datetime import datetime
import time
import os


class CommandLineParse:
    def __init__(self, file):
        self.file = file
        self.parser = optparse.OptionParser()
        self._parse_command(self.parser)
        self.options, self.arguments = self.parser.parse_args()

    @staticmethod
    def _parse_command(parser):
        parser.add_option(
            '-r', '--region', dest='region', default=None,
            help='Region for which the HAWK process needs to run'
        )
        parser.add_option(
            '-c', '--country', dest='country', default=None,
            help='Country for which the HAWK process needs to run'
        )
        parser.add_option(
            '--env', dest='environment', default=None,
            help='Environment to Use and Load Process'
        )
        parser.add_option(
            '-d', '--refreshdate', dest='refreshdate', default=None,
            help='Refresh Date for Daily/Time frequency HAWK Process ('
                 'in yyyy-mm-dd( HH:MM:SS) format)'
        )
        parser.add_option(
            '-m', '--mode', dest='mode', default=None,
            help='FULL Refresh Or DAILY Refresh'
        )
        parser.add_option(
            '--mongodb', dest='mongodb', default=None,
            help='Mongo DB Connection Name'
        )
        parser.add_option(
            '--dbconn', dest='dbconn', default=None,
            help='SQL Server Database Connection Name'
        )
        parser.add_option(
            '--olmconn', dest='olmconn', default=None,
            help='If OLM and EDW are different then OLM Database connection'
                 ' name'
        )
        parser.add_option(
            '--iterspeed', dest='iterspeed', default=None,
            help='Iteration Speed while loading to MongoDB'
        )
        parser.add_option(
            '-i', '--issamedb', dest='issamedb', action="store_true",
            help='If both OLM And EDW data resides on same Database'
        )
        parser.add_option(
            '--iterate', dest='iterate', action="store_true",
            help='If Iteration is needed during loading to MongoDB'
        )
        parser.add_option(
            '--dryrun', dest='dryrun', action="store_true",
            help='Do a Dry Run and DO NOT load data to MongoDB'
        )
        parser.add_option(
            '-v', '--viewdata', dest='viewdata', action="store_true",
            help='Do you want to view data'
        )
        parser.add_option(
            '--noofviewdata', dest='noofviewdata', default=None,
            help='Number of Records to View'
        )
        parser.add_option(
            '-l', '--limitdata', dest='limitdata', default=None,
            help='Limiting the number of data to process'
        )
        parser.add_option(
            '--logfile', dest='logfile', help='Log File',
        )
        parser.add_option(
            '--noolm', dest='noolm', action="store_true",
            help='Do not include data from OLM System'
        )
        parser.add_option(
            '--crmdatabase', dest='crmdatabase', default=None,
            help='Database Name for the CRM system'
        )
        parser.add_option(
            '--crmlive', dest='crmlive', action="store_true",
            help='Extract data from CRM System tables'
        )
        parser.add_option(
            '--marketgroup', dest='marketgroup', default=None,
            help='Market Group to be processed for'
        )

    def getoptions(self):
        return self.options

    def checkoptions(self):
        if self.options.mode.upper() not in ("FULL", "DAILY"):
            raise Exception(
                "Invalid mode [{}], must be (FULL or DAILY)".format(
                    self.options.mode)
            )
        if self.options.mode.upper() == "DAILY":
            refdate = time.strptime(self.options.refreshdate, "%Y-%m-%d")
            curdate = time.strptime(datetime.now().strftime("%Y-%m-%d"),
                                    "%Y-%m-%d")
            if curdate <= refdate:
                raise Exception(
                    "Invalid Refresh date [{}], must be less than TODAY".format(
                        self.options.refreshdate
                    )
                )

    def setvalues(self):
        currpath = os.path.dirname(os.path.abspath(self.file))
        print(currpath)
        print(self.file)
