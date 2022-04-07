from Modules.tickers import get_tickerlist
from Modules.timeperiodbot import getalldates_range
from webapp.servernotes import getstockdata

# list of all dates in tickerlist_common range
allavailabledates = getalldates_range(getstockdata()["earliest"], getstockdata()["latest"], 0)

# earliest stock date available
staticmindate = getstockdata()["earliest"]

# latest stock date available
staticmaxdate = getstockdata()["latest"]

# list of all common tickers + bench
tickers = get_tickerlist('common+bench')
