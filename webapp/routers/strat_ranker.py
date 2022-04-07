"""
Title: Strat Ranker
Date Started: Mar 13, 2022
Version: 1.00
Version Start: Mar 13, 2022
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose:  Rank metricvalue ranges of each strat test run.

"""
# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
#   THIRD PARTY IMPORTS
from dash import dcc, html
from dash.dependencies import Input, Output
from dashappobject import app
import plotly.express as px
import pandas as pd
#   LOCAL APPLICATION IMPORTS
from ..botclasses import BotParams
from ..os_functions import get_currentscript_filename
from ..dashinputs import dash_inputbuilder
from .strattester_helper_leaderboard import gen_leaderboard
from ..datatables import sort_datatable
from Modules.ranking_functions import gen_ranking
from webapp.routers.strattester_helper_leaderboard_colconfig import quality_cols
from formatting import format_tabs
from Modules.dataframe_functions import join_matrices


bp = BotParams(
    get_currentscript_filename(__file__),
    'Strategy Ranker',
    "Get metricvalue range of each quality metric then rank them across all strat test runs.",
    None
)


def gen_ranksourcetable():
    quality_rank_tuples = [
        ['effective_daily_growthrate', 1/11, 0],
        ['effective_daily_growthrate_margin', 2/11, 0],
        ['margin_daily_growthrate_min', 2/11, 0],
        ['abovezerotally_pct', 1/11, 0],
        ['abovezerotally_margin_pct', 2/11, 0],
        ['abovebench_tally_pct', 2/11, 0],
        ['abovebench_pos_tally_pct', 1/11, 0]
        ]
    df = gen_leaderboard(['strat_name', 'num_periods']+quality_cols)
    df = df[df['num_periods'] >= 20]
    df = df[['strat_name']+quality_cols]
    lofdf = []
    for m in ['MEDIAN', 'MIN', 'MAX']:
        mdf = df.groupby('strat_name', as_index=False).median() if m == 'MEDIAN' else df.groupby('strat_name', as_index=False).min() if m == 'MIN' else df.groupby('strat_name', as_index=False).max()
        mdf.rename(columns={k: f'{k}_{m}' for k in quality_cols}, inplace=True)
        lofdf.append(mdf)
    finaldf = join_matrices('strat_name', lofdf, 1)
    grinputs = [[f'{c[0]}_{m}', (1/3)*c[1], c[2]] for c in quality_rank_tuples for m in ['MEDIAN', 'MIN', 'MAX']]
    finaldf = gen_ranking(grinputs, finaldf)
    return finaldf


layout = html.Div([
    dash_inputbuilder({
        'id': f'rankbutton_{bp.botid}',
        'buttontext': 'Rank',
        'inputtype': 'button_submit'
        }),
    dcc.Tabs([
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
            ], id=f'displayresult_{bp.botid}')], className=format_tabs),
        dcc.Tab(label='Ranker', id=f'leadertab_{bp.botid}', children=[
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
        }), hidden='hidden')
], className='w-auto')


# gen graph
@app.callback(
    Output(f"sourcetable_{bp.botid}", "data"),
    Input(f"rankbutton_{bp.botid}", 'n_clicks')
    )
def gen_ranktable(n_clicks):
    sourcetabledata = gen_ranksourcetable()
    return sourcetabledata.to_dict('records')


# gen graph
@app.callback(
    Output(f'overallstats_{bp.botid}', "figure"),
    Input(f"sourcetable_{bp.botid}", "data"),
    Input(f"hovermode_{bp.botid}", 'value')
    )
def gen_graph(sourcetable, hovermode):
    df = pd.DataFrame.from_records(sourcetable)
    ycols = [f'{k}_{m}' for k in quality_cols for m in ['MEDIAN', 'MIN', 'MAX']]
    fig = px.line(df, x='strat_name', y=ycols, markers=False)
    fig.update_layout(transition_duration=500, legend_title_text='Legend', hovermode=hovermode, uirevision='some-constant')
    return fig


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


# filter, sort ranking
@app.callback(
    Output(f'leaderboardtable_{bp.botid}', 'data'),
    Output(f'leaderboardtable_{bp.botid}', 'columns'),
    Input(f'sourcetable_{bp.botid}', 'data'),
    Input(f'leaderboardtable_{bp.botid}', 'sort_by')
    )
def gen_rank_table(hiddenltable, sort_by):
    df = pd.DataFrame.from_records(hiddenltable)
    df = sort_datatable(sort_by, df)
    columns = [
        {'name': i, 'id': i, 'type': table_type(df[i]), 'hideable': True} for i in df.columns
    ]
    return df.to_dict('records'), columns
