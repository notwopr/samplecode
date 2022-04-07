"""
Title: Update Price Data File Locations
Date Started: Dec 7, 2020
Version: 1.0
Version Date: Dec 7, 2020
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose: Set commonly retrieved filelocs in a separate file to avoid loading updatepricedata scripts into cache for functions not related to updating pricedata.
Versions:
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
#   THIRD PARTY IMPORTS
#   LOCAL APPLICATION IMPORTS
from computersettings import computerobject


'''DEFINE FOLDER STRUCTURE'''
PRICEDATAPARENT = computerobject.pricedata
PRICES = PRICEDATAPARENT / "prices"
MARKETCAP = PRICEDATAPARENT / "marketcap"
FUNDIES = PRICEDATAPARENT / "fundies"
TICKERS = PRICEDATAPARENT / "tickers"
DATES = PRICEDATAPARENT / "dates"
FULL_INFO_DB = PRICEDATAPARENT / 'fullinfodb'
STOCKPRICES = PRICES / "stockprices"
INDEXPRICES = PRICES / "indexprices"
DATE_DUMP = DATES / 'dump'
DATE_RESULTS = DATES / 'results'
MARKETCAPDATE_DUMP = DATES / 'marketcapdump'
MARKETCAPDATE_RESULTS = DATES / 'marketcapdateresults'
FUNDIESDATE_DUMP = DATES / 'fundiesdump'
FUNDIESDATE_RESULTS = DATES / 'fundiesresults'


# SET FILENAMES
tickerlistall_name = 'tickerlist_all'
tickerlistcommon_name = 'tickerlist_common'
pricematrix_common_name = 'allpricematrix_common'
pricematrix_bench_name = 'allpricematrix_bench'
daterangedb_name = 'daterangedb_prices'
daterangedb_name_marketcap = 'daterangedb_marketcap'
daterangedb_name_fundies = 'daterangedb_fundies'

# FILE PATHS
tickerlistall_source = TICKERS / f'{tickerlistall_name}.pkl'
tickerlistcommon_source = TICKERS / f'{tickerlistcommon_name}.pkl'
tickerlistall_source_csv = TICKERS / f'{tickerlistall_name}.csv'
tickerlistcommon_source_csv = TICKERS / f'{tickerlistcommon_name}.csv'
pricematrix_common_source = PRICES / f'{pricematrix_common_name}.pkl'
pricematrix_bench_source = PRICES / f'{pricematrix_bench_name}.pkl'
daterangedb_source = DATE_RESULTS / f'{daterangedb_name}.pkl'
daterangedb_source_marketcap = MARKETCAPDATE_RESULTS / f'{daterangedb_name_marketcap}.pkl'
daterangedb_source_fundies = FUNDIESDATE_RESULTS / f'{daterangedb_name_fundies}.pkl'
alltickerfiles = [
    tickerlistall_source,
    tickerlistcommon_source,
    tickerlistall_source_csv,
    tickerlistcommon_source_csv
]
alldatefiles = [
    daterangedb_source,
    daterangedb_source_marketcap,
    daterangedb_source_fundies
]
