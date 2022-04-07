from Modules.price_history import grabsinglehistory
from Modules.dates import num_days


# get stock's birthdate
def get_bdate(stock):
    return grabsinglehistory(stock)['date'].iloc[0]


# get stock's latestdate
def get_ldate(stock):
    return grabsinglehistory(stock)['date'].iloc[-1]


# get full age of a stock
def get_fullage(stock):
    prices = grabsinglehistory(stock)
    return num_days(prices['date'].iloc[0], prices['date'].iloc[-1])


# get age of stock as of given datetime object date
def get_asofage(stock, date):
    return max(0, num_days(get_bdate(stock), date))
