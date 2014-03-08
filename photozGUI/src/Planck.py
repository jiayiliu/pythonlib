__author__ = 'jiayiliu'

from accessDB import *


class Planck(Candidate):
    """
    Planck cluster/candidate database model
    """

    def get_pos(self, planck_id, method='mmf3'):
        """
        get the position from Planck catalog

        :param planck_id: planck ID
        :param method: detection method
        :returns: [R.A., Dec., position_error, R500]
        """
        self.cur.execute("SELECT ra, dec, poserr, r500 FROM {0:s} WHERE id = ?".format(method), (planck_id,))
        return self.cur.fetchone()

    def get_redshift(self, planck_id):
        """
        get the redshift of the Planck cluster

        :param planck_id: planck ID
        :return: redshift or -1
        """
        self.cur.execute("SELECT redshift FROM planck WHERE id = ?", (planck_id,))
        result = self.cur.fetchone()
        if result[0] is None:
            return -1
        else:
            return result[0]

    def get_info(self, planck_id):
        """
        return the R500 information of given cluster

        :param planck_id: Planck ID
        :return: string information of R500 of Planck cluster
        """

        def get_one_r500(method):
            self.cur.execute("SELECT r500, poserr from {0:s} WHERE id = ?".format(method), (planck_id,))
            result = self.cur.fetchone()
            if result is not None:
                return method + ": %5f %5f\n" % result
            else:
                return ""

        mmf1 = get_one_r500("mmf1")
        mmf3 = get_one_r500("mmf3")
        pws = get_one_r500("pws")
        return mmf1 + mmf3 + pws


if __name__ == "__main__":
    db = Planck()
    db.create_comment()