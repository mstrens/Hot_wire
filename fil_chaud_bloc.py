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



class Bloc:
    def __init__(self,nb , app ):
        self.first = 0
        self.nb = nb
        self.app = app
        self.frame = ttk.Frame(self.nb)
        self.level = 20
        self.nb.add(self.frame, text='   Bloc (top view)   ')
        r = 0
        tk.Label(self.frame, text="Wingspan (mm)").grid(column=0, row=r, pady=(1,1), sticky=W)
        EntryFloat(self.frame, self.app.blocLX , 10 , 1000, self.level , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
    
        r += 1
        tk.Label(self.frame, text="Bloc thickness (mm)").grid(column=0, row=r, pady=(1,1), sticky=W)
        EntryFloat(self.frame, self.app.blocHZ , 1 , 500, self.level , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
    
        r += 1
        tk.Label(self.frame, text="Flèche (mm)").grid(column=0, row=r, pady=(10,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="    Leading edge").grid(column=0, row=r, pady=(1,1), sticky=W)
        EntryFloat(self.frame, self.app.fLeading , -500 , 500, self.level , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
    
        r += 1
        tk.Label(self.frame, text="    Trailing edge").grid(column=0, row=r, pady=(1,1), sticky=W)
        #EntryFloat(self.frame, self.app.fTrailing , -500 , 500, self.level+3 , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        tk.Entry(self.frame, textvariable=self.app.fTrailing, width='6', state='disabled').grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)

        r += 1
        tk.Label(self.frame, text="Margins (mm)").grid(column=0, row=r, pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="     Leading edge").grid(column=0, row=r, pady=(1,1), sticky=W)
        EntryFloat(self.frame, self.app.mLeading , -20 , 50, self.level , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
    
        r += 1
        tk.Label(self.frame, text="     Root trailing edge").grid(column=0, row=r, pady=(1,1), sticky=W)
        EntryFloat(self.frame, self.app.mTrailingRoot , -20 , 50, self.level , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
    
        r += 1
        tk.Label(self.frame, text="     Tip trailing edge").grid(column=0, row=r, pady=(1,1), sticky=W)
        EntryFloat(self.frame, self.app.mTrailingTip , -20 , 50, self.level , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
    
        r += 1
        tk.Label(self.frame, text="Left / Right wing").grid(column=0, row=r, pady=(20,1), sticky=W)
        r += 1
        tk.Radiobutton(self.frame, text="Left", variable=self.app.leftRightWing, value="Left",
            command=self.validateAllLevelBloc).grid(column=0, row=r, pady=(1,1), sticky=W)
        r += 1
        tk.Radiobutton(self.frame, text="Right", variable=self.app.leftRightWing, value="Right",
            command=self.validateAllLevelBloc).grid(column=0, row=r, pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="Distance between table and block (mm)").grid(column=0, columnspan=2, row=r, pady=(1,1), sticky=W)
        r += 1
        tk.Radiobutton(self.frame, text="On the left side", variable=self.app.blocPosition, value="Left",
            command=self.blocPositionChanged).grid(column=0, row=r, pady=(1,1), sticky=W)
        
        self.blocToTableLeftBox = EntryFloat(self.frame, self.app.blocToTableLeft , 0 , 1000, self.level , width='6' )
        self.blocToTableLeftBox.grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Radiobutton(self.frame, text="On the rigth side", variable=self.app.blocPosition, value="Right",
            command=self.blocPositionChanged).grid(column=0, row=r, pady=(1,1), sticky=W)
        self.blocToTableRightBox = EntryFloat(self.frame, self.app.blocToTableRight , 0 , 1000, self.level , width='6' , state='disabled')
        self.blocToTableRightBox.grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="Distance between table origin and ").grid(column=0, columnspan=2, row=r, pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="   Root trailing edge").grid(column=0, row=r, pady=(1,1), sticky=W)
        EntryFloat(self.frame, self.app.blocToTableTrailingRoot , 0 , 500, self.level , width='6').grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="   Tip trailing edge").grid(column=0, row=r, pady=(1,1), sticky=W)
        tk.Entry(self.frame, textvariable=self.app.blocToTableTrailingTip , width='5' , state='disabled').grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        
        r += 1
        tk.Label(self.frame, text="   Root leading edge").grid(column=0, row=r, pady=(1,1), sticky=W)
        tk.Entry(self.frame, textvariable=self.app.blocToTableLeadingRoot , width='5', state='disabled').grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="   Tip leading edge").grid(column=0, row=r, pady=(1,1), sticky=W)
        tk.Entry(self.frame, textvariable=self.app.blocToTableLeadingTip , width='5', state='disabled').grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        
        self.dotX = 10 # define the size and ratio of the figure
        self.dotY = 6
        self.blocTopFig = Figure(figsize=(self.dotX, self.dotY), dpi=100)
        self.blocTopAxes = self.blocTopFig.add_subplot(1,1,1)
        self.blocTopAxes.set_title('Top view')
        self.blocTopAxes.spines['top'].set_visible(False)
        self.blocTopAxes.spines['right'].set_visible(False)
        self.blocTopAxes.autoscale(enable=False)
        self.plotTable, = self.blocTopAxes.plot([], [] , color='green') #draw table
        self.plotBloc, = self.blocTopAxes.plot([], [] , color='black') #draw bloc
        self.plotLeading, = self.blocTopAxes.plot([], [] , 'k-.', color='black') #draw leading edge
        self.plotTrailing, = self.blocTopAxes.plot([], [] , 'k--', color='black') #draw trailing edge
        self.blocTopFig.legend((self.plotTable, self.plotBloc,self.plotLeading,self.plotTrailing ), ('Table', 'Bloc', 'Leading','Trailing'), 'upper right')
        self.blocTopFig.set_tight_layout(True)
        self.blocTopCanvas = FigureCanvasTkAgg(self.blocTopFig, master=self.frame)  # A tk.DrawingArea.
        self.blocTopCanvas.draw()
        self.blocTopCanvas.get_tk_widget().grid(column=2, row=0, rowspan=20, padx=10 , pady=(20,2))
        self.updatePlotBloc()
        
    def validateAllLevelBloc(self):
        self.app.validateAll(self.level)
    
    """
    def validate_blocToTableLeft(self):
        if self.first > 0:
            self.app.validateAll() 
        self.first = 1

        return True
    """

    def blocPositionChanged(self):
        if self.app.blocPosition.get() == 'Left':
            self.blocToTableLeftBox['state']='normal'
            self.blocToTableRightBox['state']='disabled'
        else:
            self.blocToTableLeftBox['state']='disabled'
            self.blocToTableRightBox['state']='normal'
        
    def updatePlotBloc(self):  #update plotting the bloc (1 canvas: Top)
        # draw table
        cMaxY = self.app.cMaxY.get()
        cMaxX = self.app.tableYY.get() - self.app.tableYG.get() - self.app.tableYD.get()
        # set the limits of X and Y depending on table size (keeping predifine ratio of the figure)
        maxX = cMaxX + 3
        maxY = cMaxY + 4
        limMinX =  - 3
        limMinY =  - 3
        zoom = 1
        if ( maxY / maxX ) < ( self.dotY / self.dotX ):
            limMaxX = limMinX + ( maxX / zoom )
            limMaxY = limMinY + ( maxX / zoom * self.dotY / self.dotX)
        else:
            limMaxY = limMinY + (maxY / zoom)
            limMaxX = limMinX + (maxY / zoom * self.dotX / self.dotY)   
        self.blocTopAxes.set_xlim(limMinX, limMaxX)
        self.blocTopAxes.set_ylim(limMinY, limMaxY)
        
        self.plotTable.set_xdata([0, 0 , cMaxX, cMaxX, 0  ])
        self.plotTable.set_ydata([0 , cMaxY, cMaxY, 0 , 0 ])
        #draw bloc
        bGX = self.app.blocToTableLeft.get()
        bDX = self.app.blocToTableLeft.get() + self.app.blocLX.get()
        if self.app.leftRightWing.get() == "Right":        
            bGTY = self.app.blocToTableTrailingRoot.get()
            bGLY = self.app.blocToTableLeadingRoot.get()
            bDTY = self.app.blocToTableTrailingTip.get()
            bDLY = self.app.blocToTableLeadingTip.get()
        else:
            bGTY = self.app.blocToTableTrailingTip.get()
            bGLY = self.app.blocToTableLeadingTip.get()
            bDTY = self.app.blocToTableTrailingRoot.get()
            bDLY = self.app.blocToTableLeadingRoot.get()
        self.plotBloc.set_xdata( [bGX , bGX , bDX, bDX , bGX ] )
        self.plotBloc.set_ydata( [bGTY , bGLY, bDLY , bDTY , bGTY] )
        # draw trailing edge
        fTGX = self.app.blocToTableLeft.get()
        fTDX = fTGX + self.app.blocLX.get()
        fTGXp = 0
        fTDXp = self.app.tableYY.get() - self.app.tableYD.get() - self.app.tableYG.get()
        if self.app.leftRightWing.get() == "Right":        
            fTGY = self.app.blocToTableTrailingRoot.get() + self.app.mTrailingRoot.get()
            fTDY = self.app.blocToTableTrailingTip.get() + self.app.mTrailingTip.get() 
        else:
            fTGY = self.app.blocToTableTrailingTip.get() + self.app.mTrailingTip.get()
            fTDY = self.app.blocToTableTrailingRoot.get() + self.app.mTrailingRoot.get() 
        fTGYp , fTDYp = projection( fTGX , fTDX , fTGY , fTDY , fTGXp , fTDXp  )
        self.plotTrailing.set_xdata( [fTGXp , fTDXp ] )
        self.plotTrailing.set_ydata( [fTGYp , fTDYp] )
        #draw leading edge
        fLGX = fTGX
        fLDX = fTDX
        fLGXp = 0
        fLDXp = fTDXp
        if self.app.leftRightWing.get() == "Right":        
            fLGY = fTGY + self.app.cRoot.get()
            fLDY = fTDY + self.app.cTip.get()
        else:    
            fLGY = fTGY + self.app.cTip.get()
            fLDY = fTDY + self.app.cRoot.get()
        fLGYp , fLDYp = projection( fLGX , fLDX , fLGY , fLDY , fLGXp , fLDXp  )
        self.plotLeading.set_xdata( [fLGXp , fLDXp ] )
        self.plotLeading.set_ydata( [fLGYp , fLDYp] )
        self.blocTopCanvas.draw()


def projection(x1 , x2 , y1 , y2, xi , xj):
    a = (y2 - y1) / (x2 - x1)
    b = y1 - a * x1
    yi = (a * xi) + b
    yj = (a * xj) + b
    return yi , yj

