"""
Title: Update Price Data - Ticker Data
Date Started: April 26, 2019
Version: 1.2
Version Start Date: Aug 25, 2021
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose: Retrieve list of tickers of all the companies listed on the NYSE and NASDAQ.

Version Notes:
1.1: Simplify Code.
1.2: Allow inclusion of ADRs into the common stock pool.
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import json as js
import requests as rq
import re
#   THIRD PARTY IMPORTS
import pandas as pd
#   LOCAL APPLICATION IMPORTS
from filelocations import savetopkl


def symfilt(x):
    return {'symbol': x['symbol'], 'name': x['name']}


def csoradr(tickerdict):
    if tickerdict['type'] == 'cs' or tickerdict['type'] == 'ad':
        return True
    else:
        return False


def storealltickers(destfolder, tickerfilename_all, tickerfilename_common):

    tickerurl = 'https://cloud.iexapis.com/stable/ref-data/symbols?token=sk_515e8be68f01497cabba3d0fcaa18638&filter=symbol,name,exchange,type'

    # RETRIEVE AND STORE TICKER DATA, AND RECORD TIMESTAMP OF RETRIEVAL
    tickraw = rq.get(tickerurl)
    ticktxt = tickraw.text
    ticklist = js.loads(ticktxt)

    # FILTER OUT NON-NYSE AND NON-NASDAQ STOCKS AS WELL AS NON-COMMON SHARES
    alltickers = list(filter(lambda x: x["exchange"] == "NAS" or x["exchange"] == "NYS", ticklist))

    # FILTER OUT NON-COMMON SHARES
    commontickers = list(filter(csoradr, alltickers))

    # FILTER THE LIST TO CONTAIN ONLY TICKER SYMBOLS and NAMES
    drafttickall = list(map(symfilt, alltickers))
    drafttickcommon = list(map(symfilt, commontickers))

    # REMOVE ANY DUPLICATES
    finaltickall = [i for n, i in enumerate(drafttickall) if i not in drafttickall[n + 1:]]
    finaltickcommon = [i for n, i in enumerate(drafttickcommon) if i not in drafttickcommon[n + 1:]]

    # EDIT LIST FOR TIINGO SYNTAX
    for stocklist in [finaltickall, finaltickcommon]:
        for stockdict in stocklist:
            if stockdict['symbol'].find('=') != -1:  # UNITS OF FORM "SYMBOL="
                newsym = stockdict['symbol'].replace("=", "-U")
                stockdict.update({'symbol': newsym})
            elif re.search('\.', stockdict['symbol']) is not None:  # PREFERRED CLASSES OF FORM "SYMBOL.*"
                newsym = stockdict['symbol'].replace(".", "-")
                stockdict.update({'symbol': newsym})
            elif re.search('-\w', stockdict['symbol']) is not None:  # PREFERRED CLASSES OF FORM "SYMBOL-*"
                newsym = stockdict['symbol'].replace("-", "-P-")
                stockdict.update({'symbol': newsym})
            elif re.search('-$', stockdict['symbol']) is not None:  # PREFERRED CLASSES OF FORM "SYMBOL-"
                newsym = stockdict['symbol'].replace("-", "-P")
                stockdict.update({'symbol': newsym})
            elif re.search('\^$', stockdict['symbol']) is not None:  # RIGHTS OF FORM "SYMBOL^"
                newsym = stockdict['symbol'].replace("^", "-R")
                stockdict.update({'symbol': newsym})
            elif re.search('\^#$', stockdict['symbol']) is not None:  # RIGHTS WHEN ISSUED OF FORM "SYMBOL^#"
                newsym = stockdict['symbol'].replace("^#", "-R-W")
                stockdict.update({'symbol': newsym})
            elif re.search('#$', stockdict['symbol']) is not None:  # WARRANTS OF FORM "SYMBOL#"
                newsym = stockdict['symbol'].replace("#", "-WI")
                stockdict.update({'symbol': newsym})
            elif re.search('\+$', stockdict['symbol']) is not None:  # WARRANTS OF FORM "SYMBOL+"
                newsym = stockdict['symbol'].replace("+", "-WS")
                stockdict.update({'symbol': newsym})
            elif stockdict['symbol'].find('+') != -1:  # WARRANTS OF FORM "SYMBOL+*"
                newsym = stockdict['symbol'].replace("+", "-WS-")
                stockdict.update({'symbol': newsym})

    finalalldf = pd.DataFrame(data=finaltickall)
    finalcommondf = pd.DataFrame(data=finaltickcommon)

    # SAVE TO FILE
    savetopkl(tickerfilename_all, destfolder, finalalldf)
    savetopkl(tickerfilename_common, destfolder, finalcommondf)
    finalalldf.to_csv(index=False, path_or_buf=destfolder / f'{tickerfilename_all}.csv')
    finalcommondf.to_csv(index=False, path_or_buf=destfolder / f'{tickerfilename_common}.csv')
