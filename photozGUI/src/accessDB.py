"""

Access the database
===================

"""

__author__ = 'jiayiliu'

import sqlite3 as sql

import numpy as np

from systools import warning
from sparameter import *


class Candidate():
    """
    Cluster candidate database model

    :param database: specify the database to use
    :param table: specify the name of table to use
    """

    def __init__(self, database=DB_FILE, table=DB_CAT, comment=DB_PZ):
        """
        Initialize the candidate database

        :param database: specify the database to use
        :param table: specify the name of table to use
        """
        self.conn = sql.connect(database)
        self.cur = self.conn.cursor()
        self.table = table
        self.comment = comment

    def create_comment(self):
        """
        create comment database


        ========== =============
        Name       Content
        ========== =============
        id         Candidate ID
        photoz     Estimated photoz
        photozerr  Estimated photoz error
        file       Input file
        comment    Comment
        ========== =============

        """
        self.cur.execute("DROP TABLE IF EXISTS {0:s}".format(self.comment))
        self.cur.execute("""CREATE TABLE {0:s} (
        id INTEGER NOT NULL REFERENCES {1:s},
        photoz FLOAT,
        photozerr FLOAT,
        method TEXT,
        comment TEXT
        )""".format(self.comment, self.table))
        self.conn.commit()

    def has_cluster(self, candidate_id):
        """
        Examine whether cluster exist in the database

        :param candidate_id: Candidate ID
        :return: True/False
        """
        self.cur.execute("SELECT id FROM {0:s} WHERE id = ?".format(self.table), (candidate_id,))
        if self.cur.fetchone() is None:
            return False
        else:
            return True

    def get_pos(self, candidate_id, method=None):
        """
        get the position from candidate catalog

        :param candidate_id: candidate ID
        :param method: detection method Not in used
        :returns: [R.A., Dec.,1, 5, SN]
        """
        self.cur.execute("SELECT ra, dec, SN FROM {0:s} WHERE id = ?".format(self.table), (candidate_id,))
        data = self.cur.fetchone()
        return [data[0], data[1], 1, 5, data[2]]

    def get_redshift(self, candidate_id):
        """
        get the redshift of the candidate cluster

        :param candidate_id: candidate ID
        :return: redshift string
        """
        #self.cur.execute("SELECT redshift FROM {0:s} WHERE id = ?".format(self.table), (candidate_id,))
        #result = self.cur.fetchone()
        result = [-1]
        if result[0] is None:
            return -1
        else:
            return result[0]

    def get_info(self, candidate_id):
        """
        return the information of given cluster candidate

        """
        data = self.get_pos(candidate_id)
        return "R.A.: {0:f}\nDec.: {1:f}\nSN: {2:f}\n".format(data[0], data[1], data[-1])

    def insert_comment(self, candidate_id, photoz, cmr_info, comment):
        """
        insert one item into table photoz

        :param candidate_id: Candidate ID
        :param photoz: photoz estimation z, z_err
        :param cmr_info: file related information
        :param comment: comment
        """
        self.cur.execute("INSERT INTO {0:s} VALUES (?,?,?,?,?)".format(self.comment),
                         (candidate_id, photoz[0], photoz[1], cmr_info, comment))
        self.conn.commit()

    def create_from_catalog(self, catalog):
        """
        create the table in database based on given catalog

        :param catalog: catalog contains [ID, SN, RA, DEC]
        """
        cat = np.loadtxt(catalog, dtype={"names": ['ID', 'SN', 'RA', 'DEC'], "formats": [int, float, float, float]},
                         comments='#')
        self.cur.execute("DROP TABLE IF EXISTS {0:s}".format(self.table))
        methods = ' INTEGER, '.join(P_method) + " INTEGER"
        self.cur.execute("""CREATE TABLE {0:s} (
                         id INTEGER NOT NULL,
                         sn FLOAT,
                         ra FLOAT,
                         dec FLOAT, {1:s})
                         """.format(self.table, methods))
        self.cur.executemany("INSERT INTO {0:s} (id, sn, ra, dec) VALUES (?,?,?,?)".format(self.table), cat)
        self.conn.commit()

    def update_method(self, catalog, method):
        """
        Update the method in database based on catalog

        :param catalog: catalog name contains ID which is detected by method, "all" will set method to 1 for all
        :param method: method want to update to 1
        """
        if method not in P_method:
            warning("Wrong method name")
            exit()
        if catalog == "all":
            self.cur.execute("UPDATE {0:s} SET {1:s} = 1".format(self.table, method))
        else:
            cid = np.loadtxt(catalog, dtype=int)
            for i in cid:
                self.cur.execute("UPDATE {0:s} SET {1:s} = 1 WHERE id = ?".format(self.table, method), (cid,))
        self.conn.commit()

    def get_method(self, cid, methods):
        """
        get the detection methods for each methods input

        :param cid: candidate ID
        :param methods: detection methods array
        :return: [0,1] array for each detection
        """
        methods_name = ','.join(methods)
        self.cur.execute("SELECT {0:s} FROM {1:s} WHERE id = ?".format(methods_name, self.table), (cid,))
        return self.cur.fetchone()


if __name__ == "__main__":
    db = Candidate()
    db.create_from_catalog("/home/moon/hennig/optfinder/optfinder/catalog.dat")
    db.create_comment()
    db.update_method("all", P_method[0])