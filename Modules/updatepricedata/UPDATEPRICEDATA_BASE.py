"""
Title: Update Price Data Base - Prices
Date Started: June 7, 2019
Version: 1.2
Version Start Date: May 5, 2020
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose: The purpose of the All Price Bot is to retrieve the entire price history of a stock.  It will return all days including non-trading days (filled in with previous last closing price).  Allows for the option to fill in the unavailable rows with Nan or the last available price.
Version Notes:
1.1: Cleaned up code.  Added FRED Nasdaq API pull.  Removed startdate and enddate specification.
1.2: Fix capitalization of filename.
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import datetime as dt
import dateutil.parser as dup
import pickle as pkl
#   THIRD PARTY IMPORTS
import pandas as pd
#   LOCAL APPLICATION IMPORTS
from UPDATEPRICEDATA_UPDATEINDEXPRICEFILE import indexpriceupdater
from UPDATEPRICEDATA_TIINGO import stockpriceretrieval, marketcapretrieval, fundamentalretrieval
from genericfunctionbot import multiprocessorshell


# STORE ENTIRE PRICE HISTORY OF A SINGLE GIVEN STOCK TO PICKLE
def download_prices(targetfolder, start, end, symbol):
    if symbol in ["^DJI", "^INX", "^IXIC"]:
        indexpriceupdater(symbol, targetfolder)
    else:
        try:
            prices = stockpriceretrieval(symbol, start, end)
            prices['date'] = prices['date'].apply(dup.parse)
            prices['date'] = prices['date'].apply(dt.datetime.date)
        except (ValueError, KeyError, TypeError):
            dates = pd.date_range(end, end)
            prices = pd.DataFrame(dates)
            prices = prices.rename(columns={0: "date"})
            prices[symbol] = float(0)
            prices["date"] = pd.to_datetime(prices["date"])
            prices["date"] = prices["date"].apply(dt.datetime.date)
        # SAVE TO FILE
        with open(targetfolder / f"{symbol}_prices.pkl", "wb") as targetfile:
            pkl.dump(prices, targetfile, protocol=4)


# DOWNLOAD ALL STOCK PRICE HISTORIES TO FILES
def store_allprices(destfolder, tickerfile, option, chunksize):
    # BENCHMARK OR NOT?
    if option == "benchmark":
        symbols = ["^DJI", "^IXIC", "^INX"]
    else:
        with open(tickerfile, "rb") as targetfile:
            tickerlistdf = pkl.load(targetfile)
            symbols = tickerlistdf['symbol'].tolist()
    # SET DATE RANGE
    start = "1962-01-01"
    end = str(dt.date.today())
    # DOWNLOAD
    #for symbol in symbols:
        #download_prices(destfolder, start, end, symbol)
    multiprocessorshell(destfolder, download_prices, symbols, 'no', (destfolder, start, end), chunksize)


# STORE ENTIRE MARKETCAP HISTORY OF A SINGLE GIVEN STOCK TO PICKLE
def download_marketcap(targetfolder, start, end, symbol):
    try:
        marketcapdf = marketcapretrieval(symbol, start, end)
        marketcapdf['date'] = marketcapdf['date'].apply(dup.parse)
        marketcapdf['date'] = marketcapdf['date'].apply(dt.datetime.date)
    except (ValueError, KeyError, TypeError):
        dates = pd.date_range(end, end)
        marketcapdf = pd.DataFrame(dates)
        marketcapdf = marketcapdf.rename(columns={0: "date"})
        marketcapdf[f'marketcap_{symbol}'] = float(0)
        marketcapdf["date"] = pd.to_datetime(marketcapdf["date"])
        marketcapdf["date"] = marketcapdf["date"].apply(dt.datetime.date)
    # SAVE TO FILE
    with open(targetfolder / f"{symbol}_marketcaps.pkl", "wb") as targetfile:
        pkl.dump(marketcapdf, targetfile, protocol=4)


# DOWNLOAD ALL STOCK MARKETCAP HISTORIES TO FILES
def store_allmarketcap(destfolder, tickerfile, chunksize):
    with open(tickerfile, "rb") as targetfile:
        tickerlistdf = pkl.load(targetfile)
        symbols = tickerlistdf['symbol'].tolist()
    # SET DATE RANGE
    start = "1962-01-01"
    end = str(dt.date.today())
    # DOWNLOAD
    multiprocessorshell(destfolder, download_marketcap, symbols, 'no', (destfolder, start, end), chunksize)


# STORE ENTIRE FUNDAMENTALS HISTORY OF A SINGLE GIVEN STOCK TO PICKLE
def download_fundamentals(targetfolder, start, end, symbol):
    try:
        fundydf = fundamentalretrieval(symbol, start, end, 'no', 'false')
        fundydf['date'] = fundydf['date'].apply(dup.parse)
        fundydf['date'] = fundydf['date'].apply(dt.datetime.date)
    except Exception:
        dates = pd.date_range(end, end)
        fundydf = pd.DataFrame(dates)
        fundydf = fundydf.rename(columns={0: "date"})
        fundydf[[f'revenue_{symbol}', f'freecashflow_{symbol}']] = float(0)
        fundydf["date"] = pd.to_datetime(fundydf["date"])
        fundydf["date"] = fundydf["date"].apply(dt.datetime.date)
    # SAVE TO FILE
    with open(targetfolder / f"{symbol}_fundies.pkl", "wb") as targetfile:
        pkl.dump(fundydf, targetfile, protocol=4)


# DOWNLOAD ALL STOCK FUNDAMENTALS HISTORIES TO FILES
def store_allfundies(destfolder, tickerfile, chunksize):
    with open(tickerfile, "rb") as targetfile:
        tickerlistdf = pkl.load(targetfile)
        symbols = tickerlistdf['symbol'].tolist()
    # SET DATE RANGE
    start = "1962-01-01"
    end = str(dt.date.today())
    # DOWNLOAD
    multiprocessorshell(destfolder, download_fundamentals, symbols, 'no', (destfolder, start, end), chunksize)
