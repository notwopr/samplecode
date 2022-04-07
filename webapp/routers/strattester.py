"""
Title: Strat Tester
Date Started: Feb 15, 2022
Version: 1.00
Version Start: Feb 15, 2022
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose:  .
    '''

    '''
            '''
            '''
"""
# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import os
import datetime as dt
import time
import copy
#   THIRD PARTY IMPORTS
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dashappobject import app
import plotly.express as px
import pandas as pd
#   LOCAL APPLICATION IMPORTS
from Modules.dates import num_days_string, plusminusdays
from ..botclasses import BotParams
from ..os_functions import get_currentscript_filename
from ..dashinputs import gen_tablecontents, prompt_builder, dash_inputbuilder
from ..botrun_parambuilder import brpb_base
from .strattester_helper_stratpanels import stratlib
from .strattester_helper_leaderboard import savetestrun, gen_leaderboard
from .strattester_helper_finalreport import strattest_sequential_final_report
from .strattester_helper_periodreports import gen_periodreports
from Modules.strattester.STRATTEST_SEQUENTIAL import run_strat_sequential
from ..common_resources import staticmindate, staticmaxdate
from file_functions import delete_folder, getbotsinglerunfolder, readpkl, getobject_byvarname
from ..datatables import sort_datatable
from Modules.timeperiodbot import random_dates
from Modules.ranking_functions import gen_ranking
from Modules.tickerportalbot import tickerportal2
from webapp.routers.strattester_helper_leaderboard_colconfig import nonrankcols, colconfig_1
from webapp.ranking_helper import gen_rankconfig_htmlchildren
from formatting import format_tabs
from computersettings import computerobject


bp = BotParams(
    get_currentscript_filename(__file__),
    'Strategy Tester',
    "Given a stock screening strategy, report how your portfolio would perform if you use the strategy for a given date range.",
    None
)

tbodydata = [
    {
        'id': f'strat_{bp.botid}',
        'prompt': 'Select a Strategy to Test.',
        'inputtype': 'dropdown',
        'options': [{'label': k, 'value': k} for k in stratlib.keys()],
        'placeholder': 'Choose a Strat',
        'multi': False,
        'searchable': False,
        'clearable': True
        },
    {
        'id': f'investperiod_{bp.botid}',
        'prompt': 'Set the investment period.',
        'details': 'This is the period for which you would hold a portfolio before running the strategy again and adjusting your holdings based on the strategy recommendations for the next period.',
        'placeholdertext': '# of days',
        'inputtype': 'number',
        'min': 1,
        'step': 1
        },
    {
        'id': f'num_periods_{bp.botid}',
        'prompt': 'Enter the number of periods you wish to run this strategy.',
        'placeholdertext': 'Enter an integer',
        'inputtype': 'number',
        'min': 1,
        'step': 1
        },
    {
        'id': f'datepicker_single_{bp.botid}',
        'prompt': 'Choose a start date.',
        'inputtype': 'datepicker_single',
        'clearable': True,
        'date': staticmindate,
        'min_date_allowed': staticmindate,
        'max_date_allowed': staticmaxdate
        },
    {
        'id': f'randomize_{bp.botid}',
        'prompt': 'Randomize date instead?',
        'buttontext': 'Randomize date',
        'inputtype': 'button_submit'
        },
    {
        'id': f'min_age_{bp.botid}',
        'prompt': 'Set the minimum age (in days) a stock must be to invest in it. Must be 3 or higher.',
        'placeholdertext': 'Enter an integer',
        'inputtype': 'number',
        'min': 3,
        'step': 1
        },
    {
        'id': f'benchmark_{bp.botid}',
        'prompt': 'Choose an available benchmark ticker (availability determined by start date chosen).',
        'inputtype': 'dropdown',
        'placeholder': 'Select or Type a Ticker',
        'options': [],
        'searchable': True,
        'clearable': True
        },
    {
        'id': f'startcapital_{bp.botid}',
        'prompt': 'Enter starting capital.',
        'placeholdertext': '$',
        'inputtype': 'number',
        'min': 1
        },
    {
        'id': f'rankstart_{bp.botid}',
        'prompt': 'Set rank lower bound for group of stocks strategy must invest in from each period ranking. Example, rankstart 0 to rankend 10 means the strategy will pick the top 10 stocks from each period ranking.',
        'details': 'Each period the strategy is run, the strategy ranks the stocks.  To determine which stocks will be chosen to invest in that period, setting ranking ranges tells the strategy what stocks from the rankings will be invested.  If you set rankstart as 0 and rankend as 10, it will choose the top 10 stocks (0 thru 9) for each period.',
        'placeholdertext': 'Enter an integer',
        'inputtype': 'number',
        'min': 0,
        'step': 1
        },
    {
        'id': f'rankend_{bp.botid}',
        'prompt': 'Set rank upper bound. This is not inclusive. For example, rankstart 0 to rankend 7 means the strategy will pick the top 7 stocks (ranked 0, 1, 2, 3, 4, 5, and 6, but not 7).',
        'details': 'Each period the strategy is run, the strategy ranks the stocks.  To determine which stocks will be chosen to invest in that period, setting ranking ranges tells the strategy what stocks from the rankings will be invested.  If you set rankstart as 0 and rankend as 10, it will choose the top 10 stocks (0 thru 9) for each period.',
        'placeholdertext': 'Enter an integer',
        'inputtype': 'number',
        'min': 0,
        'step': 1
        }

]

layout = html.Div([
    html.Div([
        html.Table(gen_tablecontents(tbodydata), style={'width': '100%'}),
        prompt_builder({
            'id': f'submitbutton_{bp.botid}',
            'inputtype': 'button_submit',
            })
    ], id=f'input_{bp.botid}'),
    html.Div(id=f'preview_{bp.botid}'),
    html.Div(id=f'output_{bp.botid}'),
    dcc.Tabs([
        dcc.Tab(label='Performance Summary', id=f'finalreport_{bp.botid}', className=format_tabs),
        dcc.Tab(label='Performance by Period', id=f'periodreports_{bp.botid}', className=format_tabs),
        dcc.Tab(label='Visuals', children=[
            html.Div([
                dcc.Graph(id=f"overallstats_{bp.botid}"),
                dash_inputbuilder({
                    'id': f'hovermode_{bp.botid}',
                    'prompt': 'Choose how you want to display data when you hover over the graph.',
                    'inputtype': 'radio',
                    'options': [{'label': x, 'value': x} for x in ['x', 'x unified', 'closest']],
                    'value': 'closest',
                    'inline': 'inline'
                    })
            ], id=f'displayresult_{bp.botid}', hidden='hidden')], className=format_tabs),
        dcc.Tab(label='Leaderboard', id=f'leadertab_{bp.botid}', children=[
            gen_rankconfig_htmlchildren(3, bp.botid),
            dash_inputbuilder({
                'id': f'rankbutton_{bp.botid}',
                'buttontext': 'Rank',
                'inputtype': 'button_submit'
                }),
            html.Div('If you would like to see a detailed summary of a test run, click on the testnumber of the desired test run to load the summary in the other tabs above.'),
            html.Span('Test run selected: '), html.Span(id=f"activecell_{bp.botid}"),
            dash_inputbuilder({
                'inputtype': 'table',
                'id': f"leaderboardtable_{bp.botid}",
                'filtering': 'native'
                })
            ], className=format_tabs)
            ]),
    html.Div(dash_inputbuilder({
        'inputtype': 'table',
        'id': f"sourcetable_{bp.botid}"
        }), hidden='hidden'),
    html.Div(dash_inputbuilder({
        'inputtype': 'table',
        'id': f"leaderboardtable_hidden_{bp.botid}"
        }), hidden='hidden')

], className='w-auto')


# get max investment period size given date and num periods chosen
def get_maxinvestperiod(num_periods, start_date):
    if num_periods and start_date:
        maxip = num_days_string(start_date, staticmaxdate) // num_periods
        maxip_prompt = f'Choose the duration of an investment period (in days).  The maximum allowed duration of an investment period based on the number of periods and starting date chosen is {maxip} day(s).'
    else:
        maxip = None
        maxip_prompt = 'Choose the duration of an investment period (in days).'
    return maxip, maxip_prompt


# get maxnum of periods and prompt
def get_maxnumpp(period, start_date):
    if period and start_date:
        maxnum = num_days_string(start_date, staticmaxdate) // period
        num_period_prompt = f'Enter the number of periods you wish to run this strategy. Max number of periods allowed based on the investment period and starting date currently set is {maxnum}.'
    else:
        maxnum = None
        num_period_prompt = 'Enter the number of periods you wish to run this strategy.'
    return maxnum, num_period_prompt


# get maxdate
def get_maxdatep(period, num_periods):
    if period and num_periods:
        newmaxdate = plusminusdays(staticmaxdate, (period * num_periods), 'subtract')
        maxdate_prompt = f'Choose a start date. Latest start date allowed based on the size of the investment period and number of periods chosen is {newmaxdate}.'
    else:
        newmaxdate = staticmaxdate
        maxdate_prompt = 'Choose a start date.'
    return newmaxdate, maxdate_prompt


# update contraints on date, num_period, and investment period inputs
@app.callback(
    Output(f'num_periods_{bp.botid}', "max"),
    Output(f'prompt_num_periods_{bp.botid}', "children"),
    Output(f'datepicker_single_{bp.botid}', "max_date_allowed"),
    Output(f'prompt_datepicker_single_{bp.botid}', "children"),
    Output(f'investperiod_{bp.botid}', "max"),
    Output(f'prompt_investperiod_{bp.botid}', "children"),
    Input(f'investperiod_{bp.botid}', "value"),
    Input(f'num_periods_{bp.botid}', "value"),
    Input(f'datepicker_single_{bp.botid}', "min_date_allowed"),
    Input(f'datepicker_single_{bp.botid}', "date")
    )
def update_inputconstraints(period, num_periods, mindate, start_date):
    # get max number of periods allowed
    maxnum, num_period_prompt = get_maxnumpp(period, start_date)
    # get max start date
    newmaxdate, maxdate_prompt = get_maxdatep(period, num_periods)
    # get max investment period
    maxip, maxip_prompt = get_maxinvestperiod(num_periods, start_date)
    return maxnum, num_period_prompt, newmaxdate, maxdate_prompt, maxip, maxip_prompt


def calc_currenddate(p, n, s):
    return dt.date.fromisoformat(s) + dt.timedelta(days=p*n)


# get random start date
@app.callback(
    Output(f'datepicker_single_{bp.botid}', "date"),
    Input(f'randomize_{bp.botid}', "n_clicks"),
    State(f'investperiod_{bp.botid}', "value"),
    State(f'num_periods_{bp.botid}', "value"),
    prevent_initial_call=True
    )
def randomize_date(n_clicks, period, num_periods):
    if period and num_periods:
        newmaxdate = plusminusdays(staticmaxdate, (period * num_periods), 'subtract')
    else:
        newmaxdate = staticmaxdate
    return random_dates(staticmindate, newmaxdate, 1)[0]


# get benchmark list
@app.callback(
    Output(f'benchmark_{bp.botid}', "options"),
    Input(f'datepicker_single_{bp.botid}', "date")
    )
def update_benchmarklist(date):
    if date:
        return sorted(tickerportal2(date, 'common+bench'))
    else:
        return []


@app.callback(
    Output(f'preview_{bp.botid}', "children"),
    Input(f'strat_{bp.botid}', "value"),
    Input(f'investperiod_{bp.botid}', "value"),
    Input(f'num_periods_{bp.botid}', "value"),
    Input(f'datepicker_single_{bp.botid}', "date"),
    Input(f'min_age_{bp.botid}', "value"),
    Input(f'benchmark_{bp.botid}', "value"),
    Input(f'startcapital_{bp.botid}', "value"),
    Input(f'rankstart_{bp.botid}', "value"),
    Input(f'rankend_{bp.botid}', "value")
    )
def preview_inputs(strat, period, num_periods, start_date, min_age, benchmark, startcapital, rankstart, rankend):
    if all([period, num_periods, start_date]):
        end_date = str(calc_currenddate(period, num_periods, start_date))
    else:
        end_date = 'None'
    # summary
    setting_summary = [
        f'strategy: {strat}',
        f'Number of Periods: {num_periods}',
        f'period duration: {period} days',
        f'start_date: {start_date}',
        f'end_date: {end_date}',
        f'min_age: {min_age} days old',
        f'benchmark: {benchmark}',
        f'starting capital: $ {startcapital}',
        f'rankstart: {rankstart}',
        f'rankend: {rankend}'
        ]
    setting_summary = [html.P([html.Div([html.Span(i), html.Br()]) for i in setting_summary])]

    if all(i is not None for i in [strat, period, num_periods, start_date, min_age, benchmark, startcapital, rankstart, rankend]):
        setting_summary += [html.P(f"Given the settings you chose, the strategy {strat} will be run for {num_periods} consecutive periods of {period} days each starting on {start_date} and finishing on {end_date}.  At the beginning of each period, the chosen strategy will be run on the universe of stocks existing at that point in time.  The strategy will produce a ranking of stocks for that period.  Stocks ranked from {rankstart} to {rankend} for that period will comprise the portfolio to be invested for that period.  Then, at the end of the period, the portfolio positions are exited, and the process starts again for the next period.  The strategy's performance will be measured against the chosen benchmark {benchmark}.  Once all periods have been processed, an overall performance summary will be given.  The minimum age a stock must be for the strategy to invest in it is {min_age} days old.")]
    return setting_summary


@app.callback(
    Output(f'output_{bp.botid}', "children"),
    Output(f'finalreport_{bp.botid}', "children"),
    Output(f'periodreports_{bp.botid}', "children"),
    Output(f"sourcetable_{bp.botid}", "data"),
    Input(f'submitbutton_{bp.botid}', 'n_clicks'),
    State(f'strat_{bp.botid}', "value"),
    State(f'investperiod_{bp.botid}', "value"),
    State(f'num_periods_{bp.botid}', "value"),
    State(f'datepicker_single_{bp.botid}', "date"),
    State(f'min_age_{bp.botid}', "value"),
    State(f'benchmark_{bp.botid}', "value"),
    State(f'startcapital_{bp.botid}', "value"),
    State(f'rankstart_{bp.botid}', "value"),
    State(f'rankend_{bp.botid}', "value"),
    Input(f'activecell_{bp.botid}', "children")
    )
def run_strattester(n_clicks, strat, period, num_periods, start_date, min_age, benchmark, startcapital, rankstart, rankend, activecell):
    if all(i is not None for i in [strat, period, num_periods, start_date, min_age, benchmark, startcapital, rankstart, rankend]):
        brp = {**brpb_base(bp.botid, 1), **{
            'strat_name': strat,
            'investperiod': period,
            'startdate': start_date,
            'enddate': str(calc_currenddate(period, num_periods, start_date)),
            'minimumage': min_age,
            'startcapital': startcapital,
            'benchmark': benchmark,
            'rankstart': rankstart,
            'rankend': rankend,
            'rankmeth': 'standard',
            'rankregime': '1isbest'
        }}
        # retrieve panel data
        libsourcecopy = copy.deepcopy(stratlib[strat])
        metriclist = getobject_byvarname(libsourcecopy['stages']['Stage 3'][0], libsourcecopy['stages']['Stage 3'][1])
        libsourcecopy['stages']['Stage 3'] = metriclist
        brp['strat_panel'] = libsourcecopy
        start = time.time()
        endcapital, endcapital_bench, allperiodstatdf, numperiods, stockperfdfreports = run_strat_sequential(brp)
        periodreports = gen_periodreports(stockperfdfreports, bp.botid)
        end = time.time()
        testrundict = savetestrun(brp, allperiodstatdf, num_periods, end-start)
        finalreport = strattest_sequential_final_report(testrundict)
        finalreport = [html.P(i) for i in finalreport]
        reply = html.P('Test complete')
        # delete temp files and folder
        delete_folder(getbotsinglerunfolder(brp['rootdir'], brp['testregimename'], brp['todaysdate'], brp['testnumber']))
    elif activecell and os.path.exists(computerobject.strattester_allperiodstatdf / f'strattester_allperiodstatdf_{activecell}.pkl'):
        reply = html.P(f'Viewing archived test run {activecell}')
        testrundict = readpkl(f'strattester_testrun_{activecell}', computerobject.strattester_testruns)
        finalreport = strattest_sequential_final_report(testrundict)
        allperiodstatdf = readpkl(f'strattester_allperiodstatdf_{activecell}', computerobject.strattester_allperiodstatdf)
        stockperfdfreports = readpkl(f'strattester_stockperfreports_{activecell}', computerobject.strattester_stockperfreports)
        periodreports = gen_periodreports(stockperfdfreports, bp.botid)
    elif activecell:
        reply = html.P(f'Detailed report of archived test run {activecell} not available.')
        finalreport = None
        allperiodstatdf = pd.DataFrame(data=[{0: 0}])
        periodreports = None
    else:
        reply = html.P('Test was not run.')
        finalreport = None
        allperiodstatdf = pd.DataFrame(data=[{0: 0}])
        periodreports = None
    if finalreport:
        finalreport = [html.Br()]+[html.P(i) for i in finalreport]
    return reply, finalreport, periodreports, allperiodstatdf.to_dict('records')


# gen graph
# sourcetable is a hidden html DIV where orig allperiodstatdf is stored to be used by grapher
@app.callback(
    Output(f'overallstats_{bp.botid}', "figure"),
    Output(f'displayresult_{bp.botid}', "hidden"),
    Input(f"sourcetable_{bp.botid}", "data"),
    Input(f"hovermode_{bp.botid}", 'value')
    )
def sort_rawdatatable(sourcetable, hovermode):
    allperiodstatdf = pd.DataFrame.from_records(sourcetable)
    if len(allperiodstatdf.columns) > 1:
        fig = px.line(allperiodstatdf, x='holdingperiod', y=allperiodstatdf.columns[8:], markers=False)
        fig.update_layout(transition_duration=500, legend_title_text='Ticker', hovermode=hovermode, uirevision='some-constant')
        hidetoggle = None
    else:
        fig = px.line([0])
        hidetoggle = 'hidden'
    return fig, hidetoggle


def table_type(df_column):
    if isinstance(df_column.dtype, pd.DatetimeTZDtype):
        return 'datetime',
    elif (isinstance(df_column.dtype, pd.StringDtype) or
            isinstance(df_column.dtype, pd.BooleanDtype) or
            isinstance(df_column.dtype, pd.CategoricalDtype) or
            isinstance(df_column.dtype, pd.PeriodDtype)):
        return 'text'
    elif (isinstance(df_column.dtype, pd.SparseDtype) or
            isinstance(df_column.dtype, pd.IntervalDtype) or
            isinstance(df_column.dtype, pd.Int8Dtype) or
            isinstance(df_column.dtype, pd.Int16Dtype) or
            isinstance(df_column.dtype, pd.Int32Dtype) or
            isinstance(df_column.dtype, pd.Int64Dtype)):
        return 'numeric'
    else:
        return 'any'


# set rankcol config to use
colconfig = colconfig_1


# rank col options update
@app.callback(
    Output(f'rc0_{bp.botid}', 'options'),
    Output(f'rc1_{bp.botid}', 'options'),
    Output(f'rc2_{bp.botid}', 'options'),
    Input(f'rc0_{bp.botid}', 'value'),
    Input(f'rc1_{bp.botid}', 'value'),
    Input(f'rc2_{bp.botid}', 'value')
    )
def update_rcoptions(c, c1, c2):
    rankcolops0 = [i for i in colconfig if i not in nonrankcols+[c1, c2]]
    rankcolops1 = [i for i in colconfig if i not in nonrankcols+[c, c2]]
    rankcolops2 = [i for i in colconfig if i not in nonrankcols+[c, c1]]
    return rankcolops0, rankcolops1, rankcolops2


'''
# gen leaderboard
@app.callback(
    Output(f'leaderboardtable_hidden_{bp.botid}', 'data'),
    Input(f'rankbutton_{bp.botid}', 'n_clicks'),
    State(f'rc0_{bp.botid}', 'value'),
    State(f'rc0_weight_{bp.botid}', 'value'),
    State(f'rc0_direct_{bp.botid}', 'value'),
    State(f'rc1_{bp.botid}', 'value'),
    State(f'rc1_weight_{bp.botid}', 'value'),
    State(f'rc1_direct_{bp.botid}', 'value'),
    State(f'rc2_{bp.botid}', 'value'),
    State(f'rc2_weight_{bp.botid}', 'value'),
    State(f'rc2_direct_{bp.botid}', 'value')
    )
def gensort_leaderboard(n_clicks, c, w, d, c1, w1, d1, c2, w2, d2):
    df = gen_leaderboard(colconfig)
    grinputs = []
    for g in [[c, w, d], [c1, w1, d1], [c2, w2, d2]]:
        if all(i is not None for i in g):
            grinputs.append(g)
    if len(grinputs) > 0:
        df = gen_ranking(grinputs, df)
    return df.to_dict('records')


# sort and filter leaderboard
@app.callback(
    Output(f'leaderboardtable_{bp.botid}', 'data'),
    Output(f'leaderboardtable_{bp.botid}', 'columns'),
    Input(f'leaderboardtable_hidden_{bp.botid}', 'data'),
    Input(f'leaderboardtable_{bp.botid}', 'sort_by')
    )
def sortfilter_leaderboard(hiddenltable, sort_by):
    df = pd.DataFrame.from_records(hiddenltable)
    df = sort_datatable(sort_by, df)
    columns = [
        {'name': i, 'id': i, 'type': table_type(df[i])} for i in df.columns
    ]
    return df.to_dict('records'), columns
'''


# filter, rank, then sort leaderboard in that order
@app.callback(
    Output(f'leaderboardtable_{bp.botid}', 'data'),
    Output(f'leaderboardtable_{bp.botid}', 'columns'),
    Output(f'activecell_{bp.botid}', 'children'),
    Input(f'rankbutton_{bp.botid}', 'n_clicks'),
    State(f'rc0_{bp.botid}', 'value'),
    State(f'rc0_weight_{bp.botid}', 'value'),
    State(f'rc0_direct_{bp.botid}', 'value'),
    State(f'rc1_{bp.botid}', 'value'),
    State(f'rc1_weight_{bp.botid}', 'value'),
    State(f'rc1_direct_{bp.botid}', 'value'),
    State(f'rc2_{bp.botid}', 'value'),
    State(f'rc2_weight_{bp.botid}', 'value'),
    State(f'rc2_direct_{bp.botid}', 'value'),
    Input(f'leaderboardtable_{bp.botid}', 'data'),
    Input(f'leaderboardtable_{bp.botid}', 'sort_by'),
    Input(f'leaderboardtable_{bp.botid}', 'active_cell')
    )
def filterranksort_leaderboard(n_clicks, c, w, d, c1, w1, d1, c2, w2, d2, hiddenltable, sort_by, active_cell):
    df = gen_leaderboard(colconfig)

    grinputs = []
    for g in [[c, w, d], [c1, w1, d1], [c2, w2, d2]]:
        if all(i is not None for i in g):
            grinputs.append(g)
    if len(grinputs) > 0:
        df = gen_ranking(grinputs, df)
    df = sort_datatable(sort_by, df)
    activecellresp = f"{df.iloc[active_cell['row']]['todaysdate']}{df.iat[active_cell['row'], active_cell['column']]}" if active_cell and active_cell['column_id'] == 'testnumber' else None
    columns = [
        {'name': i, 'id': i, 'type': table_type(df[i]), 'hideable': True} for i in df.columns
    ]
    return df.to_dict('records'), columns, activecellresp
