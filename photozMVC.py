#!/usr/bin/env python

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import numpy as np
import Tkinter as tk
from os.path import isfile

import numpy as np
import axplot
import accessDB as db

## Method for Planck clusters
PButtons =["MMF1","MMF3","PwS"]
## color combinations
CMR = axplot.clabels
## sigma clipping 
NSIGMA = 3

##
#  Model for photoz
class photozModel():
    def __init__(self):
        ## cluster id
        self.cid = 0
        ## data path
        self.path = axplot.PhotozPath
        
    ## load cluster photo-z result
    def load(self,cid):
        self.cid = cid
        ## photo-z data array
        self.pz = {}
        ## Cluster class provides information from database
        self.cluster = db.planckCand(cid)
        ## detection method
        self.method = None
        if self.cluster is not None:
            return True
        else:
            return False

    ## get the cluster informaiton
    def getInfo(self):
        return self.cluster.getR500()

    ## get the cluster known redshift
    def getZ(self):
        return self.cluster.getRedshift()
    
    ## get the method data
    # \return 1 for method exists, 0 for fail to find corresponding file
    def loadMethod(self,method):
        fpath = self.path+method+"/%d_0_bg.dat"%self.cid
        if isfile(fpath):
            self.pz[method] = axplot.getdata(self.path+method+"/%d"%self.cid)
            return 1

    ## plot the P(z) data in given method
    def plotpz(self,ax,method):
        self.method = method
        for c in CMR:
            ax.plot(self.pz[method][c][:,0],self.pz[method][c][:,1],'.',label=c)
            ax.set_title(method)
        ax.legend()

    ## fit the P(z) data for given color
    def fitpz(self,ax,color,fitx=0):
        if self.method is None:
            print "error! no method defined"
            return [0,0]
        ## detection color
        self.color = color
        ## fit peak or mean
        self.fitx = fitx
        x = self.pz[self.method][color][:,0]
        y = self.pz[self.method][color][:,1]
        if fitx == 0:
            fit = axplot.g3g(x,y,nsigma=NSIGMA)
        else:
            fit = axplot.g3gf(x,y,nsigma=NSIGMA)
        y = np.max(y)*np.exp(-(x-fit[0])**2/2./fit[1]**2)
        ax.plot(x,y,'--')
        ## store the fitting result centre value and std
        self.rfit = fit

    ## store the result and present the result
    def insertComment(self,photoz,comment):
        self.insertComment(self.cid,photoz,"%s-%s"%(self.method,self.color),comment)
        
##
#  Viewer of photoz
class photozViewer(tk.Frame):
    ## initial two segaments frame
    # left for p(z) plotting, right for information
    def __init__(self,master=None):
        tk.Frame.__init__(self,width='10.5i',height='5.5i')
        ## photoz
        self.photoz = tk.StringVar()
        self.photoz.set("-")
        ## photoz error
        self.photozerr = tk.StringVar()
        self.photozerr.set("-")
        ## comment
        self.comment = tk.StringVar()
        self.grid_propagate(0)
        self.grid()
        self.createFig()
        self.createInfo()
        self.createControl()
        
        
    ## create figure area
    #  create canvas handler, fig handler
    def createFig(self):
        figurePanel = tk.Frame(self,width='6i',height='5.5i')
        figurePanel.grid(rowspan=3)
        self.fig = Figure(figsize=(6,4))
        self.canvas = FigureCanvasTkAgg(self.fig,master=figurePanel)
        self.canvas.get_tk_widget().pack()
        toolbar = NavigationToolbar2TkAgg(self.canvas,figurePanel)
        self.canvas.show()

    ## create information panel
    def createInfo(self):
        ## Cluster ID input
        self.cid = tk.IntVar();
        infoFrame = tk.Frame(self,width='4.2i',height='2i')
        infoFrame.grid_propagate(0)
        infoFrame.grid(row=0,column=1)
        label = tk.Label(infoFrame,text="Cluster ID")
        label.grid(row=0,column=0)
        clusterIdEntry = tk.Entry(infoFrame,textvariable=self.cid,width=4)
        clusterIdEntry.grid(row=0,column=1)
        ## cluster ID input button
        self.clusterIdEntryButton = tk.Button(infoFrame,text="Load")
        self.clusterIdEntryButton.grid(row=0,column=2)
        quitButton = tk.Button(infoFrame, text='Quit', command=self.quit)
        quitButton.grid(row=0,column=3)
        ## cluster information button
        self.clusterInfoLabel = tk.Label(infoFrame,text="-",width=23,height=6)
        self.clusterInfoLabel.grid(row=2,column=0,rowspan=3,columnspan=4)

    ## create control panel
    #  \param buttons contains an array of available methods
    def createControl(self,buttons=PButtons):
        ## choose to fit mean-z or peak-z
        self.fitx = tk.IntVar()
        self.fitx.set(1)
        controlFrame = tk.Frame(self,width='4.2i',height='0.8i')
        controlFrame.grid_propagate(0)
        controlFrame.grid(row=1,column=1)
        fitx  = tk.Checkbutton(controlFrame, text='Peak?', variable=self.fitx, onvalue=1, offvalue=0)
        fitx.grid(row=0,column=0)
        ## record buttons created
        self.pzButton = {}
        for i,method in enumerate(buttons):
            self.pzButton[method] = tk.Button(controlFrame,text=method,state=tk.DISABLED)
            self.pzButton[method].grid(row=1,column=i)
        fitFrame = tk.Frame(self,width='4.2i',height='2.4i')
        fitFrame.grid_propagate(0)
        fitFrame.grid(row=2,column=1)
        self.fitButton = {}
        for i,c in enumerate(CMR):
            self.fitButton[c] = tk.Button(fitFrame,text=c,state=tk.DISABLED)
            self.fitButton[c].grid(row=0,column=i)
        photozEntry = tk.Entry(fitFrame,textvariable=self.photoz,width=5)
        photozEntry.grid(row=1,column=0,columnspan=2)
        pmlabel = tk.Label(fitFrame,text="+/-")
        pmlabel.grid(row=1,column=2)
        photozerrEntry = tk.Entry(fitFrame,textvariable=self.photozerr,width=5)
        photozerrEntry.grid(row=1,column=3,columnspan=2)
        photozcommentEntry = tk.Entry(fitFrame,textvariable=self.comment)
        photozcommentEntry.grid(row=2,column=0,columnspan=5)
        self.commentButton = tk.Button(fitFrame,text="Commment")
        self.commentButton.grid(row=3,column=0,columnspan=3)
        self.showSpeczButton = tk.Button(fitFrame,text="Spec-z")
        self.showSpeczButton.grid(row=3,column=3,columnspan=2)
        self.commentLabel = tk.Label(fitFrame)
        self.commentLabel.grid(row=4,column=0,columnspan=5)
                
    ## reset the information in the view
    def reset(self):
        for button in self.pzButton.keys():
            self.pzButton[button].configure(state=tk.DISABLED)
        self.clusterInfoLabel.configure(text="")
        self.fig.clf()
##
#  Controller of photoz
class PhotozController(tk.Frame):
    ## create the photoz window
    def __init__(self, master=None):
        # Viewer
        self.view = photozViewer(master=master)
        # Model
        self.model = photozModel()
        ## axis for matplotlib plotting
        self.ax = None
        self.view.clusterIdEntryButton.configure(command=self.loadcluster)

    ## load cluster data
    def loadcluster(self):
        self.view.reset()
        cid = self.view.cid.get()
        if self.model.load(cid):
            self.view.clusterInfoLabel.configure(text=self.model.getInfo())
            self.view.showSpeczButton.configure(command=lambda:self.showz())
        for method in PButtons:
            if self.model.loadMethod(method):
                self.view.pzButton[method].configure(state=tk.NORMAL,command=lambda x=method:self.plotpz(x))
        for c in CMR:
            self.view.fitButton[c].configure(state=tk.NORMAL,command=lambda y=c:self.fitpz(y))
        self.view.commentButton.configure(command=lambda:self.addcomment())
        self.view.commentLabel.configure(text="")
                
    ## driver for plot the P(z)
    def plotpz(self,method):
        self.method = method
        self.view.fig.clf()
        self.ax = self.view.fig.add_subplot(111)
        self.model.plotpz(self.ax,method)
        self.view.canvas.show()

    ## driver for fit the P(z)
    def fitpz(self,color):
        self.color = color
        self.model.fitpz(self.ax,color,fitx=self.view.fitx.get())
        # fill in the fitting result
        self.view.photoz.set("%6.4f"%self.model.rfit[0])
        self.view.photozerr.set("%6.4f"%self.model.rfit[1])
        self.view.canvas.show()

    ## show the spec-z
    def showz(self):
        self.view.clusterInfoLabel.configure(text="%s%s"%(self.model.getInfo(),self.model.getZ()))

    ## push to database
    def addcomment(self):
        photoz = [float(self.view.photoz.get()),float(self.view.photozerr.get())]
        self.model.insertComment(photoz,self.view.comment.get())
        self.view.commentLabel.configure(text="Comment in")
        
if __name__ == '__main__':
    root = tk.Tk()
    root.title("Photo-z Examination")
    #root.geometry('450x500-20+20')
    app = PhotozController(master=root)
    root.mainloop()
    
