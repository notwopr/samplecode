"""
Title: Strat Reporter
Date Started: Feb 23, 2022
Version: 1.00
Version Start: Feb 23, 2022
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose:  .

"""
# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import time
#   THIRD PARTY IMPORTS
from dash import html, callback_context
from dash.dependencies import Input, Output, State
from dashappobject import app
import pandas as pd
#   LOCAL APPLICATION IMPORTS
from ..botclasses import BotParams
from ..os_functions import get_currentscript_filename
from ..dashinputs import gen_tablecontents, prompt_builder, dash_inputbuilder
from ..botrun_parambuilder import brpb_base
from .strattester_helper_stratpanels import stratlib
from Modules.strattester.STRAT_REPORTER_BASE import getstratdfandpool
from file_functions import delete_folder, getbotsinglerunfolder
from ..datatables import sort_datatable
from ..common_resources import staticmindate, staticmaxdate
from Modules.timeperiodbot import random_dates


bp = BotParams(
    get_currentscript_filename(__file__),
    'Strategy Reporter',
    "Given a stock screening strategy and date, returns the resulting stock ranking as of that date based on that strategy.",
    None
)

tbodydata = [
    {
        'id': f'strat_{bp.botid}',
        'prompt': 'Select a Strategy to apply.',
        'inputtype': 'dropdown',
        'options': [{'label': k, 'value': k} for k in stratlib.keys()],
        'placeholder': 'Choose a Strat',
        'multi': False,
        'searchable': False,
        'clearable': True
        },
    {
        'id': f'datepicker_single_{bp.botid}',
        'prompt': 'Choose a current date.',
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
        'prompt': 'Set the minimum age (in days) a stock must be to invest in it. Must be 1 or higher.',
        'placeholdertext': 'Enter an integer',
        'inputtype': 'number',
        'min': 1,
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
    html.P(id=f'output_{bp.botid}'),
    dash_inputbuilder({
                'inputtype': 'table',
                'id': f"result_table_{bp.botid}"
                }),
    html.Div(dash_inputbuilder({
        'inputtype': 'table',
        'id': f"sourcetable_{bp.botid}"
        }), id=f"hidden_{bp.botid}", hidden='hidden')
])


# get random date
@app.callback(
    Output(f'datepicker_single_{bp.botid}', "date"),
    Input(f'randomize_{bp.botid}', "n_clicks"),
    prevent_initial_call=True
    )
def randomize_date(n_clicks):
    return random_dates(staticmindate, staticmaxdate, 1)[0]



@app.callback(
    Output(f'preview_{bp.botid}', "children"),
    Input(f'strat_{bp.botid}', "value"),
    Input(f'datepicker_single_{bp.botid}', "date"),
    Input(f'min_age_{bp.botid}', "value")
    )
def preview_inputs(strat, date, min_age):
    setting_summary = [
        f'strategy: {strat}',
        f'date: {date}',
        f'min_age: {min_age} days old'
        ]
    setting_summary = [html.P([html.Div([html.Span(i), html.Br()]) for i in setting_summary])]
    return setting_summary


@app.callback(
    Output(f'output_{bp.botid}', "children"),
    Output(f"result_table_{bp.botid}", "data"),
    Input(f'submitbutton_{bp.botid}', 'n_clicks'),
    State(f'strat_{bp.botid}', "value"),
    State(f'datepicker_single_{bp.botid}', "date"),
    State(f'min_age_{bp.botid}', "value"),
    Input(f'result_table_{bp.botid}', "data"),
    Input(f'result_table_{bp.botid}', 'sort_by'),
    Input(f'output_{bp.botid}', 'children')
    )
def run_stratreporter(n_clicks, strat, date, min_age, result_table, sort_by, reply):
    if result_table and callback_context.triggered[0]['prop_id'].endswith('sort_by'):
        df = pd.DataFrame.from_records(result_table)
        df = sort_datatable(sort_by, df)
        return reply, df.to_dict('records')
    elif all(i is not None for i in [strat, date, min_age]):
        brp = {**brpb_base(bp.botid, 1), **{
            'strat_name': strat,
            'strat_panel': stratlib[strat],
            'exist_date': date,
            'minimumage': min_age,
            'rankmeth': 'standard',
            'rankregime': '1isbest'
        }}
        start = time.time()
        df = getstratdfandpool(brp)
        end = time.time()
        # delete temp files and folder
        delete_folder(getbotsinglerunfolder(brp['rootdir'], brp['testregimename'], brp['todaysdate'], brp['testnumber']))
        return f'Run complete. Runtime: {end-start} secs', df.to_dict('records')
    else:
        return 'Test was not run.', None

'''
# gen rank table
@app.callback(
    Output(f'result_table_{bp.botid}', "data"),
    Input(f"sourcetable_{bp.botid}", "data"),
    Input(f'result_table_{bp.botid}', "data"),
    Input(f'chunkranktable_{bp.botid}', 'sort_by')
    )
def sort_rawdatatable(sourcetable, result_table, sort_by):
    if callback_context.triggered[0]['prop_id'].endswith('sort_by'):
        df = pd.DataFrame.from_records(result_table)
        df = sort_datatable(sort_by, df)
        return df.to_dict('records')
    elif sourcetable:
        df = pd.DataFrame.from_records(sourcetable)
        return df.to_dict('records')
    else:
        return None
'''
