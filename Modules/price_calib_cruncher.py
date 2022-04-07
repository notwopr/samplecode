"""
Title: FINAL BAREMINCRUNCHER
Date Started: Mar 6, 2020
Version: 1.1
Version Start: June 2, 2020
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose: Current best baremincruncher formula as of Version Date.
Versions:
1.1: Making code more concise.

WARNING: These functions assume that the input pricelist is ordered in chronological order, the first item being the oldest date and the last item being the youngest.
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
#   THIRD PARTY IMPORTS
import numpy as np
#   LOCAL APPLICATION IMPORTS


def baremax_cruncher(origpricelist):
    newpricelist = []
    # for each pricepoint...
    for item in origpricelist:
        # if newlist is empty, add the first pricepoint
        if len(newpricelist) == 0:
            newpricelist.append(item)
        # otherwise...
        else:
            # if pricepoint greater than/equal to last item, add
            if item >= newpricelist[-1]:
                newpricelist.append(item)
            elif item and np.isnan(newpricelist[-1]):
                newpricelist.append(item)
            # otherwise repeat last item
            else:
                lastprice = newpricelist[-1]
                newpricelist.append(lastprice)
    return newpricelist


def baremin_cruncher(origpricelist):
    startprice = origpricelist[0]
    newpricelist = []
    # for each pricepoint...
    for item in origpricelist:
        # if newlist is empty, add the first pricepoint
        if len(newpricelist) == 0:
            newpricelist.append(item)

        # otherwise...
        else:
            # if pricepoint >= last item in newlist, add
            if item >= newpricelist[-1]:
                newpricelist.append(item)
            # else if pricepoint < starting price...
            elif item < startprice:
                # remove all prev items > starting price...
                remove_count = 0
                while startprice < newpricelist[-1]:
                    # remove last item...
                    newpricelist.pop()
                    remove_count += 1
                    # if no more items are left to remove, escape loop
                    if len(newpricelist) == 0:
                        break
                # replace removed items with starting price and add starting price
                addlist = np.repeat(startprice, remove_count+1).tolist()
                newpricelist.extend(addlist)
            # else if pricepoint < last item in newlist...
            elif item < newpricelist[-1]:
                # remove all prev items greater than item
                remove_count = 0
                while item < newpricelist[-1]:
                    # remove last item...
                    newpricelist.pop()
                    remove_count += 1
                    # if no more items are left to remove, escape loop
                    if len(newpricelist) == 0:
                        break
                # replace removed items with the current item and add current item
                addlist = np.repeat(item, remove_count+1).tolist()
                newpricelist.extend(addlist)

    return newpricelist


def oldbaremin_cruncher(origpricelist):
    newpricelist = []
    # for each pricepoint...
    for item in origpricelist:
        # if newlist is empty, add the first pricepoint
        if len(newpricelist) == 0:
            newpricelist.append(item)
        # otherwise...
        else:
            # if pricepoint >= last item in newlist, add
            if item >= newpricelist[-1]:
                newpricelist.append(item)
            # otherwise...
            else:
                # remove all prev items greater than item
                remove_count = 0
                while item < newpricelist[-1]:
                    # remove last item...
                    newpricelist.pop()
                    remove_count += 1
                    # if no more items are left to remove, escape loop
                    if len(newpricelist) == 0:
                        break
                # replace removed items with the current item and add current item
                addlist = np.repeat(item, remove_count+1).tolist()
                newpricelist.extend(addlist)
    return newpricelist
