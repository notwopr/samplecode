"""
Title: Stat Research Bot
Date Started: July 18, 2019
Version: 1.1
Version Start Date: Mar 29, 2020
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied
    without the express written consent of David Hyongsik Choi.
Purpose: The purpose of the Stat Research Bot is to perform various research tests.

TO DO:
--create function that inputs various data into the num_trial_bot and finds the regression model.

Version 1.1:  Added sharpe and sharpemad to stat_summarizer
"""
# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
#   THIRD PARTY IMPORTS
import numpy as np
import matplotlib.pyplot as plt
#   LOCAL APPLICATION IMPORTS


# TAKES A LIST AND FILTERS OUT OUTLIERS
def outlier_remover(verbose, plot, strength, figure):

    q1_perf = np.nanquantile(figure, 0.25)
    q3_perf = np.nanquantile(figure, 0.75)
    iqr = q3_perf - q1_perf
    outlier_base = (strength * iqr)
    upper_limit = q3_perf + outlier_base
    lower_limit = q1_perf - outlier_base

    filtered_figure = [elem for elem in figure if elem <= upper_limit and elem >= lower_limit]
    outliers = list(set(figure).difference(set(filtered_figure)))

    num_outliers = len(outliers)
    num_orig = len(figure)
    num_filtered = len(filtered_figure)
    num_check = num_filtered + num_outliers

    if verbose == 'verbose':

        print('original (sorted):', sorted(figure))
        print('filtered (sorted):', sorted(filtered_figure))
        print('outliers (sorted):', sorted(outliers))
        print('upper_limit:', upper_limit)
        print('lower_limit:', lower_limit)
        print('CORRECT NUMBER OF OUTLIERS WERE REMOVED:', num_check == num_orig)
        print('num_outliers:', num_outliers)
        print('num_orig:', num_orig)
        print('num_filtered:', num_filtered)
        print('num_filtered + num_outliers:', num_check, '(if this matches num_orig, then outlier removal operation was successful)')

    if plot == 'plot':

        plt.plot(figure, 'bo')
        plt.plot(outliers, 'ro')
        plt.ylabel('strength: ' + str(strength))
        plt.xlabel('Outlier Range: ' + str(lower_limit) + ' to ' + str(upper_limit))
        plt.title('Number of Outliers: ' + str(num_outliers), loc='right')
        plt.title('% Outliers: ' + str(100 * (num_outliers / num_orig)) + '%', loc='left')
        plt.show()

    return filtered_figure
