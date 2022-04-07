"""
Title: STRAT TEST SINGLE BASE
Date Started: July 10, 2020
Version: 2
Version Start: Oct 20, 2020
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose:  Given an existence date, runs pool thru first pass screening, runs again through given screening method, and returns percentage of resulting pool that beat market during the test period.
VERSIONS:
1.01: Optimize with updated functions.  Allow for more modulatory.
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
#   THIRD PARTY IMPORTS
import pandas as pd
#   LOCAL APPLICATION IMPORTS
from Modules.strattester.STRATTEST_SINGLE_BASE_CRUNCHER_ALLMETRICVALS import lookbackcruncher_single
from Modules.multiprocessing import multiprocessorshell_mapasync_getresults
from Modules.ranking_calib import mmcalibrated
from Modules.metriclibrary.STRATTEST_FUNCBASE import getmetcolname, priceslicer_shortenend
from Modules.metriclibrary.STRATTEST_FUNCBASE_RAW import getpricedate_single
from Modules.price_history_slicing import pricedf_daterange, pricedf_daterange_fundies
from Modules.dataframe_functions import filtered_double, filtered_single


def recoverybotshell_single(datasourcetype, metrics_to_run, benchmatrixchangesdf, beg_date, end_date, stock):
    # separate currtoath metric from rest
    currtoathmetrics = [item for item in metrics_to_run if item['metricname'].startswith('currtoath')]
    remaindermetrics = [item for item in metrics_to_run if not item['metricname'].startswith('currtoath')]
    # GET PRICE HISTORY
    prices = pricedf_daterange(stock, beg_date, end_date)
    # CREATE MASTER SUMMARY
    summary = {
        'stock': stock,
        'age': len(prices) - 1
        }
    # add currtoath stats to summary first
    summary = lookbackcruncher_single(summary, datasourcetype, prices.copy(), currtoathmetrics, benchmatrixchangesdf, stock)
    preath_occur = currtoathmetrics[0]['ath_occur']
    ath_date = getpricedate_single(prices.copy(), stock, 'max', preath_occur)
    # add preathend date to summary
    summary.update({f'ATHdate_{preath_occur}': ath_date})
    # slice prices to new end_date
    prices = priceslicer_shortenend(prices, ath_date)
    # if new range has less than two rows, skip
    if len(prices) >= currtoathmetrics[0].get('min_preath_age', 2):
        # run remaining metrics on pre-ATH date range
        summary = lookbackcruncher_single(summary, datasourcetype, prices, remaindermetrics, benchmatrixchangesdf, stock)
    return summary


def lookbackshell_single(datasourcetype, metrics_to_run, benchmatrixchangesdf, beg_date, end_date, stock):
    # GET DATA SOURCE HISTORY
    if datasourcetype == 'revenue' or datasourcetype == 'freecashflow':
        datadf = pricedf_daterange_fundies(stock, 'fundies', beg_date, end_date)
        # KEEP ONLY ONE AND CHANGE NAME
        datadf = datadf[["date", f'{datasourcetype}_{stock}']].copy()
        datadf.rename(columns={f'{datasourcetype}_{stock}': stock}, inplace=True)
        # CREATE MASTER SUMMARY
        summary = {
            'stock': stock,
            }
    else:
        datadf = pricedf_daterange(stock, beg_date, end_date)
        # CREATE MASTER SUMMARY
        summary = {
            'stock': stock,
            'age': len(datadf) - 1
            }
    summary = lookbackcruncher_single(summary, datasourcetype, datadf, metrics_to_run, benchmatrixchangesdf, stock)
    return summary


def allmetricval_cruncher(datasourcetype, scriptname, scriptparams, beg_date, end_date, tickerlist, rankmeth, rankregime, chunksize):
    nonwinratemetrics_to_run = scriptparams
    # load marketbeater benchmarkdf if metric chosen
    benchmatrixchangesdf = ''
    # run metricsval multiprocessor
    if scriptname.startswith('recoverybot'):
        mpfunc = recoverybotshell_single
    else:
        mpfunc = lookbackshell_single
    # run multiprocessor
    table_results = multiprocessorshell_mapasync_getresults(mpfunc, tickerlist, 'no', (datasourcetype, nonwinratemetrics_to_run, benchmatrixchangesdf, beg_date, end_date), chunksize)
    masterdf = pd.DataFrame(data=table_results)
    # RANK DATA
    sumcols = []
    weight_total = 0
    for metricitem in scriptparams:
        # DEFINE RANK PARAMS
        metricweight = metricitem['metricweight']
        metcolname = getmetcolname(metricitem)
        # RANK METRIC DATA COLUMN
        rankcolname = f'RANK_{metcolname} (w={metricweight})'
        subjectcolname = metcolname
        # SET METRIC COLUMN RANK DIRECTION
        rankdirection = metricitem['rankascending']
        if rankmeth == 'minmax':
            masterdf[rankcolname] = mmcalibrated(masterdf[subjectcolname].to_numpy(), rankdirection, rankregime)
        elif rankmeth == 'standard':
            masterdf[rankcolname] = masterdf[subjectcolname].rank(ascending=rankdirection)
        # GET EACH RANKCOLUMN'S WEIGHTED RANK VALUE
        wrankcolname = f'w_{rankcolname}'
        masterdf[wrankcolname] = (masterdf[rankcolname] * metricweight)
        # KEEP TRACK OF THE WEIGHTED RANK COLUMN TO SUM LATER
        sumcols.append(wrankcolname)
        # ADD WEIGHT TO WEIGHT TOTAL
        weight_total += metricweight
    # sum weighted rankcols
    if weight_total <= 0.98 or weight_total >= 1.02:
        print(f'weight total for rankings does not equal 1: ({weight_total}) Aborting...please check the metricweights.  If everything is correct, then run again by removing this code check')
        exit()
    masterwrankcolname = f'MASTER WEIGHTED RANK {weight_total}'
    masterdf[masterwrankcolname] = masterdf[sumcols].sum(axis=1, min_count=len(sumcols))
    # rank overall weighted rankcol
    if rankmeth == 'minmax':
        if rankregime == '1isbest':
            finalrankascend = 0
        elif rankregime == '0isbest':
            finalrankascend = 1
    elif rankmeth == 'standard':
        finalrankascend = 1
    finalrankcolname = f'MASTER FINAL RANK as of {end_date}'
    masterdf[finalrankcolname] = masterdf[masterwrankcolname].rank(ascending=finalrankascend)
    # RE-SORT AND RE-INDEX
    masterdf.sort_values(ascending=True, by=[finalrankcolname], inplace=True)
    masterdf.reset_index(drop=True, inplace=True)
    return masterdf


# FILTER THE ALLMETRIC DF
def filterallmetrics(datasourcetype, scriptname, scriptparams, allmetricsdf, metrics_to_run, beg_date, end_date, rankmeth, rankregime, chunksize):
    # GET PERCENTILE RANKS IF ANY
    for metricitem in metrics_to_run:
        thresholdtype = metricitem['thresholdtype']
        metcolname = getmetcolname(metricitem)
        if thresholdtype == 'pctrank':
            rankdirection = metricitem['rankascending']
            pctrankcol = f'pctrank_{metcolname}'
            allmetricsdf[pctrankcol] = allmetricsdf[metcolname].rank(ascending=rankdirection, pct=True)
    # FILTER EACH METRIC
    for metricitem in metrics_to_run:
        thresholdtype = metricitem['thresholdtype']
        filterdirection = metricitem['filterdirection']
        metcolname = getmetcolname(metricitem)
        # DEFINE FILTER COLUMN
        if thresholdtype == 'pctrank':
            pctrankcol = f'pctrank_{metcolname}'
            filtercol = pctrankcol
        else:
            filtercol = metcolname
        # CAPTURE THRESHOLDS & FILTER OUT STOCKS ACCORDING TO FILTER DIRECTION
        if filterdirection in ['>', '>=', '<', '<=']:
            if metricitem['threshold'] == 'bestbench':
                threshvaldf = allmetricval_cruncher(datasourcetype, scriptname, scriptparams, beg_date, end_date, ["^DJI", "^INX", "^IXIC"], rankmeth, rankregime, chunksize)
                targetvals = threshvaldf[threshvaldf['stock'].isin(["^DJI", "^INX", "^IXIC"])][filtercol]
                threshval = max(targetvals) if metricitem['better'] == 'bigger' else min(targetvals)
            else:
                threshval = metricitem['threshold']
            allmetricsdf = filtered_single(allmetricsdf, filterdirection, threshval, filtercol)
        elif filterdirection in ['><', '><=', '>=<', '>=<=']:
            upperthresh = metricitem['upperthreshold']
            lowerthresh = metricitem['lowerthreshold']
            allmetricsdf = filtered_double(allmetricsdf, filterdirection, lowerthresh, upperthresh, filtercol)
        if len(allmetricsdf) == 0:
            return allmetricsdf
    return allmetricsdf


# SAVE REMAINING STOCKS AS PORTFOLIO TO RUN PERFORMANCE TEST
def stagecruncher(stagenum, stagescript, beg_date, end_date, pool, rankmeth, rankregime, chunksize):
    scriptname = stagescript['scriptname']
    scriptparams = stagescript['scriptparams']
    if 'datasourcetype' in stagescript.keys():
        datasourcetype = stagescript['datasourcetype']
    else:
        datasourcetype = 'prices'
    allmetricsdf = allmetricval_cruncher(datasourcetype, scriptname, scriptparams, beg_date, end_date, pool, rankmeth, rankregime, chunksize)
    return filterallmetrics(datasourcetype, scriptname, scriptparams, allmetricsdf, scriptparams, beg_date, end_date, rankmeth, rankregime, chunksize)


# GIVEN STRAT PANEL, EXISTENCE DATE, RETURNS RESULTING DF AND POOL
def getstratdfandpool(setrunparent, exist_date, strat_panel, currentpool, rankmeth, rankregime, chunksize):
    for stagenum, stagescript in strat_panel['stages'].items():
        stagename = f'{stagenum}_{stagescript["scriptname"]}'
        stagedf = stagecruncher(stagenum, stagescript, '', exist_date, currentpool, rankmeth, rankregime, chunksize)
        currentpool = stagedf['stock'].tolist()
        if len(currentpool) == 0:
            print(f'Stage {stagenum}: All remaining stocks were filtered out.')
            break
    finalistfn = f"{stagename}_finalists_as_of_{exist_date}"
    stagedf.to_csv(index=False, path_or_buf=setrunparent / f"{finalistfn}.csv")
    return currentpool
