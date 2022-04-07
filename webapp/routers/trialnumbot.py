"""
Title: Trial Num Bot Endpoint
Date Started: Feb 8, 2022
Version: 1
Version Start: Feb 8, 2022
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose:  To provide API endpoint for Age bot.
"""
# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
#   THIRD PARTY IMPORTS
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dashappobject import app
import plotly.express as px
import pandas as pd
#   LOCAL APPLICATION IMPORTS
from Modules.stats_profilers import stat_profilerv3
from ..dashinputs import prompt_builder, gen_tablecontents, dash_inputbuilder
from ..botclasses import BotParams
from Modules.referencetools.statresearch.trialnumbot import num_trial_bot, num_trial_bot_report
from ..os_functions import get_currentscript_filename

bp = BotParams(
    get_currentscript_filename(__file__),
    'Trial Num Bot',
    "The Trial Num Bot returns the number of trials recommended to run based on how much an effect you desire an additional sample should have on the overall mean of the population.",
    num_trial_bot
)
tbodydata = [
    {
        'id': f'randmin_{bp.botid}',
        'placeholdertext': 'min value',
        'prompt': 'Enter the smallest value a random sample can have',
        'inputtype': 'number'
        },
    {
        'id': f'randmax_{bp.botid}',
        'placeholdertext': 'max value',
        'prompt': 'Enter the largest value a random sample can have',
        'inputtype': 'number'
        },
    {
        'placeholdertext': 'tolerance level',
        'id': f'tolerance_{bp.botid}',
        'prompt': "Set the tolerance.  This is the number an additional sample's effect on the overall mean of the population must stay below for that sample's effect to be considered statistically insignificant.",
        'details': 'For example, entering 0.025 means that for an additional sample to have no significant impact on the overall population, it would have to have an impact of less than 2.5%, meaning it may only move the overall population average by an amount less than that.',
        'inputtype': 'number',
        'min': 0
        },
    {
        'placeholdertext': 'window proportion',
        'id': f'win_prop_{bp.botid}',
        'prompt': 'Set the proportion of all samples starting with most recent that you want to include when considering the effect a sample has on the overall mean.',
        'details': 'For example, entering 0.5 means that the bot will use the most recent 50% of all trial samples to determine what is the recent maximum effect an additional sample had on the overall population.',
        'inputtype': 'number',
        'min': 0,
        'max': 1
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
    html.Div(id=f'output_{bp.botid}')
])


@app.callback(
    Output(f'output_{bp.botid}', 'children'),
    Input(f'submitbutton_{bp.botid}', 'n_clicks'),
    State(f'randmin_{bp.botid}', "value"),
    State(f'randmax_{bp.botid}', "value"),
    State(f'tolerance_{bp.botid}', "value"),
    State(f'win_prop_{bp.botid}', "value"),
    prevent_initial_call=True
    )
def calc_numtrialbot(
        n_clicks,
        randmin,
        randmax,
        tolerance,
        win_prop
        ):
    s = num_trial_bot(randmin, randmax, tolerance, win_prop)
    report = num_trial_bot_report(s)
    df = pd.DataFrame(data=s)
    statdf = pd.DataFrame(data=[stat_profilerv3(s[-1]['data'])])
    return [
        html.Div([html.P(i) for i in report]),
        html.Div([
            html.P('Stat summary of all trial samples:'),
            dash_inputbuilder({
                'data': statdf.to_dict('records'),
                'inputtype': 'table',
                'id': f"statsumtable_{bp.botid}"
                })
            ]),
        dcc.Graph(figure=px.line(
            df.iloc[:, :-2],
            x='trial',
            y=['sample', 'avg_before', 'avg_after', 'sample_effect', 'recent_max_effect', 'tolerance'],
            markers=False
            ))
    ]
