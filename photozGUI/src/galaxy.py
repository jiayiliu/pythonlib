"""

Galaxy Model
============

"""
__author__ = 'jiayiliu'

import numpy as np
from scipy.stats import linregress

from sparameter import CAT_PATH, CAT_PATTERN, CAT_BANDS


class Galaxy():
    """
    galaxy catalog class

    :param cid: cluster id (specify input/output files)
    :param path_pattern:
    """

    def __init__(self, cid, path_pattern=CAT_PATH + CAT_PATTERN):
        """
        Initial Cmr class

        :param cid: cluster id (specify input/output files)
        :param path_pattern:
        """
        try:
            self.data = np.loadtxt(path_pattern.format(cid))
        except IOError:
            print "\033[31m Fail to open tile ID {0:d} \033[0m".format(cid)
            raise IOError

    def plot_sky(self, axis, gid=None, all=False, **args):
        """
        plot the RA-Dec. distribution

        :param axis: the axis for plotting
        :param gid: galaxy id to plot
        :param all: True to plot all galaxies
        """
        if all:
            return axis.plot(self.data[:, 0], self.data[:, 1], zorder=1, **args)
        if gid is not None:
            return axis.plot(self.data[gid, 0], self.data[gid, 1], zorder=2, **args)

    def in_sky_region(self, pos, radius):
        """
        return the list of galaxy ID within given radius

        :param pos: center position
        :param radius: radius to select
        :return: index of galaxies inside the circle
        """
        projection = np.cos(np.radians(pos[1]))
        r = ((self.data[:, 0] - pos[0]) * projection) ** 2 + (self.data[:, 1] - pos[1]) ** 2
        r = np.sqrt(r)
        return np.where(r < radius)[0]

    def plot_cmr(self, band1, band2, axis, gid=None, all=False, **args):
        """
        plot the galaxy color - magnitude distribution

        :param band1: blue band
        :param band2: red band
        :param axis: axis for plotting
        :param gid: galaxy id
        :param all: flag to plot all galaxies
        """
        axis.set_xlim([14, 26])
        axis.set_ylim([-2, 4])
        if (band1 in CAT_BANDS) and (band2 in CAT_BANDS):
            if all:
                return axis.plot(self.data[:, 2 + CAT_BANDS[band2]],
                                 self.data[:, 2 + CAT_BANDS[band1]] - self.data[:, 2 + CAT_BANDS[band2]],
                                 **args)
            if gid is not None:
                return axis.plot(self.data[gid, 2 + CAT_BANDS[band2]],
                                 self.data[gid, 2 + CAT_BANDS[band1]] - self.data[gid, 2 + CAT_BANDS[band2]],
                                 **args)

    def in_cmr_band(self, band1, band2, cmr1, cmr2, width=0.1):
        """
        return the list of galaxy ID within in color magnitude band
        just within cmr band, no extrapolation

        :param band1: blue band
        :param band2: red band
        :param cmr1: color magnitude relation array
        :param cmr2: color magnitude relation array
        :param width: width to select galaxies
        :return: index of galaxies
        """
        b = self.data[:, 2 + CAT_BANDS[band1]]
        r = self.data[:, 2 + CAT_BANDS[band2]]
        gradient, intercept, r_value, p_value, std_err = linregress(cmr2, cmr1 - cmr2)
        diffy = np.abs((b - r) - (r * gradient + intercept))
        return np.where((diffy < width) & (r < np.max(cmr2)))[0]

    def save_reg(self, filename, gid, shape='circle', size=0.0003, color='red'):
        """
        save the region file into disk

        :param filename: output filename
        :param gid: index of galaxies
        :param shape: shape to output to ds9
        :param size: size of the shape, about 1 arcsec
        :param color: color of the shape
        """
        if gid is None:
            return
        ds9color = dict(r='red', b='blue', w='white', g='green', y='yellow', c='cyan', k='black')
        with open(filename, 'w') as f:
            f.write("fk5\n")
            for i in gid:
                f.write(shape + " ({0:f}, {1:f}, {2:f}) # color = {3:s}\n"
                        .format(self.data[i, 0], self.data[i, 1], size, ds9color[color]))


if __name__ == "__main__":
    import matplotlib.pylab as plt

    ax = plt.subplot(111)
    g = Galaxy(124)
    #g.plot_sky(ax)
    g.plot_cmr('g', 'r', ax)
    plt.show()

