import tkinter as tk
from tkinter import X, Y, BOTTOM, RIGHT, LEFT, HORIZONTAL , END , DISABLED , ttk
from tkinter import StringVar , Tk , W ,E , S , BOTH, HIDDEN, DoubleVar , Spinbox , IntVar , filedialog

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib

from fil_chaud_validate import EntryFloat

class Margin:
    def __init__(self,nb , app ):
        self.first = 0
        self.nb = nb
        self.app = app
        self.frame = ttk.Frame(self.nb)
        self.level = 20
        self.nb.add(self.frame, text='   Heights & Margins (side view)   ')
        r = 0
        tk.Label(self.frame, text="Block height (mm)").grid(column=0, row=r, pady=(1,1), sticky=W)
        EntryFloat(self.frame, self.app.blocHZ , 1 , 500, self.level , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
    
        r += 1
        tk.Label(self.frame, text="Block elevation (mm)").grid(column=0, row=r, pady=(1,1), sticky=W)
        EntryFloat(self.frame, self.app.hOffset , 0 , 500, self.level , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
    
        r += 3
        tk.Label(self.frame, text="Vertical positioning of the profile (mm)").grid(column=0, row=r, pady=(10,1), sticky=W)
        EntryFloat(self.frame, self.app.hProfil , 0 , 500, self.level , width='6' ).grid(column=1, row=r , padx=1,pady=(10,1), sticky=W)
    
        r += 1
        tk.Label(self.frame, text="Profile alignment").grid(column=0, row=r, pady=(10,1), sticky=W)
        r += 1
        tk.Radiobutton(self.frame, text="Align trailing edges", variable=self.app.alignProfil, value="Trailing",
            command=self.validateAllLevelMargin).grid(column=0, row=r, pady=(1,1), sticky=W)
        r += 1
        tk.Radiobutton(self.frame, text="Align leading edges", variable=self.app.alignProfil, value="Leading",
            command=self.validateAllLevelMargin).grid(column=0, row=r, pady=(1,1), sticky=W)
        r += 1
        tk.Radiobutton(self.frame, text="Align intrados", variable=self.app.alignProfil, value="Intrados",
            command=self.validateAllLevelMargin).grid(column=0, row=r, pady=(1,1), sticky=W)
        r += 1
        tk.Radiobutton(self.frame, text="Align extrados", variable=self.app.alignProfil, value="Extrados",
            command=self.validateAllLevelMargin).grid(column=0, row=r, pady=(1,1), sticky=W)
        r =0
        tk.Label(self.frame, text=" - Heights relative to block-").grid(column=3, row=r, columnspan = 5, pady=(10,1), sticky=(W,E))
        r += 1
        tk.Label(self.frame, text="Trailing edge").grid(column=3, row=r, columnspan = 3, pady=(1,1), sticky=W)
        tk.Label(self.frame, text="Leading edge").grid(column=7, row=r, columnspan = 3, pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="Root").grid(column=2, row=r, pady=(1,1), sticky=W)
        tk.Entry(self.frame, textvariable=self.app.hTrailingRoot , width='6', state='disabled').grid(column=3, row=r , padx=1,pady=(1,1), sticky=W)
        tk.Entry(self.frame, textvariable=self.app.hLeadingRoot , width='6', state='disabled').grid(column=7, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="Tip").grid(column=2, row=r, pady=(1,1), sticky=W)
        tk.Entry(self.frame, textvariable=self.app.hTrailingTip , width='6', state='disabled').grid(column=3, row=r , padx=1,pady=(1,1), sticky=W)
        tk.Entry(self.frame, textvariable=self.app.hLeadingTip , width='6', state='disabled').grid(column=7, row=r , padx=1,pady=(1,1), sticky=W)
        r = 0
        tk.Label(self.frame, text=" - Margins relative to block -").grid(column=13, row=r, columnspan = 5, pady=(10,1), sticky=(W,E))
        r += 1
        tk.Label(self.frame, text="Intrados").grid(column=13, row=r, columnspan = 3, pady=(1,1), sticky=W)
        tk.Label(self.frame, text="Extrados").grid(column=17, row=r, columnspan = 3, pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="Root").grid(column=12, row=r, pady=(1,1), sticky=W)
        tk.Entry(self.frame, textvariable=self.app.hMinRoot , width='6', state='disabled').grid(column=13, row=r , padx=1,pady=(1,1), sticky=W)
        tk.Entry(self.frame, textvariable=self.app.hMaxRoot , width='6', state='disabled').grid(column=17, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="Tip").grid(column=12, row=r, pady=(1,1), sticky=W)
        tk.Entry(self.frame, textvariable=self.app.hMinTip , width='6', state='disabled').grid(column=13, row=r , padx=1,pady=(1,1), sticky=W)
        tk.Entry(self.frame, textvariable=self.app.hMaxTip , width='6', state='disabled').grid(column=17, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, textvariable=self.app.warningMsg, fg='red').grid(column=2, columnspan=15, row=r, pady=(1,1) )

        #lists to draw the bloc
        blocRootX = [self.app.blocToTableTrailingRoot.get(), self.app.blocToTableLeadingRoot.get(), self.app.blocToTableLeadingRoot.get() ,
            self.app.blocToTableTrailingRoot.get(), self.app.blocToTableTrailingRoot.get() ]
        blocTipX = [self.app.blocToTableTrailingTip.get(), self.app.blocToTableLeadingTip.get(), self.app.blocToTableLeadingTip.get() ,
            self.app.blocToTableTrailingTip.get(), self.app.blocToTableTrailingTip.get()]
        hOffset = self.app.hOffset.get()
        blocHZ =  self.app.blocHZ.get()
        blocRootY = [hOffset , hOffset, hOffset + blocHZ, hOffset + blocHZ, hOffset]
        blocTipY = blocRootY
        
        self.figRoot = Figure(figsize=(10, 2), dpi=100)
        self.axesRoot = self.figRoot.add_subplot(1,1,1)
        self.axesRoot.set_xlim(0, 1300)
        self.axesRoot.set_ylim(0, 260)
        self.axesRoot.set_title('Root')
        self.axesRoot.autoscale(enable=False)
        self.axesRoot.spines['top'].set_visible(False)
        self.axesRoot.spines['right'].set_visible(False)
        
        self.plotBlocRoot, = self.axesRoot.plot(blocRootX , blocRootY , color='black')
        self.plotRoot, = self.axesRoot.plot(self.app.pRootX , self.app.pRootY , color='red')
        self.canvasRoot = FigureCanvasTkAgg(self.figRoot, master=self.frame)  # A tk.DrawingArea.
        self.canvasRoot.draw()
        self.canvasRoot.get_tk_widget().grid(column=2, rowspan=3, columnspan=20, row=5, pady=(20,2))
        
        self.figTip = Figure(figsize=(10, 2), dpi=100)
        self.axesTip = self.figTip.add_subplot(1,1,1)
        self.axesTip.set_xlim(0,1300)
        self.axesTip.set_ylim(0, 260)
        self.axesTip.set_title('Tip')
        self.axesTip.autoscale(enable=False)
        self.axesTip.spines['top'].set_visible(False)
        self.axesTip.spines['right'].set_visible(False)
        
        self.plotBlocTip, = self.axesTip.plot(blocTipX , blocTipY , color='black')
        self.plotTip, = self.axesTip.plot(self.app.pTipX , self.app.pTipY , color='blue')
        self.canvasTip = FigureCanvasTkAgg(self.figTip, master=self.frame)  # A tk.DrawingArea.
        self.canvasTip.draw()
        self.canvasTip.get_tk_widget().grid(column=2, rowspan=3, columnspan=20 , row=9, pady=(20,2))
    
    def updatePlotMargin(self):
        blocRootX = [self.app.blocToTableTrailingRoot.get(), self.app.blocToTableLeadingRoot.get(), self.app.blocToTableLeadingRoot.get() ,
            self.app.blocToTableTrailingRoot.get(), self.app.blocToTableTrailingRoot.get() ]
        blocTipX = [self.app.blocToTableTrailingTip.get(), self.app.blocToTableLeadingTip.get(), self.app.blocToTableLeadingTip.get() ,
            self.app.blocToTableTrailingTip.get(), self.app.blocToTableTrailingTip.get()]
        hOffset = self.app.hOffset.get()
        blocHZ =  self.app.blocHZ.get()
        blocRootY = [hOffset , hOffset, hOffset + blocHZ, hOffset + blocHZ, hOffset]
        blocTipY = blocRootY
        # draw root bloc
        self.plotBlocRoot.set_xdata(blocRootX)
        self.plotBlocRoot.set_ydata(blocRootY)
        #draw root profil
        self.plotRoot.set_xdata(self.app.pRootX.tolist())
        self.plotRoot.set_ydata(self.app.pRootY.tolist())
        self.canvasRoot.draw()
        # draw tip bloc
        self.plotBlocTip.set_xdata(blocTipX)
        self.plotBlocTip.set_ydata(blocTipY)
        #draw tip profil
        self.plotTip.set_xdata(self.app.pTipX.tolist())
        self.plotTip.set_ydata(self.app.pTipY.tolist())
        self.canvasTip.draw()
        
    def validateAllLevelMargin(self):
        self.app.validateAll(self.level)
    