"""

Model for galaxy photo-z measurement
====================================

"""
__author__ = 'jiayiliu'
from math import cos, radians, sqrt

from matplotlib.patches import Ellipse

from galaxy import Galaxy
from cmr import Cmr
from interactiveModel import SelectCircle

#from accessDB import Candidate as Candidate
from accessDB import Candidate as Candidate


class GalModel():
    """
    Model of MVC
    """

    def __init__(self):
        self.cmr = Cmr()
        self.candidate = Candidate()
        self.galaxy = None
        self.cluster_id = None
        self.circle = None
        self.c1 = None
        self.c2 = None
        self.center = None
        self.radius = None
        self.s = None
        self.gid = None  # for sketch galaxy
        self.cgid = dict(gr=None, gi=None, ri=None, rz=None, iz=None)  # for cmr galaxy

    def load_gal(self, cluster_id):
        """
        Load galaxy sample

        :param cluster_id: cluster candidate ID
        """
        self.galaxy = Galaxy(cluster_id)
        self.cluster_id = cluster_id
        self.gid = [i for i in range(len(self.galaxy.data))]

    def get_method(self, methods):
        """
        Return the Candidate detection method for drawing radius corresponding radius

        :param methods: array of methods
        :return: the available detection method
        """
        return self.candidate.get_method(self.cluster_id, methods)

    def get_info(self):
        """
        Return the information about the cluster candidate

        :return: string contains information to show
        """
        return "cluster {0:d}\nredshift is {1:f}".format(self.cluster_id, self.candidate.get_redshift(self.cluster_id))

    def draw_candidate(self, ax, method="mmf3"):
        """
        Over draw the Candidate contour

        :param ax: axis for plotting
        :param method: Method from Candidate
        """
        data = self.candidate.get_pos(self.cluster_id, method)
        if self.c1 is not None:
            self.c1.remove()
            self.c2.remove()
        if data is not None:
            projection = cos(radians(data[1])) * 60.
            self.c1 = Ellipse((data[0], data[1]), data[2] / projection, data[2] / 60., ec='r', fill=False, lw=3,
                              zorder=10)
            self.c2 = Ellipse((data[0], data[1]), data[3] / projection, data[3] / 60., ec='g', fill=False, lw=3,
                              zorder=10)
            ax.add_patch(self.c1)
            ax.add_patch(self.c2)

    def draw_in_circle(self, figure):
        """
        create a circle in figure

        :param figure: figure to create selective circle
        """
        if self.s is None:
            self.s = SelectCircle(figure, on_release=self.get_pos)
        else:
            del self.s
            self.s = SelectCircle(figure, on_release=self.get_pos)

    def get_pos(self, event):
        """
        Get the position when button is released
        Overwrite the release_event in SelectCircle

        :param event: matplotlib release event
        """
        if self.circle is not None:
            self.circle.remove()
            self.circle = None
        self.center = self.s.pos
        r = (self.center[0] - event.xdata) ** 2 + (self.center[1] - event.ydata) ** 2
        r = sqrt(r)
        projection = cos(radians(self.center[1]))
        self.s.c.remove()
        self.s.c = None

        self.circle = Ellipse(self.center, width=2 * r / projection, height=2 * r, fill=False, ec='r', lw=3, zorder=11)
        self.s.fig.axes[0].add_patch(self.circle)
        self.s.fig.canvas.show()
        self.s.pos = None

        self.gid = self.galaxy.in_sky_region(self.center, r)
