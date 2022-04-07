from dash import html
from webapp.dashinputs import dash_inputbuilder


# enter vstack if you want to stack vertically, hstack horizontally
def gen_rankcol_param_single(rcnum, botid):
    rankcolschema_standard = [
        {
            'id': f'rc{rcnum}_{botid}',
            'inputtype': 'dropdown',
            'options': [],
            'placeholder': 'Choose column',
            'searchable': True,
            'clearable': True
            },
        {
            'id': f'rc{rcnum}_weight_{botid}',
            'placeholdertext': 'column weight',
            'inputtype': 'number',
            'min': 0,
            'max': 1
            },
        {
            'id': f'rc{rcnum}_direct_{botid}',
            'options': [
                {'label': 'ascending', 'value': 1},
                {'label': 'descending', 'value': 0}
            ],
            'inputtype': 'dropdown',
            'placeholder': 'rank direction',
            'clearable': True
            }
    ]
    return html.Div([dash_inputbuilder(i) for i in rankcolschema_standard], className='d-flex')


def gen_rankconfig_htmlchildren(numrankcols, botid):
    return html.Div([gen_rankcol_param_single(i, botid) for i in range(numrankcols)], title='Choose a column to rank. Then, assign weight to that rank column (1 = 100%).  Lastly, indicate whether the column is ranked in ascending or descending order.')
