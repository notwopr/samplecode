"""
Title: Generic Function Bot
Date Started: July 10, 2019
Version: 1.01
Version Start Date: July 21, 2020
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied
    without the express written consent of David Hyongsik Choi.
Purpose: The purpose of the Generic Function Bot is to be a clearinghouse for random generic functions.
VERSIONS:
1.01: Added round up and round down functions.
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
#   THIRD PARTY IMPORTS
#   LOCAL APPLICATION IMPORTS
from Modules.price_history import grabsinglehistory, grabsinglehistory_fundies
from Modules.price_history_fillgaps import fill_gaps2
from Modules.dataframe_functions import filtered_single, filtered_double


def fillgapreset(prices, beg_date, end_date):
    prices = fill_gaps2(prices, beg_date, end_date)  # fill in (fill in missing days and crop to date range)
    prices.reset_index(drop=True, inplace=True)  # reset index
    return prices


# returns pricedf with dates filled and sliced.
# advantage of this is that the date column can be compared to string dates
def pricedf_daterange(stock, beg_date, end_date):
    prices = grabsinglehistory(stock)  # get full raw history (only trading days)
    prices = fillgapreset(prices, beg_date, end_date)
    return prices


def getsingleprice(stock, date):
    prices = pricedf_daterange(stock, '', '')
    singleprice = prices[prices['date'] == date][stock].item()
    return singleprice


def pricedf_daterange_fundies(stock, datatype, beg_date, end_date):
    prices = grabsinglehistory_fundies(stock, datatype)  # get full raw history (only trading days)
    prices = fillgapreset(prices, beg_date, end_date)
    return prices


# returns df trimmed by whatever bound(s) is given
def trimdfbydate(df, datecol, beg_date, end_date):
    if beg_date != "" and end_date != "":
        return filtered_double(df, '>=<=', beg_date, end_date, datecol)
    elif end_date != "":
        return filtered_single(df, '<=', end_date, datecol)
    elif beg_date != "":
        return filtered_single(df, '>=', beg_date, datecol)
