"""
Title: Competitive Edge Bot Endpoint
Date Started: Feb 1, 2022
Version: 1.00
Version Start: Feb 1, 2022
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose:
"""
# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
#   THIRD PARTY IMPORTS
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dashappobject import app
import plotly.express as px
#   LOCAL APPLICATION IMPORTS
from ..dashinputs import prompt_builder, gen_tablecontents
from ..botclasses import BotParams
from Modules.referencetools.businessmodel.businessmodelbot_base import comp_edge_needed, gen_fundprofiles, gen_fund_df, gen_edgeratedf
from ..os_functions import get_currentscript_filename

bp = BotParams(
    get_currentscript_filename(__file__),
    'Competitive Edge Bot',
    "The Competitive Edge Bot returns the hypothetical growth rate your fund must achieve if you want to win over clients as compared to a competitor.",
    comp_edge_needed
)
tbodydata = [
    {
        'id': f'name_you_{bp.botid}',
        'prompt': 'Name your fund.',
        'placeholdertext': 'name of your fund',
        'inputtype': 'text'
        },
    {
        'id': f'name_comp_{bp.botid}',
        'prompt': "Name your competitor's fund.",
        'placeholdertext': 'name of comp fund',
        'inputtype': 'text'
        },
    {
        'id': f'client_principal_{bp.botid}',
        'prompt': 'Enter an amount a client wants to invest.',
        'placeholdertext': '$ client principal',
        'inputtype': 'number',
        'min': 1
        },
    {
        'id': f'num_clients_{bp.botid}',
        'prompt': 'Enter the number of clients your fund would have.',
        'placeholdertext': '# of your clients',
        'inputtype': 'number',
        'min': 1,
        'step': 1
        },
    {
        'id': f'comp_num_clients_{bp.botid}',
        'prompt': 'Enter the number of clients your competitor would have.',
        'placeholdertext': '# of comp clients',
        'inputtype': 'number',
        'min': 1,
        'step': 1
        },
    {
        'id': f'perf_cut_{bp.botid}',
        'prompt': 'Your performance rate fee.  Enter the portion of gains your clients earn that would go to you.',
        'details':  "For example, if your client money grew by $100, and you entered 0.25, your cut would be 25% of that gain, or $25.",
        'placeholdertext': 'your perf fee rate',
        'inputtype': 'number',
        'min': 0
        },
    {
        'id': f'comp_perf_cut_{bp.botid}',
        'prompt': 'Competitor performance rate fee.  Enter the portion of gains competitor clients earn that would go to the competitor.',
        'placeholdertext': 'comp perf fee rate',
        'inputtype': 'number',
        'min': 0
        },
    {
        'id': f'aum_rate_{bp.botid}',
        'prompt': "Your AUM Rate. Enter the proportion of the client's principal that would go to you as a fee for managing their investments.",
        'details': "For example, if you entered 0.05, 5% of the client principal would be charged to client).  AUM stands for assets under management.",
        'placeholdertext': 'your AUM rate',
        'inputtype': 'number',
        'min': 0
        },
    {
        'id': f'comp_aum_rate_{bp.botid}',
        'prompt': 'Competitor AUM Rate.  The rate your competitor would charge their client for managing their assets.',
        'placeholdertext': 'comp AUM rate',
        'inputtype': 'number',
        'min': 0
        },
    {
        'id': f'mkt_perf_{bp.botid}',
        'prompt': 'Enter hypothetical performance of the market.',
        'details': 'This is for comparison purposes, so you can compare how you and your competitors did against a hypothetical market.  If you entered 0.12, for example, the market growth rate would be 12% over the time period being considered.',
        'placeholdertext': 'market growth rate',
        'inputtype': 'number',
        },
    {
        'id': f'your_perf_{bp.botid}',
        'prompt': 'Enter how well your fund performed over the time period being considered.',
        'details': 'For example, entering 0.18 is the equivalent to 18%.',
        'placeholdertext': 'your growth rate',
        'inputtype': 'number',
        },
    {
        'id': f'comp_perf_{bp.botid}',
        'prompt': "Enter how well your competitor's fund performed over the time period being considered.",
        'details': 'For example, entering 0.18 is the equivalent to 18%.',
        'placeholdertext': 'comp growth rate',
        'inputtype': 'number',
        },
    {
        'id': f'switch_factor_{bp.botid}',
        'prompt': "Enter a switch factor.  This is an amount more that a competitor client would need to earn with your fund for them to switch to your fund.  For example, if you entered 0.20, to convince the client to switch to your fund, the client would have to earn 20% more (after fees paid) than they would with competitor.",
        'details': 'For example, if the switch factor was 0.05, and the client grew his money by $100 investing through the competitor after all fees were paid, then for the client to go with your fund, the client would need to have earned 5% more than that, or $5 (0.05 of $100), for a total gain of $105. If the client earned only $102 through your fund, that means the client would not switch to you because they would have earned only $2 more, or 2%, which is less than the 5% switch factor.',
        'placeholdertext': 'enter switch factor',
        'inputtype': 'number',
        'min': 0
        },
    {
        'id': f'overhead_cost_{bp.botid}',
        'prompt': 'Your overhead costs.  Enter the total overhead cost you would incur over the time period being considered.',
        'placeholdertext': '$ your overhead',
        'inputtype': 'number',
        'min': 0
        },
    {
        'id': f'comp_overhead_cost_{bp.botid}',
        'prompt': 'Competitor overhead costs.  Enter the total overhead cost competitor would incur over the time period being considered',
        'placeholdertext': '$ comp overhead',
        'inputtype': 'number',
        'min': 0
        },
    {
        'id': f'perf_fee_regime_{bp.botid}',
        'prompt': 'Your Performance Fee Regime.  Choose a performance fee regime for your fund.  A performance fee regime determines under which circumstances your fund earns a fee based on how well the fund performs.  The perf fee rate determined above determines the amount.  "v1" is a world where the fund does not earn a performance fee if the fund is losing money or it is losing against the market.  The fund would instead pay the client the amount by which the fund is losing against the market, or if the fund is at a loss but still beating the market, it will pay the client to make them whole.  "v2" is a world where a performance fee is paid regardless whether the fund is losing money or not so long as it is beating the market.  "v3" is a world where a performance fee is paid only if the fund grows and beats the market.  Whichever option you choose, the performance fee calculated for when the fund earns a fee is determined by the performance cut rate you selected.',
        'inputtype': 'dropdown',
        'options': ['v1', 'v2', 'v3'],
        'placeholder': 'your perf fee regime'
        },
    {
        'id': f'comp_perf_fee_regime_{bp.botid}',
        'prompt': 'Competitor Performance Fee Regime. Choose a performance fee regime for the competitor fund.',
        'inputtype': 'dropdown',
        'options': ['v1', 'v2', 'v3'],
        'placeholder': 'comp perf fee regime'
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
    html.Div([
        html.Div(id=f'compedgereport_{bp.botid}'),
        dcc.Markdown(id=f'fundperfdf_{bp.botid}'),
        dcc.Graph(id=f"graph_edgerate_{bp.botid}"),
        html.Div([
            html.Span(id=f"you_perf_slidelabel_{bp.botid}"),
            dcc.Slider(-1, 1, step=0.01, marks=None, id=f"you_perf_{bp.botid}", tooltip={"placement": "bottom", "always_visible": True})
        ])
    ], id=f'output_{bp.botid}')
])


@app.callback(
    Output(f'compedgereport_{bp.botid}', 'children'),
    Output(f'fundperfdf_{bp.botid}', 'children'),
    Output(f'you_perf_{bp.botid}', 'value'),
    Output(f'you_perf_slidelabel_{bp.botid}', 'children'),
    Input(f'submitbutton_{bp.botid}', 'n_clicks'),
    State(f'name_you_{bp.botid}', "value"),
    State(f'name_comp_{bp.botid}', "value"),
    State(f'client_principal_{bp.botid}', "value"),
    State(f'num_clients_{bp.botid}', "value"),
    State(f'comp_num_clients_{bp.botid}', "value"),
    State(f'perf_cut_{bp.botid}', "value"),
    State(f'comp_perf_cut_{bp.botid}', "value"),
    State(f'aum_rate_{bp.botid}', "value"),
    State(f'comp_aum_rate_{bp.botid}', "value"),
    State(f'mkt_perf_{bp.botid}', "value"),
    State(f'your_perf_{bp.botid}', "value"),
    State(f'comp_perf_{bp.botid}', "value"),
    State(f'switch_factor_{bp.botid}', "value"),
    State(f'overhead_cost_{bp.botid}', "value"),
    State(f'comp_overhead_cost_{bp.botid}', "value"),
    State(f'perf_fee_regime_{bp.botid}', "value"),
    State(f'comp_perf_fee_regime_{bp.botid}', "value"),
    prevent_initial_call=True
    )
def calc_compedge_analysis(
        n_clicks,
        your_name,
        comp_name,
        client_principal,
        num_clients,
        comp_num_clients,
        perf_cut,
        comp_perf_cut,
        aum_rate,
        comp_aum_rate,
        mkt_perf,
        your_perf,
        comp_perf,
        switch_factor,
        overhead_cost,
        comp_overhead_cost,
        perf_fee_regime,
        comp_perf_fee_regime
        ):
    # form bot run-specific parameters ('brp').
    brp = {
        'your_name': your_name,
        'comp_name': comp_name,
        'client_principal': client_principal,
        'num_clients': num_clients,
        'comp_num_clients': comp_num_clients,
        'perf_cut': perf_cut,
        'comp_perf_cut': comp_perf_cut,
        'aum_rate': aum_rate,
        'comp_aum_rate': comp_aum_rate,
        'mkt_perf': mkt_perf,
        'your_perf': your_perf,
        'comp_perf': comp_perf,
        'switch_factor': switch_factor,
        'overhead_cost': overhead_cost,
        'comp_overhead_cost': comp_overhead_cost,
        'perf_fee_regime': perf_fee_regime,
        'comp_perf_fee_regime': comp_perf_fee_regime
    }
    # get func output
    your_fund, comp_fund, mkt_fund = gen_fundprofiles(brp)
    compedgereport = bp.botfunc(brp)
    fundperfdf = gen_fund_df([your_fund, comp_fund, mkt_fund])
    return [html.P(i) for i in compedgereport], dcc.Markdown(fundperfdf.to_markdown()), your_perf, f'{your_name} Perf Rate'


@app.callback(
    Output(f'graph_edgerate_{bp.botid}', 'figure'),
    Input(f'name_you_{bp.botid}', "value"),
    Input(f'name_comp_{bp.botid}', "value"),
    Input(f'client_principal_{bp.botid}', "value"),
    Input(f'num_clients_{bp.botid}', "value"),
    Input(f'comp_num_clients_{bp.botid}', "value"),
    Input(f'perf_cut_{bp.botid}', "value"),
    Input(f'comp_perf_cut_{bp.botid}', "value"),
    Input(f'aum_rate_{bp.botid}', "value"),
    Input(f'comp_aum_rate_{bp.botid}', "value"),
    Input(f'mkt_perf_{bp.botid}', "value"),
    Input(f'comp_perf_{bp.botid}', "value"),
    Input(f'switch_factor_{bp.botid}', "value"),
    Input(f'overhead_cost_{bp.botid}', "value"),
    Input(f'comp_overhead_cost_{bp.botid}', "value"),
    Input(f'perf_fee_regime_{bp.botid}', "value"),
    Input(f'comp_perf_fee_regime_{bp.botid}', "value"),
    Input(f"you_perf_{bp.botid}", "value"),
    prevent_initial_call=True
    )
def update_edgerategraph(
        your_name,
        comp_name,
        client_principal,
        num_clients,
        comp_num_clients,
        perf_cut,
        comp_perf_cut,
        aum_rate,
        comp_aum_rate,
        mkt_perf,
        comp_perf,
        switch_factor,
        overhead_cost,
        comp_overhead_cost,
        perf_fee_regime,
        comp_perf_fee_regime,
        new_you_perf
        ):
    new_brp = {
        'your_name': your_name,
        'comp_name': comp_name,
        'client_principal': client_principal,
        'num_clients': num_clients,
        'comp_num_clients': comp_num_clients,
        'perf_cut': perf_cut,
        'comp_perf_cut': comp_perf_cut,
        'aum_rate': aum_rate,
        'comp_aum_rate': comp_aum_rate,
        'mkt_perf': mkt_perf,
        'your_perf': new_you_perf,
        'comp_perf': comp_perf,
        'switch_factor': switch_factor,
        'overhead_cost': overhead_cost,
        'comp_overhead_cost': comp_overhead_cost,
        'perf_fee_regime': perf_fee_regime,
        'comp_perf_fee_regime': comp_perf_fee_regime
    }
    graphdf = gen_edgeratedf(new_you_perf, 100, -1, 1, new_brp)
    fig = px.line(graphdf, x=f'{comp_name} perfrate', y=['under/over_performing', f'{new_brp["your_name"]} perfrate needed', 'edgerate needed'], markers=False)
    fig.update_layout(transition_duration=500, legend_title_text='Edge Rate')
    return fig
