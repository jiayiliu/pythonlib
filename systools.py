##  
# \file systools.py
# \package systools
# quick tools for general purposes
#

## 
#  \brief Create warning message in red
#  \param message a string of warning message
#  \param color the color of the warning message
#  
#  The selection of colors refers to 
#  [ANSI Escape sequences](http://ascii-table.com/ansi-escape-sequences.php)
#
#  --------------
#  | id | color |
#  |----|-------|
#  | 31 | red   |
#  | 34 | blue  |
#  | 32 | green |
#  | 33 | yellow|
#  --------------
def warning(message,color=31):
    ## Define warning color
    cWARNING = '\033[%dm'%color
    ## Define Normal color
    ENDC = '\033[0m'
    print cWARNING+message+ENDC
    
## Newline symbol for Linux system
NEWLINE = '\n'
