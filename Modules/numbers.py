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
import math
#   THIRD PARTY IMPORTS
#   LOCAL APPLICATION IMPORTS


# ROUNDS UP GIVEN NUMBER
def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier


# ROUNDS DOWN GIVEN NUMBER
def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier


# FORMATS A NUMBER TO x,xxx,xxx.00 (becomes a string)
def formalnumber(n):
    return f'{round(n, 2):,.2f}'


# FORMATS A NUMBER TO x,xxx,xxx (becomes a string)
def formalnumber_integer(n):
    return f'{round(n, 2):,}'


# rounds decimal to 2 decimals returning as float datatype
def twodecp(n):
    return round(n, 2)
