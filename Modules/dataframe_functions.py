"""
Title: Generic Dataframes Functions
Date Started: Jan 30, 2022
Version: 1.0
Version Start Date: Jan 30, 2022
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied
    without the express written consent of David Hyongsik Choi.
Purpose:
VERSIONS:
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
from functools import partial
import multiprocessing as mp
#   THIRD PARTY IMPORTS
import pandas as pd
#   LOCAL APPLICATION IMPORTS


# double bounded filtering df
def filtered_double(df, filtertype, lowerbound, upperbound, targetcol):
    if filtertype == '>=<=':
        return df[(df[targetcol] >= lowerbound) & (df[targetcol] <= upperbound)]
    elif filtertype == '>=<':
        return df[(df[targetcol] >= lowerbound) & (df[targetcol] < upperbound)]
    elif filtertype == '><=':
        return df[(df[targetcol] > lowerbound) & (df[targetcol] <= upperbound)]
    elif filtertype == '><':
        return df[(df[targetcol] > lowerbound) & (df[targetcol] < upperbound)]


# single bounded filtering df
def filtered_single(df, filtertype, bound, targetcol):
    if filtertype == '>':
        return df[df[targetcol] > bound]
    elif filtertype == '>=':
        return df[df[targetcol] >= bound]
    elif filtertype == '<':
        return df[df[targetcol] < bound]
    elif filtertype == '<=':
        return df[df[targetcol] <= bound]


# sets df's chosen column as the index
def dfindexcolprep(colname, df):
    df.set_index(colname, inplace=True)
    return df


# creates list of dfs given list of identifiers and func to generate each df
def gen_listofdfs(listofids, dfgenfunc, chunksize):
    # make list of all stockdfs to combine
    pool = mp.Pool(mp.cpu_count())
    resultlist = pool.map_async(dfgenfunc, listofids, chunksize).get()
    pool.close()
    pool.join()
    return resultlist


# joins multiple dataframes in a list together that share a column
def join_matrices(sharedcolname, lofdfs, chunksize):
    # make list of all stockdfs to combine
    pool = mp.Pool(mp.cpu_count())
    fn = partial(dfindexcolprep, sharedcolname)
    resultlist = pool.map_async(fn, lofdfs, chunksize).get()
    pool.close()
    pool.join()
    # join all stock dfs together
    mdf = pd.concat(resultlist, ignore_index=False, axis=1)
    # sort by shared col
    mdf.sort_values(by=sharedcolname, inplace=True)
    # add index col and reinstate shared col
    mdf.reset_index(inplace=True)
    mdf.rename(columns={'index': sharedcolname}, inplace=True)
    return mdf


# joins multiple dataframes in a list together that share a column
def join_matrices_slim(sharedcolname, lofdfs, chunksize):
    # make list of all stockdfs to combine
    pool = mp.Pool(mp.cpu_count())
    fn = partial(dfindexcolprep, sharedcolname)
    resultlist = pool.map_async(fn, lofdfs, chunksize).get()
    pool.close()
    pool.join()
    # join all stock dfs together
    mdf = pd.concat(resultlist, ignore_index=False, axis=1)
    # sort by shared col
    mdf.sort_values(by=sharedcolname, inplace=True)
    return mdf


# transposes dataframe from AxB to BxA; requires 1RowxnCol -> nRowx1Col
def transpose1rdf(df, colheadername, origrowname):
    df = df.transpose()
    df = df.iloc[1:]
    df.reset_index(inplace=True)
    df.rename(columns={'index': colheadername, 0: origrowname}, inplace=True)
