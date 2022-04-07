"""
Title: Price Graph Explorer
Date Started: Feb 3, 2022
Version: 1.00
Version Start: Feb 3, 2022
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose:  .

"""
# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
from itertools import permutations
#   THIRD PARTY IMPORTS
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output
from dashappobject import app
import plotly.express as px
import pandas as pd
import numpy as np
from webapp.servernotes import getstockdata
#   LOCAL APPLICATION IMPORTS
from Modules.dataframe_functions import filtered_double, filtered_single
from Modules.datetime_functions import from_pts_to_dtdate
from Modules.price_history_slicing import pricedf_daterange
from Modules.price_calib import convertpricearr, add_calibratedprices_portfolio
from .pricehistoryexplorer_helper_diffcomp import add_comparisons_portfolio, add_pdiffpctchange_portfolio
from .pricehistoryexplorer_helper_volstats import getallmetricvalsdf
from .pricehistoryexplorer_helper_volstats_definitions import volstat_definitions
from ..botclasses import BotParams
from ..os_functions import get_currentscript_filename
from ..common_resources import tickers, staticmindate, staticmaxdate
from ..dashinputs import gen_tablecontents, prompt_builder, dash_inputbuilder
from ..datatables import sort_datatable
from formatting import format_tabs


bp = BotParams(
    get_currentscript_filename(__file__),
    'Price Explorer',
    "Display the price graphs of any NYSE/NASDAQ stock and index.",
    None
)

# set date index dictionary and base df; otherwise cannot update graph with date range slider, because it requires storing data between callbacks which requires JSONifying.
eldate = getstockdata()
mdf = pd.DataFrame().reindex(pd.date_range(eldate["earliest"], eldate["latest"]))
mdf.reset_index(inplace=True)
mdf.rename(columns={'index': 'date'}, inplace=True)
mdf['date'] = mdf['date'].apply(lambda x: from_pts_to_dtdate(x))
mdf['$'] = 0

tbodydata = [
    {
        'id': f'ticker_{bp.botid}',
        'prompt': 'Select or Search for a Ticker(s).',
        'inputtype': 'dropdown',
        'options': tickers,
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
        'id': f'portcurve_{bp.botid}',
        'prompt': '[*only available when normalized pricing is chosen and more than one stock is selected.  This option shows an aggregate growth curve of all selected stocks.]',
        'inputtype': 'checklist',
        'options': []
        },
    {
        'id': f'sd_{bp.botid}',
        'prompt': 'Choose a different start date. The current graphs are "cut" to that new start date. Helpful when using the normalized price view.',
        'inputtype': 'datepicker_single',
        'clearable': True,
        'min_date_allowed': staticmindate,
        'max_date_allowed': staticmaxdate
        },
    {
        'id': f'sd_bydd_{bp.botid}',
        'prompt': 'Or choose one of the start dates of one of the tickers already graphed.',
        'inputtype': 'dropdown',
        'options': [],
        'placeholder': 'Choose a start date',
        'multi': False,
        'clearable': True
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
        html.Table(gen_tablecontents(tbodydata), style={'width': '100%'}),
    ], id=f'input_{bp.botid}'),
    html.Div([
        html.Div(dash_inputbuilder({
            'inputtype': 'table',
            'id': f"sourcetable_{bp.botid}"
            }), id=f"hidden_{bp.botid}", hidden='hidden'),
        html.Div(dash_inputbuilder({
            'inputtype': 'table',
            'id': f"voltable_{bp.botid}"
            }), id=f"stats_{bp.botid}"),
        dcc.Tabs([
            dcc.Tab(label='Price History', children=[dcc.Graph(id=f"graph_{bp.botid}")], className=format_tabs),
            dcc.Tab(label='Periodic Change', children=[dcc.Graph(id=f"graphdiff_{bp.botid}")], className=format_tabs),
            dcc.Tab(label='Comparative', children=[dcc.Graph(id=f"graphcomp_{bp.botid}")], className=format_tabs),
            dcc.Tab(label='Raw Data', children=[dash_inputbuilder({
                'inputtype': 'table',
                'id': f"rawdata_{bp.botid}"
                })], className=format_tabs)
        ]),
        prompt_builder({
            'prompt': 'Date Range Slider',
            'id': f'dateslider_{bp.botid}',
            'inputtype': 'rangeslider',
            'min': 0,
            'max': len(mdf)-1,
            'value': [0, len(mdf)-1]
            })
        ], id=f'output_{bp.botid}')

])


@app.callback(
    Output(f"graph_{bp.botid}", "figure"),
    Output(f"graphdiff_{bp.botid}", "figure"),
    Output(f"graphcomp_{bp.botid}", "figure"),
    Output(f"dateslider_{bp.botid}", "min"),
    Output(f"sd_{bp.botid}", "min_date_allowed"),
    Output(f"sd_bydd_{bp.botid}", "options"),
    Output(f"sourcetable_{bp.botid}", "data"),
    Input(f"ticker_{bp.botid}", "value"),
    Input(f"calib_{bp.botid}", "value"),
    Input(f"sd_{bp.botid}", "date"),
    Input(f"sd_bydd_{bp.botid}", "value"),
    Input(f"contour_{bp.botid}", "value"),
    Input(f"graphcompoptions_{bp.botid}", "value"),
    Input(f"graphdiff_mode_{bp.botid}", "value"),
    Input(f"graphdiff_changecol_{bp.botid}", "value"),
    Input(f"graphdiff_period_{bp.botid}", "value"),
    Input(f"portcurve_{bp.botid}", "value"),
    Input(f"bench_{bp.botid}", 'value'),
    Input(f"dateslider_{bp.botid}", 'value'),
    Input(f"hovermode_{bp.botid}", 'value')
    )
def gen_graph(ticker, calib, sd, sd_bydd, contour, graphcomp, gdm, gdc, gdp, portcurve, bench, date, hovermode):
    if ticker:
        portfolio = ticker.copy()
        df = pricedf_daterange(ticker[0], '', '')
        for t in ticker[1:]:
            df = df.join(pricedf_daterange(t, '', '').set_index('date'), how="outer", on="date")
        df.sort_values(by='date', inplace=True)
        df.reset_index(inplace=True, drop=True)
        new_sd = str(df['date'].iloc[0].date())  # shift graph&slider to start at beginning of oldest selected stock
        all_sd = [{'label': f"{t}'s startdate", 'value': df['date'].iloc[sum(np.isnan(df[t]))]} for t in ticker]
        for b in bench:
            bdf = pricedf_daterange(b, '', '')
            bdf.rename(columns={b: f'bench_{b}'}, inplace=True)
            df = df.join(bdf.set_index('date'), how="left", on="date")
        ticker += [f'bench_{b}' for b in bench]
        if sd is not None:  # choose a diff start from datepicker
            df = filtered_single(df, '>=', sd, 'date')
            df.reset_index(drop=True, inplace=True)
        if sd_bydd is not None:  # choose a diff start from selected stocks list
            df = filtered_single(df, '>=', sd_bydd, 'date')
            df.reset_index(drop=True, inplace=True)
        if calib == 'normalize':
            df[ticker] = df[ticker].apply(lambda x: convertpricearr(x, 'norm1'))
            if len(ticker) > 1 and 'portcurve' in portcurve:
                df['portcurve'] = df[ticker].mean(axis=1)
                ticker += ['portcurve']
        df = add_calibratedprices_portfolio(df, contour, ticker)
        if len(contour) > 0:
            ticker += [f'{t}_{c}' for c in contour for t in ticker]
        if graphcomp:
            gc_inputs = graphcomp.split(" ")
            gcomp_portfolio = portfolio+[f'bench_{b}' for b in bench]+['portcurve'] if 'portcurve' in ticker else portfolio+[f'bench_{b}' for b in bench]
            df = add_comparisons_portfolio(df, gc_inputs[0], gc_inputs[1], gcomp_portfolio)
            compgraphcols = [f'{s}_{gc_inputs[0]}to{gc_inputs[1]}' for s in gcomp_portfolio]
        else:
            compgraphcols = None
        df, sourcecols = add_pdiffpctchange_portfolio(df, gdc, gdp, gdm, ticker)
        diffgraphcols = [f'{s}_{gdp}d_{gdm}' for s in sourcecols]
        new_min = mdf.index[mdf['date'] == df['date'].iloc[0].date()].tolist()[0]
        filterdf = filtered_double(df, '>=<=', str(mdf['date'][date[0]]), str(mdf['date'][date[1]]), 'date')
    else:
        filterdf = mdf
        compgraphcols, diffgraphcols, ticker = '$', '$', '$'
        new_min = 0
        new_sd = staticmindate
        all_sd = []
    fig = px.line(filterdf, x='date', y=ticker, markers=False)#, template=chosenfigtemp)
    fig.update_layout(transition_duration=500, legend_title_text='Ticker', hovermode=hovermode, uirevision='some-constant')
    fig.update_traces(hovertemplate='date=%{x|%Y-%m-%d}<br>value=%{y}')
    fig_diff = px.line(filterdf, x='date', y=diffgraphcols, markers=False)#, template=chosenfigtemp)
    fig_diff.update_layout(transition_duration=500, legend_title_text='Ticker', hovermode=hovermode, uirevision='some-constant')
    fig_diff.update_traces(hovertemplate='date=%{x|%Y-%m-%d}<br>value=%{y}')
    fig_comp = px.line(filterdf, x='date', y=compgraphcols, markers=False)#, template=chosenfigtemp)
    fig_comp.update_layout(transition_duration=500, legend_title_text='Ticker', hovermode=hovermode, uirevision='some-constant')
    fig_comp.update_traces(hovertemplate='date=%{x|%Y-%m-%d}<br>value=%{y}')
    return fig, fig_diff, fig_comp, new_min, new_sd, all_sd, filterdf.to_dict('records')


@app.callback(
    Output(f"portcurve_{bp.botid}", "options"),
    Output(f"portcurve_{bp.botid}", "value"),
    Input(f"ticker_{bp.botid}", "value"),
    Input(f"calib_{bp.botid}", "value"),
    Input(f"portcurve_{bp.botid}", "value")
    )
def show_portcurve_option(ticker, calib, portcurvevalue):
    if ticker and calib == 'normalize' and len(ticker) > 1:
        return [
            {'label': 'Add portfolio graph', 'value': 'portcurve'}
        ], portcurvevalue

    else:
        return [], []


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


# sort raw data table
# sourcetable is a hidden html DIV where orig filterdf is stored to be used by voldf and rawdatatable tab
@app.callback(
    Output(f"rawdata_{bp.botid}", "data"),
    Input(f"rawdata_{bp.botid}", 'sort_by'),
    Input(f"rawdata_{bp.botid}", "data"),
    Input(f"sourcetable_{bp.botid}", "data")
    )
def sort_rawdatatable(sort_by, rawdatatable, sourcetable):
    if rawdatatable and callback_context.triggered[0]['prop_id'].endswith('sort_by'):
        # convert table back to dataframe
        filterdf = pd.DataFrame.from_records(rawdatatable)
        # because filterdf is converted to .to_dict('records') and then back from that; the date col type is changed to strings
        # as consequence have to change datecol back to original datatype: <class 'pandas._libs.tslibs.timestamps.Timestamp'>
        filterdf['date'] = filterdf['date'].apply(lambda x: pd.Timestamp(x))
        filterdf = sort_datatable(sort_by, filterdf)
        return filterdf.to_dict('records')
    else:
        return sourcetable


# get volstats
@app.callback(
    Output(f"voltable_{bp.botid}", "data"),
    Output(f"voltable_{bp.botid}", "tooltip_header"),
    Input(f"ticker_{bp.botid}", "value"),
    Input(f"portcurve_{bp.botid}", "value"),
    Input(f"bench_{bp.botid}", 'value'),
    Input(f"voltable_{bp.botid}", 'sort_by'),
    Input(f"voltable_{bp.botid}", "data"),
    Input(f"sourcetable_{bp.botid}", "data")
    )
def gen_volstats(ticker, portcurve, bench, sort_by, voldata, sourcetable):
    if voldata and callback_context.triggered[0]['prop_id'].endswith('sort_by'):
        # convert table back to dataframe
        voldf = pd.DataFrame.from_records(voldata)
        voldf = sort_datatable(sort_by, voldf)
        tooltip = {i: volstat_definitions[i] for i in voldf.columns[1:]}
    elif ticker:
        portfolio = ticker.copy()
        filterdf = pd.DataFrame.from_records(sourcetable)
        # because filterdf is converted to .to_dict('records') and then back from that; the date col type is changed to strings
        # as consequence have to change datecol back to original datatype: <class 'pandas._libs.tslibs.timestamps.Timestamp'>
        filterdf['date'] = filterdf['date'].apply(lambda x: pd.Timestamp(x))
        metdftickers = portfolio+[f'bench_{b}' for b in bench]+['portcurve'] if 'portcurve' in portcurve else portfolio+[f'bench_{b}' for b in bench]
        voldf = getallmetricvalsdf(filterdf, metdftickers, bench, str(filterdf.iat[0, 0].date()), str(filterdf.iat[-1, 0].date()))
        tooltip = {i: volstat_definitions[i] for i in voldf.columns[1:]}
    else:
        voldf = pd.DataFrame(data=['No ticker selected.'])
        tooltip = None
    return voldf.to_dict('records'), tooltip


'''
df = pricedf_daterange(ticker[0], '', '')
for t in ticker[1:]:
    df = df.join(pricedf_daterange(t, '', '').set_index('date'), how="outer", on="date")
df.sort_values(by='date', inplace=True)
df.reset_index(inplace=True, drop=True)
for b in bench:
    bdf = pricedf_daterange(b, '', '')
    bdf.rename(columns={b: f'bench_{b}'}, inplace=True)
    df = df.join(bdf.set_index('date'), how="left", on="date")
ticker += [f'bench_{b}' for b in bench]
if sd is not None:  # choose a diff start from datepicker
    df = filtered_single(df, '>=', sd, 'date')
    df.reset_index(drop=True, inplace=True)
if sd_bydd is not None:  # choose a diff start from selected stocks list
    df = filtered_single(df, '>=', sd_bydd, 'date')
    df.reset_index(drop=True, inplace=True)
if calib == 'normalize':
    df[ticker] = df[ticker].apply(lambda x: convertpricearr(x, 'norm1'))
    if len(ticker) > 1 and 'portcurve' in portcurve:
        df['portcurve'] = df[ticker].mean(axis=1)
        ticker += ['portcurve']
filterdf = filtered_double(df, '>=<=', str(mdf['date'][date[0]]), str(mdf['date'][date[1]]), 'date')
'''
