# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
#   THIRD PARTY IMPORTS
#   LOCAL APPLICATION IMPORTS
from Modules.price_history_slicing import pricedf_daterange
from Modules.dataframe_functions import filtered_single
from Modules.price_calib import add_calibratedprices
from Modules.list_functions import removedupes


def allmetrics_single(metrics_to_run, beg_date, end_date, stock):
    prices = pricedf_daterange(stock, beg_date, end_date)
    summary = {'stock': stock}
    allcalibrations = [item for metricitem in metrics_to_run.values() for item in metricitem['calibration']]
    allcalibrations = removedupes(allcalibrations)
    prices = add_calibratedprices(prices, allcalibrations, stock)
    for metricitem in metrics_to_run.values():
        metricname = metricitem['metricname']
        if metricname.startswith('growthrate'):
            focuscol = stock if metricitem['focuscol'] == 'rawprice' else metricitem['focuscol']
            metricparams = {'prices': prices.copy(), 'focuscol': focuscol}
        elif metricname.startswith('unifatscore') or metricname.startswith('unifatrawscore'):
            idealcol = stock if metricitem['idealcol'] == 'rawprice' else metricitem['idealcol']
            focuscol = stock if metricitem['focuscol'] == 'rawprice' else metricitem['focuscol']
            metricparams = {'prices': prices.copy(), 'focuscol': focuscol, 'idealcol': idealcol, 'stat_type': metricitem['stat_type']}
        elif metricname.startswith('drop_') or metricname.startswith('allpctdrop'):
            uppercol = stock if metricitem['uppercol'] == 'rawprice' else metricitem['uppercol']
            lowercol = stock if metricitem['lowercol'] == 'rawprice' else metricitem['lowercol']
            metricparams = {'prices': prices.copy(), 'uppercol': uppercol, 'lowercol': lowercol}
            if not metricname.startswith('drop_prev'):
                metricparams.update({'stat_type': metricitem['stat_type']})
        summary.update({metricname: metricitem['metricfunc'](**metricparams)})
    return summary


def filterallmetrics(allmetricsdf, metrics_to_run, configdict):
    # create copy df for purposes of getting threshvals. otherwise the filtered_df may not have all stocks available to grab the threshval requested
    threshvaldf = allmetricsdf.copy()
    for metricitem in metrics_to_run:
        colname = metrics_to_run[metricitem]['metricname']
        if configdict[metricitem] == 'byticker':
            threshval = threshvaldf[threshvaldf['stock'] == configdict[f'byticker_{metricitem}']][colname].item()
        elif configdict[metricitem] == 'bynumber':
            threshval = configdict[f'bynumber_{metricitem}']
        elif configdict[metricitem] == 'bybench':
            targetvals = threshvaldf[threshvaldf['stock'].isin(["^DJI", "^INX", "^IXIC"])][colname]
            threshval = max(targetvals) if metrics_to_run[metricitem]['better'] == 'bigger' else min(targetvals)
        if configdict[f'{metricitem}_margin']:
            if configdict[f'{metricitem}_filter'] in ['>', '>=']:
                threshval += configdict[f'{metricitem}_margin']
            elif configdict[f'{metricitem}_filter'] in ['<', '<=']:
                threshval -= configdict[f'{metricitem}_margin']
        allmetricsdf = filtered_single(allmetricsdf, configdict[f'{metricitem}_filter'], threshval, colname)
        if len(allmetricsdf) == 0:
            return allmetricsdf
    return allmetricsdf
