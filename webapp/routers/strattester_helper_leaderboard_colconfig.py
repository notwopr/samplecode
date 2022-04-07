nonrankcols = [
    'todaysdate',
    'testnumber',
    'runtime',
    'runtimeperperiod',
    'strat_name',
    'min_preath_age',
    'investperiod',
    'num_periods',
    'startdate',
    'enddate',
    'minimumage',
    'rankstart',
    'rankend',
    'portsize',
    'benchmark']

colconfig_orig = [
    'todaysdate',
    'testnumber',
    'runtime',
    'runtimeperperiod',
    'strat_name',
    'investperiod',
    'num_periods',
    'startdate',
    'enddate',
    'minimumage',
    'rankstart',
    'rankend',
    'portsize',
    'benchmark',
    'effective_daily_growthrate',
    'effective_daily_growthrate_bench',
    'effective_daily_growthrate_margin',
    'effective_period_growthrate',
    'effective_period_growthrate_bench',
    'effective_period_growthrate_margin',
    'margin_daily_growthrate_min'
    ] + [
        f'period_{i}_{j}' for j in ['min', 'mean', 'median', 'max', 'std', 'mad'] for i in ['growthrate', 'growthrate_bench', 'growthrate_margin']
        ] + [
            f'daily_{i}_{j}' for j in ['min', 'mean', 'median', 'max', 'std', 'mad'] for i in ['growthrate', 'growthrate_bench', 'growthrate_margin']
        ] + [
            'abovezerotally',
            'abovezerotally_bench',
            'abovezerotally_margin',
            'abovezerotally_pct',
            'abovezerotally_bench_pct',
            'abovezerotally_margin_pct',
            'abovebench_tally',
            'abovebench_tally_pct',
            'abovebench_pos_tally',
            'abovebench_pos_tally_pct'
            ]

colconfig_1 = [
    'todaysdate',
    'testnumber',
    'strat_name',
    'min_preath_age',
    'investperiod',
    'num_periods',
    'startdate',
    'enddate',
    'minimumage',
    'rankstart',
    'rankend',
    'benchmark',
    'effective_daily_growthrate',
    'effective_daily_growthrate_bench',
    'effective_daily_growthrate_margin',
    'margin_daily_growthrate_min',
    'daily_growthrate_min',
    'daily_growthrate_margin_min',
    'daily_growthrate_std',
    'daily_growthrate_mad',
    'margin_daily_growthrate_std',
    'margin_daily_growthrate_mad',
    'abovezerotally',
    #'abovezerotally_bench',
    #'abovezerotally_margin',
    'abovezerotally_pct',
    #'abovezerotally_bench_pct',
    'abovezerotally_margin_pct',
    'abovebench_tally',
    'abovebench_tally_pct',
    'abovebench_pos_tally',
    'abovebench_pos_tally_pct'
    ]

quality_cols = [
    'effective_daily_growthrate',
    'effective_daily_growthrate_margin',
    'margin_daily_growthrate_min',
    'abovezerotally_pct',
    'abovezerotally_margin_pct',
    'abovebench_tally_pct',
    'abovebench_pos_tally_pct'
    ]
