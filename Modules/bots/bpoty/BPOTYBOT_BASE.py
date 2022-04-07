"""
Title: Best Part of the Year Bot
Date Started: Nov 4, 2019
Version: 3.0
Version Start: Sept 17, 2020
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied
    without the express written consent of David Hyongsik Choi.
Purpose: Find best parts of the year to invest in.
"""
# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import math
import datetime as dt
from dateutil.relativedelta import relativedelta
from collections import ChainMap
#   THIRD PARTY IMPORTS
import numpy as np
import pandas as pd
#   LOCAL APPLICATION IMPORTS
from Modules.multiprocessing import multiprocessorshell_nocheck, multiprocessorshell_mapasync_getresults
from Modules.price_history_slicing import pricedf_daterange
from file_functions import readpkl_fullpath, savetopkl, buildfolders_singlechild, buildfolders_regime_testrun
from Modules.growthcalcbot import removeleadingzeroprices
from file_hierarchy import daterangedb_source, tickerlistcommon_source


def getpotynamesandperiods(potydef, potylen, earliestdate, latestdate):
    # STORE RANGE OF YEARS TO TEST
    first_year = int(dt.datetime.fromisoformat(earliestdate).year)
    end_year = int(dt.datetime.fromisoformat(latestdate).year)
    testyears = list(range(first_year, end_year + 1))
    # STORE POTY NAMES and TEST PERIODS
    if potydef == 'month':
        poty_names = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JLY', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        all_periods = [[[str((dt.datetime(year, month, 1)).date()), str((dt.datetime(year, month, 1) + relativedelta(months=+1) - dt.timedelta(days=1)).date())] for month in range(1, 13)] for year in testyears]
    elif potydef == 'year':
        poty_names = ['wholeyear']
        all_periods = [[str((dt.datetime(year, 1, 1)).date()), str(dt.datetime(year+1, 1, 1).date())] for year in testyears]
    else:
        totalchunks = math.ceil(366 / potylen)
        poty_names = [f'{potylen}-daychunk{chunknum}' for chunknum in range(1, totalchunks+1)]
        all_periods = [[[str((dt.datetime(year, 1, 1)).date() + dt.timedelta(days=potylen*(chunknum-1))), str((dt.datetime(year, 1, 1)).date() + dt.timedelta(days=potylen*chunknum))] for chunknum in range(1, totalchunks+1)] for year in testyears]
    # CORRECT DATE ERROR
    if all_periods[0][0][0] == '1962-01-01':
        all_periods[0][0][0] = '1962-01-02'
    '''
    if verbose == 'verbose':
        print('all_periods:', all_periods)
    '''
    return all_periods, poty_names, testyears


def getfoliogrowth_singlechunk(earliestdate, latestdate, ticker, daterangedb_source, tickerlistcommon_source, prices, itertuple):
    poty_name = itertuple[0]
    period = itertuple[1]
    '''
    if verbose == 'verbose':
        print('chunk:', poty_name)
        print('period:', period)
    '''
    # if period is within dates available...
    period_startobj = dt.date.fromisoformat(period[0])
    earliestdate_obj = dt.date.fromisoformat(earliestdate)
    period_endobj = dt.date.fromisoformat(period[1])
    latestdate_obj = dt.date.fromisoformat(latestdate)
    '''
    if verbose == 'verbose':
        print('start date of period:', period_startobj)
        print('earliest date available:', earliestdate_obj)
        print('ending date of period:', period_endobj)
        print('latest date available:', latestdate_obj)
        print('We have enough data available:', (period_endobj <= latestdate_obj) & (period_startobj >= earliestdate_obj))
    '''
    if period_endobj <= latestdate_obj and period_startobj >= earliestdate_obj:
        # slice prices
        slicedprices = prices.copy()
        slicedprices = slicedprices.loc[(slicedprices['date'] >= period[0]) & (slicedprices['date'] <= period[1])].copy()
        # RESET INDEX
        slicedprices.reset_index(drop=True, inplace=True)
        # remove leading zeroes
        slicedprices = removeleadingzeroprices(slicedprices, [ticker])
        # CALCULATE GROWTH over period
        startp = slicedprices[slicedprices['date'] == period[0]][ticker].item()
        endp = slicedprices[slicedprices['date'] == period[1]][ticker].item()
        if startp != 0:
            growth = (endp - startp) / startp
        else:
            growth = np.nan
    else:
        growth = np.nan
    summary = {poty_name: growth}
    '''
    if verbose == 'verbose':
        print(f'summary: {summary}')
    '''
    return summary


def getyearsummary(tyear, year_periods, potydef, earliestdate, latestdate, ticker, prices, poty_names, chunksize):
    '''
    if verbose == 'verbose':
        print('year:', tyear)
        print('periods:', year_periods)
    '''
    summary = {'YEAR': tyear}
    if potydef == 'year':
        foliogrowthdict = getfoliogrowth_singlechunk(earliestdate, latestdate, ticker, daterangedb_source, tickerlistcommon_source, prices, (poty_names[0], year_periods))
        summary.update(foliogrowthdict)
    else:
        # FOR EACH POTY CHUNK
        subsummarylist = multiprocessorshell_mapasync_getresults(getfoliogrowth_singlechunk, zip(poty_names, year_periods), 'no', (earliestdate, latestdate, ticker, daterangedb_source, tickerlistcommon_source, prices), chunksize)
        summary = dict(ChainMap(*subsummarylist, summary))
    # APPEND SUMMARY GROWTH FOR THAT YEAR TO RESULT LIST
    return summary


def getbpotychart(testrunparent, potydef, testyears, all_periods, earliestdate, latestdate, ticker, prices, poty_names, chunksize):
    '''
    all_rows = []
    # FOR EACH TEST YEAR...
    for (tyear, year_periods) in zip(testyears, all_periods):
        if verbose == 'verbose':
            print('year:', tyear)
            print('periods:', year_periods)
        summary = {'YEAR': tyear}
        if potydef == 'year':
            #tyeardump = buildfolders_singlechild(foliogrowthdump_parent, f'{tyear}_dumpfiles')
            foliogrowthdict = getfoliogrowth_singlechunk(verbose, earliestdate, latestdate, ticker, daterangedb_source, tickerlistcommon_source, prices, (poty_names[0], year_periods))
            summary.update(foliogrowthdict)
        else:
            # FOR EACH POTY CHUNK
            subsummarylist = multiprocessorshell_mapasync_getresults(getfoliogrowth_singlechunk, zip(poty_names, year_periods), 'no', (verbose, earliestdate, latestdate, ticker, daterangedb_source, tickerlistcommon_source, prices), chunksize)
            summary = dict(ChainMap(*subsummarylist, summary))
        # APPEND SUMMARY GROWTH FOR THAT YEAR TO RESULT LIST
        all_rows.append(summary)
    '''
    # CREATE DATAFRAME OF RESULTS
    all_rows = [getyearsummary(tyear, year_periods, potydef, earliestdate, latestdate, ticker, prices, poty_names, chunksize) for (tyear, year_periods) in zip(testyears, all_periods)]
    colorder = ['YEAR'] + poty_names
    masterdf = pd.DataFrame(data=all_rows, columns=colorder)
    #if verbose == 'verbose':
        #print(masterdf)
    # ARCHIVE TO FILE
    #firstyearname = str(testyears[0])
    #lastyearname = str(testyears[-1])
    #masterdfname = f"best{potydef}_{ticker}_{firstyearname}_to_{lastyearname}"
    # ARCHIVE FULL RESULTS
    #savetopkl(masterdfname, testrunparent, masterdf)
    #masterdf.to_csv(index=False, path_or_buf=testrunparent / f"{masterdfname}.csv")
    return masterdf


def get_poty_average(globalparams):
    # FIND EARLIEST AND LATEST DATE AVAILABLE
    prices = pricedf_daterange(globalparams['ticker'], globalparams['beg_date'], globalparams['end_date'])
    earliestdate = str(prices.iat[0, 0].date())
    latestdate = str(prices.iat[-1, 0].date())
    # get all periods, poty names and testyears
    all_periods, poty_names, testyears = getpotynamesandperiods(globalparams['potydef'], globalparams['potylen'], earliestdate, latestdate)
    # get bpotychart df
    testregimeparent, testrunparent = buildfolders_regime_testrun(globalparams['rootdir'], globalparams['testnumber'], globalparams['todaysdate'], globalparams['testregimename'])
    return getbpotychart(testrunparent, globalparams['potydef'], testyears, all_periods, earliestdate, latestdate, globalparams['ticker'], prices, poty_names, globalparams['chunksize'])
