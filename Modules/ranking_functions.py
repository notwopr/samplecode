# given a dict of rankcol: rankweight, and a dataframe, return dataframe sorted by ranking specs
def gen_ranking(rankingtuples, df):
    w_total = 0
    for t in rankingtuples:
        c = t[0]
        w = t[1]
        a = t[2]
        r = f'RANK_{c} (w={w})'
        df[r] = df[c].rank(ascending=True if a == 1 else False)
        df[f'w_{c}'] = (df[r] * w)
        w_total += w
    m = f'wRANK {w_total}'
    sumcols = [f'w_{t[0]}' for t in rankingtuples]
    df[m] = df[sumcols].sum(axis=1, min_count=len(sumcols))
    f = 'FINAL RANK'
    df[f] = df[m].rank(ascending=1)
    df.sort_values(ascending=True, by=[f], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df
