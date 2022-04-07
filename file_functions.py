"""
Title: File and Folder Operations
Date Started: June 20, 2019
Version: 1.3
Version Start Date: Oct 21, 2021
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose: The purpose of the File Location Bot is to store the address of data files.

Version Notes:
1.1: Update notes and use f string syntax.
1.2: added readcsv
1.3: add amazon cloud config.
"""

# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import os
import shutil
import pickle as pkl
import glob
import importlib
#   THIRD PARTY IMPORTS
import pandas as pd
#   LOCAL APPLICATION IMPORTS


# LOAD MODULE BY ITS LOCATION IN STRING FORM
def getmodule(modulename):
    return importlib.import_module(modulename)


# LOAD OBJECT WITHIN MODULE BY ITS NAME IN STRING FORM AND ITS MODULE IN STRING FORM
def getobject_byvarname(modulename, varname):
    return getattr(importlib.import_module(modulename), varname)


# RETRIEVE LOCATION OF SINGLE RUN OF A BOT
def getbotsinglerunfolder(rootdump, testregimename, todaysdate, testnumber):
    testregimeparent = rootdump / testregimename
    mod_date = todaysdate.replace("-", "")
    testcode = 'D' + mod_date + 'T' + str(testnumber)
    testrunparent = testregimeparent / testcode
    return testrunparent


# DELETE FOLDER
def delete_folder(location):
    if os.path.isdir(location) is True:
        shutil.rmtree(location)


# DELETE AND CREATE FOLDERS
def delete_create_folder(location):
    delete_folder(location)
    os.makedirs(location)


# CREATE FOLDER IF DOESN'T EXIST
def create_nonexistent_folder(location):
    if os.path.isdir(location) is False:
        os.makedirs(location)


# DELETE FILE IF EXISTS
def delete_file(path):
    if os.path.exists(path) is True:
        os.remove(path)


# SAVE TO PKL
def savetopkl(filename, directory, data):
    with open(directory / f"{filename}.pkl", "wb") as targetfile:
        pkl.dump(data, targetfile, protocol=4)


# SAVE TO DF to CSV
def savedftocsv(filename, directory, data):
    data.to_csv(index=False, path_or_buf=directory / f"{filename}.csv")


# READ PKL
def readpkl(filename, directory):
    # OPEN FILE
    with open(directory / f"{filename}.pkl", "rb") as targetfile:
        data = pkl.load(targetfile)
    # PRINT DATA
    return data


# READ PKL but fullpath
def readpkl_fullpath(fullpath):
    with open(fullpath, "rb") as targetfile:
        data = pkl.load(targetfile)
    return data


# READ CSV
def readcsv(filename, directory):
    data = pd.read_csv(directory / f"{filename}.csv")
    return data


# GET LOCATION OF NEWEST FILE IN FOLDER
def newestfileloc(searchfolder):

    list_of_files = glob.glob(f'{searchfolder}/*')
    latest_file_loc = max(list_of_files, key=os.path.getctime)

    return latest_file_loc


def buildfolders_regime_testrun(rootdump, testnumber, todaysdate, testregimename):

    testregimeparent = rootdump / testregimename
    mod_date = todaysdate.replace("-", "")
    testcode = 'D' + mod_date + 'T' + str(testnumber)
    testrunparent = testregimeparent / testcode
    important_index = [
        testregimeparent,
        testrunparent
    ]
    for item in important_index:
        create_nonexistent_folder(item)

    return testregimeparent, testrunparent


def buildfolders_parent_cresult_cdump(parent, custom_name):

    subparent = parent / custom_name
    child_result = subparent / 'resultfiles'
    child_dump = subparent / 'dumpfiles'
    important_index = [
        subparent,
        child_result,
        child_dump
    ]
    for item in important_index:
        create_nonexistent_folder(item)

    return subparent, child_result, child_dump


def buildfolders_singlechild(parent, custom_name):
    child_folder = parent / custom_name
    create_nonexistent_folder(child_folder)
    return child_folder
