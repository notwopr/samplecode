"""
Title: Dates functions.
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import datetime as dt
#   THIRD PARTY IMPORTS
#   LOCAL APPLICATION IMPORTS


# RETURNS INTEGER DIFFERENCE IN DAYS BETWEEN datetime object DATES
def num_days(beg_date, end_date):
    return (end_date - beg_date).days


# RETURNS INTEGER DIFFERENCE IN DAYS BETWEEN TWO STRING DATES
def num_days_string(beg_date, end_date):
    return num_days(dt.date.fromisoformat(beg_date), dt.date.fromisoformat(end_date))


# RETURN STRING DATE GIVEN DATE MINUS/PLUS SOME INTEGER
def plusminusdays(date, integer, mode):
    if mode == 'subtract':
        return str(dt.date.fromisoformat(date) - dt.timedelta(days=integer))
    elif mode == 'add':
        return str(dt.date.fromisoformat(date) + dt.timedelta(days=integer))
