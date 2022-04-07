"""
Title: AGE BOT MASTER
Date Started: Jan 4, 2021
Version: 1.00
Version Start: Jan 4, 2021
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose:  Returns age statistics on stocks that meet specified growth rates for given time period.
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import datetime as dt
import pickle as pkl
#   THIRD PARTY IMPORTS
import pandas as pd
#   LOCAL APPLICATION IMPORTS
from Modules.dataframe_functions import filtered_single, filtered_double
from Modules.age import get_asofage
from file_functions import buildfolders_singlechild, readpkl, buildfolders_regime_testrun, savetopkl
from Modules.tickerportalbot import tickerportal2
from file_hierarchy import daterangedb_source, tickerlistcommon_source, PRICES
from Modules.timeperiodbot import getrandomexistdate_multiple
from Modules.stats_profilers import stat_profilerv2
from Modules.growthcalcbot import get_growthdf
from Modules.multiprocessing import multiprocessorshell


# single pulloutbot trial
def agebot_singletrial(trialdumpparent, pricematrixdf, testlen, rank_beg, rank_end, gr_u, gr_l, dir_u, dir_l, trial):
    trialno = trial[0]
    exist_date = trial[1]
    # get existing stocks
    existpool = tickerportal2(exist_date, 'common')
    # get test period dates
    test_beg = exist_date
    test_end = str(dt.date.fromisoformat(exist_date) + dt.timedelta(days=testlen))
    # get growth rates over test period, filter out rates < 0 and sort rates
    agedf = get_growthdf(pricematrixdf, existpool, test_beg, test_end, False)
    if all([gr_u, gr_l, dir_u, dir_l]):
        agedf = filtered_double(agedf, dir_l+dir_u, gr_l, gr_u, f'GROWTH {test_beg} TO {test_end}')
    elif all([gr_u, dir_u]):
        agedf = filtered_single(agedf, dir_u, gr_u, f'GROWTH {test_beg} TO {test_end}')
    elif all([gr_l, dir_l]):
        agedf = filtered_single(agedf, dir_l, gr_l, f'GROWTH {test_beg} TO {test_end}')
    if len(agedf) == 0:
        # create summary
        trialsummary = {
            'trialno': trialno,
            'testlen': testlen,
            'rank_beg': rank_beg,
            'rank_end': rank_end,
            'test_beg': test_beg,
            'test_end': test_end,
            'poolsize': len(agedf)
        }
    else:
        # filter by rank limit
        agedf = agedf.iloc[rank_beg:rank_end, :].copy()
        # create summary
        trialsummary = {
            'trialno': trialno,
            'testlen': testlen,
            'rank_beg': rank_beg,
            'rank_end': rank_end,
            'test_beg': test_beg,
            'test_end': test_end,
            'poolsize': len(agedf)
        }
        if len(agedf) > 0:
            # add ages column
            agedf['age'] = agedf['STOCK'].map(lambda x: get_asofage(x, dt.date.fromisoformat(test_beg)))
            # get stats
            agestats = stat_profilerv2(agedf['age'].tolist())
            growstats = stat_profilerv2(agedf[f'GROWTH {test_beg} TO {test_end}'].tolist())
            # add stats to summary
            for stattype in ['age', 'growthrate']:
                if stattype == 'age':
                    statdict = agestats
                elif stattype == 'growthrate':
                    statdict = growstats
                for key, val in statdict.items():
                    trialsummary.update({f'{stattype}_{key}': val})
    # save to file
    savetopkl(f'agestats_trial{trialno}', trialdumpparent, trialsummary)


# main pulloutbot function
def agebotmaster(global_params):
    # build folders
    testregimeparent, testrunparent = buildfolders_regime_testrun(global_params['rootdir'], global_params['testnumber'], global_params['todaysdate'], global_params['testregimename'])
    # get trialexistdates
    if len(global_params['statictrialexistdates']) != 0:
        if len(global_params['statictrialexistdates']) == global_params['num_trials']:
            alltrialexistdates = global_params['statictrialexistdates']
        else:
            print('The static trial exist dates you want to use do not equal the number of trials you want to run.  Exiting...')
            exit()
    else:
        alltrialexistdates = getrandomexistdate_multiple(global_params['num_trials'], global_params['firstdate'], global_params['latestdate'], global_params['testlen'], daterangedb_source)
    # load price matrices into RAM
    pricematrixdf = readpkl('allpricematrix_common', PRICES)
    # run multitrial processor
    trialdumpparent = buildfolders_singlechild(testrunparent, 'trialdumpparent')
    targetvars = (trialdumpparent, pricematrixdf, global_params['testlen'], global_params['rank_beg'], global_params['rank_end'], global_params['gr_u'], global_params['gr_l'], global_params['dir_u'], global_params['dir_l'])
    multiprocessorshell(trialdumpparent, agebot_singletrial, alltrialexistdates, 'yes', targetvars, global_params['chunksize'])
    # construct alltrialsummariesdf
    table_results = []
    for child in trialdumpparent.iterdir():
        with open(child, "rb") as targetfile:
            unpickled_raw = pkl.load(targetfile)
        table_results.append(unpickled_raw)
    alltrialsummariesdf = pd.DataFrame(data=table_results)
    # save df
    alltrialsummariesdf.to_csv(index=False, path_or_buf=testrunparent / "agebot_alltrialsummaries.csv")
    # crunch overall test stats
    allstatdicts = []
    statcols = list(alltrialsummariesdf.columns)[7:]
    for statcol in statcols:
        datarr = alltrialsummariesdf[statcol].dropna().to_numpy()
        if len(datarr) >= 2:
            statdict = stat_profilerv2(datarr)
        else:
            statdict = {}
        statdict.update({'category': statcol})
        allstatdicts.append(statdict)
    # CREATE STATDF
    statdf = pd.DataFrame(data=allstatdicts)
    # save results
    statsfn = "agebotstatanalysis"
    statdf.to_csv(index=False, path_or_buf=testrunparent / f"{statsfn}.csv")
    return statdf, alltrialsummariesdf
