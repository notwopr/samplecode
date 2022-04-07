"""
Title: Tickers
Date Started: Jan 31, 2022
Version: 1.0
Version Start Date: Jan 31, 2022
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied
    without the express written consent of David Hyongsik Choi.

"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
#   THIRD PARTY IMPORTS
#   LOCAL APPLICATION IMPORTS
from file_functions import readpkl
from file_hierarchy import TICKERS


# returns list of ticker symbols given criteria
def get_tickerlist(mode):
    b = ["^DJI", "^INX", "^IXIC"]
    if mode == 'common' or mode == 'all':
        return readpkl(f'tickerlist_{mode}', TICKERS)['symbol'].tolist()
    elif mode == 'bench':
        return b
    elif mode == 'common+bench' or mode == 'all+bench':
        return b + readpkl(f'tickerlist_{mode[:-6]}', TICKERS)['symbol'].tolist()
