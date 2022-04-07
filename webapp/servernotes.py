"""
Title: Server Stats
Date Started: Jan 22, 2022
Version: 1.00
Version Start: Jan 22, 2022
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose:  Server stat info.
"""
# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import os
import datetime as dt
#   THIRD PARTY IMPORTS
import numpy as np
#   LOCAL APPLICATION IMPORTS
from file_hierarchy import PRICES, DATE_RESULTS, daterangedb_name, tickerlistcommon_name, TICKERS
from file_functions import readpkl
from Modules.price_history import grabsinglehistory
from Modules.numbers import formalnumber_integer


def getlastmodified(folder, filename):
    modtime_since_epoc = os.path.getmtime(folder / filename)
    modtime = dt.datetime.fromtimestamp(modtime_since_epoc).strftime('%Y-%m-%d %H:%M:%S')
    return modtime


def getstockdata():
    daterangefile = readpkl(daterangedb_name, DATE_RESULTS)
    # limit to common stock
    tickerlist_common = readpkl(tickerlistcommon_name, TICKERS)
    daterangefile = daterangefile[daterangefile['stock'].isin(tickerlist_common['symbol'])]
    # shift latest date by one to account for tiingo data sync idiosyncracy
    latestdate = str(dt.date.fromisoformat(np.max(daterangefile['last_date'])) - dt.timedelta(days=1))
    return {
        'earliest': np.min(daterangefile['first_date']),
        'latest': latestdate,
        'numtickers': len(tickerlist_common['symbol'])
        }


# get benchmark earliest and latestdate
def getbenchdates(benchmarks):
    for k, v in benchmarks.items():
        benchprices = grabsinglehistory(v['ticker'])
        benchmarks[k].update({
            'earliestdate': benchprices.iloc[0]['date'],
            'latestdate': benchprices.iloc[-1]['date']
        })
    return benchmarks


# BENCHMARK KEY DICT
benchmarks = {
    'dow': {
        'name': 'Dow Jones',
        'ticker': '^DJI'
        },
    'snp': {
        'name': 'S&P 500',
        'ticker': '^INX'
        },
    'nasdaq': {
        'name': 'NASDAQ',
        'ticker': '^IXIC'
        }
}

# SERVER STATS
stockdata = getstockdata()
benchmarkdata = getbenchdates(benchmarks)
server_stats = {
    'Stock data available': 'All common shares traded on the United States NASDAQ and NYSE exchanges.',
    'Types of pricing data available': 'End of Day prices only.',
    'Number of ticker symbols available': f'{formalnumber_integer(stockdata["numtickers"])}',
    'Stock price data last updated': f'{getlastmodified(PRICES, "allpricematrix_common.pkl")}',
    'Benchmark price data last updated': f'{getlastmodified(PRICES, "allpricematrix_bench.pkl")}',
    'Dates available for stock price data': f'{stockdata["earliest"]} to {stockdata["latest"]}'
    }
for v in benchmarkdata.values():
    server_stats.update(
        {f'Dates available for the {v["name"]} price data': f'{v["earliestdate"]} to {v["latestdate"]}'}
        )
