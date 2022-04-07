"""
Title: DIP DATE VISUALIZER
Date Started: Dec 11, 2020
Version: 1.00
Version Start: Dec 11, 2020
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose:  Shows you graph of requested date range and stock and gives you dates of the highest and lowest points of the largest crash in the range.
"""
# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
#   THIRD PARTY IMPORTS
#   LOCAL APPLICATION IMPORTS
from Modules.price_history_slicing import pricedf_daterange
from Modules.timeperiodbot import dipdates, peakdiprecoverydates
from Modules.dates import num_days_string
from Modules.numbers import formalnumber, formalnumber_integer


def dipdatevisualizer_old(stock, beg_date, end_date):

    prices = pricedf_daterange(stock, beg_date, end_date)
    '''
    # graph
    # get trueline
    allprices = prices[stock].tolist()
    oldbareminrawpricelist = oldbaremin_cruncher(allprices)
    prices['lowestprice'] = np.array(oldbareminrawpricelist)
    baremaxrawpricelist = baremax_cruncher(allprices)
    prices['baremaxraw'] = np.array(baremaxrawpricelist)
    prices['pctdrops'] = (prices['lowestprice'] - prices[stock]) / prices[stock]
    # graph
    graphtopbottom(prices, prices, 'date', 'date', [stock, 'lowestprice'], ['pctdrops'], [2, 1], True, True)
    '''
    peakdate, valleydate = dipdates(prices, stock)
    peakprice = prices[prices['date'] == peakdate][stock].item()
    valleyprice = prices[prices['date'] == valleydate][stock].item()
    return f"Between {beg_date} and {end_date}, {stock}'s largest drop in price spanned a total of {formalnumber_integer(num_days_string(peakdate, valleydate))} days ({peakdate} to {valleydate}), during which time it dropped {formalnumber(((valleyprice-peakprice)/peakprice)*100)} %, falling ${formalnumber(valleyprice-peakprice)} per share, from ${formalnumber(peakprice)} down to ${formalnumber(valleyprice)}."


def getpeakvalleyprices(prices, stock, peakdate, valleydate):
    peakprice = prices[prices['date'] == peakdate][stock].item()
    valleyprice = prices[prices['date'] == valleydate][stock].item()
    return peakprice, valleyprice


def dipdate_report(stock, beg_date, end_date, peakdate, valleydate, peakprice, valleyprice, recoverydate):
    dipdatereport = f"Between {beg_date} and {end_date}, {stock}'s largest drop in price spanned a total of {formalnumber_integer(num_days_string(peakdate, valleydate))} days ({peakdate} to {valleydate}), during which time it dropped {formalnumber(((valleyprice-peakprice)/peakprice)*100)} %, falling ${formalnumber(valleyprice-peakprice)} per share, from ${formalnumber(peakprice)} down to ${formalnumber(valleyprice)}."
    if recoverydate is None:
        recoveryreport = f"  {stock} price never recovered its ${formalnumber(peakprice)} per share peak price before the end of the date range provided ({end_date}).  However, it is possible that it might have recovered beyond the range provided."
    else:
        recoveryreport = f"  {stock} recovered its peak price of ${formalnumber(peakprice)} per share within the date range. It took {formalnumber_integer(num_days_string(valleydate, recoverydate))} days to recover its peak price (from {valleydate} (the date of its lowest price) to {recoverydate})."
    return dipdatereport + recoveryreport


def get_dipregion(prices, stock, valleydate, peakdate):
    prices['dipregion'] = prices[stock].where((prices['date'] <= valleydate) & (prices['date'] >= peakdate))
    return prices


def get_recoveryregion(prices, stock, valleydate, recoverydate):
    prices['recoveryregion'] = prices[stock].where((prices['date'] <= recoverydate) & (prices['date'] >= valleydate))
    return prices


def dipdatevisualizer_dash(stock, beg_date, end_date):
    prices = pricedf_daterange(stock, beg_date, end_date)
    peakdate, valleydate = dipdates(prices, stock)
    peakprice, valleyprice = getpeakvalleyprices(prices, stock, peakdate, valleydate)
    recoverydate = peakdiprecoverydates(prices, valleydate, peakprice, stock)
    prices = get_dipregion(prices, stock, valleydate, peakdate)
    if recoverydate is not None:
        prices = get_recoveryregion(prices, stock, valleydate, recoverydate)
    dipreport = dipdate_report(stock, beg_date, end_date, peakdate, valleydate, peakprice, valleyprice, recoverydate)
    return dipreport, prices
