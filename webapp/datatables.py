# sort table
def sort_datatable(sortinput, targetdf):
    if len(sortinput):
        return targetdf.sort_values(
            by=sortinput[0]['column_id'],
            ascending=sortinput[0]['direction'] == 'asc',
            inplace=False
            )
    else:
        return targetdf
