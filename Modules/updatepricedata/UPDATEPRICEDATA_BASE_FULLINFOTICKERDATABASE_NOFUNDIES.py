"""
Title: Update Price Database - Create Full Info Stock Database NO FUNDIES
Date Started: Apr 14, 2021
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied
    without the express written consent of David Hyongsik Choi.
Purpose: Create database that contains ticker, fullname, start and end dates, and age, and whether stock is common or not.
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import pickle as pkl
import datetime as dt
#   THIRD PARTY IMPORTS
import pandas as pd
#   LOCAL APPLICATION IMPORTS
from filelocations import savetopkl


# CREATES DATABASE DATE RANGE, AGES, SYMBOLS, STOCK TYPE OF ALL STOCKS IN NASDAQ AND NYSE
def create_fullinfotickerdatabase(tickerlistcommon_source, tickerlistall_source, daterangedb_source, destfolder):

    # DATAFRAME OF ALL TICKERS
    with open(tickerlistall_source, "rb") as targetfile:
        allticker_fullnames = pkl.load(targetfile)

    # CREATE STOCK TYPE COLUMN
    with open(tickerlistcommon_source, "rb") as targetfile:
        unpickled_raw = pkl.load(targetfile)
    commontickers = unpickled_raw['symbol'].tolist()
    allticker_fullnames['STOCK_TYPE'] = allticker_fullnames['symbol'].apply(lambda x: 'common' if x in commontickers else 'all')
    # PULL DATE DATABASE
    with open(daterangedb_source, "rb") as targetfile:
        allticker_dateranges = pkl.load(targetfile)
    # MODIFY COLUMN NAMES IF NECESSARY
    firstdatecol = 'first_date'
    lastdatecol = 'last_date'
    # JOIN DATERANGE DB TO TICKER LIST DB
    allticker_fullnames = allticker_fullnames.join(allticker_dateranges.set_index('stock'), how="left", on="symbol")
    # MAKE MASTER DATA FRAME DATE COLUMN DATETIME OBJECT
    allticker_fullnames[lastdatecol] = pd.to_datetime(allticker_fullnames[lastdatecol])
    allticker_fullnames[lastdatecol] = allticker_fullnames[lastdatecol].apply(dt.datetime.date)
    allticker_fullnames[firstdatecol] = pd.to_datetime(allticker_fullnames[firstdatecol])
    allticker_fullnames[firstdatecol] = allticker_fullnames[firstdatecol].apply(dt.datetime.date)

    # ADD AGE COLUMN
    allticker_fullnames['AGE'] = allticker_fullnames['last_date'] - allticker_fullnames['first_date']

    # REMOVE 'DAYS' from age column
    allticker_fullnames['AGE'] = allticker_fullnames['AGE'].apply(lambda x: x.days)

    # ARCHIVE FILE
    filename = 'fullinfo_db'
    savetopkl(filename, destfolder, allticker_fullnames)
    allticker_fullnames.to_csv(index=False, path_or_buf=destfolder / f'{filename}.csv')
