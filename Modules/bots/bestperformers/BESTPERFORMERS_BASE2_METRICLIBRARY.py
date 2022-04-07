from Modules.metriclibrary.STRATTEST_FUNCBASE_RAW import getpctchange_single
from Modules.metriclibrary.STRATTEST_FUNCBASE_MMBM import unifatshell_single, dropmag_single, dropprev_single, dropscore_single, allpctdrops_single

allmetrics = {
    'growthrate': {
            'metricname': 'growthrate',
            'metricfunc': getpctchange_single,
            'focuscol': 'rawprice',
            'calibration': [],
            'better': 'bigger'
        },
    'fatscore_baremaxtoraw': {
            'metricname': 'unifatscore_rawbaremaxraw_avg',
            'metricfunc': unifatshell_single,
            'focuscol': 'rawprice',
            'idealcol': 'baremaxraw',
            'stat_type': 'avg',
            'calibration': ['baremaxraw'],
            'better': 'smaller'
        },
    'fatscore_baremaxtobaremin': {
            'metricname': 'unifatscore_bareminbaremax_avg',
            'metricfunc': unifatshell_single,
            'focuscol': 'oldbareminraw',
            'idealcol': 'baremaxraw',
            'stat_type': 'avg',
            'calibration': ['oldbareminraw', 'baremaxraw'],
            'better': 'smaller'
        },
    'drop_mag': {
            'metricname': 'drop_mag_avg',
            'metricfunc': dropmag_single,
            'uppercol': 'baremaxraw',
            'lowercol': 'rawprice',
            'stat_type': 'avg',
            'calibration': ['baremaxraw'],
            'better': 'bigger'
        },
    'drop_prev': {
            'metricname': 'drop_prev',
            'metricfunc': dropprev_single,
            'uppercol': 'baremaxraw',
            'lowercol': 'rawprice',
            'calibration': ['baremaxraw'],
            'better': 'smaller'
        },
    'dropscore': {
            'metricname': 'drop_score',
            'metricfunc': dropscore_single,
            'uppercol': 'baremaxraw',
            'lowercol': 'rawprice',
            'stat_type': 'avg',
            'calibration': ['baremaxraw'],
            'better': 'bigger'
        },
    'maxdd': {
            'metricname': 'allpctdrop_rawbaremaxraw_max',
            'metricfunc': allpctdrops_single,
            'calibration': ['baremaxraw'],
            'uppercol': 'baremaxraw',
            'lowercol': 'rawprice',
            'stat_type': 'min',
            'better': 'bigger'
        }
}
