"""

Viewer for galaxy photo-z measurement
=====================================

"""
__author__ = 'jiayiliu'

import Tkinter as Tk

from sparameter import P_method, CMR_combination
from GUItools import PlotWindow


class GalViewer(Tk.Tk):
    """
    Viewer of MVC

    :param controller: controller of MVC
    """

    def __init__(self, controller):
        """
        initialize the viewer

        :param controller controller of MVC
        """
        Tk.Tk.__init__(self)
        self.controller = controller  # Controller
        # Data loading part
        Tk.Label(self, text="ID:").grid(row=0, column=0, columnspan=2)
        self.entry_id = Tk.Entry(self)
        self.entry_id.grid(row=0, column=2)
        self.button_load = Tk.Button(self, text="load", command=self.load_catalog)
        self.button_load.grid(row=0, column=3)
        self.button_fits_gri = Tk.Button(self, text="FITS gri", state=Tk.DISABLED,
                                         command=lambda: controller.view_fits('gri'))
        self.button_fits_gri.grid(row=1, column=0)
        self.button_fits_riz = Tk.Button(self, text="FITS riz", state=Tk.DISABLED,
                                         command=lambda: controller.view_fits('riz'))
        self.button_fits_riz.grid(row=1, column=1)
        self.button_fits_grz = Tk.Button(self, text="FITS grz", state=Tk.DISABLED,
                                         command=lambda: controller.view_fits('grz'))
        self.button_fits_grz.grid(row=1, column=2)
        self.button_sketch = Tk.Button(self, text="Sketch", state=Tk.DISABLED, command=self.create_sketch)
        self.button_sketch.grid(row=1, column=3, columnspan=2)
        self.button_cmr = dict()
        self.cmr_window = dict()
        for ii, i in enumerate(CMR_combination):
            self.button_cmr[i] = Tk.Button(self, state=Tk.DISABLED, text=i,
                                           command=lambda: controller.view_cmr(i[0], i[1]))
            self.button_cmr[i].grid(row=2, column=ii)
        # Selection part
        self.button_select_sketch = Tk.Button(self, text="Select sketch", state=Tk.DISABLED,
                                              command=self.controller.select_galaxy_sketch)
        self.button_select_sketch.grid(row=3, column=0)
        self.button_update_select = Tk.Button(self, text="Update", state=Tk.DISABLED,
                                              command=self.controller.update_selection)
        self.button_update_select.grid(row=3, column=1)
        self.button_resample = Tk.Button(self, text="Resample", state=Tk.DISABLED, command=self.controller.resample)
        self.button_resample.grid(row=3, column=2)
        self.redshift = Tk.DoubleVar()
        self.str_redshift = Tk.StringVar()
        Tk.Label(self, textvariable=self.str_redshift).grid(row=4, column=0, columnspan=2)
        self.z_scale = Tk.Scale(self, from_=0, to=1.6, orient=Tk.HORIZONTAL, resolution=0.01, length=320,
                                command=self.controller.update_cmr_z, variable=self.redshift, showvalue=0)
        self.z_scale.grid(row=4, column=2, columnspan=4)
        self.bind("<Left>", self.key_cmr_left)
        self.bind("<Right>", self.key_cmr_right)
        # Saving part
        self.button_save_reg = Tk.Button(self, text="Save Region", state=Tk.DISABLED, command=self.save_window)
        self.button_save_reg.grid(row=5, column=1)
        self.button_clean = Tk.Button(self, text="Clean Region", state=Tk.DISABLED,
                                      command=self.controller.clean_selection)
        self.button_clean.grid(row=5, column=3)
        # cluster information panel
        self.cluster_frame = Tk.Frame()
        self.cluster_frame.grid(row=6, columnspan=5)
        self.sketch = None
        self.multi_list = None
        self.button_method = {}

    def key_cmr_left(self, event):
        """
        Move CMR to lower redshift
        """
        self.redshift.set(self.redshift.get()-0.01)
        self.controller.update_cmr_z(self.redshift.get())

    def key_cmr_right(self, event):
        """
        Move CMR to higher redshift
        """
        self.redshift.set(self.redshift.get()+0.01)
        self.controller.update_cmr_z(self.redshift.get())

    def load_catalog(self):
        """
        Call the controller to load the galaxy catalog

        :return: None
        """
        self.controller.initialize_galaxy(int(self.entry_id.get()))
        # enable button when data is ready
        self.button_fits_gri.config(state=Tk.NORMAL)
        self.button_fits_riz.config(state=Tk.NORMAL)
        self.button_fits_grz.config(state=Tk.NORMAL)
        self.button_sketch.config(state=Tk.NORMAL)
        for i in CMR_combination:
            self.button_cmr[i].config(state=Tk.NORMAL)
        self.button_select_sketch.config(state=Tk.NORMAL)
        self.button_update_select.config(state=Tk.NORMAL)
        self.button_resample.config(state=Tk.NORMAL)

    def set_cluster(self, info, method):
        """
         set cluster detail with given method

        :param info: basic information about the cluster
        :param method: detection method array [01]
        """
        Tk.Label(self.cluster_frame, text=info).grid(row=3, column=0, columnspan=3)
        for j in self.button_method.keys():
            self.button_method[j].destroy()
        i = 0
        for j in range(len(P_method)):
            if method[j] == 1:
                self.button_method[j] = Tk.Button(self.cluster_frame,
                                                  text=P_method[j],
                                                  command=lambda m=P_method[j]: self.controller.update_candidate_sketch(
                                                      m))
                self.button_method[j].grid(row=1, column=i)
                self.button_method[j].config(state=Tk.DISABLED)
                i += 1

    def create_sketch(self):
        """
        create sketch to show galaxy distribution
        """
        self.sketch = PlotWindow(master=self, title="Sketch")
        self.controller.view_sketch(self.sketch.axis)
        for j in self.button_method:
            self.button_method[j].config(state=Tk.NORMAL)

    def select_galaxy_sketch(self):
        """
        Driver to select galaxy from sketch

        :return: None
        """
        self.controller.select_galaxy_sketch()
        self.button_update_select.config(Tk.NORMAL)
        self.button_resample.config(Tk.NORMAL)
        self.sketch.update()

    def create_cmr(self, color):
        """
        create figure to show galaxy color-magnitude relation

        :param color: color combination to create
        """
        self.cmr_window[color] = PlotWindow(master=self, title="CMR {0:s}".format(color))
        return self.cmr_window[color].axis

    def save_window(self):
        """
        create save region file window
        """
        save_window = Tk.Toplevel(self)
        save_window.title("Save region files")
        NAMES = ["Sketch"] + CMR_combination
        self.multi_list = Tk.Listbox(save_window, selectmode=Tk.MULTIPLE)
        self.multi_list.pack()
        for i in range(6):
            self.multi_list.insert(Tk.END, NAMES[i])
        Tk.Button(save_window, text="Save",
                  command=self.controller.save_reg).pack()

    def run(self):
        """
        run GUI
        """
        self.mainloop()


