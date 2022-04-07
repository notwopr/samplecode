"""
Title: Generic Function Bot
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
import importlib
import copy
#   THIRD PARTY IMPORTS
#   LOCAL APPLICATION IMPORTS
from Modules.metriclibrary.STRATTEST_FUNCBASE import getmetcolname
from file_functions import getobject_byvarname


# combines several paramscripts together using no importlib, removes dupes
def scriptjoiner_removedupes_noimportlib(scriptlist, customname):
    # for each paramscript
    master_paramslist = []
    for script in scriptlist:
        # get metricslist
        metricslist = script['scriptparams']
        # for each metricitem, if item not already in final list, add it
        for metricitem in metricslist:
            # get metcolname
            metcolname = getmetcolname(metricitem)
            # get current final list of metcolnames
            currmetcolnamelist = [getmetcolname(mastermetitem) for mastermetitem in master_paramslist]
            if metcolname not in currmetcolnamelist:
                # append metlist to mastermetlist
                master_paramslist.append(metricitem)
            if metcolname in currmetcolnamelist:
                print(f'dupe: {metcolname}')
    master_params = {
        'scriptname': customname,
        'scriptparams': master_paramslist
        }
    return master_params


# combines several paramscripts together, removes dupes
def scriptjoiner_removedupes(scriptlist, customname):
    # for each paramscript
    master_paramslist = []
    for script in scriptlist:
        # get scriptobject
        paramfilename = script['scriptfilename']
        scriptmodule = importlib.import_module(paramfilename)
        scriptobject = scriptmodule.stage2_params
        # get metricslist
        metricslist = scriptobject['scriptparams']
        # for each metricitem, if item not already in final list, add it
        for metricitem in metricslist:
            # get metcolname
            metcolname = getmetcolname(metricitem)
            # get current final list of metcolnames
            currmetcolnamelist = [getmetcolname(mastermetitem) for mastermetitem in master_paramslist]
            if metcolname not in currmetcolnamelist:
                # append metlist to mastermetlist
                master_paramslist.append(metricitem)
            if metcolname in currmetcolnamelist:
                print(f'dupe: {metcolname}')
    master_params = {
        'scriptname': customname,
        'scriptparams': master_paramslist
        }
    return master_params


# TAKES SEVERAL PARAMSCRIPTS AND COMBINES THEM GIVEN WEIGHTINGS
def scriptjoiner(scriptlist, customname):
    # for each paramscript
    master_paramslist = []
    newname = ''
    for script in scriptlist:
        # get script weight
        scriptweight = script['scriptweight']
        # get metricslist
        metricslist = copy.deepcopy(getobject_byvarname(script['scriptfilename'][0], script['scriptfilename'][1])['scriptparams'])
        # for each metricitem, pull metricweight and update value
        for metricitem in metricslist:
            currweight = metricitem['metricweight']
            #print(f"metricitem: {metricitem['metricname']}, scriptweight: {scriptweight}, metricweight {currweight}, finalweight: {currweight * scriptweight}")
            metricitem.update({'metricweight': currweight * scriptweight})
        # append modified metricslist to masterlist
        master_paramslist += metricslist
        # add to mastername
        if customname == '':
            nickname = script['scriptnickname']
            newname += f'{nickname}({scriptweight})_'
    # create master paramscriptshell
    # add customname if field not empty
    if customname != '':
        newname = customname
    master_params = {
        'scriptname': newname,
        'scriptparams': master_paramslist
        }
    return master_params
