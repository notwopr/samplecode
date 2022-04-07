"""
Title: Ticker Portal
Date Started: April 26, 2019
Version: 3.0
Vers Date: Nov 9, 2019
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose: Return list of all NASDAQ/NYSE stocks at a given point in history.
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import pickle as pkl
import datetime as dt
#   THIRD PARTY IMPORTS
#   LOCAL APPLICATION IMPORTS
from file_functions import readpkl_fullpath
from Modules.tickers import get_tickerlist
from file_hierarchy import daterangedb_source


# returns full ticker list limited by date
def tickers_possible(date_left, date_right):
    all_startdates = readpkl_fullpath(daterangedb_source)
    # all stocks existing during all dates within a range
    if date_left != '' and date_right != '':
        return all_startdates[(all_startdates['first_date'] <= date_left) & (all_startdates['last_date'] >= date_right)]
    # all stocks existing on or before a date (if before, not necessarily exists on the date or later)
    elif date_left != '':
        return all_startdates[all_startdates['first_date'] <= date_left]
    # all stocks existing on or after a date (if after, not necessarily exists on the date or before)
    elif date_right != '':
        return all_startdates[all_startdates['last_date'] >= date_right]


# RETURNS A LIST OF ALL THE TICKERS AVAILABLE AT OR BEFORE A GIVEN DATE AND AT OR AFTER GIVEN DATE
def tickerportal(beg_date, end_date, pool):
    pool = pool if type(pool) == list else get_tickerlist(pool)
    valid_rows = tickers_possible(beg_date, end_date)
    return valid_rows[valid_rows['stock'].isin(pool)]['stock'].tolist()


# RETURNS A LIST OF ALL THE TICKERS AVAILABLE AT OR BEFORE A GIVEN DATE
def tickerportal2(date, pool):
    pool = pool if type(pool) == list else get_tickerlist(pool)
    valid_rows = tickers_possible(date, '')
    return valid_rows[valid_rows['stock'].isin(pool)]['stock'].tolist()


# RETURNS A LIST OF ALL THE TICKERS THAT (1) EXISTED ON OR BEFORE A GIVEN DATE AND (2) WAS x DAYS OLD AT A MINIMUM
def tickerportal3(date, pool, agemin):
    pool = pool if type(pool) == list else get_tickerlist(pool)
    valid_rows = tickers_possible(str(dt.date.fromisoformat(date) - dt.timedelta(days=agemin)), '')
    return valid_rows[valid_rows['stock'].isin(pool)]['stock'].tolist()


# RETURNS A LIST OF ALL THE TICKERS THAT (1) EXISTED ON OR BEFORE A GIVEN DATE, (2) AND ON OR AFTER A GIVEN DATE AND (3) WAS x DAYS OLD AT A MINIMUM
def tickerportal4(beg_date, end_date, pool, agemin):
    pool = pool if type(pool) == list else get_tickerlist(pool)
    valid_rows = tickers_possible(str(dt.date.fromisoformat(beg_date) - dt.timedelta(days=agemin)), end_date)
    return valid_rows[valid_rows['stock'].isin(pool)]['stock'].tolist()


# RETURNS A LIST OF ALL THE TICKERS WHOSE FUNDY DATA HAS ENOUGH ROWS AND ITS LAST REPORT IS NOT OLDER THAN x DAYS
def tickerportal4mindata(tickerlistcommon_source, exist_date, pool, fundyagemin, lastfundyreportage):
    # LOAD DATAFRAME OF EARLIEST DATES
    with open(daterangedb_source, "rb") as targetfile:
        all_startdates = pkl.load(targetfile)
    # remove rows that have no dates
    all_startdates.dropna(axis=0, how='any', inplace=True)
    # get earliest date that last fundy report can be published
    lastreportdate = str(dt.date.fromisoformat(exist_date) - dt.timedelta(days=lastfundyreportage))
    # if last_date < lastreportdate, filter out
    all_startdates = all_startdates[all_startdates['last_date'] >= lastreportdate]
    # correct end date = exist_date if end_date > exist_date, else =end_date
    all_startdates['adjlast_date'] = all_startdates['last_date'].apply(lambda x: dt.date.fromisoformat(exist_date) if dt.date.fromisoformat(x) > dt.date.fromisoformat(exist_date) else dt.date.fromisoformat(x))
    # convert first date col to datetime object
    all_startdates['first_date'] = all_startdates['first_date'].apply(lambda x: dt.date.fromisoformat(x))
    # create age col
    all_startdates['age'] = all_startdates['adjlast_date'] - all_startdates['first_date']
    all_startdates['age'] = all_startdates['age'].apply(lambda x: x.days)
    # return tickers whose len of existdate - first date >=fundyagemin
    valid_rows = all_startdates[all_startdates['age'] >= fundyagemin]
    valid_stocks = valid_rows['stock'].tolist()
    # FILTER
    if type(pool) == list:
        final_pool = list(set(valid_stocks).intersection(set(pool)))
    elif pool == 'common':
        with open(tickerlistcommon_source, "rb") as targetfile:
            tickerlistdf = pkl.load(targetfile)
        tickerlist = tickerlistdf['symbol'].tolist()
        final_pool = list(set(valid_stocks).intersection(set(tickerlist)))
    else:
        final_pool = valid_stocks
    # RETURN FINAL LIST
    return final_pool


# RETURNS A LIST OF ALL THE TICKERS THAT (1) EXISTED ON OR BEFORE A GIVEN DATE, (2) WAS x DAYS OLD AT A MINIMUM AND (4) HAS FUNDAMENTAL DATA AVAILABLE for at least on or before given date or minage date
def tickerportal5(tickerlistcommon_source, daterangedb_source_fundies, beg_date, end_date, pool, agemin):
    # GET POOL PRE-FUNDY FILTER
    final_pool = tickerportal4(daterangedb_source, tickerlistcommon_source, beg_date, end_date, pool, agemin)
    # FILTER OUT STOCKS THAT HAVE NO FUNDY DATA
    final_pool = tickerportal4(daterangedb_source_fundies, '', beg_date, end_date, final_pool, agemin)
    # RETURN FINAL LIST
    return final_pool


# RETURNS A LIST OF ALL THE TICKERS THAT (1) EXISTED ON OR BEFORE A GIVEN DATE, (2) WAS x DAYS OLD AT A MINIMUM AND (4) HAS FUNDAMENTAL DATA AVAILABLE for a min of x days
def tickerportal6(tickerlistcommon_source, daterangedb_source_fundies, beg_date, end_date, pool, agemin, fundyagemin, lastfundyreportage):
    # GET POOL PRE-FUNDY FILTER
    final_pool = tickerportal4(daterangedb_source, tickerlistcommon_source, beg_date, end_date, pool, agemin)
    # FILTER OUT STOCKS THAT HAVE fundy data < min amount
    final_pool = tickerportal4mindata(daterangedb_source_fundies, tickerlistcommon_source, end_date, final_pool, fundyagemin, lastfundyreportage)
    # RETURN FINAL LIST
    return final_pool
