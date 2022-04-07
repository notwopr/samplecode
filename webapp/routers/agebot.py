"""
Title: Age Bot Endpoint
Date Started: Jan 27, 2022
Version: 1.01
Version Start: Feb 7, 2022
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose:  To provide API endpoint for Age bot.
Version 1.01: Convert to Dash.
"""
# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
#   THIRD PARTY IMPORTS
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State
from dashappobject import app
import pandas as pd
#   LOCAL APPLICATION IMPORTS
from ..dashinputs import prompt_builder, gen_tablecontents, dash_inputbuilder
from ..common_resources import allavailabledates, staticmindate, staticmaxdate
from ..botrun_parambuilder import brpb_base
from file_functions import delete_folder, getbotsinglerunfolder
from ..botclasses import BotParams
from Modules.bots.agebot.AGEBOT_BASE import agebotmaster
from ..os_functions import get_currentscript_filename
from ..datatables import sort_datatable
from Modules.dates import plusminusdays
from Modules.timeperiodbot import random_dates
from formatting import format_tabs


bp = BotParams(
    get_currentscript_filename(__file__),
    'Age Bot',
    "The Age Bot returns age stats on stocks based on the user's chosen growth requirements.  The ticker symbols considered are all United States NASDAQ and NYSE common stock.",
    agebotmaster
)
tbodydata = [
    {
        'id': f'num_trials_{bp.botid}',
        'placeholdertext': '# of trials',
        'prompt': 'How many trials do you want to run?',
        'inputtype': 'number',
        'min': 1,
        'max': 100,
        'step': 1
        },
    {
        'placeholdertext': 'trial length',
        'id': f'testlen_{bp.botid}',
        'prompt': 'The size of the date range over which each trial is considered (in days).',
        'inputtype': 'number',
        'min': 1,
        'max': 10*365,
        'step': 1
        },
    {
        'placeholdertext': 'Optional',
        'id': f'rank_beg_{bp.botid}',
        'prompt': 'Rank batch start bound:',
        'inputtype': 'number',
        'min': 0,
        'max': 1000,
        'step': 1
        },
    {
        'placeholdertext': 'Optional',
        'id': f'rank_end_{bp.botid}',
        'prompt': 'Rank batch end bound:',
        'inputtype': 'number',
        'min': 0,
        'max': 1000,
        'step': 1
        },
    {
        'id': f'daterange_{bp.botid}',
        'prompt': 'Specify a date range from which the bot will choose random trials.',
        'inputtype': 'datepicker_range',
        'clearable': True,
        'min_date_allowed': staticmindate,
        'max_date_allowed': staticmaxdate
        },
    {
        'id': f'randomize_{bp.botid}',
        'prompt': 'Randomize dates instead?',
        'buttontext': 'Randomize dates',
        'inputtype': 'button_submit'
        },
    {
        'id': f'datepicker_{bp.botid}',
        'prompt': 'Alternatively, you can hand pick the trial dates yourself  The number of dates you select must equal the number of trials you set above.',
        'inputtype': 'dropdown',
        'options': allavailabledates,
        'value': [],
        'clearable': True,
        'searchable': True,
        'multi': True
        },
    {
        'id': f'gr_upper_{bp.botid}',
        'prompt': 'Set upper bound growth rate (1.00 = 100%).',
        'placeholdertext': 'Optional',
        'inputtype': 'number'
        },
    {
        'id': f'gr_upper_filter_{bp.botid}',
        'prompt': 'Keep stocks that are __ the upper bound growth rate.',
        'options': ['<', '<='],
        'inputtype': 'dropdown',
        'clearable': True
        },
    {
        'id': f'gr_lower_{bp.botid}',
        'prompt': 'Set lower bound growth rate (1.00 = 100%).',
        'placeholdertext': 'Optional',
        'inputtype': 'number'
        },
    {
        'id': f'gr_lower_filter_{bp.botid}',
        'prompt': 'Keep stocks that are __ the lower bound growth rate.',
        'options': ['>', '>='],
        'inputtype': 'dropdown',
        'clearable': True
        }
]

layout = html.Div([
    html.Div([
        html.Table(gen_tablecontents(tbodydata)),
        prompt_builder({
            'id': f'submitbutton_{bp.botid}',
            'inputtype': 'button_submit'
            })
        ], id=f'input_{bp.botid}'),
    dcc.Tabs([
        dcc.Tab(label='Overall Stats', children=[
            dash_inputbuilder({
                'inputtype': 'table',
                'id': f"agestats_{bp.botid}"
                })], className=format_tabs
                ),
        dcc.Tab(label='Stats by Trial', children=[
            dash_inputbuilder({
                'inputtype': 'table',
                'id': f"trialstats_{bp.botid}"
                })], className=format_tabs
                )
    ]),
    html.Div(id=f'output_{bp.botid}')
])


# get random dates
@app.callback(
    Output(f'daterange_{bp.botid}', "start_date"),
    Output(f'daterange_{bp.botid}', "end_date"),
    Input(f'randomize_{bp.botid}', "n_clicks"),
    prevent_initial_call=True
    )
def randomize_date(n_clicks):
    new_start = random_dates(staticmindate, staticmaxdate, 1)[0]
    new_end = random_dates(plusminusdays(new_start, 1, 'add'), staticmaxdate, 1)[0]
    return new_start, new_end


@app.callback(
    Output(f'agestats_{bp.botid}', 'data'),
    Output(f'trialstats_{bp.botid}', 'data'),
    Input(f'submitbutton_{bp.botid}', 'n_clicks'),
    State(f'num_trials_{bp.botid}', "value"),
    State(f'testlen_{bp.botid}', "value"),
    State(f'daterange_{bp.botid}', "start_date"),
    State(f'daterange_{bp.botid}', "end_date"),
    State(f'datepicker_{bp.botid}', "value"),
    State(f'rank_beg_{bp.botid}', "value"),
    State(f'rank_end_{bp.botid}', "value"),
    State(f'gr_upper_{bp.botid}', "value"),
    State(f'gr_upper_filter_{bp.botid}', "value"),
    State(f'gr_lower_{bp.botid}', "value"),
    State(f'gr_lower_filter_{bp.botid}', "value"),
    Input(f"agestats_{bp.botid}", 'sort_by'),
    Input(f"trialstats_{bp.botid}", 'sort_by'),
    Input(f"agestats_{bp.botid}", 'data'),
    Input(f"trialstats_{bp.botid}", 'data'),
    prevent_initial_call=True
    )
def calc_agebot(
        n_clicks,
        num_trials,
        testlen,
        beg_date,
        end_date,
        manualselectdates,
        rank_beg,
        rank_end,
        gr_upper,
        gr_upper_dir,
        gr_lower,
        gr_lower_dir,
        agestat_sort,
        trialstat_sort,
        agestat_data,
        trialstat_data
        ):
    if agestat_data and trialstat_data and callback_context.triggered[0]['prop_id'].endswith('sort_by'):
        # convert table back to dataframe
        statdf = pd.DataFrame.from_records(agestat_data)
        statdf = sort_datatable(agestat_sort, statdf)
        alltrialsummariesdf = pd.DataFrame.from_records(trialstat_data)
        alltrialsummariesdf = sort_datatable(trialstat_sort, alltrialsummariesdf)
        return statdf.to_dict('records'), alltrialsummariesdf.to_dict('records')
    else:
        # form bot run-specific parameters ('brp').
        brp = {**brpb_base(bp.botid, 1), **{
            'num_trials': num_trials,
            'testlen': testlen,
            'firstdate': beg_date,
            'latestdate': end_date,
            'statictrialexistdates': manualselectdates,
            'rank_beg': rank_beg,
            'rank_end': rank_end,
            'gr_u': gr_upper,
            'gr_l': gr_lower,
            'dir_u': gr_upper_dir,
            'dir_l': gr_lower_dir
            }}
        # create table
        statdf, alltrialsummariesdf = bp.botfunc(brp)
        # delete temp files and folder
        delete_folder(getbotsinglerunfolder(brp['rootdir'], brp['testregimename'], brp['todaysdate'], brp['testnumber']))
        return statdf.to_dict('records'), alltrialsummariesdf.to_dict('records')
