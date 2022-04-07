"""
Title: volstats functions
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
from functools import partial
import multiprocessing as mp
#   THIRD PARTY IMPORTS
import pandas as pd
#   LOCAL APPLICATION IMPORTS
from Modules.price_calib import add_calibratedprices_portfolio
from Modules.metriclibrary.STRATTEST_FUNCBASE_MMBM import unifatshell_single, dropmag_single, dropprev_single, dropscoreratio_single, dropscore_single
from Modules.list_functions import removedupes


# get all calibrations needed metrics_to_run for single stock
def get_all_calibs_single(metrics_to_run, pricedf, stock):
    # get list of all calibrations needed
    allcalibrations = [item for metricitem in metrics_to_run for item in metricitem['calibration']]
    allcalibrations = removedupes(allcalibrations)
    # get calibrated prices
    return add_calibratedprices_portfolio(pricedf, allcalibrations, [stock])


# get dict of stock and its metricscores for metrics requested
def getmetricvals_single(filterdf, beg_date, end_date, bench, stock):
    '''INSERT LISTOF DICTS OF METRICS TO RUN HERE'''
    metrics_to_run = [
        {
            'metricname': 'fatscore_baremaxtoraw',
            'metricfunc': unifatshell_single,
            'metricparams': {
                'prices': None,
                'idealcol': f'{stock}_baremaxraw',
                'focuscol': stock,
                'stat_type': 'avg'
            },
            'calibration': ['baremaxraw']
        },
        {
            'metricname': 'fatscore_baremaxtobaremin',
            'metricfunc': unifatshell_single,
            'metricparams': {
                'prices': None,
                'idealcol': f'{stock}_baremaxraw',
                'focuscol': f'{stock}_oldbareminraw',
                'stat_type': 'avg'
            },
            'calibration': ['oldbareminraw', 'baremaxraw']
        },
        {
            'metricname': 'drop_mag',
            'metricfunc': dropmag_single,
            'metricparams': {
                'prices': None,
                'uppercol': f'{stock}_baremaxraw',
                'lowercol': stock,
                'stat_type': 'avg'
            },
            'calibration': ['baremaxraw']
        },
        {
            'metricname': 'drop_prev',
            'metricfunc': dropprev_single,
            'metricparams': {
                'prices': None,
                'uppercol': f'{stock}_baremaxraw',
                'lowercol': stock
            },
            'calibration': ['baremaxraw']
        },
        {
            'metricname': 'dropscore',
            'metricfunc': dropscore_single,
            'metricparams': {
                'prices': None,
                'uppercol': f'{stock}_baremaxraw',
                'lowercol': stock,
                'stat_type': 'avg'
            },
            'calibration': ['baremaxraw']
        }
    ]
    # add different benchmark versions of dropscore ratio
    benchnames_byticker = {
        '^DJI': 'Dow Jones',
        '^INX': 'S&P 500',
        '^IXIC': 'NASDAQ'
        }
    if len(bench) > 0:
        for b in bench:
            metrics_to_run.append(
                {
                    'metricname': f'dropscoreratio_{benchnames_byticker[b]}',
                    'metricfunc': dropscoreratio_single,
                    'metricparams': {
                        'prices': None,
                        'uppercol': f'{stock}_baremaxraw',
                        'lowercol': stock,
                        'stat_type': 'avg',
                        'benchticker': b
                    },
                    'calibration': ['baremaxraw']
                }
            )
    else:
        metrics_to_run.append(
            {
                'metricname': 'dropscoreratio_NASDAQ',
                'metricfunc': dropscoreratio_single,
                'metricparams': {
                    'prices': None,
                    'uppercol': f'{stock}_baremaxraw',
                    'lowercol': stock,
                    'stat_type': 'avg',
                    'benchticker': '^IXIC'
                },
                'calibration': ['baremaxraw']
            }
        )

    '''END OF METRICS TO RUN LIST'''
    # get all required calibrations
    pricedf = get_all_calibs_single(metrics_to_run, filterdf[['date', stock]], stock)
    # update metricparams with new pricedf
    for m in metrics_to_run:
        m['metricparams'].update({'prices': pricedf})
    summary = {
        f'stock {beg_date} to {end_date}': stock
        }
    summary.update({f'{m["metricname"]}': m['metricfunc'](**m['metricparams']) for m in metrics_to_run})
    return summary


# return df of stocks and their metricvals for all metrics requested
def getallmetricvalsdf(filterdf, tickerlist, bench, beg_date, end_date):
    # FOR EACH STOCK IN POOL, GET METRIC VALUE
    pool = mp.Pool(mp.cpu_count())
    fn = partial(getmetricvals_single, filterdf, beg_date, end_date, bench)
    resultlist = pool.map_async(fn, tickerlist).get()
    pool.close()
    pool.join()
    # assemble dataframe of results
    resultdf = pd.DataFrame(data=resultlist)
    return resultdf
