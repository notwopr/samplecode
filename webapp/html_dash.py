from dash import html
from formatting import format_stats_leftcols, format_stats_rightcols


# where row input is a key, value pair
def gen_tablerow_footer(k, v):
    return html.Tr([
            html.Td(html.Small(k), className=format_stats_leftcols),
            html.Td(html.Small(v), className=format_stats_rightcols)
        ])


# generate list of html.Tr() objects from dictionary
def gen_trlist_from_dict_footer(d):
    return [gen_tablerow_footer(k, v) for k, v in d.items()]


# where row input is a key, value pair
def gen_tablerow(k, v):
    return html.Tr([
            html.Td(k),
            html.Td(v)
        ])


# generate list of html.Tr() objects from dictionary
def gen_trlist_from_dict(d):
    return [gen_tablerow(k, v) for k, v in d.items()]


# generate table from list of html.Tr() objects
def gen_htmltable(trlist):
    return html.Table(html.Tbody(trlist))
