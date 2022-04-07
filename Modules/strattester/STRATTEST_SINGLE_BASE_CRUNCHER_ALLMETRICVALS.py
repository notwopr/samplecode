"""
Title: STRAT TESTER SINGLE BASE CRUNCHER - ALLMETRIC VALUES
Date Started: Dec 8, 2020
Version: 6.00
Version Start: Mar 11, 2021
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose: Running several metrics on the same pool of stocks and running a weighted ranking over all metric outcomes to return an overall ranking.

VERSION NOTES
1.01: Added marketbeater method.
1.02: Added look_back options.
1.03: Split winvol and winrate into separate functions.
1.04: Shift squeeze metrics to mmbm calibration.
1.05: Switch bmflat metrics to oldbareminraw graph instead of bareminraw graph.
1.06: Remove old smooth squeeze function references.  Replaced with new optimized formulas.
2.0: Removed deprecated functions.
4: Simplify.  Remove references to metric functions.  Move that responsibility to each paramscript.
5: simplify allmetricvals code for calibrating pricedata and prepping and selecting datatypes.
6: make accommodations for revenue and free cash flow datasources.
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import pickle as pkl
from functools import partial
from multiprocessing import Pool
#   THIRD PARTY IMPORTS
import pandas as pd
#   LOCAL APPLICATION IMPORTS
from Modules.price_calib import add_calibratedprices
from Modules.list_functions import removedupes
from Modules.price_history_slicing import pricedf_daterange, pricedf_daterange_fundies
from Modules.price_history_types import tradedateonlypricedf
from file_functions import savetopkl, readpkl, buildfolders_singlechild
from file_hierarchy import PRICES
from Modules.metriclibrary.STRATTEST_FUNCBASE import allpctchanges, getmetcolname, priceslicer, alldpcmargins, priceslicer_shortenend
from Modules.ranking_calib import mmcalibrated
from Modules.multiprocessing import multiprocessorshell, multiprocessorshell_mapasync_getresults
from Modules.metriclibrary.STRATTEST_FUNCBASE_RAW import resampledslopescoredata_single, getpricedate_single
from Modules.file_tests import checknum


# GET LBSUFFIX FOR MARKETBEATER FUNC
def getlbsuffix(metricitem):
    look_backval = metricitem['look_back']
    lbsuffix = f'_LB{look_backval}'
    return lbsuffix


# PREP BENCHMATRIX FOR MARKETBEATER METRIC USE
def getbenchmatrixchangedf(benchcols):
    # pull bench pricematrix
    benchmatrixdf = readpkl('allpricematrix_bench', PRICES)
    # add daily pct change cols to matrix
    dailychangecols = []
    for item in benchcols:
        benchmatrixdf[f'dpc_{item}'] = benchmatrixdf[item].pct_change(periods=1, fill_method='ffill')
        dailychangecols.append(f'dpc_{item}')
    # delete price columns
    benchmatrixchangesdf = benchmatrixdf[['date'] + dailychangecols].copy()
    return benchmatrixchangesdf


# send summary object and paramsettings to proper metricfunction to calculate results
def metric_shell(metricitem, summary, **metricparams):
    metricfunc = metricitem['metricfunc']
    # run metric
    metricscore = metricfunc(**metricparams)
    # update summary with metric answer
    metricname = metricitem['metricname']
    if metricname == 'marketbeater':
        summary.update(metricscore)
    else:
        metcolname = getmetcolname(metricitem)
        summary.update({metcolname: metricscore})
    return summary


# get all dpc data of single series
def getalldpcs(dpctype, slicedprices, stock, focuscol, benchmatrixchangesdf):
    if dpctype == 'margin':
        dpc = alldpcmargins(slicedprices, stock, benchmatrixchangesdf, '^IXIC')
    else:
        dpc = allpctchanges(slicedprices, focuscol, 1)
    return dpc


# create dict of dpc data needed
def getdpcdatadict(alldpctypes, slicedprices, benchmatrixchangesdf, stock):
    dpcdict = {}
    for dpctype in ['', 'bmin', 'bmax', 'true', 'straight', 'margin']:
        # get focuscol
        if dpctype == '':
            focuscol = stock
        elif dpctype == 'bmin':
            focuscol = 'oldbareminraw'
        elif dpctype == 'bmax':
            focuscol = 'baremaxraw'
        elif dpctype == 'true':
            focuscol = 'trueline'
        elif dpctype == 'straight':
            focuscol = 'straight'
        # if nonzerodpc absolute value exists
        if f'{dpctype}dpc_nonzero_abs' in alldpctypes:
            # get all dpcs
            dpc = getalldpcs(dpctype, slicedprices, stock, focuscol, benchmatrixchangesdf)
            # get nonzero dpc
            dpc_nonzero = [item for item in dpc if item != 0]
            # get absolute values
            dpc_nonzero_abs = [abs(item) for item in dpc_nonzero]
            # update dpcdict
            dpcdict.update({
                f'{dpctype}dpc': dpc,
                f'{dpctype}dpc_nonzero': dpc_nonzero,
                f'{dpctype}dpc_nonzero_abs': dpc_nonzero_abs
            })
        # if nonzerodpc exists
        elif f'{dpctype}dpc_nonzero' in alldpctypes:
            # get all dpcs
            dpc = getalldpcs(dpctype, slicedprices, stock, focuscol, benchmatrixchangesdf)
            # get nonzero dpc
            dpc_nonzero = [item for item in dpc if item != 0]
            # update dpcdict
            dpcdict.update({
                f'{dpctype}dpc': dpc,
                f'{dpctype}dpc_nonzero': dpc_nonzero
            })
        # otherwise if just dpc version exists
        elif f'{dpctype}dpc' in alldpctypes:
            # get all dpcs
            dpc = getalldpcs(dpctype, slicedprices, stock, focuscol, benchmatrixchangesdf)
            dpcdict.update({f'{dpctype}dpc': dpc})
        # if dpc absolute value exists
        if f'{dpctype}dpc_abs' in alldpctypes:
            # if dpc already created:
            if f'{dpctype}dpc' in alldpctypes or f'{dpctype}dpc_nonzero' in alldpctypes or f'{dpctype}dpc_nonzero_abs' in alldpctypes:
                # all absolute values
                dpc_abs = [abs(item) for item in dpc]
                # update dpcdict
                dpcdict.update({
                    f'{dpctype}dpc_abs': dpc_abs
                })
            else:
                # get all dpcs
                dpc = getalldpcs(dpctype, slicedprices, stock, focuscol, benchmatrixchangesdf)
                # all absolute values
                dpc_abs = [abs(item) for item in dpc]
                # update dpcdict
                dpcdict.update({
                    f'{dpctype}dpc': dpc,
                    f'{dpctype}dpc_abs': dpc_abs
                })
        # if dpc pos value exists
        if f'{dpctype}dpc_pos' in alldpctypes:
            # if dpc already created:
            if f'{dpctype}dpc' in alldpctypes or f'{dpctype}dpc_nonzero' in alldpctypes or f'{dpctype}dpc_nonzero_abs' in alldpctypes or f'{dpctype}dpc_abs' in alldpctypes:
                # all pos values
                dpc_pos = [item for item in dpc if item > 0]
                # update dpcdict
                dpcdict.update({
                    f'{dpctype}dpc_pos': dpc_pos
                })
            else:
                # get all dpcs
                dpc = getalldpcs(dpctype, slicedprices, stock, focuscol, benchmatrixchangesdf)
                # all pos values
                dpc_pos = [item for item in dpc if item > 0]
                # update dpcdict
                dpcdict.update({
                    f'{dpctype}dpc': dpc,
                    f'{dpctype}dpc_pos': dpc_pos
                })
        # if dpc neg value exists
        if f'{dpctype}dpc_neg' in alldpctypes:
            # if dpc already created:
            if f'{dpctype}dpc' in alldpctypes or f'{dpctype}dpc_nonzero' in alldpctypes or f'{dpctype}dpc_nonzero_abs' in alldpctypes or f'{dpctype}dpc_abs' in alldpctypes or f'{dpctype}dpc_pos' in alldpctypes:
                # all neg values
                dpc_neg = [item for item in dpc if item < 0]
                # update dpcdict
                dpcdict.update({
                    f'{dpctype}dpc_neg': dpc_neg
                })
            else:
                # get all dpcs
                dpc = getalldpcs(dpctype, slicedprices, stock, focuscol, benchmatrixchangesdf)
                # all neg values
                dpc_neg = [item for item in dpc if item < 0]
                # update dpcdict
                dpcdict.update({
                    f'{dpctype}dpc': dpc,
                    f'{dpctype}dpc_neg': dpc_neg
                })
    return dpcdict


def allmetrics_single(datasourcetype, slicedprices, summary, lookbackmetrics_to_run, benchmatrixchangesdf, stock):
    # get list of all calibrations needed
    allcalibrations = [item for metricitem in lookbackmetrics_to_run for item in metricitem['calibration']]
    allcalibrations = removedupes(allcalibrations)
    # get calibrated prices
    slicedprices = add_calibratedprices(slicedprices, allcalibrations, stock)
    # get list of dpc data needed
    alldpctypes = [metricitem['data'] for metricitem in lookbackmetrics_to_run]
    alldpctypes = removedupes(alldpctypes)
    # create dpc data dict
    dpcdict = getdpcdatadict(alldpctypes, slicedprices, benchmatrixchangesdf, stock)
    # if metrics that require tradedateonly data are present get tradedatedpc data
    allmetnames = [item['metricname'] for item in lookbackmetrics_to_run]
    tradedateneeded = 'no'
    if datasourcetype == 'prices':
        tradedatemetnames = [
            'statseglen_pos',
            'statseglen_neg',
            'psegnegsegratio',
            'consecsegprev',
            'benchbeatpct',
            'accretionscore',
            'accretiontally',
            'posnegmagtrade',
            'posnegmagratiotrade',
            'posnegprevalencetrade'
        ]
        for metname in allmetnames:
            for tdmetname in tradedatemetnames:
                if metname.startswith(tdmetname):
                    tradedateneeded = 'yes'
                    break
    if tradedateneeded == 'yes':
        # get tradedate pricedf
        tradeslicedprices = tradedateonlypricedf(slicedprices)
        if len(tradeslicedprices) > 1:
            # get tradedate dpc data
            tradedatedpcdict = getdpcdatadict(alldpctypes, tradeslicedprices, benchmatrixchangesdf, stock)
        else:
            tradedatedpcdict = dpcdict
    elif tradedateneeded == 'no':
        tradeslicedprices = slicedprices
        tradedatedpcdict = dpcdict
    # get age
    age = len(slicedprices) - 1
    # get slopescoredata in resampless metrics are run
    for metricitem in lookbackmetrics_to_run:
        if metricitem['metricname'].startswith('resampledslopescore') or metricitem['metricname'].startswith('magtodevresampssratio'):
            focuscol = metricitem['focuscol']
            if focuscol == 'rawprice':
                focuscol = stock
            slopescoredata = resampledslopescoredata_single(slicedprices.copy(), focuscol, metricitem['resamplefreq'])
            break
    # get metricval for each metric item in stage script
    for metricitem in lookbackmetrics_to_run:
        # get name
        metricname = metricitem['metricname']
        # get dpctype
        dpctype = metricitem['data']
        fulldpctype = ''
        if dpctype.endswith('nonzero'):
            fulldpctype = metricitem['data'][:-8]
        # set metricparams
        metricparams = {}
        if metricname.startswith('age_'):
            metricparams = {'prices': slicedprices.copy()}
        elif metricname.startswith('currtoathdiff') or metricname.startswith('currmarketcap'):
            metricparams = {'prices': slicedprices.copy(), 'stock': stock}
        elif metricname.startswith('currtoathdays'):
            metricparams = {'prices': slicedprices.copy(), 'stock': stock, 'ath_occur': metricitem['ath_occur']}
        elif metricname.startswith('fundypositiveslope'):
            metricparams = {'prices': slicedprices.copy(), 'stock': stock, 'datatype': metricitem['datatype']}
        elif metricname.startswith('flatlinescore_') or metricname.startswith('posnegprevratio'):
            metricparams = {'daily_changes': dpcdict[dpctype]}
        elif metricname == 'crasheventloss':
            metricparams = {'stock': stock, 'beg_date': metricitem['eventstart'], 'end_date': metricitem['eventend']}
        elif metricname.startswith('slopescore') or metricname.startswith('growthrate') or metricname.startswith('slopeto') or metricname.startswith('unifatvolscore') or metricname.startswith('growthrate'):
            focuscol = metricitem['focuscol']
            if focuscol == 'rawprice':
                focuscol = stock
            metricparams = {'prices': slicedprices.copy(), 'focuscol': focuscol}
        elif metricname.startswith('dgfslopescore'):
            metricparams = {'prices': slicedprices.copy(), 'dgf': metricitem['dgf']}
        elif metricname.startswith('sslitmusratio'):
            focuscol = metricitem['focuscol']
            if focuscol == 'rawprice':
                focuscol = stock
            metricparams = {'prices': slicedprices.copy(), 'focuscol': focuscol, 'dgf': metricitem['dgf']}
        elif metricname.startswith('minslopescore'):
            metricparams = {'prices': slicedprices.copy(), 'overallrate': metricitem['overallrate']}
        elif metricname.startswith('actualtominssratio'):
            focuscol = metricitem['focuscol']
            if focuscol == 'rawprice':
                focuscol = stock
            metricparams = {'prices': slicedprices.copy(), 'overallrate': metricitem['overallrate'], 'focuscol': focuscol}
        elif metricname.startswith('dpctominss'):
            metricparams = {'prices': slicedprices.copy(), 'overallrate': metricitem['overallrate'], 'dpcdata': dpcdict[dpctype], 'mode': metricitem['mode']}
        elif metricname == 'positiveslope' or metricname.startswith('accretionscore') or metricname.startswith('accretiontally'):
            focuscol = metricitem['focuscol']
            if focuscol == 'rawprice':
                focuscol = stock
            if metricname.startswith('accretionscore') or metricname.startswith('accretiontally'):
                metricparams = {'datadf': tradeslicedprices.copy(), 'focuscol': focuscol, 'accret_type': metricitem['accret_type']}
            else:
                metricparams = {'datadf': slicedprices.copy(), 'focuscol': focuscol}
        elif metricname.startswith('rollingslopescore'):
            focuscol = metricitem['focuscol']
            if focuscol == 'rawprice':
                focuscol = stock
            metricparams = {'prices': slicedprices.copy(), 'focuscol': focuscol, 'win_len': metricitem['win_len'], 'agg_type': metricitem['agg_type']}
        elif metricname.startswith('segbackslopescore'):
            focuscol = metricitem['focuscol']
            if focuscol == 'rawprice':
                focuscol = stock
            metricparams = {'prices': slicedprices.copy(), 'focuscol': focuscol, 'segsback': metricitem['segsback'], 'winlen': metricitem['winlen']}
        elif metricname.startswith('resampledslopescore'):
            metricparams = {'slopescoredata': slopescoredata, 'aggtype': metricitem['aggtype']}
        elif metricname.startswith('magtodevresampssratio'):
            metricparams = {'slopescoredata': slopescoredata, 'aggtype_mag': metricitem['aggtype_mag'], 'aggtype_dev': metricitem['aggtype_dev']}
        elif metricname.startswith('selectsampfreqslopescore'):
            metricparams = {'prices': slicedprices.copy(), 'freqlist': metricitem['freqlist'], 'aggtype': metricitem['aggtype'], 'agg2type': metricitem['agg2type']}
        elif metricname == 'allsampfreqslopescore':
            metricparams = {'prices': slicedprices.copy(), 'aggtype': metricitem['aggtype'], 'agg2type': metricitem['agg2type']}
        elif metricname.startswith('changeratetrend') or metricname.startswith('prevalencetrend'):
            metricparams = {'prices': slicedprices.copy(), 'stock': stock, 'changewinsize': metricitem['changewinsize'], 'changetype': metricitem['changetype']}
        elif metricname == 'dollarsperday' or metricname == 'kneescore' or metricname == 'reg1reg2ratio' or metricname == 'lastdiplen' or metricname == 'reg1pct' or metricname == 'priceageratio':
            metricparams = {'prices': slicedprices.copy(), 'stock': stock}
        elif metricname == 'currentprice':
            metricparams = {'prices': slicedprices.copy(), 'stock': stock, 'type': metricitem['type']}
        elif metricname == 'marketbeater':
            lbsuffix = getlbsuffix(metricitem)
            metricparams = {'prices': slicedprices.copy(), 'stock': stock, 'benchcols': list(metricitem['bweights'].keys()), 'benchmatrixchangesdf': benchmatrixchangesdf, 'lbsuffix': lbsuffix}
        elif metricname == 'marketbeaterv2':
            metricparams = {'prices': slicedprices.copy(), 'stock': stock, 'bweights': metricitem['bweights'], 'benchmatrixchangesdf': benchmatrixchangesdf, 'avgtype': metricitem['avgtype'], 'usedev': metricitem['usedev']}
        elif metricname.startswith('posarea') or metricname.startswith('benchbeatpct'):
            metricparams = {'prices': tradeslicedprices.copy(), 'stock1': stock, 'stock2': metricitem['benchstock']}
        elif metricname.startswith('unifatscore') or metricname.startswith('unifatrawscore'):
            idealcol = metricitem['idealcol']
            focuscol = metricitem['focuscol']
            if focuscol == 'rawprice':
                focuscol = stock
            if idealcol == 'rawprice':
                idealcol = stock
            metricparams = {'prices': slicedprices.copy(), 'focuscol': focuscol, 'idealcol': idealcol, 'stat_type': metricitem['stat_type']}
        elif metricname.startswith('psegnegsegratio'):
            metricparams = {'daily_changes': tradedatedpcdict[dpctype], 'stat_type': metricitem['stat_type']}
        elif metricname.startswith('posnegmagratio'):
            metricparams = {'daily_changes': dpcdict[dpctype], 'stat_type': metricitem['stat_type']}
        elif metricname.startswith('posnegmagratiotrade'):
            metricparams = {'daily_changes': tradedatedpcdict[dpctype], 'stat_type': metricitem['stat_type']}
        elif metricname == 'posnegratioproduct':
            metricparams = {'daily_changes': dpcdict[fulldpctype], 'nonzerosamples': dpcdict[dpctype], 'stat_type': metricitem['stat_type']}
        elif metricname.startswith('statseglen') or metricname.startswith('seglife') or metricname.startswith('consecsegprev'):
            if metricname.startswith('statseglen_pos') or metricname.startswith('statseglen_neg'):
                metricparams = {'daily_changes': tradedatedpcdict[dpctype], 'mode': metricitem['mode'], 'stat_type': metricitem['stat_type']}
            elif metricname.startswith('consecsegprev'):
                metricparams = {'daily_changes': tradedatedpcdict[dpctype], 'numer_type': metricitem['numer_type']}
            else:
                metricparams = {'daily_changes': dpcdict[dpctype], 'mode': metricitem['mode'], 'stat_type': metricitem['stat_type']}
        elif metricname == 'maxflatlitmus' or metricname == 'maxbmflatlitmus' or metricname == 'maxbmaxflatlitmus':
            thresh_maxratio = metricitem['thresh_maxratio']
            thresh_maxseg = metricitem['thresh_maxseg']
            metricparams = {'daily_changes': dpcdict[dpctype], 'age': age, 'thresh_maxratio': thresh_maxratio, 'thresh_maxseg': thresh_maxseg}
        elif metricname == 'flatlinescorelitmus' or metricname == 'bmflatlinescorelitmus':
            thresh_flatscore = metricitem['thresh_flatscore']
            thresh_meanseglen = metricitem['thresh_meanseglen']
            metricparams = {'daily_changes': dpcdict[dpctype], 'thresh_flatscore': thresh_flatscore, 'thresh_meanseglen': thresh_meanseglen}
        elif metricname.startswith('posnegscore') or metricname.startswith('posnegdpcscore') or metricname.startswith('posnegdevscore'):
            metricparams = {'dpcdata': dpcdict[dpctype], 'statmeth': metricitem['statmeth'], 'statmeth2': metricitem['statmeth2'], 'calcmeth': metricitem['calcmeth']}
        elif metricname.startswith('posnegprevalence'):
            metricparams = {'daily_changes': dpcdict[dpctype], 'changetype': metricitem['changetype']}
        elif metricname.startswith('posnegprevalencetrade'):
            metricparams = {'daily_changes': tradedatedpcdict[dpctype], 'changetype': metricitem['changetype']}
        elif metricname.startswith('posnegmag_') or metricname.startswith('posnegmagprevscore'):
            metricparams = {'daily_changes': dpcdict[dpctype], 'changetype': metricitem['changetype'], 'stat_type': metricitem['stat_type']}
        elif metricname.startswith('posnegmagtrade_'):
            metricparams = {'daily_changes': tradedatedpcdict[dpctype], 'changetype': metricitem['changetype'], 'stat_type': metricitem['stat_type']}
        elif metricname.startswith('dpc_cruncher'):
            metricparams = {'dpcdata': dpcdict[dpctype], 'mode': metricitem['mode']}
        elif metricname.startswith('slopeoverloss'):
            metricparams = {'prices': slicedprices.copy(), 'stock': stock, 'stat_type': metricitem['stat_type'], 'combtype': metricitem['combtype']}
        elif metricname.startswith('growthtoloss'):
            metricparams = {'prices': slicedprices.copy(), 'stock': stock, 'groparams': metricitem['groparams'], 'lossparams': metricitem['lossparams'], 'combtype': metricitem['combtype']}
        elif metricname.startswith('rollgrowthtoloss'):
            metricparams = {'prices': slicedprices.copy(), 'stock': stock, 'win_len': metricitem['win_len'], 'agg_type': metricitem['agg_type'], 'groparams': metricitem['groparams'], 'lossparams': metricitem['lossparams'], 'combtype': metricitem['combtype']}
        elif metricname.startswith('area_') or metricname == "squeezearea":
            uppercol = metricitem['uppercol']
            lowercol = metricitem['lowercol']
            datarangecol = metricitem['datarangecol']
            if uppercol == 'rawprice':
                uppercol = stock
            if lowercol == 'rawprice':
                lowercol = stock
            if datarangecol == 'rawprice':
                datarangecol = stock
            metricparams = {'prices': slicedprices.copy(), 'datarangecol': datarangecol, 'uppercol': uppercol, 'lowercol': lowercol}
        elif metricname.startswith('drop_') or metricname.startswith('allpctdrop'):
            uppercol = metricitem['uppercol']
            lowercol = metricitem['lowercol']
            if uppercol == 'rawprice':
                uppercol = stock
            if lowercol == 'rawprice':
                lowercol = stock
            if metricname.startswith('drop_prev'):
                metricparams = {'prices': slicedprices.copy(), 'uppercol': uppercol, 'lowercol': lowercol}
            else:
                metricparams = {'prices': slicedprices.copy(), 'uppercol': uppercol, 'lowercol': lowercol, 'stat_type': metricitem['stat_type']}
        elif metricname.startswith('dropscoreratio'):
            uppercol = metricitem['uppercol']
            lowercol = metricitem['lowercol']
            if uppercol == 'rawprice':
                uppercol = stock
            if lowercol == 'rawprice':
                lowercol = stock
            metricparams = {'prices': slicedprices.copy(), 'uppercol': uppercol, 'lowercol': lowercol, 'stat_type': metricitem['stat_type'], 'benchticker': metricitem['benchticker']}
        elif metricname.startswith('unis'):
            metricparams = {'prices': slicedprices.copy(), 'uppercol': metricitem['uppercol'], 'lowercol': metricitem['lowercol'], 'stat_type': metricitem['stat_type']}
        elif metricname.startswith('rollingsmooth') or metricname.startswith('rollingsqueeze'):
            metricparams = {'prices': slicedprices.copy(), 'win_len': metricitem['win_len'], 'age': age, 'stat_type': metricitem['stat_type'], 'agg_type': metricitem['agg_type'], 'uppercol': metricitem['uppercol'], 'lowercol': metricitem['lowercol'], 'origpricecol': stock}
        elif metricname == 'dipfinder':
            metricparams = {'prices': slicedprices.copy(), 'uppercol': metricitem['uppercol'], 'lowercol': metricitem['lowercol']}
        elif metricname.startswith('bigjump'):
            metricparams = {'daily_changes': dpcdict[dpctype], 'bigjumpstrength': metricitem['bigjumpstrength']}
        elif metricname.startswith('reg1stats'):
            metricparams = {'prices': slicedprices.copy(), 'stock': stock, 'stat_type': metricitem['stat_type']}
        elif metricname.startswith('regqualscore'):
            metricparams = {'prices': slicedprices.copy(), 'stock': stock, 'region': metricitem['region']}
        # calculate metric value
        summary = metric_shell(metricitem, summary, **metricparams)
    return summary


def lookbackcruncher_single(summary, datasourcetype, prices, metrics_to_run, benchmatrixchangesdf, stock):
    # GROUP BATCH ELEMENTS BY LOOKBACK
    lookback_vals = removedupes([item['look_back'] for item in metrics_to_run])
    metric_batches = [{'look_backval': look_backval, 'lookback_batch': [item for item in metrics_to_run if item['look_back'] == look_backval]} for look_backval in lookback_vals]
    # FOR EACH LOOK_BACK BATCH...
    for lookbackbatch in metric_batches:
        look_back = lookbackbatch['look_backval']
        lookbackmetrics_to_run = lookbackbatch['lookback_batch']
        # SLICE IF LOOK_BACK SETTING EXISTS
        if look_back != 0:
            slicedprices = priceslicer(prices, look_back)
        else:
            slicedprices = prices.copy()
        summary = allmetrics_single(datasourcetype, slicedprices, summary, lookbackmetrics_to_run, benchmatrixchangesdf, stock)
    return summary


def lookbackshell_single(resultfolder, datasourcetype, metrics_to_run, benchmatrixchangesdf, beg_date, end_date, stock):
    # GET DATA SOURCE HISTORY
    if datasourcetype == 'revenue' or datasourcetype == 'freecashflow':
        datadf = pricedf_daterange_fundies(stock, 'fundies', beg_date, end_date)
        # KEEP ONLY ONE AND CHANGE NAME
        datadf = datadf[["date", f'{datasourcetype}_{stock}']].copy()
        datadf.rename(columns={f'{datasourcetype}_{stock}': stock}, inplace=True)
        # CREATE MASTER SUMMARY
        summary = {
            'stock': stock,
            }
    else:
        datadf = pricedf_daterange(stock, beg_date, end_date)
        # CREATE MASTER SUMMARY
        summary = {
            'stock': stock,
            'age': len(datadf) - 1
            }
    summary = lookbackcruncher_single(summary, datasourcetype, datadf, metrics_to_run, benchmatrixchangesdf, stock)
    # SAVE TO FILE
    #filename = f"{stock}_layercake"
    #savetopkl(filename, resultfolder, summary)
    return summary


def recoverybotshell_single(resultfolder, datasourcetype, metrics_to_run, benchmatrixchangesdf, beg_date, end_date, stock):
    # separate currtoath metric from rest
    currtoathmetrics = [item for item in metrics_to_run if item['metricname'].startswith('currtoath')]
    remaindermetrics = [item for item in metrics_to_run if not item['metricname'].startswith('currtoath')]
    # GET PRICE HISTORY
    prices = pricedf_daterange(stock, beg_date, end_date)
    # CREATE MASTER SUMMARY
    summary = {
        'stock': stock,
        'age': len(prices) - 1
        }
    # add currtoath stats to summary first
    summary = lookbackcruncher_single(summary, datasourcetype, prices.copy(), currtoathmetrics, benchmatrixchangesdf, stock)
    preath_occur = currtoathmetrics[0]['ath_occur']
    ath_date = getpricedate_single(prices.copy(), stock, 'max', preath_occur)
    # add preathend date to summary
    summary.update({f'ATHdate_{preath_occur}': ath_date})
    # slice prices to new end_date
    prices = priceslicer_shortenend(prices, ath_date)
    # if new range has less than two rows, skip
    if len(prices) >= currtoathmetrics[0].get('min_preath_age', 2):
        # run remaining metrics on pre-ATH date range
        summary = lookbackcruncher_single(summary, datasourcetype, prices, remaindermetrics, benchmatrixchangesdf, stock)
    # SAVE TO FILE
    filename = f"{stock}_layercake"
    savetopkl(filename, resultfolder, summary)


def winraterankershell(resultfolder, dumpfolder, metcolname, winratemetricitem, beg_date, end_date, tickerlist, rankmeth, rankregime, savemode):
    metricfunc = winratemetricitem['metricfunc']
    winrateranksdf = metricfunc(metcolname, winratemetricitem, resultfolder, dumpfolder, beg_date, end_date, tickerlist, rankmeth, rankregime, savemode)
    # PREP WINRATERANKDF
    wrprepdf = winrateranksdf[['stock', metcolname]].copy()
    return wrprepdf


def allmetricval_cruncher(allmetricsresults, datasourcetype, scriptname, scriptparams, beg_date, end_date, tickerlist, rankmeth, rankregime, savemode, chunksize):

    # construct masterdf
    masterdf = pd.DataFrame(data={'stock': tickerlist})
    # separate winrate- from nonwinrate- metrics
    winratemetrics_to_run = [metricitem for metricitem in scriptparams if metricitem['metricname'].startswith('winrateranker') is True]
    nonwinratemetrics_to_run = [metricitem for metricitem in scriptparams if metricitem['metricname'].startswith('winrateranker') is False]

    # get metric vals for all non-winrate metrics
    if len(nonwinratemetrics_to_run) != 0:
        nonwinratedump = buildfolders_singlechild(allmetricsresults, 'nonwinrate_dumpfiles')
        # load marketbeater benchmarkdf if metric chosen
        benchmatrixchangesdf = ''
        for metricitem in nonwinratemetrics_to_run:
            if metricitem['metricname'].startswith('marketbeater') or metricitem['data'] == 'margindpc_nonzero' or metricitem['data'] == 'margindpc':
                # get tickers
                if metricitem['metricname'].startswith('marketbeater'):
                    benchtickers = list(metricitem['bweights'].keys())
                else:
                    benchtickers = ['^IXIC']
                benchmatrixchangesdf = getbenchmatrixchangedf(benchtickers)
        # run metricsval multiprocessor
        if scriptname.startswith('recoverybot'):
            mpfunc = recoverybotshell_single
        else:
            mpfunc = lookbackshell_single
        # run multiprocessor
        table_results = multiprocessorshell_mapasync_getresults(mpfunc, tickerlist, 'no', (nonwinratedump, datasourcetype, nonwinratemetrics_to_run, benchmatrixchangesdf, beg_date, end_date), chunksize)
        nonwinratedf = pd.DataFrame(data=table_results)

        # save to file
        filename = f"nonwinratemetricvals_as_of_{end_date}"
        if savemode == 'pkl':
            savetopkl(filename, allmetricsresults, nonwinratedf)
        elif savemode == 'csv':
            fullcsvpath = allmetricsresults / f"{filename}.csv"
            if len(str(fullcsvpath)) > 260:
                fullcsvpath = f'\\\\?\\{fullcsvpath}'
            nonwinratedf.to_csv(index=False, path_or_buf=fullcsvpath)
        # append df to masterdf
        masterdf = masterdf.join(nonwinratedf.set_index('stock'), how="left", on="stock")

    # run winrate metrics if any
    if len(winratemetrics_to_run) != 0:
        # for each winratemetric..
        for winratemetricitem in winratemetrics_to_run:
            metcolname = getmetcolname(winratemetricitem)
            # create winratemetric folders
            metric_dumpfolder = buildfolders_singlechild(allmetricsresults, f'{metcolname}_dumpfiles')
            wrprepdf = winraterankershell(allmetricsresults, metric_dumpfolder, metcolname, winratemetricitem, beg_date, end_date, tickerlist, rankmeth, rankregime, savemode)
            # append df to masterdf
            masterdf = masterdf.join(wrprepdf.set_index('stock'), how="left", on="stock")

    # RANK DATA
    sumcols = []
    weight_total = 0
    for metricitem in scriptparams:
        # DEFINE RANK PARAMS
        metricweight = metricitem['metricweight']
        metricname = metricitem['metricname']
        metcolname = getmetcolname(metricitem)
        # IF MARKETBEATER, PREPARE RANKCOLUMN
        if metricname == 'marketbeater':
            lbsuffix = getlbsuffix(metricitem)
            mbsumcols = []
            for bcol in list(metricitem['bweights'].keys()):
                for metric in metricitem['mweights'].keys():
                    # RANK EACH COLUMN NEEDED TO BE RANKED
                    colweight = metricitem['bweights'][bcol] * metricitem['mweights'][metric]
                    mbsubjectcolname = f'{bcol}_{metric}{lbsuffix}'
                    mbrankcolname = f'RANK_{mbsubjectcolname} (w={colweight})'
                    if metric == 'pct_neg':
                        rankascend = 1
                    else:
                        rankascend = 0
                    if rankmeth == 'minmax':
                        masterdf[mbrankcolname] = mmcalibrated(masterdf[mbsubjectcolname].to_numpy(), rankascend, rankregime)
                    elif rankmeth == 'standard':
                        masterdf[mbrankcolname] = masterdf[mbsubjectcolname].rank(ascending=rankascend)
                    # GET EACH RANKCOLUMN'S WEIGHTED RANK VALUE
                    masterdf[f'w_{mbrankcolname}'] = (masterdf[mbrankcolname] * colweight)
                    # KEEP TRACK OF THE WEIGHTED RANK COLUMN TO SUM LATER
                    mbsumcols.append(f'w_{mbrankcolname}')

            # SUM WEIGHTED RANK VALUES TOGETHER
            masterdf[metcolname] = masterdf[mbsumcols].sum(axis=1, min_count=len(mbsumcols))

        # RANK METRIC DATA COLUMN
        rankcolname = f'RANK_{metcolname} (w={metricweight})'
        subjectcolname = metcolname
        # SET METRIC COLUMN RANK DIRECTION
        if metricname.startswith('winrateranker'):
            if metricitem['rankmeth'] == 'standard':
                rankdirection = 1
            elif metricitem['rankmeth'] == 'minmax' or metricitem['rankmeth'] == 'minmax_nan':
                if metricitem['rankregime'] == '1isbest':
                    rankdirection = 0
                elif metricitem['rankregime'] == '0isbest':
                    rankdirection = 1
        else:
            rankdirection = metricitem['rankascending']
        if rankmeth == 'minmax':
            masterdf[rankcolname] = mmcalibrated(masterdf[subjectcolname].to_numpy(), rankdirection, rankregime)
        elif rankmeth == 'standard':
            masterdf[rankcolname] = masterdf[subjectcolname].rank(ascending=rankdirection)

        # GET EACH RANKCOLUMN'S WEIGHTED RANK VALUE
        wrankcolname = f'w_{rankcolname}'
        masterdf[wrankcolname] = (masterdf[rankcolname] * metricweight)

        # KEEP TRACK OF THE WEIGHTED RANK COLUMN TO SUM LATER
        sumcols.append(wrankcolname)

        # ADD WEIGHT TO WEIGHT TOTAL
        weight_total += metricweight

    # sum weighted rankcols
    masterwrankcolname = f'MASTER WEIGHTED RANK {weight_total}'
    masterdf[masterwrankcolname] = masterdf[sumcols].sum(axis=1, min_count=len(sumcols))
    # rank overall weighted rankcol
    if rankmeth == 'minmax':
        if rankregime == '1isbest':
            finalrankascend = 0
        elif rankregime == '0isbest':
            finalrankascend = 1
    elif rankmeth == 'standard':
        finalrankascend = 1
    finalrankcolname = f'MASTER FINAL RANK as of {end_date}'
    masterdf[finalrankcolname] = masterdf[masterwrankcolname].rank(ascending=finalrankascend)

    # RE-SORT AND RE-INDEX
    masterdf.sort_values(ascending=True, by=[finalrankcolname], inplace=True)
    masterdf.reset_index(drop=True, inplace=True)

    # ARCHIVE TO FILE
    filename = f"allmetricvals_ranks_as_of_{end_date}"
    if savemode == 'pkl':
        savetopkl(filename, allmetricsresults, masterdf)
    elif savemode == 'csv':
        masterdf.to_csv(index=False, path_or_buf=allmetricsresults / f"{filename}.csv")
    return masterdf
