

# add periodic diff and pct change cols
# changecol options are 'rawprice', 'baremaxraw', 'oldbareminraw', 'straight', 'trueline'
def add_pdiffpctchange_portfolio(df, changecol, period, mode, portfolio):
    if changecol == 'all':
        sourcecols = portfolio
    elif changecol == 'rawprice':
        sourcecols = [s for s in portfolio if not any([b in s for b in ['baremaxraw', 'oldbareminraw', 'straight', 'trueline']])]
    else:
        sourcecols = [s for s in portfolio if changecol in s]
    if mode == 'pdiff':
        df[[f'{s}_{period}d_{mode}' for s in sourcecols]] = df[sourcecols].diff(periods=period)
    if mode == 'pctchange':
        df[[f'{s}_{period}d_{mode}' for s in sourcecols]] = df[sourcecols].pct_change(periods=period, fill_method='ffill')
    return df, sourcecols


# add col comparisons
# WARNING uppercol&lowercol can only take values ['baremaxraw', 'oldbareminraw', 'straight', 'trueline', 'rawprice']
def add_comparisons_portfolio(df, uppercol, lowercol, portfolio):
    # get comparison
    for s in portfolio:
        upper_label = s if uppercol == 'rawprice' else f'{s}_{uppercol}'
        lower_label = s if lowercol == 'rawprice' else f'{s}_{lowercol}'
        df[f'{s}_{uppercol}to{lowercol}'] = (df[upper_label] - df[lower_label]) / df[lower_label]
    return df
