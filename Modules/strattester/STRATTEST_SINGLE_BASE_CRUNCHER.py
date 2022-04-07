"""
Title: STRAT TEST SINGLE BASE CRUNCHER
Date Started: May 15, 2020
Version: 5.00
Version Start Date: Mar 11, 2021
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose: Scheme for running filter for each metric to be tested.

Versions:
1.01:  Added metric categories and 2018 metrics.
1.02:  Make it easier to customize each filter with its own lookback setting.
2.00:  Percentile rank thresholds.
3.00:  Cleaned up code to shift all work to layercake script.
5: Add accommodations for revenue and freecashflow data sources.
"""
# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
#   THIRD PARTY IMPORTS
#   LOCAL APPLICATION IMPORTS
from file_functions import savetopkl
from Modules.strattester.STRATTEST_SINGLE_BASE_CRUNCHER_ALLMETRICVALS import allmetricval_cruncher
from Modules.strattester.STRATTEST_SINGLE_BASE_CRUNCHER_FILTER import filterallmetrics


# SAVE REMAINING STOCKS AS PORTFOLIO TO RUN PERFORMANCE TEST
def stagecruncher(dumpfolder, stagenum, stagescript, beg_date, end_date, pool, rankmeth, rankregime, savemode, chunksize):
    # parse stage script
    scriptname = stagescript['scriptname']
    scriptparams = stagescript['scriptparams']
    # if datasource key in stagescript
    if 'datasourcetype' in stagescript.keys():
        datasourcetype = stagescript['datasourcetype']
    else:
        datasourcetype = 'prices'
    # set stage name
    stagename = f'{stagenum}_{scriptname}'
    # get df of all metric values
    allmetricsdf = allmetricval_cruncher(dumpfolder, datasourcetype, scriptname, scriptparams, beg_date, end_date, pool, rankmeth, rankregime, savemode, chunksize)
    # filter df
    finaldf = filterallmetrics(dumpfolder, allmetricsdf, scriptparams, beg_date, end_date, rankmeth, rankregime, savemode)

    # if finaldf not empty, save to file
    if len(finaldf) != 0:
        finalistfn = f"{stagename}_finalists_as_of_{end_date}"
        if savemode == 'pkl':
            savetopkl(finalistfn, dumpfolder, finaldf)
        elif savemode == 'csv':
            finaldf.to_csv(index=False, path_or_buf=dumpfolder / f"{finalistfn}.csv")
    else:
        print('All stock candidates filtered out.')
    return finaldf
