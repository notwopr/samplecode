"""
Title: Computer Settings Bot
Date Started: Oct 24, 2019
Version: 2.2
Version Date: Oct 26, 2021
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose: Settings depending on computer used to run code.
On AMD D drive, downloading all prices: 1 min 35 secs
On AMD C drive, downloading all prices: 0 min 34 secs

Version Notes:
1.1: Changed AMD processor max to usecores - 4.  With Python 3.8.1 update started getting errors when processors was 61 or higher.  So made max 60.
1.2: Simplified code and added Surface Laptop.
2.0: Converted Computer settings scheme to a class object scheme.
2.1: Made computer switching automatically detected.
2.2: Added Amazon Cloud9 configuration.
"""
# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
from pathlib import Path
import psutil
import platform
# GET NUMBER OF CORES
num_cores = psutil.cpu_count(logical=True)


class ComputerSystem():

    def __init__(self, computername):
        if computername == 'DESKTOP-CATJPV0':  # AMD computer
            self.computername = 'amdcomp'
            self.dump_predicate = 'D:'
            self.pricedata_predicate = self.dump_predicate
            self.report_predicate = 'C:/Users/david/'
            self.use_cores = num_cores - 4

        elif "us-west-1" in computername:  # aws computer
            self.computername = 'awsbeanstalk'
            self.dump_predicate = '/efs'#'/home/ec2-user/environment/EBS'
            self.pricedata_predicate = self.dump_predicate
            self.report_predicate = self.dump_predicate
            self.use_cores = num_cores
        else:
            print("computer system has not been configured yet.  Please update computersettings.py with the profile of the computer system you are trying to run this program on.  Exiting now...")
            exit()

        self.pricedata = Path(f'{self.pricedata_predicate}/PRICEDATAPARENT')
        self.bot_dump = Path(f'{self.dump_predicate}/BOT_DUMP')
        self.bot_report = Path(f'{self.dump_predicate}/BOT_REPORTS')
        self.strattester = Path(f'{self.dump_predicate}/STRATTESTER')
        self.strattester_testruns = Path(f'{self.dump_predicate}/STRATTESTER/STRATTESTER_TESTRUNS')
        self.strattester_stockperfreports = Path(f'{self.dump_predicate}/STRATTESTER/STRATTESTER_STOCKPERFREPORTS')
        self.strattester_allperiodstatdf = Path(f'{self.dump_predicate}/STRATTESTER/STRATTESTER_ALLPERIODSTATDF')
        self.auth = Path(<authpath>)
        #self.bot_report = Path(f'{self.report_predicate}/Google Drive/Goals/Careers/Business/Good Business Ideas/Fund Business/Investment Strategy Research/BOT_REPORTS')


'''PLEASE CHOOSE WHICH ABOVE COMPUTER TO RUN ON'''
try:
    compid = platform.uname().node
except AttributeError:
    compid = platform.uname()[1]

computerobject = ComputerSystem(compid)
