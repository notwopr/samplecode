"""
Title: Update Data Bot
Date Started: June 26, 2019
Version: 4.4
Version Date: Feb 28, 2021
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose: List of functions needed to run to update data.

Versions:
4.2: Revise price matrix functions. 2.0 version of price matrix script.
4.3: Fixed capitalization of filename.
4.4: Replaced multiprocessor functions with generic multiprocessorshell function
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import os
#   THIRD PARTY IMPORTS
from playsound import playsound
#   LOCAL APPLICATION IMPORTS
from file_functions import delete_create_folder
from UPDATEPRICEDATA_BASE import store_allprices, store_allmarketcap, store_allfundies
from UPDATEPRICEDATA_BASE_TICKER import storealltickers
from UPDATEPRICEDATA_BASE_DATERANGES import create_daterangedb
from UPDATEPRICEDATA_BASE_PRICEMATRIX import allprice_matrix
from UPDATEPRICEDATA_BASE_FULLINFOTICKERDATABASE import create_fullinfotickerdatabase
from file_hierarchy import STOCKPRICES, TICKERS, DATES, DATE_DUMP, DATE_RESULTS, FULL_INFO_DB, INDEXPRICES, MARKETCAP, MARKETCAPDATE_DUMP, MARKETCAPDATE_RESULTS, FUNDIES, FUNDIESDATE_DUMP, FUNDIESDATE_RESULTS, tickerlistall_name, tickerlistcommon_name, alltickerfiles, tickerlistall_source, tickerlistcommon_source, PRICES, daterangedb_name, daterangedb_source, daterangedb_name_marketcap, daterangedb_name_fundies, alldatefiles, daterangedb_source_marketcap, daterangedb_source_fundies

chunksize = 5
if __name__ == '__main__':

    '''DELETE ALL EXCEPT INDEXPRICE FOLDER'''
    folder_index = [
        STOCKPRICES,
        TICKERS,
        DATES,
        DATE_DUMP,
        DATE_RESULTS,
        FULL_INFO_DB,
        MARKETCAP,
        MARKETCAPDATE_DUMP,
        MARKETCAPDATE_RESULTS,
        FUNDIES,
        FUNDIESDATE_DUMP,
        FUNDIESDATE_RESULTS
    ]
    for folder in folder_index:
        delete_create_folder(folder)

    '''BENCHMARK DOWNLOAD (INDEPENDENT)'''
    store_allprices(INDEXPRICES, '', "benchmark", chunksize)

    '''TICKERLIST DOWNLOAD'''
    storealltickers(TICKERS, tickerlistall_name, tickerlistcommon_name)

    '''STOCKPRICE DOWNLOAD (DEPENDENT ON TICKERLIST DOWNLOAD)'''
    # WAIT UNTIL TICKERLIST FILES EXIST
    for fileloc in alltickerfiles:
        tlistexist = os.path.isfile(fileloc)
        while tlistexist is False:
            tlistexist = os.path.isfile(fileloc)

    # DOWNLOAD STOCK PRICES
    store_allprices(STOCKPRICES, tickerlistall_source, "", chunksize)

    '''DOWNLOAD MARKETCAPS'''
    store_allmarketcap(MARKETCAP, tickerlistall_source, chunksize)

    '''DOWNLOAD FUNDAMENTALS'''
    store_allfundies(FUNDIES, tickerlistall_source, chunksize)

    '''CREATE DATE DATABASE (DEPENDENT ON STOCK PRICE DOWNLOAD)'''
    create_daterangedb(tickerlistall_source, DATE_RESULTS, daterangedb_name, 'prices', chunksize)
    tlistexist = os.path.isfile(daterangedb_source)
    while tlistexist is False:
        tlistexist = os.path.isfile(daterangedb_source)

    '''CREATE MARKETCAP DATE DATABASE (DEPENDENT ON MARKETCAPS DOWNLOAD)'''
    create_daterangedb(MARKETCAPDATE_DUMP, tickerlistall_source, MARKETCAP, MARKETCAPDATE_RESULTS, daterangedb_name_marketcap, 'marketcap', chunksize)
    tlistexist = os.path.isfile(daterangedb_source_marketcap)
    while tlistexist is False:
        tlistexist = os.path.isfile(daterangedb_source_marketcap)

    '''CREATE FUNDIES DATE DATABASE (DEPENDENT ON FUNDAMENTALS DOWNLOAD)'''
    create_daterangedb(FUNDIESDATE_DUMP, tickerlistall_source, FUNDIES, FUNDIESDATE_RESULTS, daterangedb_name_fundies, 'fundies', chunksize)
    tlistexist = os.path.isfile(daterangedb_source_fundies)
    while tlistexist is False:
        tlistexist = os.path.isfile(daterangedb_source_fundies)

    '''CREATE FULL INFO DATABASE'''
    create_fullinfotickerdatabase(tickerlistcommon_source, tickerlistall_source, daterangedb_source, daterangedb_source_marketcap, daterangedb_source_fundies, FULL_INFO_DB)

    '''CREATE PRICE HISTORY MATRIX (DEPENDENT ON STOCK PRICE DOWNLOAD)'''
    #allprice_matrix(tickerlistall_source, STOCKPRICES, PRICES)
    allprice_matrix(tickerlistcommon_source, STOCKPRICES, PRICES)
    #allprice_matrix('faang', STOCKPRICES, PRICES)
    allprice_matrix('bench', INDEXPRICES, PRICES)

    playsound('C:\Windows\Media\Ring03.wav')
