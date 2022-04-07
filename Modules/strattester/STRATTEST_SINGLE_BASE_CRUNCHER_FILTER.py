"""
Title: STRAT TEST SINGLE BASE CRUNCHER - FILTERMETRICS
Date Started: May 15, 2020
Version: 4.00
Version Start Date: Oct 20, 2020
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose: Scheme for running filter for each metric to be tested.

Versions:
1.01:  Added metric categories and 2018 metrics.
1.02:  Make it easier to customize each filter with its own lookback setting.
2.00:  Percentile rank thresholds.
3.00:  Cleaned up code to shift all work to layercake script.
"""
# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
#   THIRD PARTY IMPORTS
#import numpy as np
#   LOCAL APPLICATION IMPORTS
from file_functions import savetopkl#, buildfolders_parent_cresult_cdump
from Modules.metriclibrary.STRATTEST_FUNCBASE import getmetcolname
#from STRATTEST_SINGLE_BASE_CRUNCHER_ALLMETRICVALS import allmetricval_cruncher


# FILTER THE ALLMETRIC DF
def filterallmetrics(dumpfolder, allmetricsdf, metrics_to_run, beg_date, end_date, rankmeth, rankregime, savemode):

    for metricitem in metrics_to_run:
        thresholdtype = metricitem['thresholdtype']
        metcolname = getmetcolname(metricitem)

        # GET PERCENTILE RANK
        if thresholdtype == 'pctrank':
            rankdirection = metricitem['rankascending']
            pctrankcol = f'pctrank_{metcolname}'
            allmetricsdf[pctrankcol] = allmetricsdf[metcolname].rank(ascending=rankdirection, pct=True)

            # SAVE PERCENTILE RANKS BEFORE FILTERING
            pctranksfn = f"allpctranks_as_of_{end_date}"
            if savemode == 'pkl':
                savetopkl(pctranksfn, dumpfolder, allmetricsdf)
            elif savemode == 'csv':
                allmetricsdf.to_csv(index=False, path_or_buf=dumpfolder / f"{pctranksfn}.csv")

    # FILTER EACH METRIC
    for metricitem in metrics_to_run:
        thresholdtype = metricitem['thresholdtype']
        filterdirection = metricitem['filterdirection']
        metcolname = getmetcolname(metricitem)

        # CAPTURE THRESHOLDS
        if filterdirection == 'above' or filterdirection == 'below' or filterdirection == 'equalabove' or filterdirection == 'equalbelow':
            threshval = metricitem['threshold']
            #threshold = metricitem['threshold']
            # DEFINE THRESHOLD
            #if threshold in ['market', '^DJI', '^INX', '^IXIC']:
                #if threshold == 'market':
                    #marketpool = ['^DJI', '^INX', '^IXIC']
                #else:
                    #marketpool = [threshold]
                # create ranks and resultfolder
                #marketparent, marketresults, marketdump = buildfolders_parent_cresult_cdump(dumpfolder, f'{metcolname}_market')
                #marketresultdf = allmetricval_cruncher(marketresults, marketdump, [metricitem], beg_date, end_date, marketpool, rankmeth, rankregime, savemode)
                # define market threshold
                #if filterdirection == 'above':
                    #threshval = np.max(marketresultdf[metcolname])
                #if filterdirection == 'below':
                    #threshval = np.min(marketresultdf[metcolname])
            #else:
                #threshval = threshold
        elif filterdirection == 'between' or filterdirection == 'betweeninclusive':
            upperthresh = metricitem['upperthreshold']
            lowerthresh = metricitem['lowerthreshold']

        # DEFINE FILTER COLUMN
        if thresholdtype == 'pctrank':
            pctrankcol = f'pctrank_{metcolname}'
            filtercol = pctrankcol
        else:
            filtercol = metcolname

        # FILTER OUT STOCKS ACCORDING TO FILTER DIRECTION
        if filterdirection == 'above':
            allmetricsdf = allmetricsdf[allmetricsdf[filtercol] > threshval].copy()
        elif filterdirection == 'equalabove':
            allmetricsdf = allmetricsdf[allmetricsdf[filtercol] >= threshval].copy()
        elif filterdirection == 'below':
            allmetricsdf = allmetricsdf[allmetricsdf[filtercol] < threshval].copy()
        elif filterdirection == 'equalbelow':
            allmetricsdf = allmetricsdf[allmetricsdf[filtercol] <= threshval].copy()
        elif filterdirection == 'between':
            allmetricsdf = allmetricsdf[(allmetricsdf[filtercol] > lowerthresh) & (allmetricsdf[filtercol] < upperthresh)].copy()
        elif filterdirection == 'betweeninclusive':
            allmetricsdf = allmetricsdf[(allmetricsdf[filtercol] >= lowerthresh) & (allmetricsdf[filtercol] <= upperthresh)].copy()
        if len(allmetricsdf) == 0:
            return allmetricsdf
    return allmetricsdf
