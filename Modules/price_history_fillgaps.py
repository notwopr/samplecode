"""
Title: Fill Gap Bot
Date Started: Nov 10, 2019
Version: 1.1
Vers. Start: May 31, 2020
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose: Fill Gaps fill in NaN gaps in a price history dateframe.  Spun off from pricehistory bot.

Versions:
1.1: Correct error that would bfill dates that existed prior to beg_date.
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
#   THIRD PARTY IMPORTS
import pandas as pd
#   LOCAL APPLICATION IMPORTS


# FILL IN GAPS BETWEEN START AND END DATES OF A GIVEN STOCK'S PRICE HISTORY (dataframe)
def fill_gaps(pdf):

    # FILL MISSING DATES
    startdate = pdf['date'].iat[0]
    enddate = pdf['date'].iat[-1]
    newdateidx = pd.date_range(startdate, enddate)
    pdf = pdf.set_index('date').reindex(newdateidx)

    # ADD INDEX COL AND RENAME DATE COL; FILL FORWARD PRICES
    pdf.reset_index(inplace=True)
    pdf.rename(columns={'index': 'date'}, inplace=True)
    pdf = pdf.fillna(method='ffill')

    return pdf


# LIKE FILL GAPS BUT SPECIFIC DATES, IF BEGDATE BLANK, THEN TAKE STOCK'S EARLIEST AVAILABLE. IF END DATE BLANK, TAKE STOCK'S LATEST DATE AVAILABLE.
def fill_gaps2(pdf, beg_date, end_date):

    pdf = fill_gaps(pdf)

    # SLICE OUT DATE RANGE REQUESTED
    if beg_date != "" and end_date != "":
        pdf = pdf[(pdf['date'] <= end_date) & (pdf['date'] >= beg_date)]
    elif end_date != "":
        pdf = pdf[(pdf['date'] <= end_date)]
    elif beg_date != "":
        pdf = pdf[(pdf['date'] >= beg_date)]

    return pdf
