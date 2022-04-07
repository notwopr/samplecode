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
from functools import partial
import multiprocessing as mp
#   THIRD PARTY IMPORTS
import numpy as np
#   LOCAL APPLICATION IMPORTS
from Modules.file_tests import checknum
from computersettings import computerobject


# multiprocessor shell
def multiprocessorshell_nocheck(dumpfolder, targetfunc, iterables, enumerateiters, targetvars, chunksize):
    if enumerateiters == 'yes':
        mpiterables = enumerate(iterables)
    else:
        mpiterables = iterables
    # run multiprocessor
    fn = partial(targetfunc, *targetvars)
    pool = mp.Pool(processes=computerobject.use_cores)
    pool.map(fn, mpiterables, chunksize)
    pool.close()
    pool.join()


# multiprocessor shell
def multiprocessorshell(dumpfolder, targetfunc, iterables, enumerateiters, targetvars, chunksize):
    if enumerateiters == 'yes':
        mpiterables = enumerate(iterables)
    else:
        mpiterables = iterables
    # run multiprocessor
    fn = partial(targetfunc, *targetvars)
    pool = mp.Pool(processes=computerobject.use_cores)
    pool.map(fn, mpiterables, chunksize)
    pool.close()
    pool.join()
    # wait for all files to download
    correct = len(iterables)
    downloadfinish = checknum(dumpfolder, correct, '')
    while downloadfinish is False:
        downloadfinish = checknum(dumpfolder, correct, '')


# multiprocessor shell
def multiprocessorshell_mapasync_getresults(targetfunc, iterables, enumerateiters, targetvars, chunksize):
    if enumerateiters == 'yes':
        mpiterables = enumerate(iterables)
    else:
        mpiterables = iterables
    # run multiprocessor
    fn = partial(targetfunc, *targetvars)
    pool = mp.Pool(mp.cpu_count())
    r = pool.map_async(fn, mpiterables, chunksize).get()
    pool.close()
    pool.join()
    return r


# multiprocessor shell
def multiprocessorshell_mapasync(dumpfolder, targetfunc, iterables, enumerateiters, targetvars, chunksize):
    if enumerateiters == 'yes':
        mpiterables = enumerate(iterables)
    else:
        mpiterables = iterables
    # run multiprocessor
    fn = partial(targetfunc, *targetvars)
    pool = mp.Pool(mp.cpu_count())
    pool.map_async(fn, mpiterables, chunksize)
    pool.close()
    pool.join()
    # wait for all files to download
    correct = len(iterables)
    downloadfinish = checknum(dumpfolder, correct, '')
    while downloadfinish is False:
        downloadfinish = checknum(dumpfolder, correct, '')


# CONVERTS AN ARRAY OF VALUES INTO MINMAX CALIBRATED VALUES GIVEN RANKDIRECTION AND REGIME
def mmcalibrated_nan(array, rankascending, regime):
    array = ((array - np.nanmin(array)) / (np.nanmax(array) - np.nanmin(array)))
    if regime == '0isbest':
        if rankascending == 1:
            array = array
        elif rankascending == 0:
            array = 1 - array
    elif regime == '1isbest':
        if rankascending == 1:
            array = 1 - array
        elif rankascending == 0:
            array = array
    return array


# CONVERTS AN ARRAY OF VALUES INTO MINMAX CALIBRATED VALUES GIVEN RANKDIRECTION AND REGIME
def mmcalibrated(array, rankascending, regime):
    array = ((array - np.min(array)) / (np.max(array) - np.min(array)))
    if regime == '0isbest':
        if rankascending == 1:
            array = array
        elif rankascending == 0:
            array = 1 - array
    elif regime == '1isbest':
        if rankascending == 1:
            array = 1 - array
        elif rankascending == 0:
            array = array
    return array
