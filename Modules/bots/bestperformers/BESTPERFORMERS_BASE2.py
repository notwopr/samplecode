"""
Title: Best Performers Base Script
Date Started: Dec 7, 2019
Version: 3.0
Version Start: Feb 19, 2022
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied
    without the express written consent of David Hyongsik Choi.
Purpose: Functions to return list of best performing stocks given time period
"""
# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
#import datetime as dt
#   THIRD PARTY IMPORTS
import pandas as pd
#   LOCAL APPLICATION IMPORTS
from Modules.multiprocessing import multiprocessorshell_mapasync_getresults
from Modules.tickerportalbot import tickerportal2
#from file_hierarchy import daterangedb_source, tickerlistcommon_source
from Modules.bots.bestperformers.BESTPERFORMERS_BASE2_METRICLIBRARY import allmetrics
from Modules.bots.bestperformers.BESTPERFORMERS_BASE2_CRUNCHER import filterallmetrics, allmetrics_single
#from webapp.servernotes import benchmarkdata


def bestperformer_cruncher(configdict):
    allexistingstocks = tickerportal2(configdict['start_date'], 'common+bench')# + [v['ticker'] for v in benchmarkdata.values() if v["earliestdate"] <= dt.date.fromisoformat(configdict['start_date'])]
    metrics_to_run = {i: allmetrics[i] for i in allmetrics if configdict[i] is not None}
    table_results = multiprocessorshell_mapasync_getresults(allmetrics_single, allexistingstocks, 'no', (metrics_to_run, configdict['start_date'], configdict['end_date']), configdict['chunksize'])
    allmetricsdf = pd.DataFrame(data=table_results)
    allmetricsdf = filterallmetrics(allmetricsdf, metrics_to_run, configdict)
    allmetricsdf.rename(columns={v['metricname']: k for k, v in allmetrics.items()}, inplace=True)
    return allmetricsdf
