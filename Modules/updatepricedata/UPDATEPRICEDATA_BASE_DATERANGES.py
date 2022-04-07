"""
Title: Update Price Data Base_Dates
Date Started: Feb 27, 2022
Version: 1.3
Version Start Date: Mar 3, 2021
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied
    without the express written consent of David Hyongsik Choi.
Purpose: The purpose of the Date Range Bot is to retrieve the earliest and latest available trade dates of a given stock.  Another function is to create a database of those dates.

Version Notes:
1.1: Update and clean up code.
1.2: Make Universal for prices, marketcap, and fundies data.
1.3: Add benchmark indices to dataframe and update code.
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import pickle as pkl
#   THIRD PARTY IMPORTS
import pandas as pd
#   LOCAL APPLICATION IMPORTS
from file_functions import savetopkl, readpkl
from Modules.multiprocessing import multiprocessorshell_mapasync_getresults
from file_hierarchy import STOCKPRICES, INDEXPRICES


# STORE A SINGLE STOCK'S DATE RANGE TO FILE
def get_daterange(datatype, stock):
    if datatype == 'prices':
        if stock in ["^DJI", "^INX", "^IXIC"]:
            pklfn = f'{stock[1:]}_prices'
            datasourcefolder = INDEXPRICES
        else:
            pklfn = f'{stock}_prices'
            datasourcefolder = STOCKPRICES
    elif datatype == 'marketcap':
        pklfn = f'{stock}_marketcaps'
    elif datatype == 'fundies':
        pklfn = f'{stock}_fundies'
    pkldata = readpkl(pklfn, datasourcefolder)
    # SAVE NAME AND FIRST DATE TO FILE
    if len(pkldata) != 0:
        summary = {
            'stock': stock,
            'first_date': str(pkldata['date'].iloc[0]),
            'last_date': str(pkldata['date'].iloc[-1])
            }
    else:
        summary = {
            'stock': stock,
            'first_date': None,
            'last_date': None
            }
    return summary


# CREATES DATABASE OF THE EARLIEST TRADE DATES OF ALL US NASDAQ AND NYSE STOCKS
def create_daterangedb(tickerlistsource, destfolder, daterangedb_name, datatype, chunksize):
    # OPEN TICKER LIST FILE AND STORE TICKER LIST TO OBJECT
    with open(tickerlistsource, "rb") as targetfile:
        tickerlistdf = pkl.load(targetfile)
    tickerlist = tickerlistdf['symbol'].tolist() + ["^DJI", "^INX", "^IXIC"]
    table_results = multiprocessorshell_mapasync_getresults(get_daterange, tickerlist, 'no', (datatype,), chunksize)
    daterangedf = pd.DataFrame(data=table_results)
    # CHECK ACCURACY
    if len(table_results) != len(tickerlist):
        print("The number of date ranges listed does not match the number of available tickers.  Program exiting...no date range database has been created.  Please fix.")
        exit()
    # ARCHIVE FILE
    savetopkl(daterangedb_name, destfolder, daterangedf)
    daterangedf.to_csv(index=False, path_or_buf=destfolder / f'{daterangedb_name}.csv')
    return daterangedf
