"""
Title: Portfolio Generator Bot
Date Started: May 20, 2019
Version: 2.0
Version Start: Oct 25, 2019
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied
    without the express written consent of David Hyongsik Choi.
Purpose: The purpose of the Portfolio Generator Bot is to return a given size portfolio of randomly selected tickers from a given pool.
"""


# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import pickle as pkl
#   THIRD PARTY IMPORTS
import numpy as np
#   LOCAL APPLICATION IMPORTS
from UPDATEPRICEDATA_FILELOCATIONS import tickerlistcommon_source, tickerlistall_source


# RETURNS RANDOM PORTFOLIO OF GIVEN SIZE FROM A GIVEN POOL
def randfoliogen(size, pool):

    # FILTER
    if type(pool) == list:
        tickerlist = pool
    elif pool == 'common':
        with open(tickerlistcommon_source, "rb") as targetfile:
            unpickled_raw = pkl.load(targetfile)
        tickerlist = unpickled_raw['symbol'].tolist()
    else:
        with open(tickerlistall_source, "rb") as targetfile:
            unpickled_raw = pkl.load(targetfile)
        tickerlist = unpickled_raw['symbol'].tolist()

    # MAKE SURE SIZE REQUESTED IS POSSIBLE
    if size > len(tickerlist):
        print("The size of the portfolio requested (", size, ") exceeds the size of the pool (", len(tickerlist), "). Program exiting...")
        exit()

    # GET LIST OF THE STOCK POOL INDICES
    a = np.arange(len(tickerlist))

    # SHUFFLE THE INDEX LIST, RETURN THE FIRST N SAMPLES, SORT THE SAMPLE LIST
    b = np.sort(np.random.permutation(a)[:size])

    # RETRIEVE EACH STOCK
    array = np.array(tickerlist)
    rawanswer = array[b]
    answer = rawanswer.tolist()

    return answer
