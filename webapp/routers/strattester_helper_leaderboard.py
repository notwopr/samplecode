import pandas as pd
from file_functions import readpkl_fullpath, savetopkl
from Modules.dict_functions import gen_dict_from_listofdicts
from computersettings import computerobject
from Modules.numbers_formulas import geometric_rate


# returns  key:val pair of a particular setting to a metric in a given strat panel
def metricsettingfinder(testrundict, paramstage, metricsettingname):
    if testrundict['strat_panel']['stages'].get(paramstage):
        stratmetricparams = testrundict['strat_panel']['stages'][paramstage]['scriptparams']
        i = 0
        while not stratmetricparams[i].get(metricsettingname) and i < len(stratmetricparams)-1:
            i += 1
        if stratmetricparams[i].get(metricsettingname):
            testrundict.update({metricsettingname: stratmetricparams[i].get(metricsettingname)})
    return testrundict


def periodtodailystat(j, s, p, mode):
    s = s.apply(lambda x: geometric_rate(x, p)) if j == 'daily' else s
    if mode == 'min':
        return s.min()
    if mode == 'mean':
        return s.mean()
    if mode == 'median':
        return s.median()
    if mode == 'max':
        return s.max()
    if mode == 'std':
        return s.std()
    if mode == 'mad':
        return s.mad()


def savetestrun(bp, allperiodstatdf, num_periods, runtime):
    endcapital = allperiodstatdf['endcapital'].iloc[-1]
    endcapital_bench = allperiodstatdf['endcapital_bench'].iloc[-1]
    startcapital = bp['startcapital']
    growthrate_overall = (endcapital / startcapital) - 1
    growthrate_bench_overall = (endcapital_bench / startcapital) - 1
    growthrate_margin_overall = growthrate_overall - growthrate_bench_overall
    growth_capital_overall = endcapital - startcapital
    growth_capital_bench_overall = endcapital_bench - startcapital
    endcapital_margin_overall = endcapital - endcapital_bench
    effective_period_growthrate = ((endcapital/startcapital) ** (1/num_periods))-1
    effective_period_growthrate_bench = ((endcapital_bench/startcapital) ** (1/num_periods))-1
    effective_daily_growthrate = ((1 + effective_period_growthrate) ** (1/bp['investperiod'])) - 1
    effective_daily_growthrate_bench = ((1 + effective_period_growthrate_bench) ** (1/bp['investperiod'])) - 1
    testrundict = {**bp, **{
        'num_periods': num_periods,
        'runtime': runtime,
        'runtimeperperiod': runtime/num_periods,
        'portsize': allperiodstatdf['portsize'].mean(),
        'endcapital': endcapital,
        'endcapital_bench': endcapital_bench,
        'growthrate_overall': growthrate_overall,
        'growthrate_bench_overall': growthrate_bench_overall,
        'growthrate_margin_overall': growthrate_margin_overall,
        'growth_capital_overall': growth_capital_overall,
        'growth_capital_bench_overall': growth_capital_bench_overall,
        'endcapital_margin_overall': endcapital_margin_overall,
        'effective_period_growthrate': effective_period_growthrate,
        'effective_period_growthrate_bench': effective_period_growthrate_bench,
        'effective_period_growthrate_margin': effective_period_growthrate - effective_period_growthrate_bench,
        'effective_daily_growthrate': effective_daily_growthrate,
        'effective_daily_growthrate_bench': effective_daily_growthrate_bench,
        'effective_daily_growthrate_margin': effective_daily_growthrate - effective_daily_growthrate_bench
    }}
    growthratestats = [{
        f'{j}_{i}_min': periodtodailystat(j, allperiodstatdf[i], bp['investperiod'], 'min'),
        f'{j}_{i}_mean': periodtodailystat(j, allperiodstatdf[i], bp['investperiod'], 'mean'),
        f'{j}_{i}_median': periodtodailystat(j, allperiodstatdf[i], bp['investperiod'], 'median'),
        f'{j}_{i}_max': periodtodailystat(j, allperiodstatdf[i], bp['investperiod'], 'max'),
        f'{j}_{i}_std': periodtodailystat(j, allperiodstatdf[i], bp['investperiod'], 'std'),
        f'{j}_{i}_mad': periodtodailystat(j, allperiodstatdf[i], bp['investperiod'], 'mad')
    } for i in ['growthrate', 'growthrate_bench', 'growthrate_margin'] for j in ['daily', 'period']]
    abovezerostats = [{
        i: allperiodstatdf[i].iloc[-1],
        f'{i}_pct': allperiodstatdf[i].iloc[-1] / num_periods
    } for i in ['abovezerotally', 'abovezerotally_bench', 'abovezerotally_margin', 'abovebench_tally', 'abovebench_pos_tally']]
    testrundict = gen_dict_from_listofdicts([testrundict]+growthratestats+abovezerostats)
    testrundict.update({
        'margin_daily_growthrate_min': testrundict['daily_growthrate_min'] - testrundict['daily_growthrate_bench_min'],
        'margin_daily_growthrate_std': testrundict['daily_growthrate_std'] - testrundict['daily_growthrate_bench_std'],
        'margin_daily_growthrate_mad': testrundict['daily_growthrate_mad'] - testrundict['daily_growthrate_bench_mad']
    })
    del testrundict['rootdir']
    # add more strat settings to profile for leaderboard purposes
    testrundict = metricsettingfinder(testrundict, 'Stage 3', 'min_preath_age')
    savetopkl(f'strattester_testrun_{bp["todaysdate"]+bp["testnumber"]}', computerobject.strattester_testruns, testrundict)
    return testrundict


def gen_leaderboard(colconfig):
    leaderdf = pd.DataFrame(data=[readpkl_fullpath(child) for child in computerobject.strattester_testruns.iterdir()])
    return leaderdf[colconfig]
