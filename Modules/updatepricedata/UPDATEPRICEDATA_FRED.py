"""
Title: Market Retriever Module - FRED
Date Started: May 5, 2020
Version: 1.00
Version Date: May 5, 2020
Legal:  All rights reserved.  This code may not be used, distributed, or copied
without the express written consent of David Hyongsik Choi.
Purpose: The purpose of the Market Retriever Module is to retrieve market
prices from a single day and prices within a given date range.
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
#   THIRD PARTY IMPORTS
import pandas as pd
#   LOCAL APPLICATION IMPORTS


def indexpriceretrieval(stock, start_date, end_date):
    # FORMAT TICKER FOR FRED TICKER SYNTAX
    if stock == '^DJI':
        ticker = 'DJIA'
    if stock == '^INX':
        ticker = 'SP500'
    if stock == '^IXIC':
        ticker = 'NASDAQCOM'

    indexurl = f'https://fred.stlouisfed.org/graph/fredgraph.csv?&id={ticker}&cosd={start_date}&coed={end_date}'
    prices = pd.read_csv(indexurl)
    # RENAME HEADERS
    prices.rename(columns={"DATE": 'date', ticker: stock}, inplace=True)
    # DELETE EMPTY ROWS
    prices.drop(prices[prices[stock] == '.'].index, inplace=True)
    # CONVERT PRICES FROM STRINGS TO FLOATS
    prices[stock] = prices[stock].astype(float)

    # RE-NUMBER INDEX
    prices.reset_index(drop=True, inplace=True)

    return prices
