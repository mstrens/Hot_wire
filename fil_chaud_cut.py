import math
import tkinter as tk
from tkinter import X, Y, BOTTOM, RIGHT, LEFT, HORIZONTAL , END , DISABLED , ttk , Text
from tkinter import StringVar , Tk , N, NW, W ,E , S , BOTH, HIDDEN, DoubleVar , Spinbox , IntVar , filedialog

import numpy as np

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib
from scipy import interpolate


from fil_chaud_validate import EntryFloat


class Cut:
    def __init__(self,nb ,app):
        self.nb = nb
        self.app = app
        self.frame = ttk.Frame(self.nb)
        self.levelCut = 30
        #self.frame2 = ttk.Frame(self.nb)
        self.nb.add(self.frame, text='   Cut   ')
        self.lastGcodeFileName = ""
        r=0
        self.cutBtn = tk.Button(self.frame, text = 'Cut', width = 25, command = self.cut, state='disabled' )
        self.cutBtn.grid(column=0, row=r , padx=1,pady=(20,1))
        r += 1
        self.cancelBtn = tk.Button(self.frame, text = 'Cancel', command=self.app.tGrbl.resetGrbl, width = 25, state='disabled' )
        self.cancelBtn.grid(column=0, columnspan=2, row=r , pady=(10,1), sticky=W)
        r += 1
        self.button2 = tk.Button(self.frame, text = 'Save Gcode', width = 25, command = self.saveGcode)
        self.button2.grid(column=0, row=r , padx=1,pady=(20,1)) 
        r += 1
        tk.Label(self.frame, text="Usual cutting speed (mm/sec)").grid(column=0, row=r, pady=(20,1), sticky=W)
        EntryFloat(self.frame, self.app.vCut, 0.1, 10, self.levelCut , width='6').grid(column=1, row=r , padx=1,pady=(20,1), sticky=W )
        
        r += 1
        tk.Label(self.frame, text="Errors").grid(column=0, row=r, pady=(20,1), padx=(10,1), sticky=W)
        r += 1
        tk.Label(self.frame, textvariable=self.app.cutMsg,  height= 10).grid(column=0, columnspan=2, row=r, pady=(1,1), padx=(10,1) , sticky=NW)

        self.figRoot = Figure(figsize=(10, 3), dpi=100)
        self.axesRoot = self.figRoot.add_subplot(1,1,1)
        self.axesRoot.autoscale(enable=False)
        self.axesRoot.set_xlim(0, 500)
        self.axesRoot.set_ybound(0, 150)
        self.axesRoot.set_title('Root')
        self.lineRoot1, = self.axesRoot.plot( [], [] ) 
        self.lineRoot2, = self.axesRoot.plot( [], [] )
        self.canvasRoot = FigureCanvasTkAgg(self.figRoot, master=self.frame)  # A tk.DrawingArea.
        self.canvasRoot.draw()
        self.canvasRoot.get_tk_widget().grid(column=2, row=0, rowspan=20, padx=10 , pady=(10,2))
        
        self.figTip = Figure(figsize=(10, 3), dpi=100)
        self.axesTip = self.figTip.add_subplot(1,1,1)
        self.axesTip.autoscale(enable=False)
        self.axesTip.set_xlim(0, 500)
        self.axesTip.set_ybound(0, 150)
        self.axesTip.set_title('Tip')
        self.lineTip1, = self.axesTip.plot( [], [] ) 
        self.lineTip2, = self.axesTip.plot( [], [] )
        self.canvasTip = FigureCanvasTkAgg(self.figTip, master=self.frame)  # A tk.DrawingArea.
        self.canvasTip.draw()
        self.canvasTip.get_tk_widget().grid(column=2, row=20, rowspan=20, padx=10 , pady=(10,2))
        
    def updateOProfil(self):  #update plotting the bloc (2 canvas: Top and Back)
        self.lineRoot1.set_xdata(self.oSimRX)
        self.lineRoot1.set_ydata(self.oSimRY)
        self.lineRoot2.set_xdata(self.app.pRootX)
        self.lineRoot2.set_ydata(self.app.pRootY)
        self.canvasRoot.draw_idle() 

        self.lineTip1.set_xdata(self.oSimTX)
        self.lineTip1.set_ydata(self.oSimTY)
        self.lineTip2.set_xdata(self.app.pTipX)
        self.lineTip2.set_ydata(self.app.pTipY)
        self.canvasTip.draw_idle() 
        

    def cut(self):
        self.app.tGrbl.stream(self.gcode)
        pass

    def saveGcode(self):
        gcodeFileName = filedialog.asksaveasfilename(title="Save as...", defaultextension="*.gcode",\
            filetypes=[("Gcode files","*.gcode"),("All files", "*")], initialfile=self.lastGcodeFileName)
        if len(gcodeFileName) > 0:
            f = open(gcodeFileName ,'w')
            f.write(self.gcode)
            f.close()
            self.lastGcodeFileName = gcodeFileName 

    def calculateRedraw(self):    
        self.calculate()
        self.updateOProfil()

    def calculate(self):
        #it start from PRoot and pTip (= profile taking care of bloc and margin)
        #add enty and exit points in bloc
        #applies offset for radiance
        #simplifies the profiles if possible = simRoot and Tip
        #calculate the projection GX GY DX and DY

        #Vérifier la présence et l'égalité du nombre de points dans les 2 profils
        #to do control number of synchro points
        if (len(self.app.tRootX) > 0) and (len(self.app.tTipX) >0 ): # and (len(self.app.tRootX) == len(self.app.tTipX)):
            # create eRoot and eTip and add entry and exit point in the bloc (before applying heating offset)      
            #print("pRootX pTipX", self.app.pRootX , self.app.pTipX)
            eRootX = self.app.pRootX.tolist()
            eRootY = self.app.pRootY.tolist()
            eRootS = list(self.app.pRootS)
            eTipX =  self.app.pTipX.tolist()
            eTipY =  self.app.pTipY.tolist()
            eTipS = list(self.app.pTipS)
            eRootX.insert(0,self.app.blocToTableTrailingRoot.get())
            eRootY.insert(0, self.app.pRootY[0])
            eTipX.insert(0,self.app.blocToTableTrailingTip.get())
            eTipY.insert(0, self.app.pTipY[0])
            eRootX.append(self.app.blocToTableTrailingRoot.get())
            eRootY.append(self.app.pRootY[-1])
            eTipX.append(self.app.blocToTableTrailingTip.get())
            eTipY.append(self.app.pTipY[-1])
            eRootS.insert(0,10) # add a Synchro and no radiance point
            eTipS.insert(0,10) # add a Synchro and no radiance point
            eRootS[-1] = 10 # mark the last point as Synchro and no radiance point
            eTipS[-1] = 10 # mark the last point as Synchro and no radiance point
            eRootS.append(4) #add a last point as Synchro
            eTipS.append(4) #add a last point as Synchro
            #print("Root=", list(zip(eRootX, eRootY, eRootS)))
            #build 2 listes with length of segments 
            rootL = lengthSegment(eRootX , eRootY)
            tipL = lengthSegment(eTipX , eTipY)

            #build list of index of pt of synchro and length of sections between synchro
            eRootI , eRootL = lengthSection( eRootS , rootL)
            eTipI , eTipL = lengthSection( eTipS , tipL)
            #print("index and length of root", eRootS , rootL ,  eRootI , eRootL)        
            
            #compare les longueurs pour trouver le coté le plus long
            compLength = compareLength( eRootL, eTipL)
            #print("compare length", compLength)
            #Calcule la radiance de chaque côté ; met 0 si 
            rRoot , rTip = self.calculate2Radiance(compLength, self.app.vCut.get())
            #print("radiance root, tip", rRoot , rTip)
            #create eRootR and eTipR with the radiance to fit the same nbr of item as exxxS
            eRootR =  self.createRadiance(eRootS , rRoot)
            #print('full radiance root', eRootR)
            eTipR =  self.createRadiance(eTipS , rTip)
            #print('full radiance tip', eTipR)
            #calcule l'offset de chaque côté; create one new point at each synchronisationil y a des points créé en trop
            self.offsetRootX , self.offsetRootY ,self.offsetRootS = self.calculateOffset(eRootX, eRootY, eRootR ,eRootS)
            #print("offset root", list(zip( self.offsetRootX , self.offsetRootY ,self.offsetRootS)))
            self.offsetTipX , self.offsetTipY , self.offsetTipS = self.calculateOffset(eTipX, eTipY, eTipR, eTipS)
            #print("len R T",len(self.offsetRootX) , len(self.offsetTipX) )
            self.syncRX , self.syncRY , self.syncTX, self.syncTY = self.synchrAllSections(
                self.offsetRootX , self.offsetRootY ,self.offsetRootS , self.offsetTipX , self.offsetTipY , self.offsetTipS)

            """
            print("eRoot X Y", eRootX, eRootY)
            print("eTip X Y", eTipX, eTipY)
            print("offset RX RY", self.offsetRootX , self.offsetRootY)
            print("offset TX TY", self.offsetTipX , self.offsetTipY)
            print("distance offset Rx Ry", self.printDistance(self.offsetRootX , self.offsetRootY))
            print("distance offset Tx Ty",  self.printDistance(self.offsetTipX , self.offsetTipY))
            """
            #élimine les points trop rapprochés (si c'est des 2 côtés)
            #print("Offset ", self.offsetRootX , self.offsetRootY , self.offsetTipX , self.offsetTipY)
            
            self.oSimRX , self.oSimRY, self.oSimTX , self.oSimTY = self.simplifyProfiles(
                self.syncRX , self.syncRY , self.syncTX, self.syncTY )

            #print("len before after",  len(self.syncRX), len(self.oSimRX))    
            
            #Calculate projections on cnc axis and speed
            if self.app.leftRightWing.get() == 'Right': #for right wing, the root is on the left side
                self.GX , self.DX , self.GY, self.DY, self.warningMsg , self.speed = self.projectionAll(
                    self.oSimRX , self.oSimTX , self.oSimRY, self.oSimTY, 
                    self.app.blocToTableLeft.get() + self.app.tableYG.get() , 
                    self.app.blocLX.get() ,
                    self.app.tableYY.get() -self.app.blocToTableLeft.get() - self.app.tableYG.get() - self.app.blocLX.get() )
            else: #Left wing = root is on rigth side
                self.GX , self.DX , self.GY, self.DY, self.warningMsg, self.speed = self.projectionAll(
                    self.oSimTX, self.oSimRX , self.oSimTY ,self.oSimRY,  
                    self.app.blocToTableLeft.get() + self.app.tableYG.get() , 
                    self.app.blocLX.get() ,
                    self.app.tableYY.get() -self.app.blocToTableLeft.get() - self.app.tableYG.get() - self.app.blocLX.get() )
                    
            #print(self.warningMsg)
            self.app.cutMsg.set(self.warningMsg) 
            #print("Projection ", self.GX , self.DX , self.GY, self.DY)
            #print("Projection ", self.GX , self.DX )
            #genère le Gcode
            # set G54 à la valeur actuelle, set absolu et mm, set feed rate, met en chauffe, attend 5 sec 
            # monte à la hauteur du ppremier point puis avance au premier point
            # passe tous les points
            # revient à la verticale de l'origine puis à l'origine
            # attend 5 sec puis éteint la chauffe puis éteint les moteurs
            
            self.gcode = self.generateGcode(self.GX , self.DX , self.GY, self.DY, self.speed)

            
            

    def createRadiance(self, s , r):
        # create a radiance list with the same nbr of items as s and using the radiance in r
        imax = len(s)
        i=0
        rIdx = 0
        rTemp = 0
        result = []
        while i < (imax-1):
            if s[i] > 0:
                if s[i] > 4:
                    rTemp= 0    
                else:
                    rTemp= r[rIdx]
                rIdx += 1
            result.append(rTemp)
            i += 1
        return result

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


    def generateGcode(self, GX , DX , GY, DY, axisSpeed):
        #gCodeStart ="G10 L20 P1 X0 Y0 Z0 A0 \n G90 G21 M3 \n G04 P5.0\n G01 X0 \n"
        #gCodeEnd = "G04 P5.0\n M5\n M2\n"
        heat = self.app.tGuillotine.calculateHeating(self.app.vCut.get())
        formatAxis = "{:.3f} "
        #A="X{:.3f} Y{:.3f} Z{:.3f} A{:.3f}\n"
        L = self.app.gCodeLetters.get() + "XYZA"   # contains 4 letters
        G00 = "G00 "+L[0] + formatAxis + L[1] + formatAxis + L[2] + formatAxis + L[3] + formatAxis + "\n"
        G01 = "G01 "+L[0] + formatAxis + L[1] + formatAxis + L[2] + formatAxis + L[3] + formatAxis + "F{:d}\n" 
        xyza = L[0] + formatAxis + L[1] + formatAxis + L[2] + formatAxis + L[3] + formatAxis + "\n"
        st = self.app.gCodeStart1.get() + "\n" + self.app.gCodeStart2.get() + "\n" + self.app.gCodeStart3.get() + "\n" + self.app.gCodeStart4.get() + "\n"
        st = st + "G10 L20 P1"+ xyza.format(0,0,0,0) #set wcs to current position: G10 L20 P1 X0 Y0 Z0 A0
        st = st + "G54\n" # apply wcs1
        st = st + "S{:d}\n".format( int(heat)) # set the heating value based on speed
        st = st + "G90 G21 M3\n" # apply  Absolute and mm and heating
        st = st + "G04 P{:.1f}\n".format(self.app.tPreHeat.get()) # pause for the preheat delay
        en = "G04 P{:.1f}\n".format(self.app.tPostHeat.get()) # pause for the post delay
        en = en + "M5\nM2\n" # stop heating and stop motor
        en = en + self.app.gCodeEnd1.get() + "\n" + self.app.gCodeEnd2.get() + "\n" + self.app.gCodeEnd3.get() + "\n" + self.app.gCodeEnd4.get() + "\n"           
        li=[]
        imax = len(GX)
        if imax > 1:
            i = 1
            li.append(st) #append start
            li.append(G00.format(0.0, GY[0] , 0.0 , DY[0]), ) #move up
            li.append(G00.format(GX[0], GY[0] , DX[0] , DY[0]), ) #move up to entry of bloc
            while i < imax:
                li.append(G01.format(GX[i], GY[i] , DX[i] , DY[i] , int(axisSpeed[i-1] * 60 ) ) ) #speed is converted to mm/min
                i += 1
            li.append(G00.format(0, GY[-1] , 0 , DY[-1]))
            li.append(G00.format(0.0, 0.0 , 0.0 , 0.0))
            li.append(en) #append End
        #print("".join(li)) #print the Gcode
        return "".join(li)  # return a string containing the /n

    def projectionAll(self, x1 , x2 , y1 , y2, lg, l, ld):
        # lg = outside length on the left side (from bloc to axis) 
        # l = legnth between the 2 sides of bloc 
        # ld = outside length on the right side (from bloc to axis)
        # x1 y1 = profil on the left side
        # x2 y2 = profil on the rigth side
        # return projection, warning msg and speed
        xg = []
        xd = []
        yg = []
        yd = []
        speed = []
        xgmin = x1[0]
        xgmax = x1[0]
        xdmin = x2[0]
        xdmax = x2[0]
        ygmin = y1[0]
        ygmax = y1[0]
        ydmin = y2[0]
        ydmax = y2[0]
        vxGMax = 0
        vyGMax = 0
        vxDMax = 0
        vyDMax = 0
        msg = ""
        i = 0
        imax = len(x1)
        if imax > 0:
            while i < imax:
                xg.append( ( (x1[i]-x2[i]) / l * lg ) + x1[i] )
                xd.append( ( (x2[i]-x1[i]) / l * (l+ld) ) + x1[i] )
                yg.append( ( (y1[i]-y2[i]) / l * lg ) + y1[i] )
                yd.append( ( (y2[i]-y1[i]) / l * (l+ld) ) + y1[i] )          
                if xg[i] < xgmin: xgmin = xg[i]
                if xg[i] > xgmax: xgmax = xg[i]
                if xd[i] < xdmin: xdmin = xd[i]
                if xd[i] > xdmax: xdmax = xd[i]
                if yg[i] < ygmin: ygmin = yg[i]
                if yg[i] > ygmax: ygmax = yg[i]
                if yd[i] < ydmin: ydmin = yd[i]
                if yd[i] > ydmax: ydmax = yd[i]
                if i > 0: #calculate speed on Y axis
                    #calculate legnth of segment
                    dx1 = x1[i-1] - x1[i]
                    dy1 = y1[i-1] - y1[i]
                    dx2 = x2[i-1] - x2[i]
                    dy2 = y2[i-1] - y2[i]
                    dxG = abs( xg[i-1] - xg[i] )
                    dyG = abs( yg[i-1] - yg[i] )
                    dxD = abs( xd[i-1] - xd[i] )
                    dyD = abs( yd[i-1] - yd[i] )
                    d1 = dx1 *dx1 + dy1 * dy1
                    d2 = dx2 *dx2 + dy2 * dy2
                    dG = dxG *dxG + dyG * dyG
                    dD = dxD *dxD + dyD * dyD
                    #select the longest side
                    if d1 >= d2:
                        d1 = math.sqrt(d1)
                        dG = math.sqrt(dG)
                        d2 = math.sqrt(d2)
                        dD = math.sqrt(dD)
                        v1 = self.app.vCut.get()
                        speed.append( v1 * dG / d1)
                        vGD = v1 * dG / d1
                        vxG = v1 * dxG / d1
                        vyG = v1 * dyG / d1
                        vxD = v1 * dxD / d1
                        vyD = v1 * dyD / d1
                    else:     
                        d1 = math.sqrt(d1)
                        dG = math.sqrt(dG)
                        d2 = math.sqrt(d2)
                        dD = math.sqrt(dD)
                        v2 = self.app.vCut.get()
                        speed.append( v2 * dD / d2)
                        vGD = v2 * dD / d2
                        vxG = v2 * dxG / d2
                        vyG = v2 * dyG / d2
                        vxD = v2 * dxD / d2
                        vyD = v2 * dyD / d2
                    #print(" point {} dG={:.3f} d1={:.3f} dD={:.3f} d2={:.3f}  vGD={:.3f} vxG={:.3f}  vyG={:.3f} , vxD={:.3f} , vyD={:.3f} "\
                    #    .format(i , dG , d1, dD , d2, vGD, vxG , vyG , vxD , vyD))
                    if vxG > vxGMax: vxGMax = vxG
                    if vyG > vyGMax: vyGMax = vyG
                    if vxD > vxDMax: vxDMax = vxD
                    if vyD > vyDMax: vyDMax = vyD 
                i += 1
            if xgmin < 0:
                msg = msg + "Left hor. axis exceeds origin\n"
            if xgmax > self.app.cMaxY.get():
                msg = msg + "Left hor. axis exceeds limit\n"
            if xdmin < 0:
                msg = msg + "Right hor. axis exceeds origin\n"
            if xdmax > self.app.cMaxY.get():
                msg = msg + "Right vertical axis exceeds limit\n"
            if ygmin < 0:
                msg = msg + "Left vertical axis exceeds origin\n"
            if ygmax > self.app.cMaxZ.get():
                msg = msg + "Left vertical axis exceeds limit\n"
            if ydmin < 0:
                msg = msg + "Right vertical axis exceeds origin\n"
            if ydmax > self.app.cMaxZ.get():
                msg = msg + "Right vertical axis exceeds limit\n"
            if vxGMax > self.app.vMaxY.get(): 
                msg = msg + "Left hor. axis exceeds speed {:.3f}\n".format(vxGMax)
            if vyGMax > self.app.vMaxZ.get():
                msg = msg + "Left vertical axis exceeds speed\n"
            if vxDMax > self.app.vMaxY.get():
                msg = msg + "Right hor. axis exceeds speed\n"
            if vyDMax > self.app.vMaxZ.get():
                msg = msg + "Right vertical axis exceeds speed\n"
        return xg ,xd ,yg , yd , msg , speed
        
    def simplifyProfiles( self , rX , rY , tX , tY ):
        imax = len(rX)
        oRX=[]
        oRY=[]
        oTX=[]
        oTY=[]
        i = 0
        if imax > 0:
            rXp = rX[i]
            rYp = rY[i]
            tXp = tX[i]
            tYp = tY[i]
            oRX.append(rXp)
            oRY.append(rYp)
            oTX.append(tXp)
            oTY.append(tYp)
            i = 1
            while i < imax:
                dRX = rX[i] - rXp
                dRX *= dRX
                dRY = rY[i] - rYp
                dRY *= dRY
                dTX = tX[i] - tXp
                dTX *= dTX
                dTY = tY[i] - tYp
                dTY *= dTY
                if dRX > 0.01 or dRY > 0.01 or dTX > 0.01 or dTY > 0.01:
                    rXp = rX[i]
                    rYp = rY[i]
                    tXp = tX[i]
                    tYp = tY[i]
                    oRX.append(rXp)
                    oRY.append(rYp)
                    oTX.append(tXp)
                    oTY.append(tYp)
                i += 1
        return oRX, oRY, oTX, oTY
                

    def calculateOffset( self , x, y , r, s ):
        #create an offset for curve x y at a distance r (which varies)
        # for each synchronisation point, create 2 offset points instead of 1 
        #x ,y, r (radiance) , s (synchro) have the same length
        # return new x y s 
        # pour 3 points successifs p1-p2-p3 avec r1-r2, calcule les pt d'intersection des 2 offsets
        ox=[]
        oy=[]
        os=[]
        imax = len(r)
        i = 0
        if imax >= 1:
            #met le premier point            
            oxi , oxj, oyi, oyj = offset1Segment(x[0], x[1] , y[0], y[1] , r[0])
            ox.append(oxi)
            oy.append(oyi)
            os.append(s[0])
            while i < (imax-1):
                oxi, oyi = offset2Segment(x[i] , x[i+1] ,x[i+2], y[i] ,y[i+1] ,y[i+2] ,r[i] )
                ox.append(oxi)
                oy.append(oyi)
                os.append(s[i+1])
                if s[i+1] > 0:
                    oxi, oyi = offset2Segment(x[i] , x[i+1] ,x[i+2], y[i] ,y[i+1] ,y[i+2] ,r[i+1] )
                    ox.append(oxi)
                    oy.append(oyi)
                    os.append(s[i+1])
                i += 1
            oxi , oxj, oyi, oyj = offset1Segment(x[i], x[i+1] , y[i], y[i+1] , r[i])
            ox.append(oxj)
            oy.append(oyj)
            os.append(s[-1])        
        return ox ,oy, os    

    def calculate2Radiance( self,  compLength , speedMax):    
        oMin = self.radiance(speedMax)
        imax = len(compLength)
        rR = [] #radiance at root
        rT = [] #radiance at tip
        i=0
        if imax > 0:
            while i < imax:
                cLi = compLength[i]
                speedLow = speedMax * cLi
                if cLi >= 0: # root is longer
                    rR.append(oMin)
                    rT.append(self.radiance(speedLow))
                else:
                    rT.append(oMin)
                    rR.append(self.radiance(-speedLow))
                i += 1        
        return rR , rT
    
    def radiance(self , speed):
        a = (self.app.mRadSpHalf.get() - self.app.mRadSpHigh.get()) / (self.app.mSpeedHalf.get() - self.app.mSpeedHigh.get())
        return 0.5 * ( ( a * ( speed - self.app.mSpeedHalf.get())) + self.app.mRadSpHalf.get() ) # use only 1/2 of radiance for the offset

    """ synchronise 2 profiles
    extrait le premier tronçon R et T
    pour chaque tronçon
        calcule la longueur R et T
        calcule la longueur cumulée R et T
        Ramène les longueurs cumulées dans un range 0 <> 1 pour R et T
        Crée une liste qui mélange les 2 (concatene, trie, élimine les doublons)
        Fait un interpolate de R et de T suivant cette liste
        Simplifie en enlevant les points trop rapprochés des 2 cotés
    """
    def synchrAllSections(self, rX, rY, rS, tX, tY , tS):
        #synchronise 2 profiles in order to get the same number of points
        #it has to respect synchronisation points
        sectionsIdxR = self.sectionsIdx (rS)
        sectionsIdxT = self.sectionsIdx (tS)
        #print("sectionIdxR", sectionsIdxR)
        #print("sectionIdxT", sectionsIdxT)
        imax = len(sectionsIdxR)
        i=0
        syncRX=[]
        syncRY=[]
        syncTX=[]
        syncTY=[]
        
        if imax > 0:
            while i < imax:
                firstR = sectionsIdxR[i][0]
                lastR =  sectionsIdxR[i][1] + 1
                firstT = sectionsIdxT[i][0]
                lastT =  sectionsIdxT[i][1] + 1
                #print( "first fast", firstR, lastR , firstT, lastT)
                #print("rX" ,  rX[firstR:lastR] )
                sRX, sRY, sTX, sTY = self.synchroOneSection( rX[firstR:lastR], rY[firstR:lastR], tX[firstT:lastT], tY[firstT:lastT])     
                syncRX = syncRX + sRX.tolist()
                syncRY = syncRY + sRY.tolist()
                syncTX = syncTX + sTX.tolist()
                syncTY = syncTY + sTY.tolist()
                i += 1
        return syncRX , syncRY , syncTX, syncTY

    def sectionsIdx(self , s):
        # return a list of turple with begin and end Idx of each section
        i=0
        imax = len(s)
        result = []
        if imax > 1:
            while i < (imax-1):
                j = i+1
                while s[j] == 0:
                    j += 1
                result.append( (i , j))
                i = j+1         
        return result
    
    def synchroOneSection(self, rX, rY, tX, tY):
        """pour chaque tronçon
        calcule la longueur cumulée R et T
        Ramène les longueurs cumulées dans un range 0 <> 1 pour R et T
        Crée une liste qui mélange les 2 (concatene, trie, élimine les doublons)
        Fait un interpolate de R et de T suivant cette liste
        Simplifie en enlevant les points trop rapprochés des 2 cotés
        """
        #print("synchro one section", rX , rY ,tX , tY)
        cumulLengthR = np.array(self.cumulLength(rX , rY))
        cumulLengthT = np.array(self.cumulLength(tX , tY))
        totLengthR = cumulLengthR[-1]
        totLengthT = cumulLengthT[-1] 
        normLengthR = cumulLengthR / totLengthR
        normLengthT = cumulLengthT / totLengthT
        mergedLength = np.concatenate([normLengthR , normLengthT]) # concatenate
        mergedLength = np.unique(mergedLength)
        mergedLength = np.insert(mergedLength , 0 , 0)
        #print("merged mergedLength=", mergedLength)

        mytck,myu=interpolate.splprep([rX,rY], k=1, s=0)
        rXnew,rYnew= interpolate.splev(mergedLength, mytck)
        mytck,myu=interpolate.splprep([tX,tY], k=1, s=0)
        tXnew,tYnew= interpolate.splev(mergedLength, mytck)
        #print("one section result" , rXnew , rYnew , tXnew , tYnew)
        return rXnew , rYnew , tXnew , tYnew
    
    def cumulLength(self, x, y):
        imax = len(x)
        i=0
        cL=[]
        cumLength = 0
        if imax > 1:
            while i < (imax-1):
                dx = x[i+1] - x[i]
                dy = y[i+1] - y[i]
                cumLength += math.sqrt(dx*dx + dy*dy) #calculate cumulative length
                cL.append(cumLength)
                i += 1
        return cL
    
"""
partir de 4 listes de coordonnées (profil): XG YG XD YD de n éléments
#en faire 4 array
construire 2 listes des longueurs des segments LG et LD

construire 2 listes des Offset OG et OD
    - determiner l'Offset min = oMin (celui pour la vitesse de coupe élevée)
    - remplir une liste avec le ratio entre la longueur root et tip de chaque segment (negatif si tip est > root)
    - chercher la distance la plus grande entre LG et LD
    - attribuer d'un coté oMin
    - pour l'autre calculer la vitesse
    - calculer l'offset correspondant à cette vitesse 
contruire une liste d'offset à gauche et puis une a droite en insérant un point en plus à chaque point
chercher à simplifier (retirer les points s'ils sont égaux au précédent des 2 côtés) 

pour faire une ligne d'offset, passer en revue 3 points successifs p1,p2,P3 et 2 offsets O1,O2
    - calculer l'offset pour p1,P2,P3 et O1; soit P2a le point d'intersection
        - calculer les 2 points avec offset (pour p1,p2 et puis pour p2,p3)
        - calculer l'intersection des 2 lignes
    - si O2 est différent de O1, calculer l'offset pour P1,P2,P3 et O2 ; soit P2b le point d'intersection
    - ajouter à la liste P2a et P2B (si O2=O1, P2a et P2b sont égaux) 
"""
def offset2Segment(x1, x2, x3, y1, y2, y3, o):
    #- calcule 2 fois l'offset de 1 segment
    #- calcule le point d'intersection
    #- retourne le point d'intersection
    
    X1 , X2 , Y1 ,Y2 = offset1Segment(x1 ,x2 ,y1 ,y2, o)
    X3 , X4 , Y3 ,Y4 = offset1Segment(x2 ,x3 ,y2 ,y3, o )
    interX , interY = intersec(X1, X2, X3, X4, Y1, Y2, Y3, Y4) 
    return interX , interY

def offset1Segment(px1, px2 , py1, py2 ,o):
#calcule les coordonnées des points avec un offset o
    X1 = px1
    X2 = px2
    Y1 = py1
    Y2 = py2
    DX = X2 - X1
    DY = Y2 - Y1
    L12 = math.sqrt(DX * DX + DY * DY)
    r = o / L12
    dx = r * DY
    dy = r * DX
    #print("offset 1 segment" , X1, X2, Y1, Y2, o , X1-dx , X2-dx , Y1+dy , Y2+dy)
    return X1-dx , X2-dx , Y1+dy , Y2+dy 

def intersec(x1 , x2 ,x3, x4 , y1 ,y2 ,y3, y4):
    u = np.cross(np.array([x1 , y1, 1]), np.array([x2 , y2, 1]))
    v = np.cross(np.array([x3 , y3, 1]), np.array([x4 , y4, 1]))
    r = np.cross(u,v)
    #print("intersec de ", x1 , x2 ,x3, x4 , y1 ,y2 ,y3, y4, "=" ,r)
    if r[2] > 1e-10 or r[2] < -1e-10: #when different from 0, then the 2 segments are not // and there is an intersection 
        return  (r[0]/r[2]) , (r[1]/r[2]) 
    return (x2+x3)/2 , (y2+y3)/2   #si // retourne le point milieu

def lengthSegment(X , Y):
    l=[]
    i = 1
    imax = len(X)
    if imax > 1:
        x = X[0]
        y = Y[0]
        while i < imax:
            xn , yn = X[i] , Y[i]
            l.append(math.sqrt( ((xn-x) * (xn-x)) + ((yn-y) * (yn-y)) ) )
            x , y = xn ,yn
            i += 1
    return l

def lengthSection( s , l):
    #create a list with index of synchro point and with the length of section
    # s = list of synchro code and l = length of segments to cumulate
    # NB:  a section is all points between synchro
    #print("len s et l", len(s) , len(l))
    #print("s et l=", s , l)
    ls=[]
    idxSynchro=[]
    i=0
    iMax = len(s)
    if iMax > 1:
        while i < (iMax-1):
            idxSynchro.append(i)
            ls.append(l[i])
            i += 1
            while s[i] == 0:
                ls[-1] += l[i]
                i += 1
        idxSynchro.append(i)
    return idxSynchro , ls #return list of index and list of length    

def compareLength( r , t): #return empty list if legnth of 2 input list are not the same
    # return the ratio between the shortest and the longest
    # value is > 0 when root is greater or equal than tip; negative if the opposite 
    c=[]
    i=0
    rmax = len(r)
    tmax = len(t)
    if rmax > 0 and rmax == tmax:
        while i < rmax:
            ri = r[i]
            ti = t[i]
            if (ri + ti ) == 0:
                c.append( 1 )
            elif ri >= ti:
                c.append( ti / ri )
            else:
                c.append( -ri / ti )
            i += 1    
    return c            

