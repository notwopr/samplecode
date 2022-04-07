from collections import ChainMap


# combine list of dictionaries into one large dictionary
def gen_dict_from_listofdicts(listofdicts):
    return dict(ChainMap(*listofdicts))


# join two dicts together
def join_dicts(d1, d2):
    return {**d1, **d2}
