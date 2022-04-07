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
from Modules.stats_profilers import stat_profilerv3

'''RETURNS NUMBER OF TRIALS IT TAKES FOR A ADDITIONAL SAMPLE TO MOVE THE AVERAGE LESS THAN THE TOLERANCE SET.  EVEN THOUGH AN ADDITIONAL SAMPLE MAY MOVE THE AVERAGE LESS THAN TOLERANCE, THE FOLLOWING SAMPLE COULD MOVE THE AVERAGE EVEN MORE, BY AN AMOUNT ABOVE TOLERANCE.  SO, THE FUNCTION SEARCHES FOR THE POINT AT WHICH THE MAX MOVEMENT FOR THE MOST RECENT 50% OF ALL TRIALS TAKEN FALLS BELOW THE TOLERANCE.
'''


# tolerance = number below which an additional sample's influence on the average is deemed statistically insignificant
# randmin - lowest number a sample's value can be
# randmax - highest number a sample's value can be
# popsize - proportion of all samples starting with most recent that you want to include when considering sample's effect on overall mean
# set tolerance below 1
def num_trial_bot(randmin, randmax, tolerance, win_prop):
    num_trials = 0
    data = []
    all_effects = []
    s = []
    recent_max_effect = 1
    while recent_max_effect > tolerance:
        if num_trials != 0:
            avg_before = np.mean(data)
        else:
            avg_before = np.nan
        sample = (randmax - randmin) * np.random.random() + randmin
        data.append(sample)
        avg_after = np.mean(data)
        if num_trials != 0:
            effect = abs((avg_after - avg_before) / avg_before)
            all_effects.append(effect)
            win_size = int(np.ceil(win_prop * (len(all_effects))))
            recent_max_effect = np.max(all_effects[-win_size:])
        else:
            effect = np.nan
            win_size = 0
        trialsumm = {
            'trial': num_trials,
            'sample': sample,
            'avg_before': avg_before,
            'avg_after': avg_after,
            'sample_effect': effect,
            'recent_max_effect': recent_max_effect,
            'win_size': win_size,
            'win_prop': win_prop,
            'tolerance': tolerance,
            'data': data,
            'all_effects': all_effects
        }
        num_trials += 1
        s.append(trialsumm)
    return s


def num_trial_bot_report(alltrialsummaries):
    return [
        f"Out of the latter {alltrialsummaries[-1]['win_size']} trials ({alltrialsummaries[-1]['win_prop']*100} % of all trial samples), the maximum percentage by which an additional sample moved the overall mean was {alltrialsummaries[-1]['recent_max_effect']*100} %, which is less than the {alltrialsummaries[-1]['tolerance']*100} % threshold set.",
        f"The number of trials it took to reach this point is {alltrialsummaries[-1]['trial']}."
        ]


def graph_num_trial_bot(tolerance, num_trials, all_effects):
    plt.plot(all_effects)
    x = np.linspace(0, num_trials + 1)
    y = [tolerance] * len(x)
    plt.plot(x, y, '-r', label='tolerance', linewidth=2.0)
    plt.ylabel('Diff between Mean before and after')
    plt.xlabel('Trials')
    plt.show()
