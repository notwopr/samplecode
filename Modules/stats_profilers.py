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
from scipy import stats
#   LOCAL APPLICATION IMPORTS


def stat_profiler_nan(figure):
    stat_min = np.nanmin(figure)
    stat_q1 = np.nanquantile(figure, 0.25)
    stat_mean = np.nanmean(figure)
    stat_med = np.nanmedian(figure)
    stat_q3 = np.nanquantile(figure, 0.75)
    stat_max = np.nanmax(figure)
    stat_std = np.nanstd(figure)
    sharpe = stat_mean / stat_std
    finaldict = {
        'stat_min': stat_min,
        'stat_q1': stat_q1,
        'stat_mean': stat_mean,
        'stat_med': stat_med,
        'stat_q3': stat_q3,
        'stat_max': stat_max,
        'stat_std': stat_std,
        'stat_sharpe': sharpe
    }
    return finaldict


def stat_profiler(figure):
    stat_min = np.min(figure)
    stat_q1 = np.quantile(figure, 0.25)
    stat_mean = np.mean(figure)
    stat_med = np.median(figure)
    stat_q3 = np.quantile(figure, 0.75)
    stat_max = np.max(figure)
    stat_std = np.std(figure)
    sharpe = stat_mean / stat_std
    finaldict = {
        'stat_min': stat_min,
        'stat_q1': stat_q1,
        'stat_mean': stat_mean,
        'stat_med': stat_med,
        'stat_q3': stat_q3,
        'stat_max': stat_max,
        'stat_std': stat_std,
        'stat_sharpe': sharpe
    }
    return finaldict


def stat_profilerv2(figure):
    stat_min = np.min(figure)
    stat_q1 = np.quantile(figure, 0.25)
    stat_mean = np.mean(figure)
    stat_med = np.median(figure)
    stat_q3 = np.quantile(figure, 0.75)
    stat_max = np.max(figure)
    stat_std = np.std(figure)
    stat_mad = stats.median_abs_deviation(figure)
    finaldict = {
        'min': stat_min,
        'q1': stat_q1,
        'mean': stat_mean,
        'med': stat_med,
        'q3': stat_q3,
        'max': stat_max,
        'std': stat_std,
        'mad': stat_mad
    }
    return finaldict


def stat_profilerv3(figure):
    stat_min = np.min(figure)
    stat_q1 = np.quantile(figure, 0.25)
    stat_mean = np.mean(figure)
    stat_med = np.median(figure)
    stat_q3 = np.quantile(figure, 0.75)
    stat_max = np.max(figure)
    stat_std = np.std(figure)
    stat_mad = stats.median_abs_deviation(figure)
    finaldict = {
        'num_samps': len(figure),
        'min': stat_min,
        'q1': stat_q1,
        'mean': stat_mean,
        'med': stat_med,
        'q3': stat_q3,
        'max': stat_max,
        'std': stat_std,
        'mad': stat_mad
    }
    return finaldict


def stat_summarizer(figure):
    avg_perf = np.nanmean(figure)
    min_perf = np.nanmin(figure)
    q1_perf = np.nanquantile(figure, 0.25)
    med_perf = np.nanmedian(figure)
    q3_perf = np.nanquantile(figure, 0.75)
    max_perf = np.nanmax(figure)
    stdev = np.nanstd(figure)
    medianabdev = stats.median_abs_deviation(figure, nan_policy='omit')
    sharpe = avg_perf / stdev
    sharpemad = med_perf / medianabdev

    finaldict = {
        'avg_perf': avg_perf,
        'med_perf': med_perf,
        'stdev': stdev,
        'medianabdev': medianabdev,
        'min_perf': min_perf,
        'max_perf': max_perf,
        'q1_perf': q1_perf,
        'q3_perf': q3_perf,
        'sharpe': sharpe,
        'sharpemad': sharpemad
    }
    return finaldict


def stat_summarizer_old(figure):
    avg_perf = np.nanmean(figure)
    min_perf = np.nanmin(figure)
    q1_perf = np.nanquantile(figure, 0.25)
    med_perf = np.nanmedian(figure)
    q3_perf = np.nanquantile(figure, 0.75)
    max_perf = np.nanmax(figure)
    iqr_perf = q3_perf - q1_perf
    max_min = max_perf - min_perf
    maxq3 = max_perf - q3_perf
    q1min = q1_perf - min_perf
    stdev = np.nanstd(figure)
    medianabdev = stats.median_abs_deviation(figure, nan_policy='omit')

    finaldict = {
        'avg_perf': avg_perf,
        'min_perf': min_perf,
        'q1_perf': q1_perf,
        'med_perf': med_perf,
        'q3_perf': q3_perf,
        'max_perf': max_perf,
        'iqr_perf': iqr_perf,
        'max_min': max_min,
        'maxq3': maxq3,
        'q1min': q1min,
        'stdev': stdev,
        'medianabdev': medianabdev
    }

    return finaldict


# TAKES A LIST AND RETURNS AGGREGATE NUMBER BASED ON METHOD REQUESTED
def list_aggregator(aggregatemethod, all_data):

    # AGGREGATE METHOD
    if aggregatemethod == 'mean':
        answer = np.nanmean(all_data)
    if aggregatemethod == 'median':
        answer = np.nanmedian(all_data)
    if aggregatemethod == 'minimum':
        answer = np.nanmin(all_data)
    if aggregatemethod == 'q1':
        answer = np.nanquantile(all_data, 0.25)
    if aggregatemethod == 'q3':
        answer = np.nanquantile(all_data, 0.75)
    if aggregatemethod == 'maximum':
        answer = np.nanmax(all_data)
    if aggregatemethod == 'stdev':
        answer = np.nanstd(all_data)
    if aggregatemethod == 'medianabdev':
        answer = stats.median_abs_deviation(all_data, nan_policy='omit')
    if aggregatemethod == 'iqr':
        q1_perf = np.nanquantile(all_data, 0.25)
        q3_perf = np.nanquantile(all_data, 0.75)
        answer = q3_perf - q1_perf
    if aggregatemethod == 'range':
        min_perf = np.nanmin(all_data)
        max_perf = np.nanmax(all_data)
        answer = max_perf - min_perf
    if aggregatemethod == 'maxq3':
        max_perf = np.nanmax(all_data)
        q3_perf = np.nanquantile(all_data, 0.75)
        answer = max_perf - q3_perf
    if aggregatemethod == 'q1min':
        q1_perf = np.nanquantile(all_data, 0.25)
        min_perf = np.nanmin(all_data)
        answer = q1_perf - min_perf
    if aggregatemethod == 'q3q1avg':
        q1_perf = np.nanquantile(all_data, 0.25)
        q3_perf = np.nanquantile(all_data, 0.75)
        answer = (q3_perf + q1_perf) / 2
    if aggregatemethod == 'q3q1avgoveriqr':
        q1_perf = np.nanquantile(all_data, 0.25)
        q3_perf = np.nanquantile(all_data, 0.75)
        iqr = q3_perf - q1_perf
        answer = ((q3_perf + q1_perf) / 2) / iqr
    if aggregatemethod == 'maxminavg':
        min_perf = np.nanmin(all_data)
        max_perf = np.nanmax(all_data)
        answer = (max_perf + min_perf) / 2
    if aggregatemethod == 'maxminavgoverrange':
        min_perf = np.nanmin(all_data)
        max_perf = np.nanmax(all_data)
        maxmin = max_perf - min_perf
        answer = ((max_perf + min_perf) / 2) / maxmin

    return answer


# TAKES LIST AND RETURNS VARIOUS STATISTICAL ANALYSES
def list_analysis(target):

    num_samp = len(target)
    abvlist = list(map(abs, target))
    simp_avg = np.mean(target)
    abv_avg = np.mean(abvlist)

    # POSITIVE SAMPLES:
    pos_samples = list(filter(lambda x: (x > 0), target))
    num_possamp = len(pos_samples)
    avg_pos = np.mean(pos_samples)

    # NEGATIVE SAMPLES:
    neg_samples = list(filter(lambda x: (x < 0), target))
    num_negsamp = len(neg_samples)
    avg_neg = np.mean(neg_samples)

    # HOW OFTEN ZERO:
    zeroes = len(list(filter(lambda x: (x == 0), target)))
    zero_rate = zeroes / num_samp
    nonzero_rate = 1 - zero_rate
    pos_rate = num_possamp / num_samp
    neg_rate = num_negsamp / num_samp

    # PROPORTION OF NONZERO SAMPLES > 0
    pos_nonzeroprop = num_possamp / (num_negsamp + num_possamp)

    # PROPORTION OF NONZERO SAMPLES < 0
    neg_nonzeroprop = num_negsamp / (num_negsamp + num_possamp)

    # REPORT
    summary = [num_samp, simp_avg, abv_avg, avg_pos, avg_neg, zero_rate, nonzero_rate, pos_rate, neg_rate, pos_nonzeroprop, neg_nonzeroprop]
    sumtitles = ['Number of samples:', 'Average value:', 'Average absolute value:', 'Average positive value:', 'Average negative value:', 'Proportion that is zero:', 'Proportion that is not zero:', 'Proportion that is positive:', 'Proportion that is negative:', 'Proportion of nonzero samples that is positive', 'Proportion of nonzero samples that is negative']

    dict_summary = dict(zip(sumtitles, summary))

    return dict_summary
