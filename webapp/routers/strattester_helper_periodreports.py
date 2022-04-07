from dash import html
from webapp.dashinputs import dash_inputbuilder


def gen_periodreports(stockperfdfreports, botid):
    return [
        html.Div([
            html.H2(f'Holding Period: {k}'),
            html.Div([html.Div([html.Span(j), html.Br()]) for j in v['report']]),
            dash_inputbuilder({
                'data': v['stockperfdf'].to_dict('records'),
                'inputtype': 'table',
                'id': f"perftable{k}_{botid}"
                })
                ]) for k, v in stockperfdfreports.items()
            ]
