# returns the dict for the marks attribute of a dash slider
# df is the dataframe containing the columns with the data you want to display on the slider, e.g. date column
# colname is the name of the column that contains the marks data

def gen_marks_dict(df, num_marks_wanted, colname):
    freqlen = len(df) // num_marks_wanted
    return {i*freqlen: str(df[colname][i*freqlen].strftime('%Y-%m-%d')) for i in range(num_marks_wanted+1)}


def get_minmax_marks(marks):
    return min(marks.keys()), max(marks.keys())


def gen_slider_marks(df, num_marks_wanted, colname):
    marks = gen_marks_dict(df, num_marks_wanted, colname)
    minmark, maxmark = get_minmax_marks(marks)
    return marks, minmark, maxmark
