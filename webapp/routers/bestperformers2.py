"""
Title: Best Performers Endpoint
Date Started: Jan 30, 2022
Version: 1.00
Version Start: Jan 30, 2022
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose:  .
fatscore_baremaxtoraw
fatscore_baremaxtobaremin
drop_mag
drop_prev
dropscore
maxdd

"""
# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
from itertools import permutations
#   THIRD PARTY IMPORTS
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State
import plotly.express as px
from dashappobject import app
import pandas as pd
#   LOCAL APPLICATION IMPORTS
from ..dashinputs import prompt_builder, gen_tablecontents, dash_inputbuilder
from ..common_resources import tickers, staticmindate, staticmaxdate
from ..botrun_parambuilder import brpb_base
from file_functions import delete_folder, getbotsinglerunfolder
from ..botclasses import BotParams
from Modules.bots.bestperformers.BESTPERFORMERS_BASE2 import bestperformer_cruncher
from ..os_functions import get_currentscript_filename
from ..datatables import sort_datatable
from webapp.servernotes import benchmarkdata
from Modules.price_history_slicing import pricedf_daterange
from Modules.price_calib import convertpricearr, add_calibratedprices_portfolio
from .pricehistoryexplorer_helper_diffcomp import add_comparisons_portfolio, add_pdiffpctchange_portfolio
from Modules.dates import plusminusdays
from Modules.timeperiodbot import random_dates
from formatting import format_htmltable_row, format_tabs


bp = BotParams(
    get_currentscript_filename(__file__),
    'Best Performers Bot',
    "The Best Performers Bot finds stocks that meet the requirements specified for the date range specified.  The ticker symbols considered are all United States NASDAQ and NYSE common stock.",
    bestperformer_cruncher
)

tbodydata = [
    {
        'id': f'datepicker_{bp.botid}',
        'prompt': 'Specify a date range.',
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
        }
]

growthrateinputs = [
    {
        'id': f'growthrate_{bp.botid}',
        'prompt': 'Set growth rate threshold.  The threshold can be determined either by a specific number, by the growth rate of another stock or benchmark, or the best performing benchmark.',
        'options': [
            {'label': 'By Ticker', 'value': 'byticker'},
            {'label': 'By Best Benchmark', 'value': 'bybench'},
            {'label': 'By specific number', 'value': 'bynumber'}
        ],
        'clearable': True,
        'inputtype': 'dropdown'
        },
    {
        'id': f'byticker_growthrate_{bp.botid}',
        'prompt': 'Choose a ticker to be the growth rate threshold.',
        'inputtype': 'dropdown',
        'options': tickers,
        'placeholder': 'Select or Type a Ticker',
        'searchable': True,
        'clearable': True
        },
    {
        'id': f'bynumber_growthrate_{bp.botid}',
        'prompt': 'Enter a growth rate threshold.',
        'inputtype': 'number'
        },
    {
        'id': f'growthrate_filter_{bp.botid}',
        'prompt': 'Keep stocks that are __ the growth rate threshold.',
        'options': ['>', '>=', '<', '<='],
        'inputtype': 'dropdown'
        },
    {
        'id': f'growthrate_margin_{bp.botid}',
        'prompt': 'By how much must a stock beat the growthrate threshold? This is added to the threshold value.  So if the filter direction is > or >= use a positive value.  If the filter direction is < or <=, use a negative value.',
        'inputtype': 'number'
        }
        ]

fatscore_baremaxtoraw_inputs = [
    {
        'id': f'fatscore_baremaxtoraw_{bp.botid}',
        'prompt': 'Set fatscore_baremaxtoraw threshold.  The threshold can be determined either by a specific number, by the fatscore_baremaxtoraw of another stock or benchmark, or the best performing benchmark.',
        'options': [
            {'label': 'By Ticker', 'value': 'byticker'},
            {'label': 'By Best Benchmark', 'value': 'bybench'},
            {'label': 'By specific number', 'value': 'bynumber'}
        ],
        'clearable': True,
        'inputtype': 'dropdown'
        },
    {
        'id': f'byticker_fatscore_baremaxtoraw_{bp.botid}',
        'prompt': 'Choose a ticker to be the fatscore_baremaxtoraw threshold.',
        'inputtype': 'dropdown',
        'options': tickers,
        'placeholder': 'Select or Type a Ticker',
        'searchable': True,
        'clearable': True
        },
    {
        'id': f'bynumber_fatscore_baremaxtoraw_{bp.botid}',
        'prompt': 'Enter a fatscore_baremaxtoraw threshold.',
        'inputtype': 'number',
        'max': 1,
        'min': 0
        },
    {
        'id': f'fatscore_baremaxtoraw_filter_{bp.botid}',
        'prompt': 'Keep stocks that are __ the fatscore_baremaxtoraw threshold.',
        'options': ['>', '>=', '<', '<='],
        'inputtype': 'dropdown'
        },
    {
        'id': f'fatscore_baremaxtoraw_margin_{bp.botid}',
        'prompt': 'By how much must a stock beat the fatscore_baremaxtoraw threshold? This is added to the threshold value.  So if the filter direction is > or >= use a positive value.  If the filter direction is < or <=, use a negative value.',
        'inputtype': 'number'
        }
        ]

fatscore_baremaxtobaremin_inputs = [
    {
        'id': f'fatscore_baremaxtobaremin_{bp.botid}',
        'prompt': 'Set fatscore_baremaxtobaremin threshold.  The threshold can be determined either by a specific number, by the fatscore_baremaxtobaremin of another stock or benchmark, or the best performing benchmark.',
        'options': [
            {'label': 'By Ticker', 'value': 'byticker'},
            {'label': 'By Best Benchmark', 'value': 'bybench'},
            {'label': 'By specific number', 'value': 'bynumber'}
        ],
        'clearable': True,
        'inputtype': 'dropdown'
        },
    {
        'id': f'byticker_fatscore_baremaxtobaremin_{bp.botid}',
        'prompt': 'Choose a ticker to be the fatscore_baremaxtobaremin threshold.',
        'inputtype': 'dropdown',
        'options': tickers,
        'placeholder': 'Select or Type a Ticker',
        'searchable': True,
        'clearable': True
        },
    {
        'id': f'bynumber_fatscore_baremaxtobaremin_{bp.botid}',
        'prompt': 'Enter a fatscore_baremaxtobaremin threshold.',
        'inputtype': 'number',
        'max': 1,
        'min': 0
        },
    {
        'id': f'fatscore_baremaxtobaremin_filter_{bp.botid}',
        'prompt': 'Keep stocks that are __ the fatscore_baremaxtobaremin threshold.',
        'options': ['>', '>=', '<', '<='],
        'inputtype': 'dropdown'
        },
    {
        'id': f'fatscore_baremaxtobaremin_margin_{bp.botid}',
        'prompt': 'By how much must a stock beat the fatscore_baremaxtobaremin threshold? This is added to the threshold value.  So if the filter direction is > or >= use a positive value.  If the filter direction is < or <=, use a negative value.',
        'inputtype': 'number'
        }
        ]

drop_mag_inputs = [
    {
        'id': f'drop_mag_{bp.botid}',
        'prompt': 'Set drop_mag threshold.  The threshold can be determined either by a specific number, by the drop_mag of another stock or benchmark, or the best performing benchmark.',
        'options': [
            {'label': 'By Ticker', 'value': 'byticker'},
            {'label': 'By Best Benchmark', 'value': 'bybench'},
            {'label': 'By specific number', 'value': 'bynumber'}
        ],
        'clearable': True,
        'inputtype': 'dropdown'
        },
    {
        'id': f'byticker_drop_mag_{bp.botid}',
        'prompt': 'Choose a ticker to be the drop_mag threshold.',
        'inputtype': 'dropdown',
        'options': tickers,
        'placeholder': 'Select or Type a Ticker',
        'searchable': True,
        'clearable': True
        },
    {
        'id': f'bynumber_drop_mag_{bp.botid}',
        'prompt': 'Enter a drop_mag threshold.',
        'inputtype': 'number',
        'max': 0,
        'min': -1
        },
    {
        'id': f'drop_mag_filter_{bp.botid}',
        'prompt': 'Keep stocks that are __ the drop_mag threshold.',
        'options': ['>', '>=', '<', '<='],
        'inputtype': 'dropdown'
        },
    {
        'id': f'drop_mag_margin_{bp.botid}',
        'prompt': 'By how much must a stock beat the drop_mag threshold? This is added to the threshold value.  So if the filter direction is > or >= use a positive value.  If the filter direction is < or <=, use a negative value.',
        'inputtype': 'number'
        }
        ]

drop_prev_inputs = [
    {
        'id': f'drop_prev_{bp.botid}',
        'prompt': 'Set drop_prev threshold.  The threshold can be determined either by a specific number, by the drop_prev of another stock or benchmark, or the best performing benchmark.',
        'options': [
            {'label': 'By Ticker', 'value': 'byticker'},
            {'label': 'By Best Benchmark', 'value': 'bybench'},
            {'label': 'By specific number', 'value': 'bynumber'}
        ],
        'clearable': True,
        'inputtype': 'dropdown'
        },
    {
        'id': f'byticker_drop_prev_{bp.botid}',
        'prompt': 'Choose a ticker to be the drop_prev threshold.',
        'inputtype': 'dropdown',
        'options': tickers,
        'placeholder': 'Select or Type a Ticker',
        'searchable': True,
        'clearable': True
        },
    {
        'id': f'bynumber_drop_prev_{bp.botid}',
        'prompt': 'Enter a drop_prev threshold.',
        'inputtype': 'number',
        'max': 1,
        'min': 0
        },
    {
        'id': f'drop_prev_filter_{bp.botid}',
        'prompt': 'Keep stocks that are __ the drop_prev threshold.',
        'options': ['>', '>=', '<', '<='],
        'inputtype': 'dropdown'
        },
    {
        'id': f'drop_prev_margin_{bp.botid}',
        'prompt': 'By how much must a stock beat the drop_prev threshold? This is added to the threshold value.  So if the filter direction is > or >= use a positive value.  If the filter direction is < or <=, use a negative value.',
        'inputtype': 'number'
        }
        ]

dropscore_inputs = [
    {
        'id': f'dropscore_{bp.botid}',
        'prompt': 'Set dropscore threshold.  The threshold can be determined either by a specific number, by the dropscore of another stock or benchmark, or the best performing benchmark.',
        'options': [
            {'label': 'By Ticker', 'value': 'byticker'},
            {'label': 'By Best Benchmark', 'value': 'bybench'},
            {'label': 'By specific number', 'value': 'bynumber'}
        ],
        'clearable': True,
        'inputtype': 'dropdown'
        },
    {
        'id': f'byticker_dropscore_{bp.botid}',
        'prompt': 'Choose a ticker to be the dropscore threshold.',
        'inputtype': 'dropdown',
        'options': tickers,
        'placeholder': 'Select or Type a Ticker',
        'searchable': True,
        'clearable': True
        },
    {
        'id': f'bynumber_dropscore_{bp.botid}',
        'prompt': 'Enter a dropscore threshold.',
        'inputtype': 'number',
        'max': 0,
        'min': -1
        },
    {
        'id': f'dropscore_filter_{bp.botid}',
        'prompt': 'Keep stocks that are __ the dropscore threshold.',
        'options': ['>', '>=', '<', '<='],
        'inputtype': 'dropdown'
        },
    {
        'id': f'dropscore_margin_{bp.botid}',
        'prompt': 'By how much must a stock beat the dropscore threshold? This is added to the threshold value.  So if the filter direction is > or >= use a positive value.  If the filter direction is < or <=, use a negative value.',
        'inputtype': 'number'
        }
        ]

maxdd_inputs = [
    {
        'id': f'maxdd_{bp.botid}',
        'prompt': 'Set maxdd threshold.  The threshold can be determined either by a specific number, by the maxdd of another stock or benchmark, or the best performing benchmark.',
        'options': [
            {'label': 'By Ticker', 'value': 'byticker'},
            {'label': 'By Best Benchmark', 'value': 'bybench'},
            {'label': 'By specific number', 'value': 'bynumber'}
        ],
        'clearable': True,
        'inputtype': 'dropdown'
        },
    {
        'id': f'byticker_maxdd_{bp.botid}',
        'prompt': 'Choose a ticker to be the maxdd threshold.',
        'inputtype': 'dropdown',
        'options': tickers,
        'placeholder': 'Select or Type a Ticker',
        'searchable': True,
        'clearable': True
        },
    {
        'id': f'bynumber_maxdd_{bp.botid}',
        'prompt': 'Enter a maxdd threshold.',
        'inputtype': 'number',
        'max': 0
        },
    {
        'id': f'maxdd_filter_{bp.botid}',
        'prompt': 'Keep stocks that are __ the maxdd threshold.',
        'options': ['>', '>=', '<', '<='],
        'inputtype': 'dropdown'
        },
    {
        'id': f'maxdd_margin_{bp.botid}',
        'prompt': 'By how much must a stock beat the maxdd threshold? This is added to the threshold value.  So if the filter direction is > or >= use a positive value.  If the filter direction is < or <=, use a negative value.',
        'inputtype': 'number'
        }
        ]

perf_graph_inputs = [
    {
        'id': f'perf_graph_ticker_{bp.botid}',
        'prompt': 'Select tickers from the full ranking list that you want to see.',
        'inputtype': 'dropdown',
        'options': [],
        'placeholder': 'Select or Search a Ticker(s)',
        'multi': True,
        'searchable': True,
        'clearable': True
        },
    {
        'id': f'calib_{bp.botid}',
        'prompt': 'Select a calibration.  Absolute is where the y-axis is in $.  Normalized is where all prices are standardized to the same scale.',
        'inputtype': 'radio',
        'options': [
            {'label': 'Absolute', 'value': 'absolute'},
            {'label': 'Normalized', 'value': 'normalize'}
        ],
        'value': 'absolute',
        'inline': 'inline'
        },
    {
        'id': f'contour_{bp.botid}',
        'prompt': 'Select whether you want to see the graphs in a different contour.',
        'details': 'Baremax displays the current all-time high price.  Baremin displays the floor price.  Trueline displays the midpoint between baremax and baremin prices.  Straight displays the straight line from first to last price.',
        'inputtype': 'checklist',
        'options': [
            {'label': 'Baremax', 'value': 'baremaxraw'},
            {'label': 'Baremin', 'value': 'oldbareminraw'},
            {'label': 'Trueline', 'value': 'trueline'},
            {'label': 'Straight', 'value': 'straight'}
        ]
        },
    {
        'id': f'graphdiff_mode_{bp.botid}',
        'prompt': 'Periodic difference measures arithmetic difference in value between adjacent periods. Periodic percent change measures the percent change difference between adjacent periods.',
        'inputtype': 'radio',
        'options': [
            {'label': 'Periodic Difference', 'value': 'pdiff'},
            {'label': 'Periodic Percent Change', 'value': 'pctchange'}
        ],
        'value': 'pctchange',
        'inline': 'inline'
        },
    {
        'id': f'graphdiff_changecol_{bp.botid}',
        'prompt': 'Select a calibration you want to compute the periodic change.',
        'inputtype': 'dropdown',
        'options': [],
        'value': 'all',
        'placeholder': 'select calibration',
        'multi': False,
        'searchable': False,
        'clearable': False
        },
    {
        'id': f'graphdiff_period_{bp.botid}',
        'prompt': 'Enter the period (in days) you want differences or percent change to calculated.  For example, period of 1 for mode "Periodic Percent Change" gives you a graph representing the daily percent change of the source calibration.',
        'inputtype': 'number',
        'value': 1,
        'min': 1,
        'step': 1,
        'debounce': True
        },
    {
        'id': f'graphcompoptions_{bp.botid}',
        'prompt': 'Graphs proportion difference between two available calibrations A and B.  Thus, option "A to B" means it will output a graph such that the graph is a representation of (A - B) / B.',
        'inputtype': 'dropdown',
        'options': [],
        'placeholder': 'select comparison',
        'multi': False,
        'searchable': False,
        'clearable': True
        },
    {
        'id': f'bench_{bp.botid}',
        'prompt': 'Select a benchmark to compare against your portfolio.',
        'details': '',
        'inputtype': 'checklist',
        'options': [
            {'label': 'Dow Jones', 'value': '^DJI'},
            {'label': 'S&P 500', 'value': '^INX'},
            {'label': 'NASDAQ', 'value': '^IXIC'}
        ],
        'inline': 'inline'
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
        html.Table(gen_tablecontents(growthrateinputs), id=f'cohort_growthrate_{bp.botid}', className=format_htmltable_row),
        html.Table(gen_tablecontents(fatscore_baremaxtoraw_inputs), id=f'cohort_fatscore_baremaxtoraw_{bp.botid}', className=format_htmltable_row),
        html.Table(gen_tablecontents(fatscore_baremaxtobaremin_inputs), id=f'cohort_fatscore_baremaxtobaremin_{bp.botid}', className=format_htmltable_row),
        html.Table(gen_tablecontents(drop_mag_inputs), id=f'cohort_drop_mag_{bp.botid}', className=format_htmltable_row),
        html.Table(gen_tablecontents(drop_prev_inputs), id=f'cohort_drop_prev_{bp.botid}', className=format_htmltable_row),
        html.Table(gen_tablecontents(dropscore_inputs), id=f'cohort_dropscore_{bp.botid}', className=format_htmltable_row),
        html.Table(gen_tablecontents(maxdd_inputs), id=f'cohort_maxdd_{bp.botid}', className=format_htmltable_row),
        prompt_builder({
            'id': f'submitbutton_{bp.botid}',
            'inputtype': 'button_submit'
            })
        ], id=f'input_{bp.botid}'),
    dcc.Tabs([
        dcc.Tab(label='Input Summary', id=f'tab_preview_{bp.botid}', className=format_tabs),
        dcc.Tab([
            html.Div(id=f"testoutput_{bp.botid}"),
            dash_inputbuilder({
                'inputtype': 'table',
                'id': f"bptable_{bp.botid}"
                })], label='Full Ranking', id=f'tab_fullranking_{bp.botid}', className=format_tabs),
        dcc.Tab([
            dash_inputbuilder({
                'id': f'hovermode_fullranking_graph_{bp.botid}',
                'prompt': 'Choose how you want to display data when you hover over the graph.',
                'inputtype': 'radio',
                'options': [{'label': x, 'value': x} for x in ['x', 'x unified', 'closest']],
                'value': 'closest',
                'inline': 'inline'
                }),
            dcc.Graph(id=f"fullranking_graph_{bp.botid}")
        ], label='Ranking Graph', id=f'tab_fullranking_graph_{bp.botid}', className=format_tabs),
        dcc.Tab([
            html.Table(gen_tablecontents(perf_graph_inputs), style={'width': '100%'}),
            dcc.Graph(id=f"perf_graph_{bp.botid}"),
            dcc.Graph(id=f"graphdiff_{bp.botid}"),
            dcc.Graph(id=f"graphcomp_{bp.botid}")
        ], label='Performance Graph', id=f'tab_perf_graph_{bp.botid}', className=format_tabs),
        dcc.Tab([dash_inputbuilder({
            'inputtype': 'table',
            'id': f"sourcetable_{bp.botid}"
            })], label='Raw Data', className=format_tabs)
        ])
])


# get random dates
@app.callback(
    Output(f'datepicker_{bp.botid}', "start_date"),
    Output(f'datepicker_{bp.botid}', "end_date"),
    Input(f'randomize_{bp.botid}', "n_clicks"),
    prevent_initial_call=True
    )
def randomize_date(n_clicks):
    new_start = random_dates(staticmindate, staticmaxdate, 1)[0]
    new_end = random_dates(plusminusdays(new_start, 1, 'add'), staticmaxdate, 1)[0]
    return new_start, new_end


# modify growth rate input fields
@app.callback(
    Output(f'inputfield_byticker_growthrate_{bp.botid}', 'hidden'),
    Output(f'prompt_byticker_growthrate_{bp.botid}', 'hidden'),
    Output(f'inputfield_bynumber_growthrate_{bp.botid}', 'hidden'),
    Output(f'prompt_bynumber_growthrate_{bp.botid}', 'hidden'),
    Output(f'inputfield_growthrate_filter_{bp.botid}', 'hidden'),
    Output(f'prompt_growthrate_filter_{bp.botid}', 'hidden'),
    Output(f'inputfield_growthrate_margin_{bp.botid}', 'hidden'),
    Output(f'prompt_growthrate_margin_{bp.botid}', 'hidden'),
    Input(f"growthrate_{bp.botid}", 'value')
    )
def update_inputs_growthrate(thresh):
    hide_inputfield_byticker = 'hidden'
    hide_prompt_byticker = 'hidden'
    hide_inputfield_bynumber = 'hidden'
    hide_prompt_bynumber = 'hidden'
    hide_inputfield_filter = 'hidden'
    hide_prompt_filter = 'hidden'
    hide_inputfield_margin = 'hidden'
    hide_prompt_margin = 'hidden'
    if thresh == 'byticker':
        hide_inputfield_byticker = None
        hide_prompt_byticker = None
    elif thresh == 'bynumber':
        hide_inputfield_bynumber = None
        hide_prompt_bynumber = None
    if thresh in ['byticker', 'bybench', 'bynumber']:
        hide_inputfield_filter = None
        hide_prompt_filter = None
        hide_inputfield_margin = None
        hide_prompt_margin = None
    return hide_inputfield_byticker, hide_prompt_byticker, hide_inputfield_bynumber, hide_prompt_bynumber, hide_inputfield_filter, hide_prompt_filter, hide_inputfield_margin, hide_prompt_margin


# modify fatscore_baremaxtoraw input fields
@app.callback(
    Output(f'inputfield_byticker_fatscore_baremaxtoraw_{bp.botid}', 'hidden'),
    Output(f'prompt_byticker_fatscore_baremaxtoraw_{bp.botid}', 'hidden'),
    Output(f'inputfield_bynumber_fatscore_baremaxtoraw_{bp.botid}', 'hidden'),
    Output(f'prompt_bynumber_fatscore_baremaxtoraw_{bp.botid}', 'hidden'),
    Output(f'inputfield_fatscore_baremaxtoraw_filter_{bp.botid}', 'hidden'),
    Output(f'prompt_fatscore_baremaxtoraw_filter_{bp.botid}', 'hidden'),
    Output(f'inputfield_fatscore_baremaxtoraw_margin_{bp.botid}', 'hidden'),
    Output(f'prompt_fatscore_baremaxtoraw_margin_{bp.botid}', 'hidden'),
    Input(f"fatscore_baremaxtoraw_{bp.botid}", 'value')
    )
def update_inputs_fatscore_baremaxtoraw(thresh):
    hide_inputfield_byticker = 'hidden'
    hide_prompt_byticker = 'hidden'
    hide_inputfield_bynumber = 'hidden'
    hide_prompt_bynumber = 'hidden'
    hide_inputfield_filter = 'hidden'
    hide_prompt_filter = 'hidden'
    hide_inputfield_margin = 'hidden'
    hide_prompt_margin = 'hidden'
    if thresh == 'byticker':
        hide_inputfield_byticker = None
        hide_prompt_byticker = None
    elif thresh == 'bynumber':
        hide_inputfield_bynumber = None
        hide_prompt_bynumber = None
    if thresh in ['byticker', 'bybench', 'bynumber']:
        hide_inputfield_filter = None
        hide_prompt_filter = None
        hide_inputfield_margin = None
        hide_prompt_margin = None
    return hide_inputfield_byticker, hide_prompt_byticker, hide_inputfield_bynumber, hide_prompt_bynumber, hide_inputfield_filter, hide_prompt_filter, hide_inputfield_margin, hide_prompt_margin


# modify fatscore_baremaxtobaremin input fields
@app.callback(
    Output(f'inputfield_byticker_fatscore_baremaxtobaremin_{bp.botid}', 'hidden'),
    Output(f'prompt_byticker_fatscore_baremaxtobaremin_{bp.botid}', 'hidden'),
    Output(f'inputfield_bynumber_fatscore_baremaxtobaremin_{bp.botid}', 'hidden'),
    Output(f'prompt_bynumber_fatscore_baremaxtobaremin_{bp.botid}', 'hidden'),
    Output(f'inputfield_fatscore_baremaxtobaremin_filter_{bp.botid}', 'hidden'),
    Output(f'prompt_fatscore_baremaxtobaremin_filter_{bp.botid}', 'hidden'),
    Output(f'inputfield_fatscore_baremaxtobaremin_margin_{bp.botid}', 'hidden'),
    Output(f'prompt_fatscore_baremaxtobaremin_margin_{bp.botid}', 'hidden'),
    Input(f"fatscore_baremaxtobaremin_{bp.botid}", 'value')
    )
def update_inputs_fatscore_baremaxtobaremin(thresh):
    hide_inputfield_byticker = 'hidden'
    hide_prompt_byticker = 'hidden'
    hide_inputfield_bynumber = 'hidden'
    hide_prompt_bynumber = 'hidden'
    hide_inputfield_filter = 'hidden'
    hide_prompt_filter = 'hidden'
    hide_inputfield_margin = 'hidden'
    hide_prompt_margin = 'hidden'
    if thresh == 'byticker':
        hide_inputfield_byticker = None
        hide_prompt_byticker = None
    elif thresh == 'bynumber':
        hide_inputfield_bynumber = None
        hide_prompt_bynumber = None
    if thresh in ['byticker', 'bybench', 'bynumber']:
        hide_inputfield_filter = None
        hide_prompt_filter = None
        hide_inputfield_margin = None
        hide_prompt_margin = None
    return hide_inputfield_byticker, hide_prompt_byticker, hide_inputfield_bynumber, hide_prompt_bynumber, hide_inputfield_filter, hide_prompt_filter, hide_inputfield_margin, hide_prompt_margin


# modify drop_mag input fields
@app.callback(
    Output(f'inputfield_byticker_drop_mag_{bp.botid}', 'hidden'),
    Output(f'prompt_byticker_drop_mag_{bp.botid}', 'hidden'),
    Output(f'inputfield_bynumber_drop_mag_{bp.botid}', 'hidden'),
    Output(f'prompt_bynumber_drop_mag_{bp.botid}', 'hidden'),
    Output(f'inputfield_drop_mag_filter_{bp.botid}', 'hidden'),
    Output(f'prompt_drop_mag_filter_{bp.botid}', 'hidden'),
    Output(f'inputfield_drop_mag_margin_{bp.botid}', 'hidden'),
    Output(f'prompt_drop_mag_margin_{bp.botid}', 'hidden'),
    Input(f"drop_mag_{bp.botid}", 'value')
    )
def update_inputs_drop_mag(thresh):
    hide_inputfield_byticker = 'hidden'
    hide_prompt_byticker = 'hidden'
    hide_inputfield_bynumber = 'hidden'
    hide_prompt_bynumber = 'hidden'
    hide_inputfield_filter = 'hidden'
    hide_prompt_filter = 'hidden'
    hide_inputfield_margin = 'hidden'
    hide_prompt_margin = 'hidden'
    if thresh == 'byticker':
        hide_inputfield_byticker = None
        hide_prompt_byticker = None
    elif thresh == 'bynumber':
        hide_inputfield_bynumber = None
        hide_prompt_bynumber = None
    if thresh in ['byticker', 'bybench', 'bynumber']:
        hide_inputfield_filter = None
        hide_prompt_filter = None
        hide_inputfield_margin = None
        hide_prompt_margin = None
    return hide_inputfield_byticker, hide_prompt_byticker, hide_inputfield_bynumber, hide_prompt_bynumber, hide_inputfield_filter, hide_prompt_filter, hide_inputfield_margin, hide_prompt_margin


# modify drop_prev input fields
@app.callback(
    Output(f'inputfield_byticker_drop_prev_{bp.botid}', 'hidden'),
    Output(f'prompt_byticker_drop_prev_{bp.botid}', 'hidden'),
    Output(f'inputfield_bynumber_drop_prev_{bp.botid}', 'hidden'),
    Output(f'prompt_bynumber_drop_prev_{bp.botid}', 'hidden'),
    Output(f'inputfield_drop_prev_filter_{bp.botid}', 'hidden'),
    Output(f'prompt_drop_prev_filter_{bp.botid}', 'hidden'),
    Output(f'inputfield_drop_prev_margin_{bp.botid}', 'hidden'),
    Output(f'prompt_drop_prev_margin_{bp.botid}', 'hidden'),
    Input(f"drop_prev_{bp.botid}", 'value')
    )
def update_inputs_drop_prev(thresh):
    hide_inputfield_byticker = 'hidden'
    hide_prompt_byticker = 'hidden'
    hide_inputfield_bynumber = 'hidden'
    hide_prompt_bynumber = 'hidden'
    hide_inputfield_filter = 'hidden'
    hide_prompt_filter = 'hidden'
    hide_inputfield_margin = 'hidden'
    hide_prompt_margin = 'hidden'
    if thresh == 'byticker':
        hide_inputfield_byticker = None
        hide_prompt_byticker = None
    elif thresh == 'bynumber':
        hide_inputfield_bynumber = None
        hide_prompt_bynumber = None
    if thresh in ['byticker', 'bybench', 'bynumber']:
        hide_inputfield_filter = None
        hide_prompt_filter = None
        hide_inputfield_margin = None
        hide_prompt_margin = None
    return hide_inputfield_byticker, hide_prompt_byticker, hide_inputfield_bynumber, hide_prompt_bynumber, hide_inputfield_filter, hide_prompt_filter, hide_inputfield_margin, hide_prompt_margin


# modify dropscore input fields
@app.callback(
    Output(f'inputfield_byticker_dropscore_{bp.botid}', 'hidden'),
    Output(f'prompt_byticker_dropscore_{bp.botid}', 'hidden'),
    Output(f'inputfield_bynumber_dropscore_{bp.botid}', 'hidden'),
    Output(f'prompt_bynumber_dropscore_{bp.botid}', 'hidden'),
    Output(f'inputfield_dropscore_filter_{bp.botid}', 'hidden'),
    Output(f'prompt_dropscore_filter_{bp.botid}', 'hidden'),
    Output(f'inputfield_dropscore_margin_{bp.botid}', 'hidden'),
    Output(f'prompt_dropscore_margin_{bp.botid}', 'hidden'),
    Input(f"dropscore_{bp.botid}", 'value')
    )
def update_inputs_dropscore(thresh):
    hide_inputfield_byticker = 'hidden'
    hide_prompt_byticker = 'hidden'
    hide_inputfield_bynumber = 'hidden'
    hide_prompt_bynumber = 'hidden'
    hide_inputfield_filter = 'hidden'
    hide_prompt_filter = 'hidden'
    hide_inputfield_margin = 'hidden'
    hide_prompt_margin = 'hidden'
    if thresh == 'byticker':
        hide_inputfield_byticker = None
        hide_prompt_byticker = None
    elif thresh == 'bynumber':
        hide_inputfield_bynumber = None
        hide_prompt_bynumber = None
    if thresh in ['byticker', 'bybench', 'bynumber']:
        hide_inputfield_filter = None
        hide_prompt_filter = None
        hide_inputfield_margin = None
        hide_prompt_margin = None
    return hide_inputfield_byticker, hide_prompt_byticker, hide_inputfield_bynumber, hide_prompt_bynumber, hide_inputfield_filter, hide_prompt_filter, hide_inputfield_margin, hide_prompt_margin


# modify maxdd input fields
@app.callback(
    Output(f'inputfield_byticker_maxdd_{bp.botid}', 'hidden'),
    Output(f'prompt_byticker_maxdd_{bp.botid}', 'hidden'),
    Output(f'inputfield_bynumber_maxdd_{bp.botid}', 'hidden'),
    Output(f'prompt_bynumber_maxdd_{bp.botid}', 'hidden'),
    Output(f'inputfield_maxdd_filter_{bp.botid}', 'hidden'),
    Output(f'prompt_maxdd_filter_{bp.botid}', 'hidden'),
    Output(f'inputfield_maxdd_margin_{bp.botid}', 'hidden'),
    Output(f'prompt_maxdd_margin_{bp.botid}', 'hidden'),
    Input(f"maxdd_{bp.botid}", 'value')
    )
def update_inputs_maxdd(thresh):
    hide_inputfield_byticker = 'hidden'
    hide_prompt_byticker = 'hidden'
    hide_inputfield_bynumber = 'hidden'
    hide_prompt_bynumber = 'hidden'
    hide_inputfield_filter = 'hidden'
    hide_prompt_filter = 'hidden'
    hide_inputfield_margin = 'hidden'
    hide_prompt_margin = 'hidden'
    if thresh == 'byticker':
        hide_inputfield_byticker = None
        hide_prompt_byticker = None
    elif thresh == 'bynumber':
        hide_inputfield_bynumber = None
        hide_prompt_bynumber = None
    if thresh in ['byticker', 'bybench', 'bynumber']:
        hide_inputfield_filter = None
        hide_prompt_filter = None
        hide_inputfield_margin = None
        hide_prompt_margin = None
    return hide_inputfield_byticker, hide_prompt_byticker, hide_inputfield_bynumber, hide_prompt_bynumber, hide_inputfield_filter, hide_prompt_filter, hide_inputfield_margin, hide_prompt_margin


# VALIDATE INPUTS
@app.callback(
    Output(f'tab_preview_{bp.botid}', "children"),
    Input(f"datepicker_{bp.botid}", 'start_date'),
    Input(f"datepicker_{bp.botid}", 'end_date'),
    Input(f"growthrate_{bp.botid}", 'value'),
    Input(f"byticker_growthrate_{bp.botid}", 'value'),
    Input(f"bynumber_growthrate_{bp.botid}", 'value'),
    Input(f"growthrate_filter_{bp.botid}", 'value'),
    Input(f"growthrate_margin_{bp.botid}", 'value'),
    Input(f"fatscore_baremaxtoraw_{bp.botid}", 'value'),
    Input(f"byticker_fatscore_baremaxtoraw_{bp.botid}", 'value'),
    Input(f"bynumber_fatscore_baremaxtoraw_{bp.botid}", 'value'),
    Input(f"fatscore_baremaxtoraw_filter_{bp.botid}", 'value'),
    Input(f"fatscore_baremaxtoraw_margin_{bp.botid}", 'value'),
    Input(f"fatscore_baremaxtobaremin_{bp.botid}", 'value'),
    Input(f"byticker_fatscore_baremaxtobaremin_{bp.botid}", 'value'),
    Input(f"bynumber_fatscore_baremaxtobaremin_{bp.botid}", 'value'),
    Input(f"fatscore_baremaxtobaremin_filter_{bp.botid}", 'value'),
    Input(f"fatscore_baremaxtobaremin_margin_{bp.botid}", 'value'),
    Input(f"drop_mag_{bp.botid}", 'value'),
    Input(f"byticker_drop_mag_{bp.botid}", 'value'),
    Input(f"bynumber_drop_mag_{bp.botid}", 'value'),
    Input(f"drop_mag_filter_{bp.botid}", 'value'),
    Input(f"drop_mag_margin_{bp.botid}", 'value'),
    Input(f"drop_prev_{bp.botid}", 'value'),
    Input(f"byticker_drop_prev_{bp.botid}", 'value'),
    Input(f"bynumber_drop_prev_{bp.botid}", 'value'),
    Input(f"drop_prev_filter_{bp.botid}", 'value'),
    Input(f"drop_prev_margin_{bp.botid}", 'value'),
    Input(f"dropscore_{bp.botid}", 'value'),
    Input(f"byticker_dropscore_{bp.botid}", 'value'),
    Input(f"bynumber_dropscore_{bp.botid}", 'value'),
    Input(f"dropscore_filter_{bp.botid}", 'value'),
    Input(f"dropscore_margin_{bp.botid}", 'value'),
    Input(f"maxdd_{bp.botid}", 'value'),
    Input(f"byticker_maxdd_{bp.botid}", 'value'),
    Input(f"bynumber_maxdd_{bp.botid}", 'value'),
    Input(f"maxdd_filter_{bp.botid}", 'value'),
    Input(f"maxdd_margin_{bp.botid}", 'value'),
    )
def validate_inputs(
    start_date,
    end_date,
    growthrate,
    byticker_growthrate,
    bynumber_growthrate,
    growthrate_filter,
    growthrate_margin,
    fatscore_baremaxtoraw,
    byticker_fatscore_baremaxtoraw,
    bynumber_fatscore_baremaxtoraw,
    fatscore_baremaxtoraw_filter,
    fatscore_baremaxtoraw_margin,
    fatscore_baremaxtobaremin,
    byticker_fatscore_baremaxtobaremin,
    bynumber_fatscore_baremaxtobaremin,
    fatscore_baremaxtobaremin_filter,
    fatscore_baremaxtobaremin_margin,
    drop_mag,
    byticker_drop_mag,
    bynumber_drop_mag,
    drop_mag_filter,
    drop_mag_margin,
    drop_prev,
    byticker_drop_prev,
    bynumber_drop_prev,
    drop_prev_filter,
    drop_prev_margin,
    dropscore,
    byticker_dropscore,
    bynumber_dropscore,
    dropscore_filter,
    dropscore_margin,
    maxdd,
    byticker_maxdd,
    bynumber_maxdd,
    maxdd_filter,
    maxdd_margin
):
    setting_summary = [
        f'start_date: {start_date}',
        f'end_date: {end_date}',
        f'growthrate: {growthrate}',
        f'byticker_growthrate: {byticker_growthrate}',
        f'bynumber_growthrate: {bynumber_growthrate}',
        f'growthrate_filter: {growthrate_filter}',
        f'growthrate_margin: {growthrate_margin}',
        f'fatscore_baremaxtoraw: {fatscore_baremaxtoraw}',
        f'byticker_fatscore_baremaxtoraw: {byticker_fatscore_baremaxtoraw}',
        f'bynumber_fatscore_baremaxtoraw: {bynumber_fatscore_baremaxtoraw}',
        f'fatscore_baremaxtoraw_filter: {fatscore_baremaxtoraw_filter}',
        f'fatscore_baremaxtoraw_margin: {fatscore_baremaxtoraw_margin}',
        f'fatscore_baremaxtobaremin: {fatscore_baremaxtobaremin}',
        f'byticker_fatscore_baremaxtobaremin: {byticker_fatscore_baremaxtobaremin}',
        f'bynumber_fatscore_baremaxtobaremin: {bynumber_fatscore_baremaxtobaremin}',
        f'fatscore_baremaxtobaremin_filter: {fatscore_baremaxtobaremin_filter}',
        f'fatscore_baremaxtobaremin_margin: {fatscore_baremaxtobaremin_margin}',
        f'drop_mag: {drop_mag}',
        f'byticker_drop_mag: {byticker_drop_mag}',
        f'bynumber_drop_mag: {bynumber_drop_mag}',
        f'drop_mag_filter: {drop_mag_filter}',
        f'drop_mag_margin: {drop_mag_margin}',
        f'drop_prev: {drop_prev}',
        f'byticker_drop_prev: {byticker_drop_prev}',
        f'bynumber_drop_prev: {bynumber_drop_prev}',
        f'drop_prev_filter: {drop_prev_filter}',
        f'drop_prev_margin: {drop_prev_margin}',
        f'dropscore: {dropscore}',
        f'byticker_dropscore: {byticker_dropscore}',
        f'bynumber_dropscore: {bynumber_dropscore}',
        f'dropscore_filter: {dropscore_filter}',
        f'dropscore_margin: {dropscore_margin}',
        f'maxdd: {maxdd}',
        f'byticker_maxdd: {byticker_maxdd}',
        f'bynumber_maxdd: {bynumber_maxdd}',
        f'maxdd_filter: {maxdd_filter}',
        f'maxdd_margin: {maxdd_margin}'
        ]
    setting_summary = [html.P([html.Div([html.Span(i), html.Br()]) for i in setting_summary])]
    return setting_summary


# CALC BEST PERFORMERS
@app.callback(
    #Output(f'testoutput_{bp.botid}', 'children'),
    Output(f'bptable_{bp.botid}', 'data'),
    Input(f'submitbutton_{bp.botid}', 'n_clicks'),
    State(f"datepicker_{bp.botid}", 'start_date'),
    State(f"datepicker_{bp.botid}", 'end_date'),
    State(f"growthrate_{bp.botid}", 'value'),
    State(f"byticker_growthrate_{bp.botid}", 'value'),
    State(f"bynumber_growthrate_{bp.botid}", 'value'),
    State(f"growthrate_filter_{bp.botid}", 'value'),
    State(f"growthrate_margin_{bp.botid}", 'value'),
    State(f"fatscore_baremaxtoraw_{bp.botid}", 'value'),
    State(f"byticker_fatscore_baremaxtoraw_{bp.botid}", 'value'),
    State(f"bynumber_fatscore_baremaxtoraw_{bp.botid}", 'value'),
    State(f"fatscore_baremaxtoraw_filter_{bp.botid}", 'value'),
    State(f"fatscore_baremaxtoraw_margin_{bp.botid}", 'value'),
    State(f"fatscore_baremaxtobaremin_{bp.botid}", 'value'),
    State(f"byticker_fatscore_baremaxtobaremin_{bp.botid}", 'value'),
    State(f"bynumber_fatscore_baremaxtobaremin_{bp.botid}", 'value'),
    State(f"fatscore_baremaxtobaremin_filter_{bp.botid}", 'value'),
    State(f"fatscore_baremaxtobaremin_margin_{bp.botid}", 'value'),
    State(f"drop_mag_{bp.botid}", 'value'),
    State(f"byticker_drop_mag_{bp.botid}", 'value'),
    State(f"bynumber_drop_mag_{bp.botid}", 'value'),
    State(f"drop_mag_filter_{bp.botid}", 'value'),
    State(f"drop_mag_margin_{bp.botid}", 'value'),
    State(f"drop_prev_{bp.botid}", 'value'),
    State(f"byticker_drop_prev_{bp.botid}", 'value'),
    State(f"bynumber_drop_prev_{bp.botid}", 'value'),
    State(f"drop_prev_filter_{bp.botid}", 'value'),
    State(f"drop_prev_margin_{bp.botid}", 'value'),
    State(f"dropscore_{bp.botid}", 'value'),
    State(f"byticker_dropscore_{bp.botid}", 'value'),
    State(f"bynumber_dropscore_{bp.botid}", 'value'),
    State(f"dropscore_filter_{bp.botid}", 'value'),
    State(f"dropscore_margin_{bp.botid}", 'value'),
    State(f"maxdd_{bp.botid}", 'value'),
    State(f"byticker_maxdd_{bp.botid}", 'value'),
    State(f"bynumber_maxdd_{bp.botid}", 'value'),
    State(f"maxdd_filter_{bp.botid}", 'value'),
    State(f"maxdd_margin_{bp.botid}", 'value'),
    Input(f"bptable_{bp.botid}", 'sort_by'),
    Input(f"bptable_{bp.botid}", 'data'),
    prevent_initial_call=True
    )
def calc_bestperformers(
        n_clicks,
        start_date,
        end_date,
        growthrate,
        byticker_growthrate,
        bynumber_growthrate,
        growthrate_filter,
        growthrate_margin,
        fatscore_baremaxtoraw,
        byticker_fatscore_baremaxtoraw,
        bynumber_fatscore_baremaxtoraw,
        fatscore_baremaxtoraw_filter,
        fatscore_baremaxtoraw_margin,
        fatscore_baremaxtobaremin,
        byticker_fatscore_baremaxtobaremin,
        bynumber_fatscore_baremaxtobaremin,
        fatscore_baremaxtobaremin_filter,
        fatscore_baremaxtobaremin_margin,
        drop_mag,
        byticker_drop_mag,
        bynumber_drop_mag,
        drop_mag_filter,
        drop_mag_margin,
        drop_prev,
        byticker_drop_prev,
        bynumber_drop_prev,
        drop_prev_filter,
        drop_prev_margin,
        dropscore,
        byticker_dropscore,
        bynumber_dropscore,
        dropscore_filter,
        dropscore_margin,
        maxdd,
        byticker_maxdd,
        bynumber_maxdd,
        maxdd_filter,
        maxdd_margin,
        sort_by,
        dfdata
        ):
    if dfdata and callback_context.triggered[0]['prop_id'].endswith('sort_by'):
        # convert table back to dataframe
        botdf = pd.DataFrame.from_records(dfdata)
        botdf = sort_datatable(sort_by, botdf)
    else:
        # form bot run-specific parameters ('brp').
        brp = {**brpb_base(bp.botid, 1), **{
            'start_date': start_date,
            'end_date': end_date,
            'growthrate': growthrate,
            'byticker_growthrate': byticker_growthrate,
            'bynumber_growthrate': bynumber_growthrate,
            'growthrate_filter': growthrate_filter,
            'growthrate_margin': growthrate_margin,
            'fatscore_baremaxtoraw': fatscore_baremaxtoraw,
            'byticker_fatscore_baremaxtoraw': byticker_fatscore_baremaxtoraw,
            'bynumber_fatscore_baremaxtoraw': bynumber_fatscore_baremaxtoraw,
            'fatscore_baremaxtoraw_filter': fatscore_baremaxtoraw_filter,
            'fatscore_baremaxtoraw_margin': fatscore_baremaxtoraw_margin,
            'fatscore_baremaxtobaremin': fatscore_baremaxtobaremin,
            'byticker_fatscore_baremaxtobaremin': byticker_fatscore_baremaxtobaremin,
            'bynumber_fatscore_baremaxtobaremin': bynumber_fatscore_baremaxtobaremin,
            'fatscore_baremaxtobaremin_filter': fatscore_baremaxtobaremin_filter,
            'fatscore_baremaxtobaremin_margin': fatscore_baremaxtobaremin_margin,
            'drop_mag': drop_mag,
            'byticker_drop_mag': byticker_drop_mag,
            'bynumber_drop_mag': bynumber_drop_mag,
            'drop_mag_filter': drop_mag_filter,
            'drop_mag_margin': drop_mag_margin,
            'drop_prev': drop_prev,
            'byticker_drop_prev': byticker_drop_prev,
            'bynumber_drop_prev': bynumber_drop_prev,
            'drop_prev_filter': drop_prev_filter,
            'drop_prev_margin': drop_prev_margin,
            'dropscore': dropscore,
            'byticker_dropscore': byticker_dropscore,
            'bynumber_dropscore': bynumber_dropscore,
            'dropscore_filter': dropscore_filter,
            'dropscore_margin': dropscore_margin,
            'maxdd': maxdd,
            'byticker_maxdd': byticker_maxdd,
            'bynumber_maxdd': bynumber_maxdd,
            'maxdd_filter': maxdd_filter,
            'maxdd_margin': maxdd_margin
        }}
        # create table
        botdf = bp.botfunc(brp)
        # delete temp files and folder
        delete_folder(getbotsinglerunfolder(brp['rootdir'], brp['testregimename'], brp['todaysdate'], brp['testnumber']))
    return botdf.to_dict('records')


# FULL RANK GRAPH
@app.callback(
    Output(f'fullranking_graph_{bp.botid}', 'figure'),
    Input(f"bptable_{bp.botid}", 'data'),
    Input(f"hovermode_fullranking_graph_{bp.botid}", 'value')
    )
def gen_fullrankgraph(dfdata, hovermode):
    if dfdata and len(pd.DataFrame.from_records(dfdata).columns) > 1:
        botdf = pd.DataFrame.from_records(dfdata)
        fig = px.line(botdf, x='stock', y=[i for i in botdf.columns if i != 'STOCK'], markers=False)
        fig.update_layout(transition_duration=500, legend_title_text='Attribute', hovermode=hovermode, uirevision='some-constant')
    else:
        fig = px.line([0])
    return fig


# generate tickerlist for performance graph
@app.callback(
    Output(f'perf_graph_ticker_{bp.botid}', 'options'),
    Input(f"bptable_{bp.botid}", 'data')
    )
def gen_perf_graph_tickerlist(dfdata):
    return pd.DataFrame.from_records(dfdata)['stock'].tolist() if dfdata else []


# gen performance graphs
@app.callback(
    Output(f"perf_graph_{bp.botid}", "figure"),
    Output(f"graphdiff_{bp.botid}", "figure"),
    Output(f"graphcomp_{bp.botid}", "figure"),
    Output(f"sourcetable_{bp.botid}", "data"),
    Input(f"perf_graph_ticker_{bp.botid}", "value"),
    Input(f"datepicker_{bp.botid}", 'start_date'),
    Input(f"datepicker_{bp.botid}", 'end_date'),
    Input(f"calib_{bp.botid}", "value"),
    Input(f"contour_{bp.botid}", "value"),
    Input(f"graphcompoptions_{bp.botid}", "value"),
    Input(f"graphdiff_mode_{bp.botid}", "value"),
    Input(f"graphdiff_changecol_{bp.botid}", "value"),
    Input(f"graphdiff_period_{bp.botid}", "value"),
    Input(f"bench_{bp.botid}", 'value'),
    Input(f"hovermode_{bp.botid}", 'value')
    )
def gen_graph(ticker, start_date, end_date, calib, contour, graphcomp, gdm, gdc, gdp, bench, hovermode):
    if ticker:
        portfolio = ticker.copy()
        df = pricedf_daterange(ticker[0], start_date, end_date)
        for t in ticker[1:]:
            df = df.join(pricedf_daterange(t, start_date, end_date).set_index('date'), how="left", on="date")
        df.sort_values(by='date', inplace=True)
        df.reset_index(inplace=True, drop=True)
        for b in bench:
            bdf = pricedf_daterange(b, start_date, end_date)
            bdf.rename(columns={b: f'bench_{b}'}, inplace=True)
            df = df.join(bdf.set_index('date'), how="left", on="date")
        ticker += [f'bench_{b}' for b in bench]
        if calib == 'normalize':
            df[ticker] = df[ticker].apply(lambda x: convertpricearr(x, 'norm1'))
        df = add_calibratedprices_portfolio(df, contour, ticker)
        if len(contour) > 0:
            ticker += [f'{t}_{c}' for c in contour for t in ticker]
        if graphcomp:
            gc_inputs = graphcomp.split(" ")
            gcomp_portfolio = portfolio+[f'bench_{b}' for b in bench]
            df = add_comparisons_portfolio(df, gc_inputs[0], gc_inputs[1], gcomp_portfolio)
            compgraphcols = [f'{s}_{gc_inputs[0]}to{gc_inputs[1]}' for s in gcomp_portfolio]
        else:
            compgraphcols = None
        df, sourcecols = add_pdiffpctchange_portfolio(df, gdc, gdp, gdm, ticker)
        diffgraphcols = [f'{s}_{gdp}d_{gdm}' for s in sourcecols]
    else:
        df = pd.DataFrame(data={'date': pd.date_range(benchmarkdata['dow']["earliestdate"], benchmarkdata['dow']["latestdate"]), '$': 0})
        compgraphcols, diffgraphcols, ticker = '$', '$', '$'
    fig = px.line(df, x='date', y=ticker, markers=False)
    fig.update_layout(transition_duration=500, legend_title_text='Ticker', hovermode=hovermode, uirevision='some-constant')
    fig.update_traces(hovertemplate='date=%{x|%Y-%m-%d}<br>value=%{y}')
    fig_diff = px.line(df, x='date', y=diffgraphcols, markers=False)
    fig_diff.update_layout(transition_duration=500, legend_title_text='Ticker', hovermode=hovermode, uirevision='some-constant')
    fig_diff.update_traces(hovertemplate='date=%{x|%Y-%m-%d}<br>value=%{y}')
    fig_comp = px.line(df, x='date', y=compgraphcols, markers=False)
    fig_comp.update_layout(transition_duration=500, legend_title_text='Ticker', hovermode=hovermode, uirevision='some-constant')
    fig_comp.update_traces(hovertemplate='date=%{x|%Y-%m-%d}<br>value=%{y}')
    return fig, fig_diff, fig_comp, df.to_dict('records')


# create options for diffgraph and comp graph
@app.callback(
    Output(f"graphcompoptions_{bp.botid}", "options"),
    Output(f"graphdiff_changecol_{bp.botid}", "options"),
    Output(f"graphdiff_changecol_{bp.botid}", "value"),
    Input(f"contour_{bp.botid}", "value")
    )
def show_diffgraph_options(contour):
    if len(contour) == 0:
        return [], ['rawprice'], 'rawprice'
    else:
        p = permutations(contour + ['rawprice'], 2)
        return [{'label': f'{i[0]} to {i[1]}', 'value': f'{i[0]} {i[1]}'} for i in p], ['all', 'rawprice']+contour, 'all'
