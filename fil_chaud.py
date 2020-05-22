import tkinter as tk
from tkinter import X, Y, BOTTOM, RIGHT, LEFT, HORIZONTAL , END , DISABLED , ttk
from tkinter import StringVar , Tk , W ,E , S , BOTH, HIDDEN, DoubleVar , Spinbox , IntVar , filedialog


import numpy as np

import configparser
import serial.tools.list_ports
import time
import threading
import atexit
import queue

import fil_chaud_config
from fil_chaud_profil import Profil
from fil_chaud_transform import Transform 
from fil_chaud_bloc import Bloc
from fil_chaud_margin import Margin
from fil_chaud_material import Material
from fil_chaud_guillotine import Guillotine
from fil_chaud_cut import Cut
from fil_chaud_table import Table
from fil_chaud_grbl import Grbl

""" to do
- afficher les trailing et leading position du bloc jusqu'à l'axe YG et YD
- afficher les parcours des axes
"""
"""
oRoot and oTip = original profil (displayed on tab profil)
tRoot and tTip = transformed profil (taking into account coord and transformation but not position)
pRoot and pTip = positioned profil (taking into account coord, transformation AND position)
offsetRoot and offsetTip = offset for radiance on pRoot and pTip (but with duplicates)
oSimR and oSimT = simplified offsetRoot and offsetTip
GX, GY, DX and DY = projection on the axes (only traject inside the bloc)

"""

class App:
    def __init__(self, master):
        self.initDone = False
        self.initGuiData()
        self.master = master
        self.master.title("Hot wire cutter (version 0.1.c)")
        self.nb = ttk.Notebook(self.master)
        self.nb.enable_traversal()    
        self.queueTkSendMsg = queue.Queue()
        self._thread_cmd = threading.Thread(target=self.execCmd, args=(self.queueTkSendMsg, "rien"))  
        self._thread_cmd.setDaemon(True) #added by mstrens in order to kill automatically the thread when program close
        self._thread_cmd.start()

        self.queueTkGetMsg = queue.Queue()
        self.tGrbl = Grbl(self.nb, self, self.queueTkGetMsg) #create an instance of Gerbil in order to communicate with GRBL
                                                       # queue is used to get message back from interface    
        
        self.tProfil = Profil(self.nb, self) #add a tab for selecting the profile
        self.tTransform = Transform(self.nb, self) #add a tab to modify the profile
        self.tBloc = Bloc(self.nb , self ) #add a tab to design the wing and the bloc
        self.tMargin = Margin(self.nb , self ) #add a tab to design the vertical margin 
        self.tMaterial = Material(self.nb, self) #add a tab to specify the material
        self.tGuillotine = Guillotine(self.nb, self, self.queueTkSendMsg ) #add a tab to make guillotine
        self.tCut = Cut(self.nb ,self) #add a tab to cut
        self.tTable = Table(self.nb , self) #add a tab to define the Table (size)
        self.nb.pack()
        atexit.register(self.tGrbl.disconnectToGrbl)
        self.initDone = True
        self.running = True
        
        self.periodicCall()
        self.validateAllOn = True
        self.validateAll(0) #validate all

        #self.tBloc.toTableRight.set(self.tTable.dY.get() - self.tTable.lG.get() - self.tTable.lD.get() - self.tBloc.toTableLeft.get() - self.tBloc.lX.get() ) 
        #print (self.tBloc.toTableRight.get())
    
    def execCmd(self , queue , rien):
        """
        thread in order to execute task outside the main tkhtread (when they can take to much time e.g.)
        get Cmd via a queue queueTkSendMsg
        used e.g. when a button is clicked in Thinker
        not sure it is really requested for this application
        """
        while True:
            msg = queue.get()
            if msg == "Connect":
                self.tGrbl.connectToGrbl()
                self.tGuillotine.updateBtnState()
            elif msg == "Disconnect":    
                self.tGrbl.disconnectToGrbl()
                self.tGuillotine.updateBtnState()

    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queueTkGetMsg.qsize(  ):
            try:
                msg = self.queueTkGetMsg.get(0) + "\n"
                # Check contents of message and do whatever is needed. As a
                # simple test, print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
                #print("getting a message in queue",msg)
                self.tGuillotine.msgBox.insert(END, msg)
            except queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass
    
    def periodicCall(self):
        """
        Check every 200 ms if there is something new in the queue.
        execute it when tkinter is sleeping
        """
        self.processIncoming()
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            #import sys
            #sys.exit(1)
            pass
        self.master.after(200, self.periodicCall)

    def initGuiData(self):
        #not saved with config
        self.validateAllOn = False
        self.warningMsg = StringVar(value="")
        self.cutMsg = StringVar(value="")
        self.configUploadFileName = None
        self.tableUploadFileName = None
        self.tableSaveFileName = None
        self.materialUploadFileName = None
        self.materialSaveFileName = None
        self.connected = StringVar(value="OFF")
        self.grblStatus= StringVar(value="Not connected")
        self.grblXG = DoubleVar(value="0") #grbl horizontal left pos
        self.grblYG = DoubleVar(value="0") #grbl vertical left pos
        self.grblXD = DoubleVar(value="0") #grbl horizontal right pos
        self.grblYD = DoubleVar(value="0") #grbl vertical right pos
        self.grblF = DoubleVar(value="0") #grbl feed rate
        self.grblS = DoubleVar(value="0") #grbl heating 
        self.gMoveAxis = StringVar(value="Both") # grbl axis to move (left,right)
        self.gMoveDist = DoubleVar(value="10") #grbl mistance to move
        # Transformed profil based on original (filled by validateTransform) ; is an numpy array and not a usual List
        #take care of Chord, but not of position of block and margins...
        self.tRootX = np.array([])                   
        self.tRootY = np.array([])
        self.tRootS = []
        self.tTipX = np.array([])                   
        self.tTipY = np.array([])
        self.tTipS = []
        # Position profil (in a numpy array) based on "t" profile and position of block and margins...
        self.pRootX = np.array([])                   
        self.pRootY = np.array([])
        self.pRootS = []
        self.pTipX = np.array([])                   
        self.pTipY = np.array([])
        self.pTipS = []
        #guillotine
        self.gVSpeedNoCut = DoubleVar(value='5')
        self.gHSpeedNoCut = DoubleVar(value='5')
        self.gCuttingSpeed = DoubleVar(value='5')
        self.gApplyCalculatedHeating = IntVar(value='1')
        self.gHeating = DoubleVar(value='50')
        self.gType = StringVar(value="Vertical")
        self.gCuttingWhile = StringVar(value="Both")
        #self.gHeatWhileArming = IntVar(value='1')
        self.gVDist = DoubleVar(value='10')
        self.gHDist = DoubleVar(value='10')
        


        #saved in config
        #profil
        self.oRootX = []   # original profil : usual python List ; saved in the files 
        self.oRootY = []
        self.oRootS = []   # synchro points
        self.oTipX = []                   
        self.oTipY = []
        self.oTipS = []
        self.nameRoot = StringVar(value="")
        self.nameTip = StringVar(value="")
        #transform
        self.cRoot = DoubleVar(value='200.0')       #chord
        self.cTip = DoubleVar(value='150.0')        #chord
        self.incidenceRoot = DoubleVar(value='0.0')
        self.thicknessRoot = DoubleVar(value='100.0')
        self.vInvertRoot = IntVar(value='0') 
        self.incidenceTip = DoubleVar(value='0.0')
        self.thicknessTip = DoubleVar(value='100.0')
        self.vInvertTip = IntVar(value='0') 
        self.covering = DoubleVar(value='0.0')
        self.keepChord = IntVar(value='0')
        self.smooth = IntVar(value='0')
        self.nbrPoints = IntVar(value='50')
        self.repartition = DoubleVar(value='2.0')
        self.reducePoints = IntVar(value='0')
        
        #bloc
        self.blocLX = DoubleVar(value='600.0')      #Length = envergure
        self.blocHZ = DoubleVar(value='50.0')    #height of the bloc
        self.fLeading = DoubleVar(value='10.0')      #fleche   
        self.fTrailing = DoubleVar(value= '-30') #self.cRoot.get() - self.cTip.get() - self.fLeading.get()) #calculated
        self.mLeading = DoubleVar(value='5.0')
        self.mTrailingRoot = DoubleVar(value='10.0')
        self.mTrailingTip = DoubleVar(value='10.0') 
        self.leftRightWing = StringVar(value='Left')
        self.blocPosition = StringVar(value='Left') #Left or Right position
        self.blocToTableLeft = DoubleVar(value='100.0')   #calculated but depend on bloc position
        self.blocToTableRight = DoubleVar(value='10.0')   #calculated but depend on bloc position
        self.blocToTableTrailingRoot = IntVar(value='50')    
        self.blocToTableTrailingTip = IntVar(value='50')    #calculated
        self.blocToTableLeadingRoot = IntVar(value='50')  #calculated
        self.blocToTableLeadingTip = IntVar(value='50')   #calculated
        #margin
        self.hTrailingRoot = DoubleVar(value='10.0')
        self.hTrailingTip = DoubleVar(value='10.0')         #calculated
        self.hLeadingRoot = DoubleVar(value='10.0')         #calculated
        self.hLeadingTip = DoubleVar(value='10.0')          #calculated
        self.hMaxRoot = DoubleVar(value='10.0')          #calculated
        self.hMaxTip = DoubleVar(value='10.0')          #calculated
        self.hMinRoot = DoubleVar(value='10.0')          #calculated
        self.hMinTip = DoubleVar(value='10.0')          #calculated
        self.hOffset = DoubleVar(value='10.0')          #heigh of the base of the bloc
        self.alignProfil = StringVar(value="Trailing")
        self.hProfil = DoubleVar(value='20.0')
        """
        self.hMaxRootNorm = 0
        self.hMinRootNorm = 0
        self.hLeadingRootNorm = 0
        self.hMaxTipNorm = 0
        self.hMinTipNorm = 0
        self.hLeadingTipNorm = 0
        """
        #Material
        self.mSpeedHigh =  DoubleVar(value='10.0')          #speed max
        self.mSpeedHalf =  DoubleVar(value='5.0')          #speed min
        self.mSpeedLow =  DoubleVar(value='1.0')          #speed min
        self.mRadSpHigh =  DoubleVar(value='0.9')          #Radiance at high max
        self.mRadSpHalf =  DoubleVar(value='1.5')          #Radiance at half speed
        self.mHeatSpHigh =  IntVar(value='90')          #Heat at High speed
        self.mHeatSpLow =  IntVar(value='40')          #Heat at low speed
        self.mName = StringVar(value="No material name")
        #table
        self.tableYY = DoubleVar(value='1000.0')   # distance between 2 axis
        self.tableYG = DoubleVar(value='20.0')     #distance between left Y axis and left table edge 
        self.tableYD = DoubleVar(value='20.0')     # same on the rigth side
        self.cMaxY = DoubleVar(value='500.0')      # max course in Y
        self.cMaxZ = DoubleVar(value='200.0')      # max course in Z (height)
        self.vMaxY = DoubleVar(value='10.0')       # max speed in Y
        self.vMaxZ = DoubleVar(value='5.0')        # max speed in Z (height)
        self.tHeatingMax = DoubleVar(value='100.0')        # max heating
        self.tName = StringVar(value="No table name")
        #self.tComPort = StringVar(value="Select a Com port")
        self.tComPort = StringVar(value="COM6")
        self.tBaudrate = StringVar(value="115200")
        self.tPreHeat = DoubleVar(value='5.0')   # delay between Heat and move
        self.tPostHeat = DoubleVar(value='5.0')   # delay between Move and Heat
        
        #cut
        self.vCut = DoubleVar(value='5.0')        # max speed for cutting (on root or tip depending the longest
        self.gCodeStart1 = StringVar(value="")
        self.gCodeStart2 = StringVar(value="")
        self.gCodeStart3 = StringVar(value="")
        self.gCodeStart4 = StringVar(value="")
        self.gCodeEnd1 = StringVar(value="")
        self.gCodeEnd2 = StringVar(value="")
        self.gCodeEnd3 = StringVar(value="")
        self.gCodeEnd4 = StringVar(value="")
        self.gCodeLetters = StringVar(value="XYZA")
        
        #self.validatePart()

    def uploadConfig(self):   
        #global configUploadFileName
        #configUploadFileName = filedialog.askopenfilename(initialdir="C:/Data/",
        self.configUploadFileName = filedialog.askopenfilename(\
                            filetypes =(("Ini files", "*.ini"),("All files","*.*")),
                            title = "Choose a file."
                            )
        if len(self.configUploadFileName) > 0:
            self.validateAllOn = False 
            #config.read('config.ini')
            config =  configparser.ConfigParser()
            config.add_section("Profil")
            config.add_section("Transform")
            config.add_section("Bloc")
            config.add_section("Material")
            config.add_section("Table")
            config.add_section("Cut")
            config.add_section("Guillotine")
            
            config.read(self.configUploadFileName)
            self.oRootX = stringToListOfFloat(config.get("Profil", "RootX"))
            self.oRootY = stringToListOfFloat(config.get("Profil", "RootY"))
            self.oRootS = stringToListOfFloat(config.get("Profil", "RootS"))
            self.oTipX = stringToListOfFloat(config.get("Profil", "TipX"))
            self.oTipY = stringToListOfFloat(config.get("Profil", "TipY"))
            self.oTipS = stringToListOfFloat(config.get("Profil", "TipS"))
            self.nameRoot.set(value= config.get("Profil", "nameRoot"))
            self.nameTip.set(value= config.get("Profil", "nameTip"))
            
            self.cRoot.set(value= config.getfloat("Transform", "cRoot"))
            self.cTip.set(value= config.getfloat("Transform", "cTip"))
            self.incidenceRoot.set(value= config.getfloat("Transform", "incidenceRoot"))
            self.thicknessRoot.set(value= config.getfloat("Transform", "thicknessRoot"))
            self.vInvertRoot.set(value= config.getint("Transform", "vInvertRoot"))
            self.incidenceTip.set(value= config.getfloat("Transform", "incidenceTip"))
            self.thicknessTip.set(value= config.getfloat("Transform", "thicknessTip"))
            self.vInvertTip.set(value= config.getint("Transform", "vInvertTip"))
            self.covering.set(value= config.getfloat("Transform", "covering"))
            self.keepChord.set(value= config.getint("Transform", "keepChord"))
            self.smooth.set(value= config.getint("Transform", "smooth"))
            self.nbrPoints.set(value= config.getint("Transform", "nbrPoints"))
            self.repartition.set(value= config.getfloat("Transform", "repartition"))
            self.reducePoints.set(value= config.getint("Transform", "reducePoints"))
            
            self.blocLX.set(value= config.getfloat("Bloc", "blocLX"))
            self.blocHZ.set(value= config.getfloat("Bloc", "blocHZ"))
            self.fLeading.set(value= config.getfloat("Bloc", "fLeading"))
            self.mLeading.set(value= config.getfloat("Bloc", "mLeading"))
            self.mTrailingRoot.set(value= config.getfloat("Bloc", "mTrailingRoot"))
            self.mTrailingTip.set(value= config.getfloat("Bloc", "mTrailingTip"))
            self.leftRightWing.set(value= config.get("Bloc", "leftRightWing"))
            self.blocPosition.set(value= config.get("Bloc", "blocPosition"))
            self.blocToTableLeft.set(value= config.getfloat("Bloc", "blocToTableLeft"))
            self.blocToTableRight.set(value= config.getfloat("Bloc", "blocToTableRight"))
            self.blocToTableTrailingRoot.set(value= config.getint("Bloc", "blocToTableTrailingRoot"))
            self.blocToTableTrailingTip.set(value= config.getint("Bloc", "blocToTableTrailingTip"))
            self.blocToTableLeadingRoot.set(value= config.getint("Bloc", "blocToTableLeadingRoot"))
            self.blocToTableLeadingTip.set(value= config.getint("Bloc", "blocToTableLeadingTip"))

            self.hTrailingRoot.set(value= config.getfloat("Bloc", "hTrailingRoot"))
            self.hTrailingTip.set(value= config.getfloat("Bloc", "hTrailingTip"))
            self.hLeadingRoot.set(value= config.getfloat("Bloc", "hLeadingRoot"))
            self.hLeadingTip.set(value= config.getfloat("Bloc", "hLeadingTip"))
            self.hMaxRoot.set(value= config.getfloat("Bloc", "hMaxRoot"))
            self.hMaxTip.set(value= config.getfloat("Bloc", "hMaxTip"))
            self.hMinRoot.set(value= config.getfloat("Bloc", "hMinRoot"))
            self.hMinTip.set(value= config.getfloat("Bloc", "hMinTip"))
            self.hOffset.set(value= config.getfloat("Bloc", "hOffset"))
            self.alignProfil.set(value= config.get("Bloc", "alignProfil"))
            self.hProfil.set(value= config.get("Bloc", "hProfil"))
            """
            self.hMaxRootNorm = config.get("Bloc", "hMaxRootNorm")
            self.hMinRootNorm = config.get("Bloc", "hMinRootNorm")
            self.hLeadingRootNorm = config.get("Bloc", "hLeadingRootNorm")
            self.hMaxTipNorm = config.get("Bloc", "hMaxTipNorm")
            self.hMinTipNorm = config.get("Bloc", "hMinTipNorm")
            self.hLeadingTipNorm = config.get("Bloc", "hLeadingTipNorm")
            """

            self.mSpeedHigh.set(value= config.getfloat("Material", "mSpeedHigh"))
            self.mSpeedHalf.set(value= config.getfloat("Material", "mSpeedHalf"))
            self.mSpeedLow.set(value= config.getfloat("Material", "mSpeedLow"))
            self.mRadSpHigh.set(value= config.getfloat("Material", "mRadSpHigh"))
            self.mRadSpHalf.set(value= config.getfloat("Material", "mRadSpHalf"))
            self.mHeatSpHigh.set(value= config.getfloat("Material", "mHeatSpHigh"))
            self.mHeatSpLow.set(value= config.getfloat("Material", "mHeatSpLow"))
            self.mName.set(value= config.get("Material", "mName"))
            
            self.tableYY.set(value= config.getfloat("Table", "tableYY"))
            self.tableYG.set(value= config.getfloat("Table", "tableYG"))
            self.tableYD.set(value= config.getfloat("Table", "tableYD"))
            self.cMaxY.set(value= config.getfloat("Table", "cMaxY"))
            self.cMaxZ.set(value= config.getfloat("Table", "cMaxZ"))
            self.vMaxY.set(value= config.getfloat("Table", "vMaxY"))
            self.vMaxZ.set(value= config.getfloat("Table", "vMaxZ"))
            self.tHeatingMax.set(value= config.getfloat("Table", "tHeatingMax"))
            self.tName.set(value= config.get("Table", "tName"))
            self.tComPort.set(value= config.get("Table", "tComPort"))
            self.tBaudrate.set(value= config.get("Table", "tBaudrate"))
            self.tPreHeat.set(value= config.getfloat("Table", "tPreHeat"))
            self.tPostHeat.set(value= config.getfloat("Table", "tPostHeat"))

            self.vCut.set(value= config.getfloat("Cut", "vCut"))
            self.gCodeStart1.set(value= config.get("Cut", "gCodeStart1"))
            self.gCodeStart2.set(value= config.get("Cut", "gCodeStart2"))
            self.gCodeStart3.set(value= config.get("Cut", "gCodeStart3"))
            self.gCodeStart4.set(value= config.get("Cut", "gCodeStart4"))
            self.gCodeEnd1.set(value= config.get("Cut", "gCodeEnd1"))
            self.gCodeEnd2.set(value= config.get("Cut", "gCodeEnd2"))
            self.gCodeEnd3.set(value= config.get("Cut", "gCodeEnd3"))
            self.gCodeEnd4.set(value= config.get("Cut", "gCodeEnd4"))
            self.gCodeLetters.set(value= config.get("Cut", "gCodeLetters"))

            self.gVSpeedNoCut.set(value= config.getfloat("Guillotine", "gVSpeedNoCut"))
            self.gHSpeedNoCut.set(value= config.getfloat("Guillotine", "gHSpeedNoCut"))
            self.gCuttingSpeed.set(value= config.getfloat("Guillotine", "gCuttingSpeed"))
            self.gApplyCalculatedHeating.set(value= config.getint("Guillotine", "gApplyCalculatedHeating"))
            self.gHeating.set(value= config.getfloat("Guillotine", "gHeating"))
            self.gType.set(value= config.get("Guillotine", "gType"))
            self.gCuttingWhile.set(value= config.get("Guillotine", "gCuttingWhile"))
            self.gVDist.set(value= config.getfloat("Guillotine", "gVDist"))
            self.gHDist.set(value= config.getfloat("Guillotine", "gHDist"))
            
            """
            x ,y , self.hMaxRootNorm, self.hMinRootNorm , self.hLeadingRootNorm = self.normaliseProfil(
                self.oRootX, self.oRootY, self.cRoot.get(), 0, 0)
            x ,y , self.hMaxTipNorm, self.hMinTipNorm , self.hLeadingTipNorm = self.normaliseProfil(
                self.oTipX, self.oTipY, self.cTip.get(), 0, 0)
            """
            self.validateAllOn = True
            self.validateAll(0)
            self.tProfil.updatePlotRoot()
            self.tProfil.updatePlotTip()

    def uploadTable(self):
        self.tableUploadFileName = filedialog.askopenfilename(\
                            filetypes =(("Table files", "*.tab"),("All files","*.*")),
                            title = "Choose a file to upload a table."
                            )
        if len(self.tableUploadFileName) > 0:
            #config.read('config.ini')
            config =  configparser.ConfigParser()
            config.add_section("Table")
            config.add_section("Cut")
            
            config.read(self.tableUploadFileName)
            self.tableYY.set(value= config.getfloat("Table", "tableYY"))
            self.tableYG.set(value= config.getfloat("Table", "tableYG"))
            self.tableYD.set(value= config.getfloat("Table", "tableYD"))
            self.cMaxY.set(value= config.getfloat("Table", "cMaxY"))
            self.cMaxZ.set(value= config.getfloat("Table", "cMaxZ"))
            self.vMaxY.set(value= config.getfloat("Table", "vMaxY"))
            self.vMaxZ.set(value= config.getfloat("Table", "vMaxZ"))
            self.tHeatingMax.set(value= config.getfloat("Table", "tHeatingMax"))
            self.tName.set(value= config.get("Table", "tName"))
            self.tComPort.set(value= config.get("Table", "tComPort"))
            self.tBaudrate.set(value= config.get("Table", "tBaudrate"))
            self.tPreHeat.set(value= config.getfloat("Table", "tPreHeat"))
            self.tPostHeat.set(value= config.getfloat("Table", "tPostHeat"))

            self.vCut.set(value= config.getfloat("Cut", "vCut"))
            self.gCodeStart1.set(value= config.get("Cut", "gCodeStart1"))
            self.gCodeStart2.set(value= config.get("Cut", "gCodeStart2"))
            self.gCodeStart3.set(value= config.get("Cut", "gCodeStart3"))
            self.gCodeStart4.set(value= config.get("Cut", "gCodeStart4"))
            self.gCodeEnd1.set(value= config.get("Cut", "gCodeEnd1"))
            self.gCodeEnd2.set(value= config.get("Cut", "gCodeEnd2"))
            self.gCodeEnd3.set(value= config.get("Cut", "gCodeEnd3"))
            self.gCodeEnd4.set(value= config.get("Cut", "gCodeEnd4"))
            self.gCodeLetters.set(value= config.get("Cut", "gCodeLetters"))

            self.validateAll(20) # recalculate and redraw bloc, margin and after

    def uploadMaterial(self):
        self.materialUploadFileName = filedialog.askopenfilename(\
                            filetypes =(("Material", "*.mat"),("All files","*.*")),
                            title = "Choose a file to upload a material"
                            )
        if len(self.materialUploadFileName) > 0:
            #config.read('config.ini')
            config =  configparser.ConfigParser()
            config.add_section("Material")
                        
            config.read(self.materialUploadFileName)
            self.mSpeedHigh.set(value= config.getfloat("Material", "mSpeedHigh"))
            self.mSpeedHalf.set(value= config.getfloat("Material", "mSpeedHalf"))
            self.mSpeedLow.set(value= config.getfloat("Material", "mSpeedLow"))
            self.mRadSpHigh.set(value= config.getfloat("Material", "mRadSpHigh"))
            self.mRadSpHalf.set(value= config.getfloat("Material", "mRadSpHalf"))
            self.mHeatSpHigh.set(value= config.getfloat("Material", "mHeatSpHigh"))
            self.mHeatSpLow.set(value= config.getfloat("Material", "mHeatSpLow"))
            self.mName.set(value= config.get("Material", "mName"))
            
            self.validateAll(30) # recalculate and redraw cutting

    def saveConfig(self):   
        config =  configparser.ConfigParser()
        config.add_section("Profil")
        config.add_section("Transform")
        config.add_section("Bloc")
        config.add_section("Material")
        config.add_section("Table")
        config.add_section("Cut")
        config.add_section("Guillotine")
                
        #save all paramaters
        config.set("Profil", "RootX", str('[{:s}]'.format(', '.join(['{}'.format(x) for x in self.oRootX]))))
        config.set("Profil", "RootY", str('[{:s}]'.format(', '.join(['{}'.format(x) for x in self.oRootY]))))
        config.set("Profil", "RootS", str('[{:s}]'.format(', '.join(['{}'.format(x) for x in self.oRootS]))))
        config.set("Profil", "TipX", str('[{:s}]'.format(', '.join(['{}'.format(x) for x in self.oTipX]))))
        config.set("Profil", "TipY", str('[{:s}]'.format(', '.join(['{}'.format(x) for x in self.oTipY]))))
        config.set("Profil", "TipS", str('[{:s}]'.format(', '.join(['{}'.format(x) for x in self.oTipS]))))
        config.set("Profil", "nameRoot" , self.nameRoot.get() )
        config.set("Profil", "nameTip" , self.nameTip.get() )

        config.set("Transform", "cRoot", str(self.cRoot.get()))
        config.set("Transform", "cTip", str(self.cTip.get()))
        config.set("Transform", "incidenceRoot", str(self.incidenceRoot.get()))
        config.set("Transform", "thicknessRoot", str(self.thicknessRoot.get()))
        config.set("Transform", "vInvertRoot", str(self.vInvertRoot.get()))
        config.set("Transform", "incidenceTip", str(self.incidenceTip.get()))
        config.set("Transform", "thicknessTip", str(self.thicknessTip.get()))
        config.set("Transform", "vInvertTip", str(self.vInvertTip.get()))
        config.set("Transform", "covering", str(self.covering.get()))
        config.set("Transform", "keepChord", str(self.keepChord.get()))
        config.set("Transform", "smooth", str(self.smooth.get()))
        config.set("Transform", "nbrPoints", str(self.nbrPoints.get()))
        config.set("Transform", "repartition", str(self.repartition.get()))
        config.set("Transform", "reducePoints", str(self.reducePoints.get()))

        config.set("Bloc", "blocLX", str(self.blocLX.get()))
        config.set("Bloc", "blocHZ", str(self.blocHZ.get()))
        config.set("Bloc", "fLeading", str(self.fLeading.get()))
        config.set("Bloc", "fTrailing", str(self.fTrailing.get()))
        config.set("Bloc", "mLeading", str(self.mLeading.get()))
        config.set("Bloc", "mTrailingRoot", str(self.mTrailingRoot.get()))
        config.set("Bloc", "mTrailingTip", str(self.mTrailingTip.get()))
        config.set("Bloc", "leftRightWing", self.leftRightWing.get())
        config.set("Bloc", "blocPosition", self.blocPosition.get())
        config.set("Bloc", "blocToTableLeft", str(self.blocToTableLeft.get()))
        config.set("Bloc", "blocToTableRight", str(self.blocToTableRight.get()))
        config.set("Bloc", "blocToTableTrailingRoot", str(self.blocToTableTrailingRoot.get()))
        config.set("Bloc", "blocToTableTrailingTip", str(self.blocToTableTrailingTip.get()))
        config.set("Bloc", "blocToTableLeadingRoot", str(self.blocToTableLeadingRoot.get()))
        config.set("Bloc", "blocToTableLeadingTip", str(self.blocToTableLeadingTip.get()))

        config.set("Bloc", "hTrailingRoot", str(self.hTrailingRoot.get()))
        config.set("Bloc", "hTrailingTip", str(self.hTrailingTip.get()))
        config.set("Bloc", "hLeadingRoot", str(self.hLeadingRoot.get()))
        config.set("Bloc", "hLeadingTip", str(self.hLeadingTip.get()))
        config.set("Bloc", "hMaxRoot", str(self.hMaxRoot.get()))
        config.set("Bloc", "hMaxTip", str(self.hMaxTip.get()))
        config.set("Bloc", "hMinRoot", str(self.hMinRoot.get()))
        config.set("Bloc", "hMinTip", str(self.hMinTip.get()))
        config.set("Bloc", "hOffset", str(self.hOffset.get()))
        config.set("Bloc", "alignProfil", self.alignProfil.get())
        config.set("Bloc", "hProfil", str(self.hProfil.get()))
        
        config.set("Material", "mSpeedHigh", str(self.mSpeedHigh.get()))
        config.set("Material", "mSpeedHalf", str(self.mSpeedHalf.get()))
        config.set("Material", "mSpeedLow", str(self.mSpeedLow.get()))
        config.set("Material", "mRadSpHigh", str(self.mRadSpHigh.get()))
        config.set("Material", "mRadSpHalf", str(self.mRadSpHalf.get()))
        config.set("Material", "mHeatSpHigh", str(self.mHeatSpHigh.get()))
        config.set("Material", "mHeatSpLow", str(self.mHeatSpLow.get()))
        config.set("Material", "mName", self.mName.get())

        config.set("Table", "tableYY", str(self.tableYY.get()))
        config.set("Table", "tableYG", str(self.tableYG.get()))
        config.set("Table", "tableYD", str(self.tableYD.get()))
        config.set("Table", "cMaxY", str(self.cMaxY.get()))
        config.set("Table", "cMaxZ", str(self.cMaxZ.get()))
        config.set("Table", "vMaxY", str(self.vMaxY.get()))
        config.set("Table", "vMaxZ", str(self.vMaxZ.get()))
        config.set("Table", "tHeatingMax", str(self.tHeatingMax.get()))
        config.set("Table", "tName", self.tName.get())
        config.set("Table", "tComPort", self.tComPort.get())
        config.set("Table", "tBaudrate", self.tBaudrate.get())
        config.set("Table", "tPreHeat", str(self.tPreHeat.get()))
        config.set("Table", "tPostHeat", str(self.tPostHeat.get()))
        
        config.set("Cut", "vCut", str(self.vCut.get()))
        config.set("Cut", "gCodeStart1", self.gCodeStart1.get())
        config.set("Cut", "gCodeStart2", self.gCodeStart2.get())
        config.set("Cut", "gCodeStart3", self.gCodeStart3.get())
        config.set("Cut", "gCodeStart4", self.gCodeStart4.get())
        config.set("Cut", "gCodeEnd1", self.gCodeEnd1.get())
        config.set("Cut", "gCodeEnd2", self.gCodeEnd2.get())
        config.set("Cut", "gCodeEnd3", self.gCodeEnd3.get())
        config.set("Cut", "gCodeEnd4", self.gCodeEnd4.get())
        config.set("Cut", "gCodeLetters", self.gCodeLetters.get())

        config.set("Guillotine", "gVSpeedNoCut", str(self.gVSpeedNoCut.get()))
        config.set("Guillotine", "gHSpeedNoCut", str(self.gHSpeedNoCut.get()))
        config.set("Guillotine", "gCuttingSpeed", str(self.gCuttingSpeed.get()))
        config.set("Guillotine", "gApplyCalculatedHeating", str(self.gApplyCalculatedHeating.get()))
        config.set("Guillotine", "gHeating", str(self.gHeating.get()))
        config.set("Guillotine", "gType", self.gType.get())
        config.set("Guillotine", "gCuttingWhile", self.gCuttingWhile.get())
        config.set("Guillotine", "gVDist", str(self.gVDist.get()))
        config.set("Guillotine", "gHDist", str(self.gHDist.get()))

        
        configSaveFileName = filedialog.asksaveasfilename(title="Save as...", defaultextension="*.ini",\
            filetypes=[("Ini files","*.ini"),("All files", "*")], initialfile=self.configUploadFileName)
        if len(configSaveFileName) > 0:
            config.write(open(configSaveFileName ,'w'))

    def saveTable(self):   
        config =  configparser.ConfigParser()
        config.add_section("Table")
        config.add_section("Cut")
        config.set("Table", "tableYY", str(self.tableYY.get()))
        config.set("Table", "tableYG", str(self.tableYG.get()))
        config.set("Table", "tableYD", str(self.tableYD.get()))
        config.set("Table", "cMaxY", str(self.cMaxY.get()))
        config.set("Table", "cMaxZ", str(self.cMaxZ.get()))
        config.set("Table", "vMaxY", str(self.vMaxY.get()))
        config.set("Table", "vMaxZ", str(self.vMaxZ.get()))
        config.set("Table", "tHeatingMax", str(self.tHeatingMax.get()))
        config.set("Table", "tName", self.tName.get())
        config.set("Table", "tComPort", self.tComPort.get())
        config.set("Table", "tBaudrate", self.tBaudrate.get())
        config.set("Table", "tPreHeat", str(self.tPreHeat.get()))
        config.set("Table", "tPostHeat", str(self.tPostHeat.get()))
        
        config.set("Cut", "vCut", str(self.vCut.get()))
        config.set("Cut", "gCodeStart1", self.gCodeStart1.get())
        config.set("Cut", "gCodeStart2", self.gCodeStart2.get())
        config.set("Cut", "gCodeStart3", self.gCodeStart3.get())
        config.set("Cut", "gCodeStart4", self.gCodeStart4.get())
        config.set("Cut", "gCodeEnd1", self.gCodeEnd1.get())
        config.set("Cut", "gCodeEnd2", self.gCodeEnd2.get())
        config.set("Cut", "gCodeEnd3", self.gCodeEnd3.get())
        config.set("Cut", "gCodeEnd4", self.gCodeEnd4.get())
        config.set("Cut", "gCodeLetters", self.gCodeLetters.get())
        
        if self.tableSaveFileName == None:
            self.tableSaveFileName = self.tableUploadFileName    
        self.tableSaveFileName = filedialog.asksaveasfilename(title="Save table as...", defaultextension="*.tab",\
            filetypes=[("Table files","*.tab"),("All files", "*")], initialfile=self.tableSaveFileName)
        if len(self.tableSaveFileName) > 0:
            config.write(open(self.tableSaveFileName ,'w'))
    
    def saveMaterial(self):   
        config =  configparser.ConfigParser()
        config.add_section("Material")
        config.set("Material", "mSpeedHigh", str(self.mSpeedHigh.get()))
        config.set("Material", "mSpeedHalf", str(self.mSpeedHalf.get()))
        config.set("Material", "mSpeedLow", str(self.mSpeedLow.get()))
        config.set("Material", "mRadSpHigh", str(self.mRadSpHigh.get()))
        config.set("Material", "mRadSpHalf", str(self.mRadSpHalf.get()))
        config.set("Material", "mHeatSpHigh", str(self.mHeatSpHigh.get()))
        config.set("Material", "mHeatSpLow", str(self.mHeatSpLow.get()))
        config.set("Material", "mName", self.mName.get())

        if self.materialSaveFileName == None:
            self.materialSaveFileName = self.materialUploadFileName    
        self.materialSaveFileName = filedialog.asksaveasfilename(title="Save material as...", defaultextension="*.material",\
            filetypes=[("Material files","*.material"),("All files", "*")], initialfile=self.materialSaveFileName)
        if len(self.materialSaveFileName) > 0:
            config.write(open(self.materialSaveFileName ,'w'))
    
    def validatePart(self):
        self.fTrailing.set( -(self.cRoot.get() - self.cTip.get() - self.fLeading.get()  ) )
        if self.blocPosition.get() == "Left" :
            self.tBloc.blocToTableRightBox['validate']='none'  # disable validate, otherwise we call validate inside validate
            self.blocToTableRight.set( self.tableYY.get() - self.tableYG.get() - self.tableYD.get() - self.blocToTableLeft.get() -  self.blocLX.get())
            self.tBloc.blocToTableRightBox['validate']='focusout'  #enable after the update
        else:
            self.tBloc.blocToTableRightBox['validate']='none' # disable validate, otherwise we call validate inside validate
            self.blocToTableLeft.set( self.tableYY.get() - self.tableYG.get() - self.tableYD.get() - self.blocToTableRight.get() - self.blocLX.get())
            self.tBloc.blocToTableRightBox['validate']='focusout'
        self.blocToTableTrailingTip.set(self.blocToTableTrailingRoot.get() - self.fTrailing.get())
        self.blocToTableLeadingRoot.set(self.blocToTableTrailingRoot.get() +  self.cRoot.get() + 
            self.mTrailingRoot.get() + self.mLeading.get() )

        self.blocToTableLeadingTip.set(self.blocToTableTrailingTip.get() +  self.cTip.get() + 
            self.mTrailingTip.get() + self.mLeading.get() )
        #self.mSpeedHalf.set(self.mSpeedHigh.get() / 2) #half speed = high speed /2
        
    def validateAll(self, level):
        # level is used to avoid to recalculate some data when not needed
        # 0 = calculate all (original profil change)
        # 10 = calculate Transform and after (Transform profil: chord, incidence...)
        # 20 = calculate Bloc/margin and after (change table or bloc position)
        # 30 = calculate cutting (change speed, material)
        if self.initDone and self.validateAllOn :  #avoid validate during the set up of tkinter widgets and when validateAll is disabled
            #try:    
            if level == 0:
                self.tProfil.updatePlotRoot()
                self.tProfil.updatePlotTip()
            
            if level <= 10:
                #create tRoot and tTipX based on oRoot and oTip and chords but not based on bloc and margin
                # draw the view in Transform (= tRoot and tTip)
                
                if ( len(self.oRootX) > 0 ) and (len(self.oTipX) >0):
                    #create tRoot and tTipX based on oRoot and oTip and chords but not based on bloc and margin
                    self.tTransform.validateTransform()
                    self.tTransform.updatePlotRoot()
                    self.tTransform.updatePlotTip()

            if level <= 20:    
                    pass
                    #create pRoot and pTipX based on tRoot and tTip and based on Table, bloc and margin 
                    self.validatePart()         
                    self.calculatePositions()
                    # draw the bloc ()
                    self.tBloc.updatePlotBloc()
                    #draw the margins
                    self.tMargin.updatePlotMargin()

                    #update heating for guillotine
                    self.tGuillotine.updateGuillotineHeating()

            if level <= 30: # calculate Cut based on Material
                if ( len(self.pRootX) > 0 ) and (len(self.pTipX) >0):
                    pass
                    self.tCut.calculateRedraw()    
            warningMsg = ""
            if ( len(self.oRootX) <= 1 ) and ( len(self.oTipX) <= 1 ):
                warningMsg = "Root and Tip profiles missing"
            elif len(self.oRootX) <= 1:
                warningMsg = "Root profile missing"
            elif len(self.oTipX) <= 1:
                warningMsg = "Tip profile missing"
            elif (self.tRootS.count(4)+self.tRootS.count(10) ) != (self.tTipS.count(4)+self.tTipS.count(10) ):
                warningMsg = "Transformed root and tip profiles must have the same number of synchro points"
            self.warningMsg.set(warningMsg)
            
            #except:
            #    print("error during validation")    
        return True

    def calculatePositions(self):
        #create bRoot and bTipX based on tRoot and tTip and based on bloc and margin
        #calculate Root and Tip offset to apply
        if (len(self.tRootX) > 0) and (len(self.tTipX) >0 ): # and (len(self.tRootX) == len(self.tTipX)):
            #calculate relative height of max, min leading
            hMaxRootNorm, hMinRootNorm , hLeadingRootNorm = self.calculateRelativeHeigths(self.tRootX , self.tRootY )        
            hMaxTipNorm, hMinTipNorm , hLeadingTipNorm = self.calculateRelativeHeigths(self.tTipX , self.tTipY )        
            
            #Apply vertical aligment
            if self.alignProfil.get() == "Trailing":
                self.hTrailingRoot.set(self.hProfil.get())
                self.hTrailingTip.set(self.hProfil.get())
            elif self.alignProfil.get() == "Leading":
                self.hTrailingRoot.set(self.hProfil.get() - hLeadingRootNorm )
                self.hTrailingTip.set(self.hProfil.get() - hLeadingTipNorm )
            elif self.alignProfil.get() == "Extrados":
                self.hTrailingRoot.set(self.hProfil.get() - hMaxRootNorm )
                self.hTrailingTip.set(self.hProfil.get() - hMaxTipNorm )
            elif self.alignProfil.get() == "Intrados":
                self.hTrailingRoot.set(self.hProfil.get() - hMinRootNorm )
                self.hTrailingTip.set(self.hProfil.get() - hMinTipNorm )
            self.hLeadingRoot.set(self.hTrailingRoot.get() + hLeadingRootNorm )
            self.hLeadingTip.set(self.hTrailingTip.get() + hLeadingTipNorm )
            self.hMaxRoot.set( self.blocHZ.get() - self.hTrailingRoot.get() - hMaxRootNorm  )
            self.hMaxTip.set(self.blocHZ.get() - self.hTrailingTip.get() - hMaxTipNorm )
            self.hMinRoot.set(self.hTrailingRoot.get() + hMinRootNorm )
            self.hMinTip.set(self.hTrailingTip.get() + hMinTipNorm )        
            
            #apply offsets
            self.pRootX = self.tRootX + self.blocToTableTrailingRoot.get() + self.mTrailingRoot.get()
            self.pTipX = self.tTipX + self.blocToTableTrailingTip.get() + self.mTrailingTip.get()
            self.pRootY = self.tRootY + self.hOffset.get() + self.hTrailingRoot.get()
            self.pTipY =  self.tTipY + self.hOffset.get() + self.hTrailingRoot.get()
            self.pRootS = list(self.tRootS) #create list of synchro
            self.pTipS = list(self.tTipS) #create list of synchro    

    """
    def validateFloat(self, reason, val , name , old,  min , max):
        if reason == "focusout":
            try :  
                v = float(val)
                if v >= float(min) and v <= float(max):
                    
                    return True
                return True    
            except : 
                return False
        elif reason == "focusout":
            if float(val) > float(max):
                print("focus out max exceeded")
                return False
            return self.validateAll()        
        return True
    """

    def normaliseArrayProfil (self , aX , aY , chord):
        #normalise the profil with chord
        if len(aX) > 0:
            minX = np.min(aX)
            maxX = np.max(aX)
            ratio= chord / ( maxX - minX )  
            aXn = aX * ratio
            aXn = aXn - aXn[0]
            aXn = -1.0 * aXn # multiply by -1 to reverse the order
            aYn = aY * ratio
            aYn = aYn - aYn[0]
            return aXn , aYn

    """
    def normaliseProfil (self , pX , pY , coord , oY, oZ):
        #normalise the profil with coord and offset of origin
        if len(pX) > 0:
            aX = np.array(pX)
            aY = np.array(pY)
            minX = np.min(aX)
            idxMin = np.where(aX == minX) #return an array with indexes
            maxX = np.max(aX)
            minY = np.min(aY)
            maxY = np.max(aY)
            ratio= coord / ( maxX - minX )  
            aX = aX * ratio
            aX = aX - aX[0]
            aX = -1 * aX # multiply by -1 to reverse the order
            aX = aX + oY
            aY = aY * ratio
            aY = aY - aY[0]
            aY = aY + oZ
            maxh = (maxY / ( maxX - minX ) ) - pY[0]
            minh = (minY / ( maxX - minX ) ) - pY[0] 
            if len(idxMin) > 0 and len(idxMin[0]) > 0:
                r = idxMin[0][0]
                leadingh = (pY[r] / ( maxX - minX ) ) - pY[0]
            else:
                leadingh = 0
                        #print("normalised aX=", aX , "aY=", aY)
            return aX.tolist() , aY.tolist() ,maxh ,minh, leadingh
    """

    def calculateRelativeHeigths (self , pX , pY ):
        maxX = np.max(pX)
        idxMax = np.where(pX == maxX) #return an array with indexes
        minY = np.min(pY)
        maxY = np.max(pY)
        maxh = maxY - pY[0]
        minh = minY - pY[0]
        if len(idxMax) > 0 and len(idxMax[0]) > 0:
            r = idxMax[0][0]
            leadingh = pY[r] - pY[0]
        else:
            leadingh = 0     
        return maxh ,minh, leadingh
    

    #def test(self):
    #    print("je passe par une fonction de app")

def stringToListOfFloat(my_string):
    if len(my_string) > 2:
        li = list(my_string[1:-1].split(","))
        return  [float(i) for i in li]
    return []

def check_presence():
    while True:
        comlist = serial.tools.list_ports.comports()
        connectedCom = []
        for element in comlist:
            connectedCom.append(element.device)
        if app.tComPort.get() in connectedCom:
            app.connected.set("ON")
        else:
            app.connected.set("OFF")
        time.sleep(1)

def main(): #run mainloop 
    global app
    root = tk.Tk()
    app = App(root)
    fil_chaud_config.initMonApp(app)
    port_controller = threading.Thread(target=check_presence)
    port_controller.setDaemon(True)
    port_controller.start()
    
    
    root.mainloop()

if __name__ == '__main__':
    main()

