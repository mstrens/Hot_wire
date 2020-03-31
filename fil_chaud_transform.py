import tkinter as tk
from tkinter import X, Y, BOTTOM, RIGHT, LEFT, HORIZONTAL , END , DISABLED , ttk 
from tkinter import StringVar , Tk , W ,E , S , BOTH, HIDDEN, DoubleVar , Spinbox , IntVar , filedialog

import math
import re

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib

import numpy as np

from shapely.geometry import LineString
from shapely import affinity
from scipy import interpolate


from fil_chaud_validate import EntryFloat

class Transform:
    def __init__(self,nb, app):
        self.nb = nb
        self.app = app
        self.frame = ttk.Frame(self.nb)
        self.level = 10
        self.nb.add(self.frame, text='   Transform   ')
        r = 0
        tk.Label(self.frame, text="Root").grid(column=0, row=r, pady=(1,2) )
        r += 1
        tk.Label(self.frame, text="Chord").grid(column=0, row=r, pady=(1,1), sticky=E)
        EntryFloat(self.frame, self.app.cRoot , 1 , self.app.cMaxY.get(), self.level , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        
        r += 1
        tk.Label(self.frame, text="Thickness (%)").grid(column=0, row=r, pady=(1,1), sticky=E)
        EntryFloat(self.frame, self.app.thicknessRoot , 1 , 500 , self.level, width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        
        r += 1
        tk.Label(self.frame, text="Incidence (°)").grid(column=0, row=r, pady=(1,1), sticky=E)
        EntryFloat(self.frame, self.app.incidenceRoot , -180 , 180, self.level , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        
        r += 1
        tk.Label(self.frame, text="Vertically invert").grid(column=0, row=r, pady=(1,1), sticky=E)
        tk.Checkbutton(self.frame, variable=self.app.vInvertRoot , text='', command=self.validateAllLevelTransform).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        
        r += 1
        tk.Label(self.frame, text="Tip").grid(column=0, row=r, pady=(20,2))
        r += 1
        tk.Label(self.frame, text="Chord").grid(column=0, row=r, pady=(1,1), sticky=E)
        EntryFloat(self.frame, self.app.cTip , 1 , self.app.cMaxY.get(), self.level , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        
        r += 1
        tk.Label(self.frame, text="Thickness (%)").grid(column=0, row=r, pady=(1,1), sticky=E)
        EntryFloat(self.frame, self.app.thicknessTip , 1 , 500, self.level , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        
        r += 1
        tk.Label(self.frame, text="Incidence (°)").grid(column=0, row=r, pady=(1,1), sticky=E)
        EntryFloat(self.frame, self.app.incidenceTip , -180 , 180, self.level , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        
        r += 1
        tk.Label(self.frame, text="Vertically invert").grid(column=0, row=r, pady=(1,1), sticky=E)
        tk.Checkbutton(self.frame, variable=self.app.vInvertTip , text='', command=self.validateAllLevelTransform).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        
        r += 1
        tk.Label(self.frame, text="Apply on both profils").grid(column=0, row=r, pady=(20,2))
        r += 1
        tk.Label(self.frame, text="Smooth profiles").grid(column=0, row=r, pady=(1,1), sticky=W)
        tk.Checkbutton(self.frame, variable=self.app.smooth , text='', command=self.changeSmooth).grid(column=1, row=r , padx=1,pady=(1,1), sticky=E)
        r += 1
        tk.Label(self.frame, text="  Number of points").grid(column=0, row=r, pady=(1,1), sticky=E)
        self.nbrPointsBox = EntryFloat(self.frame, self.app.nbrPoints , 10 , 1000, self.level , width='6' )
        self.nbrPointsBox.grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="  Spreading factor").grid(column=0, row=r, pady=(1,1), sticky=E)
        self.repartitionBox = EntryFloat(self.frame, self.app.repartition , 0.5 , 2, self.level , width='6' )
        self.repartitionBox.grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        
        r += 1
        tk.Label(self.frame, text="Covering (mm)").grid(column=0, row=r, pady=(1,1), sticky=W)
        EntryFloat(self.frame, self.app.covering , -5 , 5, self.level , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        
        r += 1
        tk.Label(self.frame, text="Extend to keep chords").grid(column=0, row=r, pady=(1,1), sticky=E)
        tk.Checkbutton(self.frame, variable=self.app.keepChord , text='', command=self.validateAllLevelTransform).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="Reduce nbr of points").grid(column=0, row=r, pady=(1,1), sticky=E)
        tk.Checkbutton(self.frame, variable=self.app.reducePoints , text='' , command=self.validateAllLevelTransform).grid(column=1, row=r , padx=1,pady=(1,1))
        
        r=12
        self.displayPoints = IntVar(value='1')
        tk.Checkbutton(self.frame, variable=self.displayPoints , text='Show points', command=self.validateAllLevelTransform).grid(column=2, row=r , padx=1,pady=(1,1))
        
        r=14
        tk.Label(self.frame, textvariable=self.app.warningMsg, fg='red').grid(column=2, columnspan=5, row=r, pady=(1,1) )
        #tk.Label(self.frame, text="test", bg='red').grid(column=2, columnspan=5, row=r, pady=(1,1))

        self.app.tRootX = np.array(self.app.oRootX)
        self.app.tRootY = np.array(self.app.oRootY)
        self.app.tTipX = np.array(self.app.oTipX)
        self.app.tTipY = np.array(self.app.oTipY)
        self.plotProfil()

    def changeSmooth(self):
        if self.app.smooth.get() == 1:
            self.nbrPointsBox['state']='normal'
            self.repartitionBox['state']='normal'
        else:
            self.nbrPointsBox['state']='disabled'
            self.repartitionBox['state']='disabled'
        self.validateAllLevelTransform()

    def validateAllLevelTransform(self):
        self.app.validateAll(self.level)

    def validateTransform(self):
        #at the end, tRoot and tTip are generated, and draw but do not take care of bloc and margin

        #convert List to numpy array
        self.app.tRootX = np.array(self.app.oRootX)
        self.app.tRootY = np.array(self.app.oRootY)
        self.app.tRootS = self.app.oRootS.copy()
        self.app.tTipX = np.array(self.app.oTipX)
        self.app.tTipY = np.array(self.app.oTipY)
        self.app.tTipS = self.app.oTipS.copy()

        #apply thickness
        if self.app.thicknessRoot.get() != 100.0:
            self.app.tRootY = self.app.tRootY * self.app.thicknessRoot.get() / 100
        if self.app.thicknessTip.get() != 100.0:
            self.app.tTipY = self.app.tTipY * self.app.thicknessTip.get() / 100
        #apply incidence
        if self.app.incidenceRoot.get() != 0:
            line = LineString(self.merge(self.app.tRootX , self.app.tRootY) ) #create a linestring with a list of turple
            rotated = affinity.rotate(line, -1 * self.app.incidenceRoot.get() ) #rotate the linestring
            rotatedXY = rotated.xy #extract the coordinate
            self.app.tRootX = np.array(rotatedXY[0])
            self.app.tRootY = np.array(rotatedXY[1])
        if self.app.incidenceTip.get() != 0:
            line = LineString(self.merge(self.app.tTipX , self.app.tTipY) ) #create a linestring with a list of turple
            rotated = affinity.rotate(line, -1 * self.app.incidenceTip.get() ) #rotate the linestring
            rotatedXY = rotated.xy #extract the coordinate
            self.app.tTipX = np.array(rotatedXY[0])
            self.app.tTipY = np.array(rotatedXY[1])
        # appy vertical invert
        if self.app.vInvertRoot.get() == 1:
            self.app.tRootY = self.app.tRootY * -1.0
            self.app.tRootX = np.flip(self.app.tRootX)
            self.app.tRootY = np.flip(self.app.tRootY)
        if self.app.vInvertTip.get() == 1:
            self.app.tTipY = self.app.tTipY * -1.0
            self.app.tTipX = np.flip(self.app.tTipX)
            self.app.tTipY = np.flip(self.app.tTipY)

        # Normalise the 2 profiles based on chords and apply covering on Root and Tip
        # Here we don't yet take care of position of bloc and of margin
        self.app.tRootX, self.app.tRootY = self.app.normaliseArrayProfil( self.app.tRootX , self.app.tRootY , self.app.cRoot.get() )
        self.app.tTipX, self.app.tTipY = self.app.normaliseArrayProfil( self.app.tTipX , self.app.tTipY , self.app.cTip.get() )   
        #print("root after normalise", self.app.tRootX, self.app.tRootY)        
        
        # apply smoothing (if asked) based on number of points and spreading repartition
        if self.app.smooth.get() == 1:
            self.app.tRootX, self.app.tRootY = self.changeNbrPoints(self.app.tRootX, self.app.tRootY)
            self.app.tTipX, self.app.tTipY = self.changeNbrPoints(self.app.tTipX, self.app.tTipY)
        
        # take care of covering
        self.applyCovering()
        
        # insert synchro points if they do not yet exist
        if len(self.app.tRootS) == 0 or len(self.app.tTipS) == 0:
            self.app.tRootS = self.addSynchroPoints(self.app.tRootX, self.app.tRootY)
            self.app.tTipS = self.addSynchroPoints(self.app.tTipX, self.app.tTipY)
        
        #self.printProfile("before simplify", self.app.tRootX , self.app.tRootY , self.app.tRootS)
        # reduce the number of points but keep the synchronisation; the parameter is the max error (in mm)
        if self.app.reducePoints.get() == 1:
            #self.app.tRootX , self.app.tRootY , self.app.tTipX , self.app.tTipY = self.simplify(0.01) 
            self.app.tRootX , self.app.tRootY , self.app.tRootS = self.simplifyOneProfile(
                self.app.tRootX , self.app.tRootY , self.app.tRootS , 0.01 )
            self.app.tTipX , self.app.tTipY , self.app.tTipS = self.simplifyOneProfile(
                self.app.tTipX , self.app.tTipY , self.app.tTipS , 0.01 )
            #self.printProfile("after simplify", self.app.tRootX , self.app.tRootY , self.app.tRootS)        
        # insert mid first and last points of profile as defined before covering when extend to original coord is requested 
        self.applyKeepChord()
        
        
        #self.printProfile("Root X Y S" , self.app.tRootX, self.app.tRootY , self.app.tRootS)

    def printProfile(self, text, x ,y ,s):
        print(text)
        print("len x y s", len(x), len(y), len(s))
        if len(x)> 0 and len(x) == len(y) and len(x) == len(s) :
            i = 0
            imax = len(x)
            while i < imax:
                print("   ",x[i], y[i] , s[i])
                i += 1


    def addSynchroPoints(self, x, y):
        #create a list with the synchronisation point (4 = synchro; 0 = no synchro, 10 = synchro and no radiance)
        #first and last points are synchronisation points
        # point with the greatest X is also a synchro 
        s = []
        if len(x) > 0:
            s = [0] * len(x) # create a list with 0 every where
            s[0] = 4  # add synchro for the first and last point
            s[-1] = 4
            # find the point with max X
            maxX = np.max(x)
            # find the index of this point
            idxMax = np.where(x == maxX) #return an array with indexes
            if len(idxMax) > 0 and len(idxMax[0]) > 0:
                r = idxMax[0][0]
                s[r] = 4
            else:
                r=0 # not sure if it can happens    
        return s

    def applyCovering(self):
        if self.app.covering.get() != 0:
            #save a copy of txxxx before covering because we use it after synchro when Extend Chord is ON
            self.nRootX = np.copy(self.app.tRootX)
            self.nRootY = np.copy(self.app.tRootY)
            self.nTipX = np.copy(self.app.tTipX)
            self.nTipY = np.copy(self.app.tTipY)
            self.app.tRootX , self.app.tRootY = self.applyOffset(self.nRootX, self.nRootY , self.app.covering.get())
            self.app.tTipX , self.app.tTipY = self.applyOffset(self.nTipX, self.nTipY , self.app.covering.get())
    
    def applyOffset(self, xN, yN, d):
        line = LineString(self.merge(xN , yN) ) #create a linestring with a list of turple
        offLine= line.parallel_offset(d , side='right' , resolution=16, join_style=2, mitre_limit=5)
        if "Multi" in str(type(offLine)) :
            offLineXY = offLine[0].xy #extract the coordinate
        else:
            offLineXY = offLine.xy #extract the coordinate
        # there is a bug in the Offset function. With side = right, sequence is revered and have to be reversed afterward    
        return np.array(list(reversed(offLineXY[0])))  , np.array(list(reversed(offLineXY[1])))
        
    def applyKeepChord(self):  
        if (self.app.keepChord.get() == 1) and (self.app.covering.get() != 0 ):
            #insert first and last points before applying offset (reuse nxxxx saved before covering)
            self.app.tRootX = np.insert(self.app.tRootX, 0, self.nRootX[0])
            self.app.tRootX = np.append(self.app.tRootX, self.nRootX[-1])
            self.app.tRootY = np.insert(self.app.tRootY, 0, self.nRootY[0])
            self.app.tRootY = np.append(self.app.tRootY, self.nRootY[-1])
            self.app.tTipX = np.insert(self.app.tTipX, 0, self.nTipX[0])
            self.app.tTipX = np.append(self.app.tTipX, self.nTipX[-1])
            self.app.tTipY = np.insert(self.app.tTipY, 0, self.nTipY[0])
            self.app.tTipY = np.append(self.app.tTipY, self.nTipY[-1])
            self.app.tRootS.insert(0,10) #insert a first point as synchro  and No radiance
            self.app.tRootS[-1] = 10 # convert last point as synchro  and No radiance
            self.app.tRootS.append( 4) #add a last point as synchro
            self.app.tTipS.insert(0,10) #insert a first point as synchro  and No radiance
            self.app.tTipS[-1] = 10 # convert last point as synchro  and No radiance
            self.app.tTipS.append( 4) #add a last point as synchro
            

    def changeNbrPoints(self, x , y):
        xnew = []
        ynew = []
        if len(x) > 0:
            # find the point with max X
            maxX = np.max(x)
            # find the index of this point
            idxMax = np.where(x == maxX) #return an array with indexes
            if len(idxMax) > 0 and len(idxMax[0]) > 0:
                r = idxMax[0][0]
            else:
                r=0 # not sure if it can happens    
            # split extrados / intrados in 2 lines
            #print("r=",r)
            #print("x,y", x, y)
            eX= x[0 : r+1]
            eY= y[0 : r+1]
            iX= x[r:]
            iY= y[r:]
            #print("extrados avant=", eX, eY)
            
            mytck,myu=interpolate.splprep([eX,eY], k=1, s=0)
            arrayRepartition = np.linspace(0,1,int(self.app.nbrPoints.get()/2) ) ** self.app.repartition.get()
            arrayRepartitionExt = (np.flip(arrayRepartition) * -1 ) + 1
            eXnew,eYnew= interpolate.splev(arrayRepartitionExt, mytck)
            #print("arrayRepartition ext",arrayRepartitionExt)
            #print("extrados après", eXnew, eYnew)    
            
            #print("intrados avant=", iX, iY)
            mytck,myu=interpolate.splprep([iX,iY], k=1, s=0)
            arrayRepartition = np.linspace(0,1,int(self.app.nbrPoints.get()/2 )) ** self.app.repartition.get()
            #print("arrayRepartition int",arrayRepartition)
            #arrayRepartition = np.flip(arrayRepartition)
            iXnew,iYnew= interpolate.splev(arrayRepartition, mytck)
            #print("intrados après",self.printDistance(iXnew, iYnew))    
            
            xnew = np.concatenate([eXnew, iXnew[1:]])
            ynew = np.concatenate([eYnew, iYnew[1:]])
            #print("xy new=" , xnew , ynew)
        return xnew, ynew

        # change points repartition for extrados and then for intrados
        # merge both
        # add the first and last point if extend is selected

    def printDistance(self,x,y):
        imax = len(x)
        i=0
        result = []
        while i < imax-1:
            d1 = x[i+1]-x[i]
            d2 = y[i+1]-y[i]
            result.append(math.sqrt(d1*d1 +d2*d2))
            i += 1
        return result

    def updatePlotRoot(self):
        self.axesRoot.clear()
        self.axesRoot.axis('equal')
        self.lineRoot, = self.axesRoot.plot(self.app.tRootX , self.app.tRootY , color='red')
        if self.displayPoints.get() == 1:
            self.lineRoot, = self.axesRoot.plot(self.app.tRootX , self.app.tRootY , 'ro')  
        self.canvasRoot.draw()
        
    def updatePlotTip(self): 
        self.axesTip.clear()
        self.axesTip.axis('equal')
        self.axesTip.plot(self.app.tTipX , self.app.tTipY , color='blue')
        if self.displayPoints.get() == 1:
            self.axesTip.plot(self.app.tTipX , self.app.tTipY , 'bo')      
        self.canvasTip.draw()
        
    def plotProfil(self ):
        self.figRoot = Figure(figsize=(10, 2), dpi=100)
        self.axesRoot = self.figRoot.add_subplot(1,1,1)
        self.axesRoot.axis('equal')
        self.axesRoot.set_title('Root')
        self.lineRoot, = self.axesRoot.plot(self.app.tRootX , self.app.tRootY , color='red')
        self.canvasRoot = FigureCanvasTkAgg(self.figRoot, master=self.frame)  # A tk.DrawingArea.
        self.canvasRoot.draw()
        self.canvasRoot.get_tk_widget().grid(column=2, rowspan=5 , row=0, padx=(10,2) , pady=(2,2))
        
        self.figTip = Figure(figsize=(10, 2), dpi=100)
        self.axesTip = self.figTip.add_subplot(1,1,1)
        self.axesTip.axis('equal')
        self.axesTip.set_title('Tip')
        self.lineTip, = self.axesTip.plot(self.app.tTipX , self.app.tTipY , color='blue')
        self.canvasTip = FigureCanvasTkAgg(self.figTip, master=self.frame)  # A tk.DrawingArea.
        self.canvasTip.draw()
        self.canvasTip.get_tk_widget().grid(column=2, rowspan=5 , row=5, padx=(10,2) ,pady=(20,2))

    def merge(self, list1, list2): 
        merged_list = tuple(zip(list1, list2))  
        return merged_list 

    def unmerge(self , liste1):
        result1 = []
        result2 = []
        for t in liste1: 
            result1.append(t[0])
            result2.append(t[1]) 
        return result1 ,  result2 
   
    def distPoint2(self, x1, x2 ,x3 ,y1, y2, y3):
        # calculate distance between point 2 and line 1-3
        # returned value is the power of 2 of the distance (avoid a square root)
        a = (x2-x1)*(x2-x1) + (y2-y1)*(y2-y1)
        b = (x3-x2)*(x3-x2) + (y3-y2)*(y3-y2)
        c = (x3-x1)*(x3-x1) + (y3-y1)*(y3-y1)
        return a - (a*a + b*b + c*c + 2*(a*c - a*b - b*c))/4/c

    def lookNextPoint(self, x, y , idx , errorMax):
        #look from idx up to max, for the next point to keep in order to keep the error less than a value
        # return the last point where the error is lower
        # if it is possible to go up to the end of the polyline, return the index of the last point
        iMax = len(x)
        i = idx + 2
        while i < iMax:
            j = idx + 1
            while j < i:
                h = self.distPoint2(x[idx], x[j], x[i], y[idx], y[j], y[i])
                if h > errorMax:
                    #print("idex max" , j , i)
                    return i-1
                #print("idx, j , i ,h" , idx , j , i , h)
                j += 1    
            i += 1
        #print("fin de iterHauteur")
        return iMax

    def lookNextSynchro(self, s , idx ):
        #look from idx + 1 up to max, for the next synchro point
        # if it is possible to go up to the end of the polyline, return the index of the last point
        iMax = len(s)
        i = idx + 1
        while i < iMax:
            if s[i] > 0:
                return i    
            i += 1
        return iMax
    """
    def simplify(self, errorMax):
        # remove points when a direct connection does not lead to to big error nor on Root nor on Tip
        # Keep always first and last points
        # Return the new Root and Tip in numpy arry
        i = 0
        errorMax2 = errorMax * errorMax #power of 2 because distance between points are calculated in power of 2
        iMax = len(self.app.tRootX)
        #always keep the first point
        rX = [self.app.tRootX[0]]
        rY = [self.app.tRootY[0]]
        tX = [self.app.tTipX[0]]
        tY = [self.app.tTipY[0]]
        while i < iMax:
            nextPointR = self.lookNextPoint(self.app.tRootX ,self.app.tRootY , i, errorMax2)
            nextPointT = self.lookNextPoint(self.app.tTipX ,self.app.tTipY , i, errorMax2)
            if nextPointR < nextPointT:
                i = nextPointR
            else:
                i = nextPointT
            if i < iMax: #add the point if we did not reach the end
                rX.append(self.app.tRootX[i])
                rY.append(self.app.tRootY[i])
                tX.append(self.app.tTipX[i])
                tY.append(self.app.tTipY[i])
        #add the last point in all cases
        rX.append(self.app.tRootX[iMax-1]) 
        rY.append(self.app.tRootY[iMax-1])
        tX.append(self.app.tTipX[iMax-1])
        tY.append(self.app.tTipY[iMax-1])
        return np.array(rX) , np.array(rY) , np.array(tX) , np.array(tY)
    """
    def simplifyOneProfile(self, x , y , s, errorMax):
        # remove points when a direct connection does not lead to to big error nor on Root nor on Tip
        # Keep always first and last points and synchro points
        # Return the new Root and Tip in numpy arry and new s in list
        i = 0
        errorMax2 = errorMax * errorMax #power of 2 because distance between points are calculated in power of 2
        iMax = len(x)
        rX=[]
        rY=[]
        rS=[]
        if iMax > 0:
            #always keep the first point
            rX.append(x[0])
            rY.append(y[0])
            rS.append(s[0])
            while i < iMax:
                nextPoint = self.lookNextPoint(x , y , i, errorMax2)
                nextSynchro = self.lookNextSynchro(s , i) #search next Synchro point
                if nextPoint < nextSynchro:
                    i = nextPoint
                else:
                    i = nextSynchro
                if i < iMax: #add the point if we did not reach the end
                    rX.append(x[i])
                    rY.append(y[i])
                    rS.append(s[i])            
            #add the last point in all cases
            #rX.append(x[iMax-1]) 
            #rY.append(y[iMax-1])
            #rS.append(s[iMax-1])
            return np.array(rX) , np.array(rY) , rS         