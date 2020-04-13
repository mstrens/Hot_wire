import tkinter as tk
from tkinter import X, Y, BOTTOM, RIGHT, LEFT, HORIZONTAL , END , DISABLED , ttk
from tkinter import StringVar , Tk , W ,E , S , BOTH, HIDDEN, DoubleVar , Spinbox , IntVar , filedialog

import re

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib

import numpy as np

class Profil:
    def __init__(self,nb, app):        
        self.nb = nb
        self.app = app
        self.frame = ttk.Frame(self.nb)
        #self.frame2 = ttk.Frame(self.nb)
        self.nb.add(self.frame, text='   Profil   ')
        r = 0
        tk.Button(self.frame, text = 'Upload old project', command=self.app.uploadConfig, width = 25).grid(column=0, row=r, pady=10)
        r += 1
        tk.Button(self.frame, text = 'Save current project', command=self.app.saveConfig, width = 25).grid(column=0, row=r, pady=10)
        r += 1
        tk.Button(self.frame, text = 'Upload from "Complexes" ', command=self.uploadComplexes, width = 25).grid(column=0, row=r, pady=20)
        #r += 1
        #tk.Label(self.frame, text="Root profil").grid(column=0, row=r, pady=(20,2))
        r += 1
        self.button1 = tk.Button(self.frame, text = 'Select root profil', command=self.uploadRoot, width = 25)
        self.button1.grid(column=0, row=r, pady=10)
        #r += 1
        #tk.Label(self.frame, text="Incidence").grid(column=0, row=r, pady=(1,1))
        #tk.Entry(self.frame, textvariable=self.app.incidenceRoot , width='5').grid(column=1, row=r , padx=1,pady=(1,1))
        
        #r += 1
        #tk.Label(self.frame, text="Tip profil").grid(column=0, row=r, pady=(20,2))
        r += 1
        self.button2 = tk.Button(self.frame, text = 'Select tip profil', command=self.uploadTip, width = 25)
        self.button2.grid(column=0, row=r, pady=10)
        #r += 1
        #tk.Label(self.frame, text="Incidence").grid(column=0, row=r, pady=(1,1))
        #tk.Entry(self.frame, textvariable=self.app.incidenceTip , width='5').grid(column=1, row=r , padx=1,pady=(1,1))
        tk.Label(self.frame, textvariable=self.app.nameRoot).grid(column=2, row=4, pady=(1,10))
        tk.Label(self.frame, textvariable=self.app.nameTip).grid(column=2, row=8, pady=(1,2))
        
        self.plotProfil()

    def plotProfil(self ):
        self.figRoot = Figure(figsize=(10, 2), dpi=100)
        self.axesRoot = self.figRoot.add_subplot(1,1,1)
        self.axesRoot.axis('equal')
        self.axesRoot.set_title('Root')
        self.lineRoot, = self.axesRoot.plot(self.app.oRootX , self.app.oRootY , color='red')
        self.canvasRoot = FigureCanvasTkAgg(self.figRoot, master=self.frame)  # A tk.DrawingArea.
        self.canvasRoot.draw()
        self.canvasRoot.get_tk_widget().grid(column=2, rowspan=3 , row=1, pady=(20,2), padx=(20,2))
        
        self.figTip = Figure(figsize=(10, 2), dpi=100)
        self.axesTip = self.figTip.add_subplot(1,1,1)
        self.axesTip.axis('equal')
        self.axesTip.set_title('Tip')
        self.lineTip, = self.axesTip.plot(self.app.oTipX , self.app.oTipY , color='blue')
        self.canvasTip = FigureCanvasTkAgg(self.figTip, master=self.frame)  # A tk.DrawingArea.
        self.canvasTip.draw()
        self.canvasTip.get_tk_widget().grid(column=2, rowspan=3 , row=5, pady=(20,2), padx=(20,2))

    def uploadRoot(self):
        self.app.oRootX , self.app.oRootY , nameRoot = self.uploadProfil("Select root profile")
        self.app.nameRoot.set(nameRoot)
        self.app.oRootS = []
        if len(self.app.oTipX) == 0: # copy root to tip when tip is empty
            self.app.oTipX = self.app.oRootX.copy()  
            self.app.oTipY = self.app.oRootY.copy()
            self.app.oTipS = []
            self.app.nameTip.set(nameRoot)
        self.app.validateAll(0)
        
    def uploadTip(self):
        # upload
        self.app.oTipX , self.app.oTipY , nameTip= self.uploadProfil("Select tip profile")   
        self.app.nameTip.set(nameTip)
        self.app.validateAll(0)
        
    def updatePlotRoot(self):
        #self.app.validateAll(0)
        self.axesRoot.clear()
        #self.axesRoot = self.figRoot.add_subplot(1,1,1)
        self.axesRoot.axis('equal')
        self.axesRoot.set_title("Root")
        self.lineRoot, = self.axesRoot.plot(self.app.oRootX , self.app.oRootY , color='red')
        self.canvasRoot.draw()
        #self.canvasRoot.flush_events()
    
    def updatePlotTip(self): 
        #self.app.validateAll(0)
        self.axesTip.clear()
        #self.axesTip = self.figTip.add_subplot(1,1,1)
        self.axesTip.axis('equal')
        self.axesTip.set_title('Tip')
        self.lineTip, = self.axesTip.plot(self.app.oTipX , self.app.oTipY , color='blue')
        self.canvasTip.draw()
        #self.canvasRoot.flush_events()       

    def uploadProfil(self ,typeName):
        rootFileName = filedialog.askopenfilename(\
                           filetypes =(("dat", "*.dat"),("All files","*.*")),
                           title = typeName
                           )
        errors = []
        name = ""
        profilDatX = []
        profilDatY = []
        linenum = 0
        lineDatNum = 0
        pattern = re.compile(r"(\s*[+-]?([0-9]*[.])?[0-9]+)\s+([+-]?([0-9]*[.])?[0-9]+)")
        #pattern = re.compile(r"(\s*[0-9]+\.?[0-9]*)|([0-9]*\.[0-9]+)")
        if len(rootFileName) > 0 :
            with open (rootFileName, 'rt') as myfile:
                for line in myfile:
                    linenum += 1
                    #print(line)
                    pSearch = pattern.search(line)           
                    if pSearch == None:  # If pattern search  does not find a match,   
                        errors.append(line.rstrip('\n'))
                    else:                            # If pattern search  does not find a match,
                        profilDatX.append(float(pSearch.group(1)))
                        profilDatY.append(float(pSearch.group(3)))
                        lineDatNum += 1
            if len(errors) > 0:
                name = errors[0]
            else:
                name = rootFileName   
            #for err i:
            # n errors:
            #    print("Line without coordinates ", str(err[0]), ": " + err[1])
            
        return profilDatX , profilDatY , name 

    def uploadComplexes(self):
        FileName = filedialog.askopenfilename(\
                        filetypes =(("cpx", "*.cpx"),("All files","*.*")),
                        title = "Select a file generated by Complexes (from RP-FC)"
                        )
        state = None
        if len(FileName) > 0 :
            with open (FileName, 'rt') as myfile:
                self.app.oRootX = []
                self.app.oRootY = []
                self.app.oRootS = []
                self.app.oTipX = []
                self.app.oTipY = []
                self.app.oTipS = []
                nbrSynchroRoot = 0
                nbrSynchroTip = 0
                for line in myfile:
                    if line == "[Emplanture]\n":
                        state = "Emplanture"
                    elif line == "[Saumon]\n":
                        state = "Saumon"
                    elif '=' in line:
                        l1 = line.split('=') 
                        if l1[0].isdigit():
                            l2 = l1[1].split(":")
                            if state == "Emplanture":
                                self.app.oRootX.append(float(l2[0]) )
                                self.app.oRootY.append(float(l2[1]) )
                                self.app.oRootS.append( int(l2[2]) & 4 ) # check only bit 2 for synchronisation
                                if (self.app.oRootS[-1] == 4):
                                    nbrSynchroRoot +=1 #count the number of synschro     
                            elif state == "Saumon":
                                self.app.oTipX.append(float(l2[0]) )
                                self.app.oTipY.append(float(l2[1]) )
                                self.app.oTipS.append(int(l2[2])  & 4)
                                if (self.app.oTipS[-1] == 4 ) :
                                    nbrSynchrotip +=1 #count the number of synschro
                        elif l1[0] == "Ecartement":
                            self.app.blocLX.set(value= float(l1[1]))   
            print ("synchro = " , nbrSynchroRoot , " " , nbrSynchroTip)    
            if nbrSynchroRoot == 0 or nbrSynchroRoot != nbrSynchroTip: # discard synchro if not equal
                self.app.oRootS = []
                self.app.oTipS = []
            self.app.validateAll(0)
            

    