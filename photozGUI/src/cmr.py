"""

Color - Magnitude Relation
==========================

"""
__author__ = 'jiayiliu'

import numpy as np

from sparameter import *
from systools import warning


class Cmr():
    """
    color magnitude model class

    :param file_name: file name of the color magnitude data
    :returns: Cmr class with property data array [z,griz ...]
    """

    def __init__(self, file_name=CMR_path):
        """
        initial the color magnitude data

        :param file_name: file name of the color magnitude data
        :returns: Cmr class with property data array [z,griz ...]
        """
        try:
            self.data = np.loadtxt(file_name)
        except IOError:
            warning("Fail to open cmr file: {0:s}".format(file_name))
            exit(1)

    def get_magnitude(self, zid, band):
        """
        get the magnitude of given redshift and band

        :param zid: redshift row to return
        :param band: color band: [griz]
        :returns: [z,griz ...]
        """
        try:
            mid = CMR_BANDS[band] + np.arange(0, CMR_NL, len(CMR_BANDS), np.dtype("I4")) + 1
            return self.data[zid, mid]
        except NameError:
            warning("wrong color band: {0:s}".format(band))
        except IndexError:
            warning("wrong number of L*")

    def get_zid(self, redshift):
        """
        return the zid of nearest row

        :param redshift: redshift for checking
        :returns: redshift id in data
        """
        return np.argmin(abs(self.data[:, 0] - redshift))

    def get_z_range(self):
        """
        get the redshift range of CMR_combination file

        :returns: min(z), max(z), length(z)
        """
        return np.min(self.data[0, :]), np.max(self.data[0, :]), len(self.data[0, :])

    def get_z_num(self):
        """
        get the length of CMR_combination model

        :returns: length(z)
        """
        return len(self.data[:, 0])

    def plot(self, zid, band1, band2, axis, **args):
        """
        plot the color-magnitude relation

        :param zid: redshift id
        :param band1: blue band
        :param band2: red band
        :param axis: axis to plot
        :param args: parameters passed to plot
        """
        mb1 = self.get_magnitude(zid, band1)
        mb2 = self.get_magnitude(zid, band2)
        return axis.plot(mb2, mb1 - mb2, '.-', **args)

    def plot_all(self, band1, band2, axis, **args):
        """
        plot color-magnitude relations across all redshifts

        :param band1: blue band
        :param band2: red band
        :param axis: axis to plot
        :param args: parameters passed to plot
        """
        for i in range(self.get_z_num()):
            self.plot(i, band1, band2, axis, **args)


if __name__ == "__main__":
    import matplotlib.pylab as plt

    c = Cmr()
    ax = plt.subplot(111)
    zmin, zmax, nz = c.get_z_range()
    for i in range(nz):
        c.plot(i, 'g', 'z', ax)
    plt.show()