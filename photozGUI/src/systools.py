"""

Quick tools for general purposes
================================

"""

__author__ = 'jiayiliu'


def warning(message, color=31):
    """
     Create warning message in red

    :param message: a string of warning message
    :param color: the color of the warning message

    The selection of colors refers to
    [ANSI Escape sequences](http://ascii-table.com/ansi-escape-sequences.php)

    +----+-------+
    | id | color |
    +====+=======+
    | 31 | red   |
    +----+-------+
    | 34 | blue  |
    +----+-------+
    | 32 | green |
    +----+-------+
    | 33 | yellow|
    +----+-------+

    """
    c_warning = '\033[{0:d}m'.format(color)  # Define warning color
    end_c = '\033[0m'  # Define Normal color
    print c_warning + message + end_c


#: Newline symbol for Linux system
NEWLINE = '\n'
