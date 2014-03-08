"""

Aux plot function
=================

"""

__author__ = 'jiayiliu'
import numpy as np

from scipy.optimize import curve_fit

from sparameter import CMR_combination


#: number of iterations for gaussian fit
NITER = 10


def get_data(input_path):
    """
    load all color combination photo-z distribution

    :param input_path: filename header
    :return: dict contains the cluster information
    """
    data = {}
    for i, c in enumerate(CMR_combination):
        data[c] = np.loadtxt(input_path + "_%d_bg.dat" % i, usecols=(0, 3))
    return data


def g3g(x, y, n_sigma=3):
    """
    Gaussian fit with three sigma clipping for mean

    :param x: x value
    :param y: weights
    :param n_sigma: sigma clipping in fitting
    :return: mean and std
    """
    x = x[y > 0]
    y = y[y > 0]
    mean = np.average(x, weights=y)
    std = np.sqrt(np.average((x - mean) ** 2, weights=y))  # wrong because x is not uniform

    def gaus(x, a, x0, sigma):
        return a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))

    for i in range(NITER):
        if len(x) < 5:
            break
        popt, pcov = curve_fit(gaus, x, y, p0=[1, mean, std])
        mean = popt[1]
        std = abs(popt[2])
        sid = np.where((x > mean - n_sigma * std) & (x < mean + n_sigma * std))[0]
        x = x[sid]
        y = y[sid]
    return mean, std


def g3gf(x, y, n_sigma=3):
    """
    Gaussian fit with three sigma clipping for peak

    :param x: x value
    :param y: weights
    :param n_sigma: sigma clipping in fitting
    :return: peak and std
    """
    from scipy.optimize import curve_fit

    x = x[y > 0]
    y = y[y > 0]
    mean = x[np.argmax(y)]
    std = np.sqrt(np.average((x - mean) ** 2, weights=y))  # wrong because x is not uniform

    def gaus(x, a, sigma):
        return a * np.exp(-(x) ** 2 / (2 * sigma ** 2))

    for i in range(NITER):
        if len(x) < 5:
            break
        popt, pcov = curve_fit(gaus, x - mean, y, p0=[1, std])
        std = abs(popt[1])
        sid = np.where((x > mean - n_sigma * std) & (x < mean + n_sigma * std))[0]
        x = x[sid]
        y = y[sid]
    return mean, std


if __name__ == "__main__":
    pass
