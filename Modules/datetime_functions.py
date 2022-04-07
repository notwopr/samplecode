import datetime as dt


# convert pandas timestamp to datetime
def from_pts_to_dt(timestamp):
    return timestamp.to_pydatetime()


# convert full datetime object to just date
def from_fulldtobj_to_date(dtobj):
    return dtobj.date()


# convert from pandas timestamp to datetime date
def from_pts_to_dtdate(timestamp):
    return from_fulldtobj_to_date(from_pts_to_dt(timestamp))


# convert from pandas timestamp to string date
def from_pts_to_stringdate(timestamp):
    return str(from_pts_to_dtdate(timestamp))


# convert string YYYY-mm-dd format to datetime.date object
def stringdate_to_dtdate(stringdate):
    return dt.date.fromisoformat(stringdate)
