"""
Title: File Test Bot
Date Started: June 8, 2019
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose: The purpose of the File Test Bot is to make sure a saved file has been preserved properly, only testing whether the length of the dataframe is the same as when it was saved.

"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import pickle as pkl
import os
#   THIRD PARTY IMPORTS
#   LOCAL APPLICATION IMPORTS


# COUNTS NUMBER OF FILES (INCLUDING FILES IN SUBDIRECTORIES)
def count_file(parent):
    count = sum(len(files) for _, _, files in os.walk(parent))
    return count


# CHECK NUMBER OF FILES IN DIRECTORY
def checknum(target, correct, verbose):

    # COUNT NUMBER OF FILES IN TARGET
    num_files = len([path.suffix for path in target.iterdir() if path.is_file() and path.suffix])

    if num_files != correct:
        if verbose == 'verbose':
            print("The download did not complete.")
            print("Number of files needed:", correct)
            print("Number of files downloaded:", num_files)
            print("Number of files that failed to download:", correct - num_files)
        return False
    else:
        if verbose == 'verbose':
            print("All files have been downloaded!!")
            print("Number of files needed:", correct)
            print("Number of files downloaded:", num_files)
            print("Number of files that failed to download:", correct - num_files)
        return True


# CHECK NUMBER OF FILES IN DIRECTORY INCLUDING FILES IN SUBDIRECTORIES
def checknum_multilevel(target, correct, verbose):

    # COUNT NUMBER OF FILES IN TARGET
    num_files = sum(len(files) for _, _, files in os.walk(target))

    if num_files != correct:
        if verbose == 'verbose':
            print("The download did not complete.")
            print("Number of files needed:", correct)
            print("Number of files downloaded:", num_files)
            print("Number of files that failed to download:", correct - num_files)
        return False
    else:
        if verbose == 'verbose':
            print("All files have been downloaded!!")
            print("Number of files needed:", correct)
            print("Number of files downloaded:", num_files)
            print("Number of files that failed to download:", correct - num_files)
        return True


def checknumfiles(csvpath, pklpath, correct):

    # CHECK IF ALL FILES HAVE BEEN DOWNLOADED
    num_pklfiles = len([path.suffix for path in pklpath.iterdir() if path.is_file() and path.suffix])
    num_csvfiles = len([path.suffix for path in csvpath.iterdir() if path.is_file() and path.suffix])
    if num_pklfiles != correct or num_csvfiles != correct:
        print("The download did not complete.")
        if num_pklfiles != correct:
            print("Number of pickle files needed:", correct)
            print("Number of pickle files downloaded:", num_pklfiles)
            print("Number of pickle files that failed to download:", correct - num_pklfiles)
        if num_csvfiles != correct:
            print("Number of csv files needed:", correct)
            print("Number of csv files downloaded:", num_csvfiles)
            print("Number of csv files that failed to download:", correct - num_csvfiles)
        print("The program will exit now. Please fix the problem.")
    else:
        print("All files have been downloaded!!")


def integritycheck(x):  # x = file to be tested
    # OPEN FILE
    with open(x, "rb") as targetfile:
        unpickled_raw = pkl.load(targetfile)

    thedata = unpickled_raw['thedata']
    timestamp = unpickled_raw['timestamp']
    origlen = unpickled_raw['origlen']
    actualen = len(thedata)

    # REPORT FINDINGS
    if actualen == origlen:
        print("FILE: ", x)
        print("Yay! The list is still the same length as when it was originally created!")
        print(
            "%s %s \n %s %s \n %s %s \n %s %s"
            % (
                "OBJECT TYPE OF UNPICKLED FILE'S LIST:",
                type(thedata),
                "LENGTH OF ORIGINAL LIST:",
                origlen,
                "LENGTH OF UNPICKLED FILE'S LIST:",
                actualen,
                "PICKLED FILE TIMESTAMP:",
                timestamp
            )
        )
        return True
    else:
        print("FILE: ", x)
        print("Uh oh! The list is not the same length as when it was originally created. The file may be corrupt.")
        print(
            "%s %s \n %s %s \n %s %s \n %s %s"
            % (
                "OBJECT TYPE OF UNPICKLED FILE'S LIST:",
                type(thedata),
                "LENGTH OF ORIGINAL LIST:",
                origlen,
                "LENGTH OF UNPICKLED FILE'S LIST:",
                actualen,
                "PICKLED FILE TIMESTAMP:",
                timestamp
            )
        )
        return False


# FIND SYMBOLS IN A FOLDER THAT WEREN'T DOWNLOADED
def find_undownloaded(tickerlistsource, sourcefolder):

    # GET TICKERLIST
    with open(tickerlistsource, "rb") as targetfile:
        unpickled_raw = pkl.load(targetfile)
    tickerlist = unpickled_raw['thedata']

    # ASSEMBLE DATA
    table_results = []
    for child in sourcefolder.iterdir():
        with open(child, "rb") as targetfile:
            unpickled_raw = pkl.load(targetfile)
        table_results.append(unpickled_raw)

    # CONSTRUCT DATAFRAME
    graphscoredf = pd.DataFrame(
        data=table_results,
        columns=[
            "stock",
            "overall_slope",
            "mean_roll_slope",
            "abvmeandev"
        ]
    )

    downloaded = graphscoredf['stock'].tolist()
    notdownloaded = []
    for elem in tickerlist:
        if elem not in downloaded:
            notdownloaded.append(elem)

    for symbol in notdownloaded:
        graphscore('', '', '', 180, 180, symbol)


# FIND SYMBOLS IN PRICE FOLDER THAT WEREN'T DOWNLOADED
def find_undownloaded_prices(sourcelist, tickerlistsource, stockpricefolder, targetfolder, suffix_len):

    if sourcelist != '':
        symbols = sourcelist
    else:
        with open(tickerlistsource, "rb") as targetfile:
            unpickled = pkl.load(targetfile)
        symbols = unpickled['thedata']
        targetfolder = stockpricefolder

    downloadedlist = []
    for child in targetfolder.iterdir():
        childname = os.path.split(child)[1]

        if sourcelist == '':
            downloaded_symbol = childname[0:-11]
        else:
            downloaded_symbol = childname[0:-suffix_len]
        downloadedlist.append(downloaded_symbol)

    notdownloaded = []
    for elem in symbols:
        if elem not in downloadedlist:
            notdownloaded.append(elem)

    print('The following symbols failed to download:')
    print(notdownloaded)


# FIND DUPLICATES IN A LIST
def find_duplicates(sourcelist):

    notduplicates = []
    duplicates = []
    for elem in sourcelist:
        if elem not in notduplicates:
            notduplicates.append(elem)
        else:
            print('duplicate found:', elem)
            duplicates.append(elem)

    return duplicates


# COMPARES TWO LISTS AND FINDS THE DIFFERENCES
def find_diff(list1, list2):

    diffs1 = []
    diffs2 = []
    for elem in list1:
        if elem not in list2:
            diffs1.append(elem)
    for elem in list2:
        if elem not in list1:
            diffs2.append(elem)

    print('Elements in list1 but not in list2:\n', diffs1)
    print('Elements in list2 but not in list1:\n', diffs2)
