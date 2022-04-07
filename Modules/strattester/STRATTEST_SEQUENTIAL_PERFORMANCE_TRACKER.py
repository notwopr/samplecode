"""
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
#   THIRD PARTY IMPORTS
import pandas as pd
#   LOCAL APPLICATION IMPORTS
from Modules.growthcalcbot import getportfoliopricesdf, getnormpricesdf, getportgrowthrate
from file_functions import readpkl
from file_hierarchy import PRICES
from Modules.price_history_slicing import getsingleprice
from Modules.numbers import twodecp


# GET PERFORMANCE PROFILE FOR ALL STOCKS IN PORTFOLIO
def gen_portfolio_perfprofile(allportstocks, startcapital, beg_date, end_date):
    # CONSTRUCT GROWTH DF SHELL
    masterdf = pd.DataFrame(data={
        'STOCK': allportstocks,
        'Start Date': beg_date,
        'End Date': end_date,
        'Starting Capital ($)': twodecp(startcapital / len(allportstocks))
        })
    # PULL UP PRICE MATRIX AND SLICE OUT STOCKS REQUESTED
    pricematrixdf = readpkl('allpricematrix_common', PRICES)
    all_cols = ['date'] + allportstocks
    sliced = pricematrixdf[all_cols].copy()
    # SLICE OUT DATE RANGE REQUESTED
    sliced = sliced.loc[(sliced['date'] >= beg_date) & (sliced['date'] <= end_date)].copy()
    # RESET INDEX
    sliced.reset_index(drop=True, inplace=True)
    # NORMALIZE EACH PRICE CURVE
    firstp = sliced.loc[0, allportstocks]
    sliced[allportstocks] = (sliced[allportstocks] - firstp) / firstp
    # REMOVE EVERY ROW EXCEPT FIRST AND LAST
    sliced = sliced.iloc[[-1], :]
    sliced.reset_index(drop=True, inplace=True)
    finaldf_transposed = sliced.transpose()
    finaldf_transposed.reset_index(inplace=True)
    finaldf_transposed.rename(columns={'index': 'STOCK', 0: 'Growth Rate (%)'}, inplace=True)
    finaldf_transposed = finaldf_transposed.iloc[1:]
    finaldf_transposed.reset_index(drop=True, inplace=True)
    masterdf = masterdf.join(finaldf_transposed.set_index('STOCK'), how="left", on="STOCK")
    masterdf['Ending Capital ($)'] = (masterdf['Starting Capital ($)'] * (1 + masterdf['Growth Rate (%)'])).apply(lambda x: twodecp(x))
    masterdf['Difference ($)'] = (masterdf['Ending Capital ($)'] - masterdf['Starting Capital ($)']).apply(lambda x: twodecp(x))
    masterdf['Growth Rate (%)'] = (masterdf['Growth Rate (%)'] * 100).apply(lambda x: twodecp(x))
    # sort reset and save
    masterdf.sort_values(ascending=False, by=['Growth Rate (%)'], inplace=True)
    masterdf.reset_index(drop=True, inplace=True)
    # reorder cols
    masterdf = masterdf[['STOCK', 'Start Date', 'End Date', 'Starting Capital ($)', 'Ending Capital ($)', 'Difference ($)', 'Growth Rate (%)']]
    return masterdf


# RETURNS BENCH rate over time period
def get_growthrate_bench(beg_date, end_date, benchmark):
    beg_price = getsingleprice(benchmark, beg_date)
    end_price = getsingleprice(benchmark, end_date)
    rawbenchrate = (end_price / beg_price) - 1
    return rawbenchrate


# RETURNS STATS IF YOU HAD CHOSEN ONE PORTFOLIO OVER ANOTHER
def get_portfolio_growthrate(beg_date, end_date, portfolio):
    pricematrixdf = readpkl('allpricematrix_common', PRICES)
    pricesummdf = getportfoliopricesdf(pricematrixdf, portfolio, beg_date, end_date)
    normdf = getnormpricesdf(pricesummdf, portfolio)
    growthrate = getportgrowthrate(normdf, portfolio, 'mean', 'no', 'no', 'no', 1.5)
    return growthrate
