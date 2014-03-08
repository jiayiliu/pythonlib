"""

Interactive Selection Model
===========================

"""

__author__ = 'jiayiliu'

from matplotlib.patches import Circle
import numpy as np


class SelectCircle:
    """
    Class to select a circle in given figure

    :param figure: matplotlib figure object
    :param on_release: function to be called when mouse is released
    """

    def __init__(self, figure, on_release=None):
        """
        Initialize class

        :param figure: matplotlib figure object
        :param on_release: function to be called when mouse is released
        """
        self.pos = None
        self.r = None
        self.c = None
        self.record = None
        self.fig = figure
        if on_release is None:
            self.on_release = self.on_release_default
        else:
            self.on_release = on_release
        self.connect()

    def connect(self):
        """
        Connect the listener
        """
        self.cidpress = self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('key_press_event', self.disconnect)

    def on_press(self, event):
        """
        Default on_press function

        :param event: event of press button
        :return: set the center of the class
        """
        if self.c is not None:
            self.c.remove()
        self.pos = (event.xdata, event.ydata)
        self.r = 0.
        self.c = Circle(self.pos, radius=self.r, fill=False, ec='r', lw=3)
        self.fig.axes[0].add_patch(self.c)

    def on_release_default(self, event):
        """
        Default on_release function

        :param event: event of release button
        :return: clean pos and r, set record
        """
        self.record = (self.pos, self.r)
        self.pos = None
        self.r = None

    def on_motion(self, event):
        """
        Default on_motion function

        :param event: event of mouse motion
        :return: set radius and update the figure
        """
        if self.pos is None:
            return
        self.r = np.sqrt((event.xdata - self.pos[0]) ** 2 + (event.ydata - self.pos[1]) ** 2)
        self.c.set_radius(self.r)
        self.fig.canvas.draw()

    def get_record(self):
        """
        return the record
        :return: [x, y, r]
        """
        return self.record

    def disconnect(self, event):
        """
        listen to key stroke "ESC" to escape the event

        :param event: "ESC" event
        :return: disconnect the listener
        """
        if event.key == 'escape':
            self.fig.canvas.mpl_disconnect(self.cidmotion)
            self.fig.canvas.mpl_disconnect(self.cidrelease)
            self.fig.canvas.mpl_disconnect(self.cidpress)


if __name__ == "__main__":
    import matplotlib.pylab as plt

    fig = plt.figure()
    ax = fig.add_subplot(111)
    x = np.random.ranf(100)
    y = np.random.ranf(100)

    ax.plot(x, y, '.')
    g = SelectCircle(fig)

    plt.show()