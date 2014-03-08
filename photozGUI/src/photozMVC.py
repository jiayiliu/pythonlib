"""

Photo-z P(z) MVC module
=======================

"""

__author__ = 'jiayiliu'

import matplotlib

matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from os.path import isfile
import numpy as np
import Tkinter as Tk

from sparameter import PHOTOZ_PATH, CMR_combination, P_method, PZ_pattern
from systools import warning
import axplot
#from accessDB import Candidate as Candidate
from accessDB import Candidate as Candidate


## sigma clipping
NSIGMA = 2


class PhotozModel():
    """
    Model of MVC for P(z) plotting
    """

    def __init__(self):
        self.cid = None  # Cluster ID
        self.path = PHOTOZ_PATH  # Data Path
        self.pz = {}
        self.db = Candidate()  # Cluster Database to get information
        self.method = None  # detection method
        self.fit_x = None  # fit peak or mean
        self.color = None  # detection color
        self.fit_result = None  # store the fitting result centre value and std

    def load(self, cid):
        """
        load cluster photo-z result

        :param cid: cluster ID
        :return: True for correct load data, False for fail to load data
        """
        self.cid = cid
        return self.db.has_cluster(self.cid)

    def get_info(self):
        """
        get the cluster information

        :return: cluster information
        """
        return self.db.get_info(self.cid)

    def get_z(self):
        """
        get the cluster known redshift

        :return: redshift of known cluster
        """
        return "redshift: {0:f}".format(self.db.get_redshift(self.cid))

    def load_method(self, method):
        """
        Get the method data

        :return: 1 for method exists, 0 for fail to find corresponding file
        """
        fpath = self.path + method.lower() + PZ_pattern.format(self.cid) + "_0_bg.dat"
        if isfile(fpath):
            self.pz[method] = axplot.get_data(self.path + method.lower() + PZ_pattern.format(self.cid))
            return 1

    def plot_pz(self, ax, method):
        """
        plot the P(z) data in given method

        :param ax: axis for plot
        :param method: method of detection as title
        """
        self.method = method
        for c in CMR_combination:
            ax.plot(self.pz[method][c][:, 0], self.pz[method][c][:, 1], '.', label=c)
            ax.set_title(method)
        ax.legend()

    def fit_pz(self, ax, color, fit_x=0):
        """
        fit the P(z) data for given color

        :param ax: axis to plot
        :param color: detection color
        :param fit_x: 0 for fix x, 1 for fit x
        """
        if self.method is None:
            warning("error! no method defined")
            return [0, 0]

        self.color = color
        self.fit_x = fit_x
        x = self.pz[self.method][color][:, 0]
        y = self.pz[self.method][color][:, 1]
        if fit_x == 0:
            fit = axplot.g3g(x, y, n_sigma=NSIGMA)
        else:
            fit = axplot.g3gf(x, y, n_sigma=NSIGMA)
        y = np.max(y) * np.exp(-(x - fit[0]) ** 2 / 2. / fit[1] ** 2)
        ax.plot(x, y, '--')
        self.fit_result = fit

    def insert_comment(self, photoz, comment):
        """
        store the result and present the result

        :param photoz: estimated photoz
        :param comment: comment information
        """
        self.db.insert_comment(self.cid, photoz, "%s-%s" % (self.method, self.color), comment)


class PhotozViewer(Tk.Frame):
    """
    View of MVC for P(z) plotting

    left for p(z) plotting, right for information

    :param master: master frame
    """

    def __init__(self, master=None):
        """
        initial two segments frame

        :param master: master frame
        """
        Tk.Frame.__init__(self, master, width='10.5i', height='5.5i')
        self.photoz = Tk.StringVar()  # photoz
        self.photoz.set("-")
        self.photoz_err = Tk.StringVar()  # photoz error
        self.photoz_err.set("-")
        self.comment = Tk.StringVar()  # comment
        self.grid_propagate(0)
        self.fig = None
        self.canvas = None
        self.cid = None  # Cluster ID input
        self.cluster_id_entry_button = None  # cluster ID input button
        self.cluster_info_label = None  # cluster information button
        self.fit_x = Tk.IntVar()  # choose to fit mean-z or peak-z
        self.pz_button = {}  # record buttons created
        self.fit_button = {}
        self.comment_button = None
        self.show_specz_button = None
        self.comment_label = None
        self.create_fig()
        self.create_info()
        self.create_control()
        self.grid()

    def create_fig(self):
        """
        create figure area
        create canvas handler, fig handler
        """
        figure_panel = Tk.Frame(self, width='6i', height='5.5i')
        figure_panel.grid(row=0, column=0, rowspan=3)
        self.fig = Figure()
        self.canvas = FigureCanvasTkAgg(self.fig, master=figure_panel)
        self.canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        NavigationToolbar2TkAgg(self.canvas, figure_panel)
        self.canvas.show()

    def create_info(self):
        """
        create information panel
        """
        self.cid = Tk.IntVar()
        info_frame = Tk.Frame(self, width='4.2i', height='2i')
        info_frame.grid_propagate(0)
        info_frame.grid(row=0, column=1)
        label = Tk.Label(info_frame, text="Cluster ID")
        label.grid(row=0, column=0)
        cluster_id_entry = Tk.Entry(info_frame, textvariable=self.cid, width=4)
        cluster_id_entry.grid(row=0, column=1)
        self.cluster_id_entry_button = Tk.Button(info_frame, text="Load")
        self.cluster_id_entry_button.grid(row=0, column=2)
        quit_button = Tk.Button(info_frame, text='Quit', command=self.quit)
        quit_button.grid(row=0, column=3)
        self.cluster_info_label = Tk.Label(info_frame, text="-", width=23, height=6)
        self.cluster_info_label.grid(row=2, column=0, rowspan=3, columnspan=4)

    def create_control(self, buttons=P_method):
        """
        create control panel
        
        :param buttons: contains an array of available methods
        """
        self.fit_x.set(1)
        control_frame = Tk.Frame(self, width='4.2i', height='0.8i')
        control_frame.grid_propagate(0)
        control_frame.grid(row=1, column=1)
        Tk.Checkbutton(control_frame, text='Peak?', variable=self.fit_x, onvalue=1, offvalue=0).grid(row=0, column=0)
        for i, method in enumerate(buttons):
            self.pz_button[method] = Tk.Button(control_frame, text=method, state=Tk.DISABLED)
            self.pz_button[method].grid(row=1, column=i)
        fit_frame = Tk.Frame(self, width='4.2i', height='2.4i')
        fit_frame.grid_propagate(0)
        fit_frame.grid(row=2, column=1)
        for i, c in enumerate(CMR_combination):
            self.fit_button[c] = Tk.Button(fit_frame, text=c, state=Tk.DISABLED)
            self.fit_button[c].grid(row=0, column=i)
        Tk.Entry(fit_frame, textvariable=self.photoz, width=5).grid(row=1, column=0, columnspan=2)
        Tk.Label(fit_frame, text="+/-").grid(row=1, column=2)
        Tk.Entry(fit_frame, textvariable=self.photoz_err, width=5).grid(row=1, column=3, columnspan=2)
        Tk.Entry(fit_frame, textvariable=self.comment).grid(row=2, column=0, columnspan=5)
        self.comment_button = Tk.Button(fit_frame, text="Comment")
        self.comment_button.grid(row=3, column=0, columnspan=3)
        self.show_specz_button = Tk.Button(fit_frame, text="Spec-z")
        self.show_specz_button.grid(row=3, column=3, columnspan=2)
        self.comment_label = Tk.Label(fit_frame)
        self.comment_label.grid(row=4, column=0, columnspan=5)

    def reset(self):
        """
        reset the information in the view
        """
        for button in self.pz_button.keys():
            self.pz_button[button].configure(state=Tk.DISABLED)
        self.cluster_info_label.configure(text="")
        self.photoz.set("")
        self.photoz_err.set("")
        self.comment.set("")
        self.fig.clf()


class PhotozController():
    """
    Controller of MVC for P(z) Plotting

    :param master: master frame passed to viewer
    """

    def __init__(self, master=None):
        """
        Initialize the MVC
        """
        self.method = None
        self.color = None
        self.view = PhotozViewer(master=master)  # Viewer
        self.model = PhotozModel()  # Model
        self.ax = None  # axis for matplotlib plotting
        self.view.cluster_id_entry_button.configure(command=self.load_cluster)

    def load_cluster(self):
        """
        load cluster data and reset the view
        """
        self.view.reset()
        cid = self.view.cid.get()
        if self.model.load(cid):
            self.view.cluster_info_label.configure(text=self.model.get_info())
            self.view.show_specz_button.configure(command=lambda: self.show_z())
        for method in P_method:
            if self.model.load_method(method):
                self.view.pz_button[method].configure(state=Tk.NORMAL, command=lambda x=method: self.plot_pz(x))
        for c in CMR_combination:
            self.view.fit_button[c].configure(state=Tk.NORMAL, command=lambda y=c: self.fit_pz(y))
        self.view.comment_button.configure(command=lambda: self.add_comment())
        self.view.comment_label.configure(text="")

    def plot_pz(self, method):
        """
        driver for plot the P(z)

        :param method: detection method
        """
        self.method = method
        self.view.fig.clf()
        self.ax = self.view.fig.add_subplot(111)
        self.model.plot_pz(self.ax, method)
        self.view.canvas.show()

    def fit_pz(self, color):
        """
        driver for fit the P(z)

        :param color: color combination to plot
        """
        self.color = color
        self.model.fit_pz(self.ax, color, fit_x=self.view.fit_x.get())
        # fill in the fitting result
        self.view.photoz.set("%6.4f" % self.model.fit_result[0])
        self.view.photoz_err.set("%6.4f" % self.model.fit_result[1])
        self.view.canvas.show()

    def show_z(self):
        """
        show the spec-z
        """
        self.view.cluster_info_label.configure(text="%s%s" % (self.model.get_info(), self.model.get_z()))

    def add_comment(self):
        """
        push to database
        """
        photoz = [float(self.view.photoz.get()), float(self.view.photoz_err.get())]
        self.model.insert_comment(photoz, self.view.comment.get())
        self.view.comment_label.configure(text="Comment in")


if __name__ == '__main__':
    root = Tk.Tk()
    root.title("Photo-z Examination")
    #root.geometry('450x500-20+20')
    app = PhotozController(master=root)
    root.mainloop()
