"""
Title: Get Metric Value DF
Date Started: Nov 30, 2021
Version: 1.0
Version Start Date: Nov 30, 2021
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose: Returns a dataframe of given stocks and their metric values over a given date range

Each metric score you need to know
1. name of metric
2. metric function
3. prep all necessary inputs: what form the data needs to be in
a. source of data to be crunched and prepped

"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
from functools import partial
import multiprocessing as mp
#   THIRD PARTY IMPORTS
import pandas as pd
#   LOCAL APPLICATION IMPORTS
from Modules.price_calib import add_calibratedprices
from Modules.price_history_slicing import pricedf_daterange
from Modules.metriclibrary.STRATTEST_FUNCBASE_MMBM import unifatshell_single, allpctdrops_single


# get smoothness for single stock
def getmetricvals_single(beg_date, end_date, group, stock):
    # get stock prices
    prices = pricedf_daterange(stock, beg_date, end_date)
    # get calibrated prices
    prices = add_calibratedprices(prices, ['baremaxraw'], stock)
    # calculate metricval
    rbmaxfatscore = unifatshell_single(prices, stock, 'baremaxraw', 'avg')
    maxdd = allpctdrops_single(prices, 'baremaxraw', stock, 'min')
    return {
        'stock': stock,
        f'{group}_rawbmaxfatscore': rbmaxfatscore,
        f'{group}_maxdd': maxdd
    }


# RETURN DF OF STOCK AND METRICVALS
def getallmetricvalsdf(beg_date, end_date, group, stockpool):
    # FOR EACH STOCK IN POOL, GET METRIC VALUE
    pool = mp.Pool(mp.cpu_count())
    fn = partial(getmetricvals_single, beg_date, end_date, group)
    resultlist = pool.map_async(fn, stockpool).get()
    pool.close()
    # assemble dataframe of results
    resultdf = pd.DataFrame(data=resultlist)
    return resultdf
