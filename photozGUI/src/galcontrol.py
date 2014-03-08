"""

Controller for galaxy photo-z measurement
=========================================

"""
__author__ = 'jiayiliu'

from galview import GalViewer
from galmodel import GalModel
from sparameter import CMR_combination, CMR_COLOR, call_ds9, P_method
from GUItools import Message


class GalController():
    """
    Controller of MVC
    """

    def __init__(self):
        """
        initialize Galaxy photo-z controller
        """
        self.model = GalModel()
        self.viewer = GalViewer(self)
        self.cluster_id = None
        self.cmr_line = dict(gr=None, gi=None, ri=None, rz=None, iz=None)
        self.cmr_dots = dict(gr=None, gi=None, ri=None, rz=None, iz=None)
        self.sketch_dots = dict(all=None, gr=None, gi=None, ri=None, rz=None, iz=None)
        self.viewer.run()

    def initialize_galaxy(self, cid):
        """
        load galaxy data file
        
        :param cid: cluster ID to load
        """
        try:
            assert isinstance(cid, int)
            self.cluster_id = cid
            self.model.load_gal(self.cluster_id)
            self.viewer.set_cluster(self.model.get_info(), self.model.get_method(P_method))
        except ValueError:
            self.cluster_id = None
            Message("Invalid Input of cluster ID!", master=self.viewer)
        except IOError:
            self.cluster_id = None
            Message("Cluster file is not available!", master=self.viewer)

    def view_fits(self, band):
        """
        call DS9 to show pseudo color image

        :param band: call ds9 to plot given band
        """
        call_ds9(self.cluster_id, band)

    def view_sketch(self, axis):
        """
        create sketch plot to show galaxy positions

        :param axis: axis for plotting
        :return: None
        """
        self.model.galaxy.plot_sky(axis, all=True,
                                   color='b', alpha=0.3, marker='.', ls='None')

    def update_candidate_sketch(self, method):
        """
        Add candidate information

        :param method: Add candidate radius with given method
        """
        self.model.draw_candidate(self.viewer.sketch.axis, method=method)
        self.viewer.sketch.update()

    def select_galaxy_sketch(self, figure):
        """
        active galaxy selection function
        this will set the model.gid

        :param figure: figure object for selecting galaxy
        """
        self.model.draw_in_circle(figure)


    def update_galaxy_sketch(self):
        """
        update the sketch figure for galaxies distribution according to manual circle selection
        """
        if self.sketch_dots['all'] is not None:
            self.sketch_dots['all'].pop(0).remove()
        self.sketch_dots['all'] = self.model.galaxy.plot_sky(self.viewer.sketch.axis, gid=self.model.gid,
                                                             color='r', marker='x', ls='None', alpha=0.6)
        self.viewer.sketch.update()

    def view_cmr(self, band1, band2):
        """
        create Color-magnitude relation plot
        plot both the galaxies and the model

        :param band1: red band
        :param band2: blue band
        """
        ax = self.viewer.create_cmr(band1 + band2)
        self.model.galaxy.plot_cmr(band1, band2, ax, all=True,
                                   marker='.', ls='None', color='b', alpha=0.3)
        self.model.cmr.plot_all(band1, band2, ax, color='c', alpha=0.5)

    def update_cmr(self):
        """
        update the galaxy of the cmr plot based on sketch selection
        """
        for icmr in self.viewer.cmr_window.keys():
            self.model.galaxy.plot_cmr(icmr[0], icmr[1],
                                       self.viewer.cmr_window[icmr].axis, gid=self.model.gid,
                                       marker='x', color="r", ls='None')
            self.viewer.cmr_window[icmr].update()

    def update_cmr_z(self, z):
        """
        update the cmr plot to highlight the redshift
        also update the sketch if available

        :param z: redshift to plot (str or float)
        """
        if type(z) is str:
            z = float(z)
        self.viewer.str_redshift.set("Redshift: {0:4.2f}".format(z))
        zid = self.model.cmr.get_zid(z)
        for icmr in self.viewer.cmr_window.keys():
            if (icmr in self.cmr_line) and (self.cmr_line[icmr] is not None):
                self.cmr_line[icmr].pop(0).remove()
            self.cmr_line[icmr] = self.model.cmr.plot(zid, icmr[0], icmr[1], self.viewer.cmr_window[icmr].axis,
                                                      color='g', lw=2)
            self.update_cmr_sketch(zid, icmr)
            if self.cmr_dots[icmr] is not None:
                self.cmr_dots[icmr].pop(0).remove()
            self.cmr_dots[icmr] = self.model.galaxy.plot_cmr(icmr[0], icmr[1],
                                                             self.viewer.cmr_window[icmr].axis,
                                                             gid=self.model.cgid[icmr],
                                                             marker='+', color=CMR_COLOR[icmr], ls='None')
            self.viewer.cmr_window[icmr].update()

    def update_cmr_sketch(self, zid, icmr, **args):
        """
        Update galaxies selected from CMR_combination plot in sketch plot

        :param zid: redshift id
        :param icmr: cmr model color combination
        :param args: arguments to plotting
        """
        if self.viewer.sketch is None:
            return
        band1 = icmr[0]
        band2 = icmr[1]
        self.model.cgid[icmr] = self.model.galaxy.in_cmr_band(band1, band2,
                                                              self.model.cmr.get_magnitude(zid, band1),
                                                              self.model.cmr.get_magnitude(zid, band2))
        if self.sketch_dots[icmr] is not None:
            self.sketch_dots[icmr].pop(0).remove()
        self.sketch_dots[icmr] = self.model.galaxy.plot_sky(self.viewer.sketch.axis, gid=self.model.cgid[icmr],
                                                            color=CMR_COLOR[icmr], marker='+', ls='None', alpha=0.8)
        self.viewer.sketch.update()

    def save_reg(self):
        """
        output to region file for DS9 to load
        """
        save_id = map(int, self.viewer.multi_list.curselection())
        for i in save_id:
            if i == 0:
                self.model.galaxy.save_reg("clu{0:d}.reg".format(self.cluster_id), self.model.gid)
            else:
                j = i - 1
                self.model.galaxy.save_reg("clu{0:d}_{1:d}.reg".format(self.cluster_id, j),
                                           self.model.cgid[CMR_combination[j]],
                                           color=CMR_COLOR[CMR_combination[j]])

    def update_selection(self):
        """
        Update sketch selection
        """
        if self.model.gid is not None:
            self.update_galaxy_sketch()
            self.update_cmr()

    def clean_selection(self):
        """
        Clean current selections
        """
        if self.model.gid is not None:
            self.model.gid = None
        for i in self.viewer.cmr_window.keys():
            if self.cmr_dots[i] is not None:
                print i
                self.cmr_dots[i].pop(0).remove()
                self.cmr_dots[i] = None
            if self.sketch_dots[i] is not None:
                self.sketch_dots[i].pop(0).remove()
                self.sketch_dots[i] = None
            if self.viewer.cmr_window[i] is not None:
                self.viewer.cmr_window[i].update()
            self.model.cgid[i] = None
        self.viewer.sketch.update()

    def resample(self):
        """
        Resample the sketch based on selection in sketch
        """
        if self.model.gid is not None:
            self.model.galaxy.data = self.model.galaxy.data[self.model.gid, :]
            self.model.gid = [i for i in range(len(self.model.gid))]  # recreate the gid
            for ic in self.model.cgid.keys():
                self.model.cgid[ic] = None


if __name__ == "__main__":
    g = GalController()
