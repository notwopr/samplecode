"""
Title: Portfolio Growth Bot
Date Started: Jun 8, 2019
Version: 4.2
Vers Start Date: May 9, 2020
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied
    without the express written consent of David Hyongsik Choi.
Purpose: The purpose of the Portfolio Growth Calculator Module is to calculate
    the growth of a portfolio and its value assuming any changes to the
    portfolio composition are made where all stocks in the new composition are
    equally funded.

Version Notes:
4.1: Revise strings to f strings.  Add correlation cruncher function.
4.2: Save subtrial correlation graphs.
"""

# IMPORT TOOLS
#   Standard library imports
#   Third party imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#   Local application imports
from Modules.stats_outlier_remover import outlier_remover
from Modules.stats_profilers import list_aggregator
from Modules.price_history_slicing import pricedf_daterange


# get growth rate of single stock
def getgrowthrate_single(stock, beg_date, end_date):
    prices = pricedf_daterange(stock, beg_date, end_date)
    prices = removeleadingzeroprices(prices, [stock])
    growthrate = (prices.iat[-1, 1] - prices.iat[0, 1]) / prices.iat[0, 1]
    return growthrate


# RETURNS DATA FRAME OF PRICES GIVEN PORTFOLIO AND TIME PERIOD
def getportfoliopricesdf(pricematrix, portfolio, beg_date, end_date):
    sliced = pricematrix[['date'] + portfolio]
    sliced = sliced[(sliced['date'] >= beg_date) & (sliced['date'] <= end_date)]
    sliced.reset_index(drop=True, inplace=True)
    return sliced


# if beginning of array is zero or set of consecutive zeros, replace it or them with the next nonzero value
def replaceleadzeros(arr):
    # if array not all zeros and if begins with zero(s)
    if arr[0] == 0 and np.any(arr):
        # find next nonzero val
        for elem in arr[1:]:
            if elem != 0:
                # get index of nonzero val
                firstnonzeroindex = np.where(arr == elem)[0][0]
                # replace all preceding elems with elem
                arr[:firstnonzeroindex] = elem
                return arr
    else:
        return arr


# REMOVE LEADING ZEROS FROM EACH COLUMN OF DATAFRAME WITH NEXT NONZERO VALUE IN THAT COLUMN
def removeleadingzeroprices(portfoliodf, modcols):
    # replace leading zero prices with next nonzero prices
    portfoliodf[modcols] = portfoliodf[modcols].apply(lambda x: replaceleadzeros(x))
    return portfoliodf


# returns dataframe of two column dataframe: stock and growthrate for given time period
def get_growthdf(pricematrix, portfolio, beg_date, end_date, sortascending):
    # DATA FRAME OF PRICES GIVEN PORTFOLIO AND TIME PERIOD
    sliced = getportfoliopricesdf(pricematrix, portfolio, beg_date, end_date)
    # REPLACE STARTING ZERO PRICES WITH NEXT NONZERO PRICE
    sliced = removeleadingzeroprices(sliced, portfolio)
    # REMOVE EVERY ROW EXCEPT FIRST AND LAST
    sliced = sliced.iloc[[0, -1], :]
    sliced.reset_index(drop=True, inplace=True)
    # CALCULATE CHANGE
    sliced.iloc[:, 1:] = sliced.iloc[:, 1:].pct_change(fill_method="ffill")
    # REFORMAT IN STOCKNAME-GROWTH COLUMN FORMAT
    sliced.drop(0, inplace=True)
    sliced.drop('date', axis=1, inplace=True)
    sliced = sliced.transpose()
    sliced.reset_index(inplace=True)
    sliced.rename(columns={'index': 'STOCK', 1: f'GROWTH {beg_date} TO {end_date}'}, inplace=True)
    # sort and reset index
    sliced.sort_values(ascending=sortascending, by=[f'GROWTH {beg_date} TO {end_date}'], inplace=True)
    sliced.reset_index(drop=True, inplace=True)
    return sliced


# GET NORMALIZED PRICES GIVEN (1) PORTFOLIO OF PRICES ALREADY TRIMMED BY DATE AND (2) PORTFOLIO CONTENTS
def getnormpricesdf(portfoliodf, portfolio):
    # replace leading zero prices with next nonzero price
    portfoliodf = removeleadingzeroprices(portfoliodf, portfolio)
    # normalize data
    firstp = portfoliodf.loc[0, portfolio]
    portfoliodf[portfolio] = (portfoliodf[portfolio] - firstp) / firstp
    return portfoliodf


def getportfoliopricecol(normpricedf, portfolio, avgmeth):
    # average across cols
    if avgmeth == 'mean':
        normpricedf[f'portfolioprices_{avgmeth}'] = normpricedf[portfolio].mean(axis=1)
    elif avgmeth == 'median':
        normpricedf[f'portfolioprices_{avgmeth}'] = normpricedf[portfolio].median(axis=1)
    elif avgmeth == 'avg':
        normpricedf['portfolioprices_mean'] = normpricedf[portfolio].mean(axis=1)
        normpricedf['portfolioprices_median'] = normpricedf[portfolio].median(axis=1)
        normpricedf[f'portfolioprices_{avgmeth}'] = normpricedf[['portfolioprices_median', 'portfolioprices_mean']].mean(axis=1)
    # slice out just the portpricecol
    normpricedf = normpricedf[['date', f'portfolioprices_{avgmeth}']].copy()
    return normpricedf


# remove every row except first and last
def getbookends(pricedf):
    pricedf = pricedf.iloc[[0, -1], :]
    pricedf.reset_index(drop=True, inplace=True)
    return pricedf


# get portfolio growth rate given normalized pricedf of stocks in portfolio already trimmed to desired date range
def getportgrowthrate(pricedf, portfolio, avgmeth, remove_outliers, verbose, plot, strength):
    # get last row
    lastrow = pricedf[portfolio].iloc[-1].to_numpy()
    # REMOVE OUTLIERS?
    if remove_outliers == 'yes':
        lastrow = outlier_remover(verbose, plot, strength, lastrow)
    # get average of last row
    if avgmeth == 'mean':
        answer = np.mean(lastrow)
    elif avgmeth == 'median':
        answer = np.median(lastrow)
    elif avgmeth == 'avg':
        answer_mean = np.mean(lastrow)
        answer_median = np.median(lastrow)
        answer = np.mean([answer_mean, answer_median])
    return answer


# RETURNS FULL GROWTH DF OF A PORTFOLIO-TIMEPERIOD PAIR GIVEN PRICEHISTORY MATRIX DATAFRAME
def period_growth_portfolio_fulldf(aggregatemethod, remove_outliers, strength, verbose, plot, pricematrix, item):

    # MAP OUT ITERATOR
    beg_date = item[1][0]
    end_date = item[1][1]
    portfolio = item[0]

    # PULL UP PRICE MATRIX AND SLICE OUT STOCKS REQUESTED
    all_cols = ['date'] + portfolio
    sliced = pricematrix[all_cols].copy()

    # SLICE OUT DATE RANGE REQUESTED
    sliced = sliced.loc[(sliced['date'] >= beg_date) & (sliced['date'] <= end_date)]

    # RESET INDEX
    sliced.reset_index(drop=True, inplace=True)

    # REMOVE EVERY ROW EXCEPT FIRST AND LAST
    sliced = sliced.iloc[[0, -1], :]
    sliced.reset_index(drop=True, inplace=True)

    # CORRECT FOR INFINITE SLOPE (IF STARTING PRICE IS ZERO, CHANGE TO 1 DOLLAR)
    sliced.replace(to_replace=float(0), value=1, inplace=True)
    finaldf_transposed = sliced.transpose()
    finaldf_transposed.reset_index(inplace=True)
    finaldf_transposed.rename(columns={'index': 'STOCK', 0: beg_date, 1: end_date}, inplace=True)
    finaldf_transposed = finaldf_transposed.iloc[1:]
    finaldf_transposed.reset_index(drop=True, inplace=True)
    finaldf_transposed['CHANGE'] = finaldf_transposed.pct_change(axis=1)[end_date]
    all_data = finaldf_transposed['CHANGE'].tolist()
    # REMOVE OUTLIERS?
    if remove_outliers == 'yes':
        all_data = outlier_remover(verbose, plot, strength, all_data)
    answer = list_aggregator(aggregatemethod, all_data)
    return sliced, answer


# RETURNS GROWTH OF A PORTFOLIO-TIMEPERIOD PAIR GIVEN PRICEHISTORY MATRIX DATAFRAME
def period_growth_portfolio(aggregatemethod, remove_outliers, strength, verbose, plot, pricematrix, item):

    # MAP OUT ITERATOR
    beg_date = item[1][0]
    end_date = item[1][1]
    portfolio = item[0]

    # PULL UP PRICE MATRIX AND SLICE OUT STOCKS REQUESTED
    all_cols = ['date'] + portfolio
    sliced = pricematrix[all_cols].copy()

    # SLICE OUT DATE RANGE REQUESTED
    sliced = sliced.loc[(sliced['date'] >= beg_date) & (sliced['date'] <= end_date)]

    # RESET INDEX
    sliced.reset_index(drop=True, inplace=True)

    # REMOVE EVERY ROW EXCEPT FIRST AND LAST
    sliced = sliced.iloc[[0, -1], :]
    sliced.reset_index(drop=True, inplace=True)

    # CORRECT FOR INFINITE SLOPE (IF STARTING PRICE IS ZERO, CHANGE TO 1 DOLLAR)
    sliced.replace(to_replace=float(0), value=1, inplace=True)

    # CALCULATE CHANGE
    sliced.iloc[:, 1:] = sliced.iloc[:, 1:].pct_change(fill_method="ffill")
    all_data = sliced.iloc[1, 1:].tolist()

    # REMOVE OUTLIERS?
    if remove_outliers == 'yes':
        all_data = outlier_remover(verbose, plot, strength, all_data)

    answer = list_aggregator(aggregatemethod, all_data)

    if verbose == 'verbose':
        max = 6
        slicedwidth = len(sliced.columns) - 1
        if slicedwidth > max:
            rounds = (slicedwidth // max)
            for round in range(rounds+1):
                factor = round * max
                if max+factor > slicedwidth:
                    listofcolnums = [0] + list(range(1+factor, slicedwidth+1))
                else:
                    listofcolnums = [0] + list(range(1+factor, (max+factor)+1))
                print(sliced.iloc[:, listofcolnums])
        else:
            print(sliced)
        print('\n')
    return answer


# MULTIPLE PERIOD GROWTH CALCULATION of POOL OF CONTIGUOUS (PORTFOLIO, PERIOD) PAIRS
def multiperiod_growth_portfolio(pricematrix, package, aggregatemethod, remove_outliers, strength, verbose, plot):

    growth_rates = [period_growth_portfolio(aggregatemethod, remove_outliers, strength, verbose, plot, pricematrix, item) for item in package]
    factors = [sample + 1 for sample in growth_rates]
    product = np.prod(factors)
    answer = product - 1
    if verbose == "verbose":
        print('Period Growth Rates + 1: {} || Product of (Growth Rates + 1): {}'.format(factors, product))
        print('Overall Total Growth: {}'.format(answer))
        print('\n')

    return answer


# RETURNS CORRELATION OF INPUT RANK TO PERFORMANCE RANK
def growthcorrelation_singleperiod(item, pricematrix, corrmethod, subtrialcorrgraph):

    # MAP OUT ITERATOR
    beg_date = item[1][0]
    end_date = item[1][1]
    portfoliodf = item[0]
    methcolname = portfoliodf.columns[1]
    rankcolname = portfoliodf.columns[-1]

    # GET LIST OF STOCKS FROM INPUT DF
    portfolio = portfoliodf['stock'].tolist()

    # PULL UP PRICE MATRIX AND SLICE OUT STOCKS REQUESTED
    all_cols = ['date'] + portfolio
    sliced = pricematrix[all_cols].copy()

    # SLICE OUT DATE RANGE REQUESTED
    sliced = sliced.loc[(sliced['date'] >= beg_date) & (sliced['date'] <= end_date)]

    # RESET INDEX
    sliced.reset_index(drop=True, inplace=True)

    # REMOVE EVERY ROW EXCEPT FIRST AND LAST
    sliced = sliced.iloc[[0, -1], :]
    sliced.reset_index(drop=True, inplace=True)

    # CORRECT FOR INFINITE SLOPE (IF STARTING PRICE IS ZERO, CHANGE TO 1 DOLLAR)
    sliced.replace(to_replace=float(0), value=0.01, inplace=True)

    # CALCULATE CHANGE
    sliced.iloc[:, 1:] = sliced.iloc[:, 1:].pct_change(fill_method="ffill")

    # PREP GROWTHDF FOR REATTACHMENT
    # DROP FIRST ROW (NANs)
    sliced = sliced.drop([0])
    # PIVOT TABLE
    pivotsliced = pd.pivot_table(sliced, columns='').reset_index()
    # RENAME COLUMNS
    pivotsliced.rename(columns={'index': 'stock', '': 'growth'}, inplace=True)
    # ADD RANK COLUMN
    pivotsliced['GROWTH RANK'] = pivotsliced['growth'].rank(ascending=0)

    # REATTACH TO INPUT DF
    portfoliodf = portfoliodf.join(pivotsliced.set_index('stock'), how="left", on="stock")
    if methcolname == rankcolname:
        keepcols = ['stock', rankcolname, 'growth', 'GROWTH RANK']
    else:
        keepcols = ['stock', methcolname, rankcolname, 'growth', 'GROWTH RANK']
    slimdf = portfoliodf[keepcols].copy()

    # RUN CORRELATION OF GROWTH RANK VS. SELPER RANK
    corr = slimdf[rankcolname].corr(slimdf['GROWTH RANK'], method=corrmethod)

    # CALCULATE ROLLING CORRELATION
    slimdf['roll_corr'] = slimdf.index.map(lambda x: slimdf.loc[:x, rankcolname].corr(slimdf.loc[:x, 'GROWTH RANK'], method='spearman'))

    # OPTIONAL: GRAPH MOVING CORRELATION
    if subtrialcorrgraph == 'yes':
        print(slimdf)
        slimdf['roll_corr'].plot(marker='o')
        plt.xlabel('Number of Trials')
        plt.ylabel(f'{corrmethod} Correlation')
        plt.title('Cumulative Correlation as a function of trials')
        plt.show()

    return corr, slimdf


# COLLECTS CORRELATION OF INPUT RANK TO PERFORMANCE RANK OF MULTI CONTIGUOUS TIME PERIODS
def multiperiod_growthcorrelation(pricematrix, package, corrmethod, subtrialcorrgraph):

    corr_results = [growthcorrelation_singleperiod(item, pricematrix, corrmethod, subtrialcorrgraph) for item in package]

    just_corrvals = [item[0] for item in corr_results]
    just_corrdfs = [item[1] for item in corr_results]
    avg_corr = np.mean(just_corrvals)

    return avg_corr, just_corrdfs
