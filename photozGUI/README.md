Photo-Z analysis GUI
====================

# Configuration

The configure file is needed in *sparameter.py*

The important requirements following:

## CMR

The color magnitude relation file from EzGal

+ **cmr_path = cmr_z_SDSS.out**

And the columns are ordered as

+ **cmr_bands = {'i': 2, 'r': 1, 'z': 3, 'g': 0}**, with first column as redshift

+ **cmr_nl = 24** specifies the total magnitudes the CMR contains

+ **cmr_combination = ['gr', 'gi', 'ri', 'rz', 'iz']** is the color combination in used

+ **cmr_color = {'iz': 'k', 'gr': 'r', 'ri': 'g', 'gi': 'b', 'rz': 'c'}** specifies the color for plotting


## Galaxy catalog

The galaxies for each cluster are stored in a file specified by the cluster ID

For files as ./data/*ID*.dat with columns as [R.A., Dec., mg, mi, mr, mu, mz, ...]

+ **cat_path = ./data/** is the path to the data directory
+ **cat_pattern = {0:d}.dat**
+ **cat_bands = {'i': 1, 'r': 2, 'u': 3, 'z': 4, 'g': 0}**


## Database

The database is build to store the information of each cluster candidate
First time run:

    python accessDB.py

+ **db_file = ./database.db**
+ **p_method = ['run']** specify the sub-directory for each detection
+ **db_cat = cat** name of the table for candidate
+ **db_pz = photoz** commentary part for photo-z estimation

## Photo-z analysis result

This is post-processed result for photozMVC.py
The result is stored at ./result/run/pz*ID*_?_bg.dat
Notice, the *run* is specified by p_method

+ **photoz_path = ./result/**
+ **pz_pattern = /pz{0:d}**


