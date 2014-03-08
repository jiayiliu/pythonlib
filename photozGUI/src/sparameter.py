"""

Parameter setup
===============
"""
__author__ = 'jiayiliu'

import ConfigParser
from os import system

config = ConfigParser.RawConfigParser()
config.read("../example.cfg")

# galaxy catalog position
CAT_PATH = config.get("Galaxy Catalog", "CAT_PATH")

## galaxy file pattern
CAT_PATTERN = config.get("Galaxy Catalog", "CAT_PATTERN")

## galaxy file content order: [ra, dec, bands ...]
CAT_BANDS = eval(config.get("Galaxy Catalog", "CAT_BANDS"))

## database position
DB_FILE = config.get("Database", "DB_FILE")

## detection method
P_method = eval(config.get("Database", "P_method"))

#: Table name for catalog
DB_CAT = config.get("Database", "DB_CAT")

#: Table name for photoz
DB_PZ = config.get("Database", "DB_PZ")

########## Color magnitude information ##########
#: CMR_combination file path
CMR_path = config.get("CMR", "CMR_path")

#: Color band information, specify the column order as [z, g, r, i, z]
CMR_BANDS = eval(config.get("CMR", "CMR_BANDS"))

#: Number of L* for all band, which is the total columns minus 1 (from redshift)
CMR_NL = config.getint("CMR", "CMR_NL")

#: color combinations, each color need to be in CMR_BANDS
CMR_combination = eval(config.get("CMR", "CMR_combination"))

#: color for plotting
CMR_COLOR = eval(config.get("CMR", "CMR_COLOR"))

########## P(z) files ##########
#: Photo-z file path
PHOTOZ_PATH = config.get("Photoz", "PHOTOZ_PATH")

#: P(z) file name pattern
PZ_pattern = config.get("Photoz", "PZ_pattern")


########### DS9 ##########
def call_ds9(cid, band):
    """
    call ds9 for plotting

    :param cid: cluster ID
    :param band: color combination
    """
    print "\033[33m ... Openning FITS file ... \033[0m"
    system("ds9.sh {0:d} {1:s}".format(cid, band))


def create_config_file(filename):
    """
    Create configure file for the first time

    :param filename: File to store
    :return:
    """
    input_config = ConfigParser.RawConfigParser()
    input_config.add_section("CMR")
    input_config.set("CMR", "CMR_path", CMR_path)
    input_config.set("CMR", "CMR_BANDS", CMR_BANDS)
    input_config.set("CMR", "CMR_NL", CMR_NL)
    input_config.set("CMR", "CMR_combination", CMR_combination)
    input_config.set("CMR", "CMR_COLOR", CMR_COLOR)
    input_config.add_section("Galaxy Catalog")
    input_config.set("Galaxy Catalog", "CAT_PATH", CAT_PATH)
    input_config.set("Galaxy Catalog", "CAT_PATTERN", CAT_PATTERN)
    input_config.set("Galaxy Catalog", "CAT_BANDS", CAT_BANDS)
    input_config.add_section("Database")
    input_config.set("Database", "DB_FILE", DB_FILE)
    input_config.set("Database", "P_method", P_method)
    input_config.set("Database", "DB_CAT", DB_CAT)
    input_config.set("Database", "DB_PZ", DB_PZ)
    input_config.add_section("Photoz")
    input_config.set("Photoz", "PHOTOZ_PATH", PHOTOZ_PATH)
    input_config.set("Photoz", "PZ_pattern", PZ_pattern)

    with open(filename, 'w') as f:
        input_config.write(f)


def valid_config_file(filename):
    """
    Validate the configure file

    :param filename: configure file name
    :return: Good/Bad
    """
    test = ConfigParser.RawConfigParser()
    test.read(filename)

    for i in test.sections():
        print i
        for j in test.options(i):
            print j, "--", test.get(i, j), type(test.get(i, j))


if __name__ == "__main__":
    #create_config_file("photoz3.cfg")
    valid_config_file("photoz3.cfg")
