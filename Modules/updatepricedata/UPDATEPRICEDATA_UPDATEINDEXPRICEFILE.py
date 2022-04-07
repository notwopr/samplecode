import datetime as dt
import dateutil.parser as dup
from UPDATEPRICEDATA_FRED import indexpriceretrieval
import pandas as pd
from filelocations import readpkl, savetopkl


def indexpriceupdater(index, indexpricefolder):

    # RETRIEVE CURRENT INDEX PRICE FILE
    fileticker = index[1:]
    oldprices = readpkl(f'{fileticker}_prices', indexpricefolder)

    # GET LAST DATE AVAILABLE
    lastdaterecorded = oldprices.iloc[-1]['date']
    newstartdate = lastdaterecorded + dt.timedelta(days=1)

    # RETRIEVE ALL FRED PRICES
    fredprices = indexpriceretrieval(index, '', '')
    # CONVERT DATE COL TO DATETIME OBJECTS
    fredprices['date'] = fredprices['date'].apply(dup.parse)
    fredprices['date'] = fredprices['date'].apply(dt.datetime.date)
    # SLICE NEW FREDPRICES
    slicedfredprices = fredprices[fredprices['date'] >= newstartdate].copy()

    # IF NO NEW PRICES, SKIP
    if len(slicedfredprices) == 0:
        return
    else:
        # ADD NEW PRICES TO OLD PRICES
        combined = pd.concat([oldprices, slicedfredprices])
        combined.reset_index(drop=True, inplace=True)

        # SAVE TO FILE
        savetopkl(f"{fileticker}_prices", indexpricefolder, combined)
