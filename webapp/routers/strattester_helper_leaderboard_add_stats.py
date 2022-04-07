'''
Purpose:  I forgot to add daily growth rate states to the testrunstats. so I created this to add them retroactively to existing statdict files.
'''
from file_functions import readpkl_fullpath, savetopkl
from Modules.numbers_formulas import geometric_rate, effective_rate
from computersettings import computerobject
from webapp.routers.strattester_helper_leaderboard import metricsettingfinder


def checkcalc(filename, testrundict):
    for k in ['effective_period_growthrate', 'effective_period_growthrate_bench']:
        print(f'{k}: {testrundict[k]} || estimated daily rate {geometric_rate(testrundict[k], testrundict["investperiod"])} || estimated orig rate: {effective_rate(geometric_rate(testrundict[k], testrundict["investperiod"]), testrundict["investperiod"])} || {testrundict[k] == effective_rate(geometric_rate(testrundict[k], testrundict["investperiod"]), testrundict["investperiod"])}')


def testrundict_addstats(filename, testrundict):
    testrundict = metricsettingfinder(testrundict, 'Stage 3', 'min_preath_age')
    '''
    margin_daily_growthrate_std = testrundict['daily_growthrate_std'] - testrundict['daily_growthrate_bench_std']
    margin_daily_growthrate_mad = testrundict['daily_growthrate_mad'] - testrundict['daily_growthrate_bench_mad']
    #margin_daily_growthrate_min = testrundict['daily_growthrate_min'] - testrundict['daily_growthrate_bench_min']
    #effective_daily_growthrate = geometric_rate(testrundict['effective_period_growthrate'], testrundict['investperiod'])
    #effective_daily_growthrate_bench = geometric_rate(testrundict['effective_period_growthrate_bench'], testrundict['investperiod'])
    testrundict.update(
        {
            'margin_daily_growthrate_std': margin_daily_growthrate_std,
            'margin_daily_growthrate_mad': margin_daily_growthrate_mad
        }
    )
    '''
    savetopkl(filename, computerobject.strattester_testruns, testrundict)


def addstats_allfiles():
    for child in computerobject.strattester_testruns.iterdir():
        testrundict_addstats(child.stem, readpkl_fullpath(child))
