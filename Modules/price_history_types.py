"""
Title: All Price Bot
Date Started: June 7, 2019
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose: The purpose of the All Price Bot is to retrieve the entire price history of a stock.  It will return all days including non-trading days (filled in with previous last closing price).  Allows for the option to fill in the unavailable rows with Nan or the last available price.
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import datetime as dt
#   THIRD PARTY IMPORTS
import pandas as pd
#   LOCAL APPLICATION IMPORTS
from Modules.price_history_fillgaps import fill_gaps2
from Modules.price_history import grabsinglehistory


# get set all trade dates
def getalltradedays(ticker):
    allprices = grabsinglehistory(ticker)
    alltradedates = allprices['date'].tolist()
    # convert to string
    alltradedates = [str(item) for item in alltradedates]
    return alltradedates


# get set of all holidays
def getallholidays(ticker):
    allprices = grabsinglehistory(ticker)
    alltradedates = allprices['date'].tolist()
    # convert to string
    alltradedates = [str(item) for item in alltradedates]
    # get full dates
    prices = fill_gaps2(allprices, '', '')
    prices.reset_index(drop=True, inplace=True)
    # isolate full dates
    fulldates = pd.to_datetime(prices['date']).tolist()
    # convert to string
    fulldates = [dt.datetime.date(item) for item in fulldates]
    fulldates = [str(item) for item in fulldates]
    allholidates = [item for item in fulldates if item not in alltradedates]
    if len(alltradedates) + len(allholidates) == len(fulldates):
        return allholidates
    else:
        print('number of holidates plus trade dates does not equal total date figure, so something went wrong. Exiting program...')
        print(f'Number of trade dates found: {len(alltradedates)}')
        print(f'Number of holi dates found: {len(allholidates)}')
        print(f'Number of total dates found: {len(fulldates)}')
        print(f'holi + trade dates equals: {len(alltradedates) + len(allholidates)}')


# returns pricedf with only rows with trade dates
def tradedateonlypricedf(pricedf):
    # get trade dates
    tradedates = getalltradedays('KO')
    # remove row if date is a holiday
    pricedf = pricedf[pricedf['date'].isin(tradedates)].copy()
    pricedf.reset_index(drop=True, inplace=True)
    return pricedf
