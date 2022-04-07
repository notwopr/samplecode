# returns the geometric rate of an existing rate
# e.g. if r is a growth rate over a 30-day period, what is the daily rate?
def geometric_rate(r, n):
    return ((1 + r) ** (1 / n)) - 1


# what is the effective rate r if the subrate is d?
# e.g. if d is the daily growth rate, what is the 30-day rate r?
def effective_rate(d, n):
    return ((1 + d) ** n) - 1
