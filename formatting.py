import dash_bootstrap_components as dbc
# external
external_stylesheets = [
    dbc.themes.ZEPHYR,
    "https://fonts.googleapis.com/css2?family=Fredoka&display=swap",
    "https://fonts.googleapis.com/css2?family=Bayon&display=swap",
    "https://fonts.googleapis.com/css2?family=Oswald:wght@500&display=swap",
    "https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap",
    "https://fonts.googleapis.com/css2?family=Sanchez&display=swap"
    ]


# UNIVERSAL ELEMENTS
shadow = 'shadow-lg'
sectionpadding = 'p-3'
sectionmargin = 'ms-4 me-4 mb-4 mt-4'
paper_color = 'paper'
wallpaper_color = ''

# font
banner_text = 'fw-bold darkgrey_txt display-1 font_banner'
text_dark_thick = 'fw-bold charcoal_txt display-3'
format_heading_txt = 'fw-bold font_heading display-5'

# HTML TABLES
format_htmltable_leftcols = 'pe-2 pb-1 pt-1 bg-transparent'
format_htmltable_rightcols = 'ps-3 pb-1 pt-1 bg-transparent'
format_htmltable_row = 'border border-light d-flex mb-3 shadow-lg rounded-1 bg-white'

# WINDOW
format_window = ''

# LOGIN PAGE
format_success_global = f'{paper_color} {sectionmargin} {sectionpadding} {shadow}'
format_navbar = f'{format_success_global} hstack gap-3'
format_top = f'{format_success_global}'
format_main = f'{format_success_global}'
format_footer = f'{format_success_global}'
format_banner = f'{banner_text} w-100 text-end'
format_loginbody = 'position-absolute top-50 start-50 translate-middle'
format_loginbody_elements = 'hstack gap-3'
format_stats_leftcols = 'pe-3'
format_stats_rightcols = 'ps-3 text-info'

# MISC ASSETS
format_tabs = 'bg-white'
buttonclass = 'btn btn-outline-dark m-1'
formaltextinput = 'border border-4 rounded-pill ps-3'
textinputboxes = 'border border-1 rounded-3 ms-2 me-2 mb-1 mt-1 w-100'
format_datatables = 'table table-hover'
format_dropdown = 'rounded-3 ms-2 me-2 mb-1 mt-1 w-auto'
format_radio_button = 'me-1'
format_radio_label = 'me-3'
format_checklist_boxes = 'me-1'
format_checklist_label = 'me-3'
format_logincopyright = 'fw-bold offwhite_txt font_logincopyright fs-3 bg-transparent position-absolute bottom-0 start-0 ps-2 m-0 fixed-bottom'
