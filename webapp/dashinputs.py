from dash import dcc, html, dash_table
from webapp.regex import wordorwords_singlespaced
from formatting import buttonclass, textinputboxes, format_htmltable_leftcols, format_htmltable_rightcols, format_dropdown, format_radio_button, format_radio_label, format_checklist_boxes, format_checklist_label


def dash_inputbuilder(c):
    if c['inputtype'] == 'text':
        return dcc.Input(
                id=c['id'],
                type='text',
                placeholder=c.get('placeholdertext', 'Type here'),
                pattern=c.get('pattern', wordorwords_singlespaced),
                className=textinputboxes
                )
    elif c['inputtype'] == 'password':
        return dcc.Input(
                id=c['id'],
                type='password',
                placeholder=c.get('placeholdertext', 'Type here'),
                className=c.get('className')
                )
    elif c['inputtype'] == 'hidden':
        return dcc.Input(
                id=c['id'],
                type='hidden'
                )
    elif c['inputtype'] == 'number':
        return dcc.Input(
                id=c['id'],
                type='number',
                value=c.get('value'),
                placeholder=c.get('placeholdertext', 'Type here'),
                debounce=c.get('debounce'),
                min=c.get('min', None),
                max=c.get('max', None),
                step=c.get('step', 'any'),
                className=textinputboxes
                )
    elif c['inputtype'] == 'dropdown':
        return dcc.Dropdown(
                id=c['id'],
                options=c.get('options'),
                multi=c.get('multi', False),
                placeholder=c.get('placeholder', 'Pick an option'),
                value=c.get('value'),
                clearable=c.get('clearable', False),
                searchable=c.get('searchable', False),
                className=format_dropdown,
                style={"min-width": "250px"}
                )
    elif c['inputtype'] == 'datepicker_range':
        return dcc.DatePickerRange(
                id=c['id'],
                min_date_allowed=c.get('min_date_allowed'),
                max_date_allowed=c.get('max_date_allowed'),
                start_date_placeholder_text=c.get('placeholdertext_sd', 'start date'),
                end_date_placeholder_text=c.get('placeholdertext_ed', 'end date'),
                display_format='YYYY-MM-DD',
                clearable=c.get('clearable', False),
                with_portal=c.get('with_portal', False)
                )
    elif c['inputtype'] == 'datepicker_single':
        return dcc.DatePickerSingle(
                id=c['id'],
                date=c.get('date'),
                min_date_allowed=c.get('min_date_allowed'),
                max_date_allowed=c.get('max_date_allowed'),
                placeholder=c.get('placeholder', 'choose date'),
                calendar_orientation=c.get('orientation', 'horizontal'),
                display_format='YYYY-MM-DD',
                clearable=c.get('clearable', False),
                with_portal=c.get('with_portal', False)
                )
    elif c['inputtype'] == 'button_submit':
        return html.Button(
                id=c['id'],
                n_clicks=0,
                children=c.get('buttontext', 'Submit'),
                type='button',
                className=buttonclass
                )
    elif c['inputtype'] == 'checklist':
        return dcc.Checklist(
                id=c['id'],
                options=c.get('options'),
                value=c.get('value', []),
                labelStyle={'display': c.get('inline', 'block')},
                className=c.get('className'),
                inputClassName=format_checklist_boxes,
                labelClassName=format_checklist_label
                )
    elif c['inputtype'] == 'radio':
        return dcc.RadioItems(
                id=c['id'],
                options=c.get('options'),
                value=c.get('value', []),
                labelStyle={'display': c.get('inline', 'block')},
                inputClassName=format_radio_button,
                labelClassName=format_radio_label
                )
    elif c['inputtype'] == 'rangeslider':
        return dcc.RangeSlider(
                id=c['id'],
                min=c.get('min'),
                max=c.get('max'),
                step=c.get('step'),
                value=c.get('value'),
                marks=c.get('marks'),
                tooltip=c.get('tooltip', {"placement": "bottom", "always_visible": True})
                )
    elif c['inputtype'] == 'slider':
        return dcc.Slider(
                id=c['id'],
                min=c.get('min'),
                max=c.get('max'),
                step=c.get('step'),
                value=c.get('value'),
                marks=c.get('marks'),
                tooltip=c.get('tooltip', {"placement": "bottom", "always_visible": True})
                )
    elif c['inputtype'] == 'table':
        return dash_table.DataTable(
                data=c.get('data'),
                tooltip_duration=None,
                sort_action='custom',
                sort_mode='single',
                columns=c.get('columns'),
                filter_action=c.get('filtering', 'none'),
                #fixed_rows={'headers': True, 'data': 0},
                sort_by=[],
                id=c['id']
            )
    elif c['inputtype'] == 'textarea':
        return dcc.Textarea(
                id=c['id'],
                value=c.get('value'),
                style={'width': '100%', 'height': 300}
            )


def prompt_builder(c):
    return html.Div([
        html.Span(c.get('prompt'), id=f'prompt_{c["id"]}'),
        html.Br(),
        dash_inputbuilder(c)
    ])


def gen_tablerow(r):
    return html.Tr([
            html.Td(dash_inputbuilder(r), id=f'inputfield_{r["id"]}', className=format_htmltable_leftcols),
            html.Td(r.get('prompt'), id=f'prompt_{r["id"]}', className=format_htmltable_rightcols)
        ], title=r.get('details'))


def gen_tablecontents(tbodydata):
    return html.Tbody([gen_tablerow(r) for r in tbodydata])
