"""
Title: Content Directory
Date Started: Feb 4, 2022
Version: 1.00
Version Start: Feb 4, 2022
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied without the express written consent of David Hyongsik Choi.
Purpose:  .
"""
# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import os
import importlib
import pkgutil
#   THIRD PARTY IMPORTS
#   LOCAL APPLICATION IMPORTS
import webapp.routers


# get list of .py filenames (without '.py') in pkgimport
def get_listofrouternames(pkgimport):
    pkgpath = os.path.dirname(pkgimport.__file__)
    restrictedfiles = [name for _, name, _ in pkgutil.iter_modules([pkgpath]) if 'helper' in name]
    return [name for _, name, _ in pkgutil.iter_modules([pkgpath]) if name not in restrictedfiles]


# retrieves bot's resource (e.g. variable, function) given pathname
def retrieve_bot_content(pathname, resourcename):
    return getattr(importlib.import_module(f'webapp.routers.{pathname}'), resourcename)


# directory ties bpdict to its pathname
bpdict = {b: retrieve_bot_content(b, 'bp') for b in get_listofrouternames(webapp.routers)}
