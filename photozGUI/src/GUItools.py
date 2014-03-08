"""

Quick Tools for GUI purpose
============================

"""

import Tkinter as Tk
from matplotlib import figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

__author__ = 'jiayiliu'


class Message():
    """
    pop warning message

    :param master: master window
    :param text: message to show
    """

    def __init__(self, text, master=None, title="Warning"):
        self.window = Tk.Toplevel(master)
        self.window.title(title)
        self.window.config(width=300)
        Tk.Message(self.window, text=text, width=300).pack()
        Tk.Button(self.window, text="OK", command=self.window.destroy).pack()


class PlotWindow():
    """
    individual plot window

    :param master: the master window
    """

    def __init__(self, master=None, title="Plotting"):
        """ Initialize a plotting window

        :param master: the master window
        """
        self.window = Tk.Toplevel(master)
        self.window.title(title)
        self.figure = figure.Figure(figsize=(8, 8))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.window)
        self.axis = self.figure.add_subplot(111)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        NavigationToolbar2TkAgg(self.canvas, self.window).update()
        self.canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

    def clf(self):
        """
        Clean current plot
        """
        self.figure.clf()
        self.axis = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.window)
        self.canvas.show()

    def update(self):
        """
        Update the figure
        """
        self.canvas.show()