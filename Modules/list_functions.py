"""
Title: List Functions
Date Started: July 10, 2019
Version: 1.01
Version Start Date: July 21, 2020
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied
    without the express written consent of David Hyongsik Choi.
Purpose: The purpose of the Generic Function Bot is to be a clearinghouse for random generic functions.
VERSIONS:
1.01: Added round up and round down functions.
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
#   THIRD PARTY IMPORTS
#   LOCAL APPLICATION IMPORTS


# INTERSECTION OF TWO LISTS
def intersectlists(list1, list2):
    intersectlist = list(set(list1).intersection(set(list2)))
    return intersectlist


# REMOVE DUPLICATES FROM LIST
def removedupes(dupelist):
    newlist = list(dict.fromkeys(dupelist))
    return newlist


# REMOVE DUPLICATES FROM LIST WHERE ELEMS ARE ALSO LISTS
def removedupes_lists(verbose, dupelist):
    newlist = []
    removeditems = []
    for item in dupelist:

        if item not in newlist:

            newlist.append(item)
        else:

            removeditems.append(item)
    if verbose == 'verbose':
        print('Original List:', dupelist)
        print('Removed items:', removeditems)
        print('Number of items removed:', len(removeditems))
        print('Revised List:', newlist)
        print('Length of Revised List:', len(newlist))
    return newlist
