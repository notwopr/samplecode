"""
Title: Price Matrix
Date Started: Nov 9, 2019
Version: 2.1
Vers. Start: Jan 31, 2022
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose: Create one dataframe for all stock price histories available.

Versions:
2.0: Remove need for masterdf.  Remove fillbackwards.
2.1: remove fillforward. Simplify get tickerlist code. use readpkl instead of written out code.
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import multiprocessing as mp
#   THIRD PARTY IMPORTS
import modin.pandas as mpd
import pandas as pd
#   LOCAL APPLICATION IMPORTS
from file_functions import savetopkl, readpkl, readpkl_fullpath


# stockdf prepper
def stockdfprep(filepath):
    # open file
    df = readpkl_fullpath(filepath)
    # set index to datecol
    df.set_index('date', inplace=True)
    return df


# CREATE MATRIX OF ALL PRICE HISTORIES OF ALL STOCKS
def allprice_matrix_modin(tlname, tickerlistfolder, pricedatafolder, destfolder, chunksize):

    # make list of all stockdfs to combine
    pool = mp.Pool(mp.cpu_count())
    resultlist = pool.map_async(stockdfprep, pricedatafolder.iterdir(), chunksize).get()
    pool.close()
    pool.join()

    # join all stock dfs together
    mdf = mpd.concat(resultlist, ignore_index=False, axis=1)

    # sort date col
    mdf.sort_values(by='date', inplace=True)

    # add missing dates
    mdf = mdf.reindex(pd.date_range(mdf.index[0], mdf.index[-1]))

    # resort columns in alphabetical order
    mdf = mdf.reindex(sorted(mdf.columns), axis=1)

    # add index col and reinstate date col
    mdf.reset_index(inplace=True)
    mdf.rename(columns={'index': 'date'}, inplace=True)

    # GET TICKERLIST
    if tlname == 'bench' or tlname == 'faang':
        bmdict = {'bench': ["DJI", "INX", "IXIC"], 'faang': ["NFLX", "AMZN", "AAPL", "FB", "GOOGL"]}
        tickerlist = bmdict[tlname]
        suffix = tlname
    else:
        tickerlist = readpkl(tlname, tickerlistfolder)['symbol'].tolist()
        suffix = tlname[11:]

    # SAVE TO FILE
    if suffix == 'faang' or suffix == 'common':
        savetopkl(f"allpricematrix_{suffix}", destfolder, mdf[['date'] + tickerlist])
    else:
        savetopkl(f"allpricematrix_{suffix}", destfolder, mdf)


# CREATE MATRIX OF ALL PRICE HISTORIES OF ALL STOCKS
# WARNING THE PRICE MATRIX DF AS IS DOES NOT HAVE PRICES FILLED FORWARD
def allprice_matrix(tlname, tickerlistfolder, pricedatafolder, destfolder, chunksize):

    # make list of all stockdfs to combine
    pool = mp.Pool(mp.cpu_count())
    resultlist = pool.map_async(stockdfprep, pricedatafolder.iterdir(), chunksize).get()
    pool.close()
    pool.join()

    # join all stock dfs together
    mdf = pd.concat(resultlist, ignore_index=False, axis=1)

    # sort date col
    mdf.sort_values(by='date', inplace=True)

    # add missing dates
    mdf = mdf.reindex(pd.date_range(mdf.index[0], mdf.index[-1]))

    # resort columns in alphabetical order
    mdf = mdf.reindex(sorted(mdf.columns), axis=1)

    # add index col and reinstate date col
    mdf.reset_index(inplace=True)
    mdf.rename(columns={'index': 'date'}, inplace=True)

    # GET TICKERLIST
    if tlname == 'bench' or tlname == 'faang':
        bmdict = {'bench': ["DJI", "INX", "IXIC"], 'faang': ["NFLX", "AMZN", "AAPL", "FB", "GOOGL"]}
        tickerlist = bmdict[tlname]
        suffix = tlname
    else:
        tickerlist = readpkl(tlname, tickerlistfolder)['symbol'].tolist()
        suffix = tlname[11:]

    # SAVE TO FILE
    if suffix == 'faang' or suffix == 'common':
        savetopkl(f"allpricematrix_{suffix}", destfolder, mdf[['date'] + tickerlist])
    else:
        savetopkl(f"allpricematrix_{suffix}", destfolder, mdf)
