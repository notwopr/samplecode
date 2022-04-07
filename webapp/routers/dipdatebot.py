"""
Title: Dip Date Bot Endpoint
Date Started: Jan 31, 2022
Version: 1.00
Version Start: Jan 31, 2022
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose:  .

"""
# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
#   THIRD PARTY IMPORTS
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State
from dashappobject import app
import plotly.express as px
import pandas as pd
#   LOCAL APPLICATION IMPORTS
from ..botclasses import BotParams
from Modules.referencetools.dipdatevisualizer.DIPDATEVISUALIZER import dipdatevisualizer_dash
from Modules.price_history import grabsinglehistory
from ..os_functions import get_currentscript_filename
from ..common_resources import tickers
from ..dashinputs import prompt_builder, gen_tablecontents, dash_inputbuilder
from ..datatables import sort_datatable
from Modules.dates import plusminusdays
from Modules.timeperiodbot import random_dates


bp = BotParams(
    get_currentscript_filename(__file__),
    'Dip Date Bot',
    "The Dip Date Bot takes a ticker symbol and date range and returns info on the largest drop in price during that span of time, including the exact dates of the fall, and the price change.",
    dipdatevisualizer_dash
)

tbodydata = [
    {
        'id': f'ticker_{bp.botid}',
        'prompt': 'Choose a single ticker.',
        'inputtype': 'dropdown',
        'options': tickers,
        'placeholder': 'Select or Type a Ticker',
        'searchable': True,
        'clearable': True
        },
    {
        'id': f'datepicker_{bp.botid}',
        'prompt': 'Select a date range.',
        'inputtype': 'datepicker_range',
        'clearable': True
        },
    {
        'id': f'randomize_{bp.botid}',
        'prompt': 'Randomize dates instead?',
        'buttontext': 'Randomize dates',
        'inputtype': 'button_submit'
        },
    {
        'id': f'hovermode_{bp.botid}',
        'prompt': 'Choose how you want to display data when you hover over the graph.',
        'inputtype': 'radio',
        'options': [{'label': x, 'value': x} for x in ['x', 'x unified', 'closest']],
        'value': 'closest',
        'inline': 'inline'
        }
]
layout = html.Div([
    html.Div([
        html.Table(gen_tablecontents(tbodydata)),
        prompt_builder({
            'id': f'submitbutton_{bp.botid}',
            'inputtype': 'button_submit',
            })
    ], id=f'input_{bp.botid}'),
    html.Div(id=f'output_{bp.botid}'),
    dash_inputbuilder({
        'inputtype': 'table',
        'id': f"timetable_{bp.botid}"
        })
])


# update min and max dates and randomize dates if requested
@app.callback(
    Output(f'datepicker_{bp.botid}', "min_date_allowed"),
    Output(f'datepicker_{bp.botid}', "max_date_allowed"),
    Output(f'datepicker_{bp.botid}', "start_date"),
    Output(f'datepicker_{bp.botid}', "end_date"),
    Input(f'ticker_{bp.botid}', "value"),
    Input(f'randomize_{bp.botid}', "n_clicks"),
    State(f'datepicker_{bp.botid}', "min_date_allowed"),
    State(f'datepicker_{bp.botid}', "max_date_allowed"))
def get_minmaxdates(ticker, n_clicks, min_date, max_date):
    if ticker:
        df = grabsinglehistory(ticker)
        min_date_allowed = df['date'].min()
        max_date_allowed = df['date'].max()
        if min_date and max_date:
            new_start = random_dates(min_date, max_date, 1)[0]
            new_end = random_dates(plusminusdays(new_start, 1, 'add'), max_date, 1)[0]
        else:
            new_start = None
            new_end = None
        return min_date_allowed, max_date_allowed, new_start, new_end
    else:
        min_date_allowed = None
        max_date_allowed = None
        new_start = None
        new_end = None
    return min_date_allowed, max_date_allowed, new_start, new_end


@app.callback(
    Output(f'output_{bp.botid}', 'children'),
    Output(f'timetable_{bp.botid}', 'data'),
    Input(f'submitbutton_{bp.botid}', 'n_clicks'),
    State(f'ticker_{bp.botid}', "value"),
    State(f'datepicker_{bp.botid}', 'start_date'),
    State(f'datepicker_{bp.botid}', 'end_date'),
    Input(f"hovermode_{bp.botid}", 'value'),
    Input(f"timetable_{bp.botid}", 'sort_by'),
    Input(f"timetable_{bp.botid}", "data"),
    Input(f'output_{bp.botid}', 'children')
    )
def get_dipdates(n_clicks, ticker, start_date, end_date, hovermode, sort_by, timetable, children):
    if timetable and callback_context.triggered[0]['prop_id'].endswith('sort_by'):
        df = pd.DataFrame.from_records(timetable)
        df = sort_datatable(sort_by, df)
        tabledata = df.to_dict('records')
        children = children
    elif ticker and start_date and end_date:
        dipreport, df = bp.botfunc(ticker, start_date, end_date)
        yaxes = [i for i in df.columns[1:] if i not in ['pctdrops', 'lowestprice']]
        fig = px.line(df, x='date', y=yaxes, markers=False)
        fig.update_layout(transition_duration=500, legend_title_text='Ticker', hovermode=hovermode)
        fig.update_traces(hovertemplate='date=%{x|%Y-%m-%d}<br>value=%{y}')
        children = [
            html.P(dipreport),
            dcc.Graph(figure=fig)
            ]
        tabledata = df.to_dict('records')
    else:
        children = 'Nothing selected yet.'
        tabledata = None
    return children, tabledata
