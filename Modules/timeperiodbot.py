"""
Title: Time Period Bot
Date Started: May 30, 2019
Version: 1.1
Version Start Date: June 14, 2020
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied
    without the express written consent of David Hyongsik Choi.
Purpose: The purpose of the Time Period Bot is to take an input and return a list of dates based on that criteria.  Number of samples returned is calculated backwards from today.

Version Notes:
1.1: Moved earliestgraphdate to here.
"""
# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import pickle as pkl
import datetime as dt
import random as rd
#   THIRD PARTY IMPORTS
import pandas as pd
import numpy as np
#   LOCAL APPLICATION IMPORTS
from Modules.price_calib_cruncher import oldbaremin_cruncher


# get earliest available date with price data
def getearliestdateavailable(daterangedb_source):
    with open(daterangedb_source, "rb") as targetfile:
        daterangedb = pkl.load(targetfile)
    firstdate_dateobj = daterangedb['first_date'].apply(lambda x: dt.date.fromisoformat(x))
    firstdates = firstdate_dateobj.tolist()
    earliestdate = str(np.min(firstdates))
    return earliestdate


# get last available date with price data
def getlatestdateavailable(daterangedb_source):
    with open(daterangedb_source, "rb") as targetfile:
        daterangedb = pkl.load(targetfile)
    lastdate_dateobj = daterangedb['last_date'].apply(lambda x: dt.date.fromisoformat(x))
    lastdates = lastdate_dateobj.tolist()
    latestdate = str(np.max(lastdates))
    return latestdate


# RETURNS THE START AND END DATE OF THE BIGGEST DIP IN A GIVEN PRICE DATAFRAME
def dipdates(dataframe, pricecol):
    # GET OLDBAREMINRAW GRAPH
    allprices = dataframe[pricecol].tolist()
    oldbareminrawpricelist = oldbaremin_cruncher(allprices)
    dataframe['lowestprice'] = np.array(oldbareminrawpricelist)
    # GET PCTDROPS
    dataframe['pctdrops'] = (dataframe['lowestprice'] - dataframe[pricecol]) / dataframe[pricecol]
    # find first peak date
    peakdatecandidates = dataframe['date'][dataframe['pctdrops'] == dataframe['pctdrops'].min()]
    firstpeakdate = peakdatecandidates.iloc[0]
    # find first lowest price after peak date
    afterpeakprices = dataframe[dataframe['date'] > firstpeakdate].copy()
    valleydatecandidates = afterpeakprices['date'][afterpeakprices[pricecol] == afterpeakprices[pricecol].min()]
    # choose first one after peakdate
    firstvalleydate = valleydatecandidates.iloc[0]
    # convert to string
    peakdate = str(firstpeakdate.date())
    valleydate = str(firstvalleydate.date())
    return peakdate, valleydate


# RETURNS THE PEAKDATE, VALLEYDATE AND RECOVERY DATE OF THE BIGGEST DIP IN A GIVEN PRICE DATAFRAME
def peakdiprecoverydates(dataframe, valleydate, peakprice, pricecol):
    aftervalleyprices = dataframe[dataframe['date'] > valleydate].copy()
    recoverydatecandidates = aftervalleyprices['date'][aftervalleyprices[pricecol] >= peakprice]
    # choose first one after peakdate
    if len(recoverydatecandidates) > 0:
        firstrecoverydate = recoverydatecandidates.iloc[0]
        recoverydate = str(firstrecoverydate.date())
    else:
        recoverydate = None
    return recoverydate


# RETURNS IPO DATE OF OLDEST STOCK IN THE PORTFOLIO
def oldeststockipodate(portfolio, daterangedb_source):
    nonbenchstocks = [item for item in portfolio if item not in ['^DJI', '^INX', '^IXIC']]
    if len(nonbenchstocks) != 0:
        # FIND EARLIEST DATE AMONG NONBENCHSTOCKS
        with open(daterangedb_source, "rb") as targetfile:
            daterangedb = pkl.load(targetfile)
        filtered_db = daterangedb[daterangedb['stock'].isin(nonbenchstocks)]
        beg_date = str(filtered_db['first_date'].apply(lambda x: dt.date.fromisoformat(x)).min())
    else:
        beg_date = '1970-01-01'
    return beg_date


# RETURNS IPO DATE OF YOUNGEST STOCK IN THE PORTFOLIO
def youngeststockipodate(portfolio, daterangedb_source):
    nonbenchstocks = [item for item in portfolio if item not in ['^DJI', '^INX', '^IXIC']]
    if len(nonbenchstocks) != 0:
        # FIND EARLIEST DATE AMONG NONBENCHSTOCKS
        with open(daterangedb_source, "rb") as targetfile:
            daterangedb = pkl.load(targetfile)
        filtered_db = daterangedb[daterangedb['stock'].isin(nonbenchstocks)]
        beg_date = str(filtered_db['first_date'].apply(lambda x: dt.date.fromisoformat(x)).max())
    else:
        beg_date = '1970-01-01'
    return beg_date


# RETURNS ONE CONTIGUOUS SET OF TIME PERIODS OF EQUAL LENGTH, BETWEEN TODAY AND EARLIEST DATE ALLOWED, GIVEN NUMBER OF PERIODS REQUESTED, AND WHETHER TO RANDOMLY CHOOSE THE SET OR USE THE SET ENDING WITH TODAY'S DATE
'''
If the dates are not set to random, it will given all dates starting with the startdate.  IT won't start from latest backwards, so as a result, the last date in the set may not be the latest date given, simply because the period length specified would translate a final date later than today's date.
if you want to return all available periods, then put num_periods = 'all'.
If you want the set to be randomly chosen, have randomize = 'random'.
'''
def timeperiodbot(period_len, earliest, latest, num_periods, randomize):
    '''
    time_unit = 'D' for days
                'W' for weeks
                'M' for months
                'Q' for quarters
                '180D' for halfyears
                'Y' for years
    '''
    if latest == "today":
        latest = dt.date.today()
    else:
        latest = dt.date.fromisoformat(latest)
    earliest = dt.date.fromisoformat(earliest)
    possibilities = pd.date_range(start=earliest, end=latest, freq=period_len).date
    maxposs = len(possibilities)
    if maxposs == 1:
        diff = (latest - earliest).days
        print("There are no possible date spans given the span length (", period_len, ") and earliest date (", earliest, "), requirements.  Between today and earliest date allowed, there are only", diff, " days (or ", diff / 7, " weeks, or ", diff / 30, " months, or ", diff / 90, " quarters, or ", diff / 180, " half-years, or ", diff / 365, " years). Program exiting...")
        exit()
    if isinstance(num_periods, int) is True and num_periods > maxposs - 1:
        print("The number of samples requested (", num_periods, ") exceeds the number of possibilities (", maxposs - 1, "). Program exiting...")
        exit()
    if randomize == "random":
        end = maxposs - rd.randrange(0, (maxposs - (num_periods + 1)) + 1)
        start = end - (num_periods + 1)
        testdates = possibilities[start:end]
    elif num_periods == "all":
        testdates = possibilities
    else:
        start = maxposs - (num_periods + 1)
        testdates = possibilities[start:]
    # CHANGE TO ISOFORMAT
    answer = [str(date) for date in testdates]
    return answer


def present_backwards_datebot(period_len_in_days, period_len, earliest, latest, num_periods, randomize):
    '''
    time_unit = 'D' for days
                'W' for weeks
                'M' for months
                'Q' for quarters
                '180D' for halfyears
                'Y' for years
    '''
    if latest == "today":
        latest = dt.date.today()
    else:
        latest = dt.date.fromisoformat(latest)
    earliest = dt.date.fromisoformat(earliest)
    possible_periods = int(np.ceil((latest - earliest).days / period_len_in_days))
    possibilities = pd.date_range(end=latest, freq=period_len, periods=possible_periods).date
    maxposs = len(possibilities)
    if maxposs == 1:
        diff = (latest - earliest).days
        print("There are no possible date spans given the span length (", period_len, ") and earliest date (", earliest, "), requirements.  Between today and earliest date allowed, there are only", diff, " days (or ", diff / 7, " weeks, or ", diff / 30, " months, or ", diff / 90, " quarters, or ", diff / 180, " half-years, or ", diff / 365, " years). Program exiting...")
        exit()
    if isinstance(num_periods, int) is True and num_periods > maxposs - 1:
        print("The number of samples requested (", num_periods, ") exceeds the number of possibilities (", maxposs - 1, "). Program exiting...")
        exit()
    if randomize == "random":
        end = maxposs - rd.randrange(0, (maxposs - (num_periods + 1)) + 1)
        start = end - (num_periods + 1)
        testdates = possibilities[start:end]
    elif num_periods == "all":
        testdates = possibilities
    else:
        start = maxposs - (num_periods + 1)
        testdates = possibilities[start:]
    # CHANGE TO ISOFORMAT
    answer = [str(date) for date in testdates]
    return answer


# RANDOMLY GENERATE UNIQUE DATES
def random_dates(start, end, n):
    # GET LIST OF ALL DATES BETWEEN START AND END
    dr = pd.date_range(start, end, freq='D')
    # CHECK IF AMOUNT REQUESTED EXCEEDS AVAILABLE AMOUNT
    if n > len(dr):
        print("The number of random dates requested (", n, ") exceeds the number of possible dates (", len(dr), "). Program exiting...")
        exit()
    # GET LIST OF THE DATE LIST INDICES
    a = np.arange(len(dr))
    # SHUFFLE THE INDEX LIST, RETURN THE FIRST N SAMPLES, SORT THE SAMPLE LIST
    b = np.sort(np.random.permutation(a)[:n])
    # RETRIEVE EACH DATE AND CHANGE TO ISOFORMAT
    answer = [str(date)[:10] for date in dr[b]]
    return answer


# GET LATEST OR EARLIEST DATE AVAILABLE GIVEN DATE SOURCE
def getfirstorlastdate(daterangedb_source, boundtype):
    if boundtype == 'earliest':
        datecol = 'first_date'
    elif boundtype == 'latest':
        datecol = 'last_date'
    # get latest possible available date
    with open(daterangedb_source, "rb") as targetfile:
        daterangedb = pkl.load(targetfile)
    if boundtype == 'earliest':
        answerdate = daterangedb[datecol].apply(lambda x: dt.date.fromisoformat(x)).min()
    elif boundtype == 'latest':
        answerdate = daterangedb[datecol].apply(lambda x: dt.date.fromisoformat(x)).max()
    return str(answerdate)


# RETURN ALL EXIST DATES IN GIVEN RANGE
# sortdir=1 to sort in descending order
def getalldates_range(start, end, sortdir):
    return [str(elem) for elem in sorted(pd.date_range(start=start, end=end).date, reverse=sortdir)]


# RETURN LAST POSSIBLE DATE GIVEN TESTLEN AND LATESTDATE IF GIVEN
def getlastpossible_selectend(latestdate, testlen, daterangedb_source):
    if latestdate == '':
        # get latest possible available date
        latestdate = getfirstorlastdate(daterangedb_source, 'latest')
    else:
        latestdate = latestdate
    last_possible_selectend = str(dt.date.fromisoformat(latestdate) - dt.timedelta(days=testlen))
    return last_possible_selectend


# RETURN ALL DATES GIVEN RANGE AND TESTLEN AND SORT ORDER
def alldatewithtestlen(testlen, earliestbound, latestbound, daterangedb_source, sortdir):
    # adjust latestbound
    latestbound = getlastpossible_selectend(latestbound, testlen, daterangedb_source)
    alldates = getalldates_range(earliestbound, latestbound, daterangedb_source, sortdir)
    return alldates


# RETURN N RANDOM EXIST DATES GIVEN TESTLEN AND LATESTDATE IF GIVEN
def getrandomexistdate_multiple(numdates, earliestbound, latestbound, testlen, daterangedb_source):
    latestpossiblerandomdate = getlastpossible_selectend(latestbound, testlen, daterangedb_source)
    randomexistdates = random_dates(earliestbound, latestpossiblerandomdate, numdates)
    return randomexistdates


# RETURN RANDOM DATE GIVEN AVAILABLE RANGE OR MANUAL RANGE AND TESTLEN
def getrandomexistdate(latestdate, firstdate, testlen, daterangedb_source):
    if latestdate == '':
        # get latest possible available date
        with open(daterangedb_source, "rb") as targetfile:
            daterangedb = pkl.load(targetfile)
        lastdate_dateobj = daterangedb['last_date'].apply(lambda x: dt.date.fromisoformat(x))
        lastdates = lastdate_dateobj.tolist()
        latestdate = str(np.max(lastdates))
    else:
        latestdate = latestdate
    if firstdate == '':
        # get earliest possible available date
        firstdate_dateobj = daterangedb['first_date'].apply(lambda x: dt.date.fromisoformat(x))
        firstdates = firstdate_dateobj.tolist()
        firstdate = str(np.min(firstdates))
    else:
        firstdate = firstdate
    last_possible_edate = str(dt.date.fromisoformat(latestdate) - dt.timedelta(days=testlen))
    exist_date = random_dates(firstdate, last_possible_edate, 1)[0]
    return exist_date


# RANDOMLY GENERATE LIST OF UNIQUE SAMPLES, EACH CONTAINING A CONTIGUOUS SET OF PERIODS OF EQUAL LENGTH
def random_time_samples(period_len, start, end, num_periods, num_samples):
    # CORRECT END INPUT
    if end == "today":
        end = str(dt.date.today())
    # CHECK IF NUMBER OF SAMPLES REQUESTED IS POSSIBLE
    sample_len = period_len * num_periods
    lastsd = dt.date.fromisoformat(end) - dt.timedelta(days=sample_len)
    possible_samples = (lastsd - dt.date.fromisoformat(start)).days + 1
    if num_samples > possible_samples:
        print("The number of samples requested (", num_samples, ") exceeds the number of possible samples (", possible_samples, "). Program exiting...")
        exit()
    # GENERATE LIST OF UNIQUE RANDOM START DATES
    start_dates = random_dates(start, lastsd, num_samples)
    # FIND END DATES TO EACH OF THE START DATES AND RETURN LIST OF THOSE PAIRS
    samples = [[str(dt.date.fromisoformat(sd) + dt.timedelta(days=(period_len * f))) for f in range(0, num_periods + 1)] for sd in start_dates]
    return samples
