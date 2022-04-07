"""
Title: RETRIEVE PRICE OF A STOCK ON GIVEN DATE
Date Started: Dec 14, 2020
Version: 1.00
Version Start: Dec 14, 2020
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose:  Returns aggregate slopescore data by Starting Letter of a stock's name.
"""
# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import pickle as pkl
#   THIRD PARTY IMPORTS
import pandas as pd
from scipy import stats
import numpy as np
#   LOCAL APPLICATION IMPORTS
from Modules.price_history_slicing import pricedf_daterange
from Modules.metriclibrary.STRATTEST_FUNCBASE_RAW import slopescore_single
from file_hierarchy import daterangedb_source, tickerlistcommon_source
from file_functions import buildfolders_regime_testrun, savetopkl, buildfolders_singlechild
from Modules.tickerportalbot import tickerportal4
from Modules.multiprocessing import multiprocessorshell, multiprocessorshell_mapasync_getresults


# get stats for one letter
def getletterdata_single(tickerlist, asofdate, letter):
    binofslopescores = [slopescore_single(pricedf_daterange(ticker, '', asofdate)) for ticker in tickerlist if ticker.startswith(letter)]
    num_samples = len(binofslopescores)
    summary = {
        'First Letter': letter,
        f'Number of Tickers (as of {asofdate})': num_samples,
        '% of Total': (num_samples / len(tickerlist))*100,
        'Mean % growth per day': np.mean(binofslopescores)*100,
        'Median % growth per day': np.median(binofslopescores)*100,
        'Spread (Standard Deviation)': np.std(binofslopescores)*100,
        'Spread (Median Absolute Deviation)': stats.median_abs_deviation(binofslopescores)*100
        }
    return summary


def masterbestletter(global_params):
    # build folders
    #testregimeparent, testrunparent = buildfolders_regime_testrun(global_params['rootdir'], global_params['testnumber'], global_params['todaysdate'], global_params['testregimename'])
    # create masterdf
    alphabetstr = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    # get tickers that have atleast two rows of prices
    tickerlist = tickerportal4(global_params['presentdate'], global_params['presentdate'], 'common', 1)
    # create multiprocessor dumpfolder
    #letterstatsdump = buildfolders_singlechild(testrunparent, 'letterstatsdump')
    # for each letter in the alphabet, get stats
    targetvars = (tickerlist, global_params['presentdate'])
    #multiprocessorshell(letterstatsdump, getletterdata_single, list(alphabetstr), 'no', targetvars, global_params['chunksize'])
    allsummaries = multiprocessorshell_mapasync_getresults(getletterdata_single, list(alphabetstr), 'no', targetvars, global_params['chunksize'])
    # assemble results
    #allsummaries = []
    #for child in letterstatsdump.iterdir():
    #    with open(child, "rb") as targetfile:
    #        unpickled_raw = pkl.load(targetfile)
    #    allsummaries.append(unpickled_raw)
    summdf = pd.DataFrame(data=allsummaries)
    # save
    #summdf.to_csv(index=False, path_or_buf=testrunparent / 'bestletterresults.csv')
    return summdf
