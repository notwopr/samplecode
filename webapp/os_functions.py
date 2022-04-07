# IMPORT TOOLS
#   STANDARD LIBRARY IMPORTS
import os
#   THIRD PARTY IMPORTS
#   LOCAL APPLICATION IMPORTS


def get_currentscript_filenameplusext(f):
    return os.path.basename(f)

    
def get_currentscript_filename(f):
    return get_currentscript_filenameplusext(f)[:-3]
