"""
Title: All Price Bot
Date Started: June 7, 2019
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose: The purpose of the All Price Bot is to retrieve the entire price history of a stock.  It will return all days including non-trading days (filled in with previous last closing price).  Allows for the option to fill in the unavailable rows with Nan or the last available price.
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
#   THIRD PARTY IMPORTS
import numpy as np
#   LOCAL APPLICATION IMPORTS
from Modules.price_calib_cruncher import oldbaremin_cruncher, baremax_cruncher


# ADDS CALIBRATED PRICE COLS TO EXISTING RAWPRICEDF
def add_calibratedprices(origpricedf, allcalibrations, stock):
    allprices = origpricedf[stock].tolist()
    if 'trueline' in allcalibrations:
        oldbareminrawpricelist = oldbaremin_cruncher(allprices)
        origpricedf['oldbareminraw'] = np.array(oldbareminrawpricelist)
        baremaxrawpricelist = baremax_cruncher(allprices)
        origpricedf['baremaxraw'] = np.array(baremaxrawpricelist)
        origpricedf['trueline'] = ((origpricedf['baremaxraw'] - origpricedf['oldbareminraw']) / 2) + origpricedf['oldbareminraw']
    else:
        if 'oldbareminraw' in allcalibrations:
            oldbareminrawpricelist = oldbaremin_cruncher(allprices)
            origpricedf['oldbareminraw'] = np.array(oldbareminrawpricelist)
        if 'baremaxraw' in allcalibrations:
            baremaxrawpricelist = baremax_cruncher(allprices)
            origpricedf['baremaxraw'] = np.array(baremaxrawpricelist)
    if 'straight' in allcalibrations:
        age = len(origpricedf) - 1
        price_start = origpricedf.iloc[0][stock]
        price_end = origpricedf.iloc[-1][stock]
        slope = (price_end - price_start) / age
        origpricedf['straight'] = [(slope * x) + price_start for x in range(age + 1)]
    return origpricedf


# ADDS CALIBRATED PRICE COLS TO EXISTING PRICEDF WHEN MULTIPLE SOURCES IN SAME DF
def add_calibratedprices_universal(origpricedf, allcalibrations, stock):
    allprices = origpricedf[stock].tolist()
    if 'trueline' in allcalibrations:
        oldbareminrawpricelist = oldbaremin_cruncher(allprices)
        origpricedf[f'{stock}_oldbareminraw'] = np.array(oldbareminrawpricelist)
        baremaxrawpricelist = baremax_cruncher(allprices)
        origpricedf[f'{stock}_baremaxraw'] = np.array(baremaxrawpricelist)
        origpricedf[f'{stock}_trueline'] = ((origpricedf[f'{stock}_baremaxraw'] - origpricedf[f'{stock}_oldbareminraw']) / 2) + origpricedf[f'{stock}_oldbareminraw']
    else:
        if 'oldbareminraw' in allcalibrations:
            oldbareminrawpricelist = oldbaremin_cruncher(allprices)
            origpricedf[f'{stock}_oldbareminraw'] = np.array(oldbareminrawpricelist)
        if 'baremaxraw' in allcalibrations:
            baremaxrawpricelist = baremax_cruncher(allprices)
            origpricedf[f'{stock}_baremaxraw'] = np.array(baremaxrawpricelist)
    if 'straight' in allcalibrations:
        age = len(origpricedf) - 1
        price_start = origpricedf.iloc[0][stock]
        price_end = origpricedf.iloc[-1][stock]
        slope = (price_end - price_start) / age
        origpricedf[f'{stock}_straight'] = [(slope * x) + price_start for x in range(age + 1)]
    return origpricedf


# CONVERTS PRICE ARRAY OR SERIES TO ANOTHER
# WARNING make sure no Nans exist between prices and that all nans exist at the beginning (FYI: 'sum(np.isnan(origarr))' is to offset beginning Nans)
def convertpricearr(origarr, convert_type):
    if convert_type == 'oldbareminraw':
        newarr = oldbaremin_cruncher(origarr)
    elif convert_type == 'baremaxraw':
        newarr = baremax_cruncher(origarr)
    elif convert_type == 'trueline':
        oldbareminrawpricearr = np.array(oldbaremin_cruncher(origarr))
        baremaxrawpricearr = np.array(baremax_cruncher(origarr))
        newarr = ((baremaxrawpricearr - oldbareminrawpricearr) / 2) + oldbareminrawpricearr
    elif convert_type == 'straight':
        origarr = origarr.array
        age = len(origarr)-sum(np.isnan(origarr)) - 1
        price_start = origarr[sum(np.isnan(origarr))]
        price_end = origarr[-1]
        slope = (price_end - price_start) / age
        newarr = np.concatenate((origarr[:sum(np.isnan(origarr))], [(slope * x) + price_start for x in range(age + 1)]))
    elif convert_type == 'rawprice':
        newarr = origarr
    elif convert_type == 'norm':  # normalized to 0
        newarr = (origarr / origarr[sum(np.isnan(origarr))]) - 1
    elif convert_type == 'norm1':  # normalized to 1
        newarr = (origarr / origarr[sum(np.isnan(origarr))])
    return newarr


# ADD ALL PRICE MODES TO DF WITHOUT DELETING ORIGINALS FOR ALL STOCKS IN SAME DF AT ONCE
# WARNING this assumes the rawprice columns are named as they are in 'portfolio'
def add_calibratedprices_portfolio(df, allcalibrations, portfolio):
    if 'trueline' in allcalibrations:
        df[[f'{s}_trueline' for s in portfolio]] = df[portfolio].apply(lambda x: convertpricearr(x, 'trueline'))
    if 'oldbareminraw' in allcalibrations:
        df[[f'{s}_oldbareminraw' for s in portfolio]] = df[portfolio].apply(lambda x: convertpricearr(x, 'oldbareminraw'))
    if 'baremaxraw' in allcalibrations:
        df[[f'{s}_baremaxraw' for s in portfolio]] = df[portfolio].apply(lambda x: convertpricearr(x, 'baremaxraw'))
    if 'straight' in allcalibrations:
        df[[f'{s}_straight' for s in portfolio]] = df[portfolio].apply(lambda x: convertpricearr(x, 'straight'))
    if 'norm' in allcalibrations:
        df[[f'{s}_norm' for s in portfolio]] = df[portfolio].apply(lambda x: convertpricearr(x, 'norm'))
    if 'norm1' in allcalibrations:
        df[[f'{s}_norm1' for s in portfolio]] = df[portfolio].apply(lambda x: convertpricearr(x, 'norm1'))
    if 'portcurve' in allcalibrations:
        df['portcurve'] = df[portfolio].apply(lambda x: convertpricearr(x, 'norm')).mean(axis=1)
    return df
