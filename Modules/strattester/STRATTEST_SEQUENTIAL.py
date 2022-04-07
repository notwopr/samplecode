"""
Title: STRAT TESTER SEQUENTIAL PERIODS
Date Started: Sept 6, 2021
Version: 1
Version Start: Sept 6, 2021
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose:  test strategy over a consecutive set of time periods and return performance reports.
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
#   THIRD PARTY IMPORTS
import pandas as pd
#   LOCAL APPLICATION IMPORTS
from Modules.timeperiodbot import timeperiodbot
from Modules.tickerportalbot import tickerportal4
from file_functions import buildfolders_regime_testrun
from Modules.strattester.STRATTEST_SEQUENTIAL_BASE import getstratdfandpool
from Modules.strattester.STRATTEST_SEQUENTIAL_PERFORMANCE_TRACKER import gen_portfolio_perfprofile, get_portfolio_growthrate, get_growthrate_bench
from Modules.numbers import formalnumber
from file_functions import savetopkl
from computersettings import computerobject


# given dates, rank range, beginning capital, beginning benchcapital, returns endcapital benchendcapital, and periodsummary
def createperiodsummary(portfolio, testind, periodlen, numperiods, enterdate, exitdate, rankstart, rankend, startcapital, startcapital_bench, benchmark):
    # get various performance stats
    growthrate = get_portfolio_growthrate(enterdate, exitdate, portfolio)
    growthrate_bench = get_growthrate_bench(enterdate, exitdate, benchmark)
    growthrate_margin = growthrate - growthrate_bench
    abovezero = 1 if growthrate > 0 else 0
    abovezero_bench = 1 if growthrate_bench > 0 else 0
    abovezero_margin = abovezero - abovezero_bench
    abovebench = 1 if growthrate > growthrate_bench else 0
    abovebench_pos = 1 if (growthrate > growthrate_bench and growthrate > 0) else 0
    endcapital = startcapital * (1 + growthrate)
    endcapital_bench_hypo = startcapital * (1 + growthrate_bench)
    endcapital_bench = startcapital_bench * (1 + growthrate_bench)
    endcapital_margin = endcapital - endcapital_bench
    endcapital_margin_hypo = endcapital - endcapital_bench_hypo
    growth_capital = endcapital - startcapital
    growth_capital_bench = endcapital_bench - startcapital_bench
    growth_capital_bench_hypo = endcapital_bench_hypo - startcapital
    growth_capital_margin = growth_capital - growth_capital_bench
    growth_capital_margin_hypo = growth_capital - growth_capital_bench_hypo
    return endcapital, endcapital_bench, {
        'holdingperiod': testind + 1,
        'periodlength': periodlen,
        'enterdate': enterdate,
        'exitdate': exitdate,
        'portsize': len(portfolio),
        'rankbatch_start': rankstart,
        'rankbatch_end': rankend,
        'benchmark': benchmark,
        'startcapital': startcapital,
        'startcapital_bench': startcapital_bench,
        'startcapital_margin': startcapital - startcapital_bench,
        'growthrate': growthrate,
        'growthrate_bench': growthrate_bench,
        'growthrate_margin': growthrate_margin,
        'abovezero': abovezero,
        'abovezero_bench': abovezero_bench,
        'abovezero_margin': abovezero_margin,
        'abovebench': abovebench,
        'abovebench_pos': abovebench_pos,
        'endcapital': endcapital,
        'endcapital_bench': endcapital_bench,
        'endcapital_margin': endcapital_margin,
        'growth_capital': growth_capital,
        'growth_capital_bench': growth_capital_bench,
        'growth_capital_margin': growth_capital_margin,
        'endcapital_bench_hypo': endcapital_bench_hypo,
        'endcapital_margin_hypo': endcapital_margin_hypo,
        'growth_capital_bench_hypo': growth_capital_bench_hypo,
        'growth_capital_margin_hypo': growth_capital_margin_hypo,
    }, [
        f"Period: {testind + 1} of {numperiods} || {enterdate} to {exitdate} || Period Length: {periodlen} days",
        f"Portfolio growth: {formalnumber(growthrate*100)} % from ${formalnumber(startcapital)} to ${formalnumber(endcapital)} (${formalnumber(growth_capital)})",
        f"{benchmark} growth: {formalnumber(growthrate_bench*100)} % from ${formalnumber(startcapital)} to ${formalnumber(endcapital_bench_hypo)} (${formalnumber(growth_capital_bench_hypo)})",
        f"Marginal growth over {benchmark}: {formalnumber(growthrate_margin*100)} % (${formalnumber(growth_capital_margin_hypo)})"
    ]


# function to keep organized by centralizing all add extra stats to allperiodstatdf
def addextrastats(df):
    # add col for abovezerotallies
    df['abovezerotally'] = df['abovezero'].expanding(1).sum()
    df['abovezerotally_bench'] = df['abovezero_bench'].expanding(1).sum()
    df['abovezerotally_margin'] = df['abovezero_margin'].expanding(1).sum()
    df['abovebench_tally'] = df['abovebench'].expanding(1).sum()
    df['abovebench_pos_tally'] = df['abovebench_pos'].expanding(1).sum()
    return df


# get full stock ranking of given strat for one period
def getoneholdingperiod(setrunparent, exist_date, testnumber, bp):
    startpool = tickerportal4(exist_date, exist_date, 'common', bp['minimumage'])
    return getstratdfandpool(setrunparent, exist_date, bp['strat_panel'], startpool, bp['rankmeth'], bp['rankregime'], bp['chunksize'])


def run_strat_sequential(bp):
    # build folders
    testregimeparent, testrunparent = buildfolders_regime_testrun(bp['rootdir'], bp['testnumber'], bp['todaysdate'], bp['testregimename'])
    # get invest dates
    allinvestdates = timeperiodbot(f"{bp['investperiod']}D", bp['startdate'], bp['enddate'], 'all', '')
    # number of investment periods
    numperiods = len(allinvestdates)-1
    # set newcapital var
    endcapital = bp['startcapital']
    endcapital_bench = bp['startcapital']
    # get all period summaries and analysis
    allperiodstats = []
    stockperfdfreports = {}
    # for each investdate, get full stock rankings
    for testind in range(numperiods):
        # get full stock ranking
        fullstockranking = getoneholdingperiod(testrunparent, allinvestdates[testind], testind, bp)
        # get rank batch
        portfolio = fullstockranking[bp['rankstart']:bp['rankend']]
        # set dates
        enterdate = allinvestdates[testind]
        exitdate = allinvestdates[testind+1]
        # get df of performance broken down by stock
        individstockperfdf = gen_portfolio_perfprofile(portfolio, endcapital, enterdate, exitdate)
        # get summary of performance over period
        endcapital, endcapital_bench, period_stats, period_report = createperiodsummary(portfolio, testind, bp['investperiod'], numperiods, enterdate, exitdate, bp['rankstart'], bp['rankend'], endcapital, endcapital_bench, bp['benchmark'])
        allperiodstats.append(period_stats)
        stockperfdfreports.update({testind+1: {'stockperfdf': individstockperfdf, 'report': period_report}})
    allperiodstatdf = pd.DataFrame(data=allperiodstats)
    # add extra stats to allperiodstatdf
    allperiodstatdf = addextrastats(allperiodstatdf)
    # save to file
    savetopkl(f'strattester_allperiodstatdf_{bp["todaysdate"]+bp["testnumber"]}', computerobject.strattester_allperiodstatdf, allperiodstatdf)
    savetopkl(f'strattester_stockperfreports_{bp["todaysdate"]+bp["testnumber"]}', computerobject.strattester_stockperfreports, stockperfdfreports)
    return endcapital, endcapital_bench, allperiodstatdf, numperiods, stockperfdfreports
