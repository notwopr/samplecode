"""
Title: Stock Price Retriever - Tiingo API
Date Started: March 16, 2019
Version: 1.1
Version Start Date: May 5, 2020
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied
    without the express written consent of David Hyongsik Choi.
Purpose: Retrieve prices for a given stock.

ON TIINGO BEHAVIOR: TIINGO WILL RETURN ANY AND ALL PRICES AVAILABLE WITHIN A GIVEN DATE RANGE.  IT WON'T RETURN ANY ENTRIES FOR DATES WHERE THE PRICES ARE NOT AVAILABLE.  IF THERE ARE NO PRICES AVAILABLE WITHIN A DATE RANGE, IT WILL RETURN A BLANK.

Version Notes:
1.1: Simplify code.

"""


# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import datetime as dt
#   THIRD PARTY IMPORTS
import requests as rq
import pandas as pd
#   LOCAL APPLICATION IMPORTS


def stockpriceretrieval(stock, start_date, end_date):
    # SET PRICE URL
    stockpriceurl = f'https://api.tiingo.com/tiingo/daily/{stock}/prices?token=ea0e9806c6cf888517ed0a6e99527f6f5b0467ad&startDate={start_date}&endDate={end_date}&resampleFreq=daily&format=json&columns=date,adjClose'
    # RETRIEVE PRICES
    prices = rq.get(stockpriceurl)
    # PARSE PRICES
    prices = prices.json()
    # CONVERT TO DATAFRAME
    prices = pd.DataFrame(prices)
    # CHANGE ORDER OF COLUMNS
    prices = prices[["date", "adjClose"]]
    prices = prices.rename(columns={"adjClose": stock})
    # RE-NUMBER INDEX
    prices.reset_index(drop=True, inplace=True)
    return prices


# retrieve marketcap data for a stock
def getindexofavailablefundamentals(savedir):
    # SET marketcap URL
    endpointsindex = 'https://api.tiingo.com/tiingo/fundamentals/definitions?token=ea0e9806c6cf888517ed0a6e99527f6f5b0467ad'
    endpointslist = rq.get(endpointsindex).json()
    endpointsindexdf = pd.DataFrame(data=endpointslist)
    # save?
    timestamp = str(dt.datetime.now())
    timestamp = timestamp.replace(".", "_")
    timestamp = timestamp.replace(":", "")
    timestamp = timestamp.replace(" ", "_")
    filename = f'availablefundamentalsdirectory_{timestamp}'
    endpointsindexdf.to_csv(index=False, path_or_buf=savedir / f"{filename}.csv")


# get ticker list of all tickers with fundamentals available
def gettickerswithavailablefundamentals(savedir):
    # SET marketcap URL
    endpointsindex = 'https://api.tiingo.com/tiingo/fundamentals/meta?token=ea0e9806c6cf888517ed0a6e99527f6f5b0467ad'
    endpointslist = rq.get(endpointsindex).json()
    endpointsindexdf = pd.DataFrame(data=endpointslist)
    # save?
    timestamp = str(dt.datetime.now())
    timestamp = timestamp.replace(".", "_")
    timestamp = timestamp.replace(":", "")
    timestamp = timestamp.replace(" ", "_")
    filename = f'tickerswithfundamentalsdirectory_{timestamp}'
    endpointsindexdf.to_csv(index=False, path_or_buf=savedir / f"{filename}.csv")


# retrieve marketcap data for a stock
def marketcapretrieval(stock, start_date, end_date):
    # SET marketcap URL
    dailymarketcapurl = f'https://api.tiingo.com/tiingo/fundamentals/{stock}/daily?token=ea0e9806c6cf888517ed0a6e99527f6f5b0467ad&startDate={start_date}&endDate={end_date}'
    # RETRIEVE PRICES
    marketcapdata = rq.get(dailymarketcapurl)
    # PARSE PRICES
    marketcapdata = marketcapdata.json()
    # CONVERT TO DATAFRAME
    marketcapdf = pd.DataFrame(data=marketcapdata)
    # CHANGE ORDER OF COLUMNS
    marketcapdf = marketcapdf[["date", "marketCap"]]
    marketcapdf = marketcapdf.rename(columns={"marketCap": f'marketcap_{stock}'})
    # RE-NUMBER INDEX
    marketcapdf.reset_index(drop=True, inplace=True)
    return marketcapdf


# filter list containing dicts
def filterlistofdicts(statementdata, statementtype, datacode):
    if statementtype in statementdata.keys():
        substatementlistdata = statementdata[statementtype]
        for item in substatementlistdata:
            if item['dataCode'] == datacode:
                return item['value']
    else:
        return None


# retrieve fundamental data for a stock
def fundamentalretrieval(stock, start_date, end_date, includeannual, asreporteddating):
    # SET fundamental URL
    fundamentalurl = f'https://api.tiingo.com/tiingo/fundamentals/{stock}/statements?token=ea0e9806c6cf888517ed0a6e99527f6f5b0467ad&startDate={start_date}&endDate={end_date}&asReported={asreporteddating}'
    # RETRIEVE fundamental
    fundydata = rq.get(fundamentalurl)
    # PARSE fundamental
    fundydata = fundydata.json()
    # CONVERT TO DATAFRAME
    fundydatadf = pd.DataFrame(data=fundydata)
    # REFORMAT AND FILTER DF
    fundydatadf[f'revenue_{stock}'] = fundydatadf['statementData'].apply(lambda x: filterlistofdicts(x, 'incomeStatement', 'revenue'))
    fundydatadf[f'freecashflow_{stock}'] = fundydatadf['statementData'].apply(lambda x: filterlistofdicts(x, 'cashFlow', 'freeCashFlow'))
    # exclude annual statements unless all that's available is yearly
    if includeannual == 'no':
        testdf = fundydatadf[fundydatadf['quarter'] != 0].copy()
        if len(testdf) != 0:
            fundydatadf = testdf
    # CHANGE ORDER OF COLUMNS
    fundydatadf = fundydatadf[["date", f'revenue_{stock}', f'freecashflow_{stock}']].copy()
    # RESORT
    fundydatadf.sort_values(ascending=True, by=['date'], inplace=True)
    # DROP ROWS IF IT CONTAINS NANs
    fundydatadf.dropna(axis=0, how='any', inplace=True)
    # RE-NUMBER INDEX
    fundydatadf.reset_index(drop=True, inplace=True)
    return fundydatadf
