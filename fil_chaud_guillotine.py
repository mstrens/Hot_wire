import tkinter as tk
from tkinter import X, Y, TOP, BOTTOM, RIGHT, LEFT, HORIZONTAL , END , DISABLED , ttk , WORD , INSERT
from tkinter import StringVar , Tk , Y, W ,E , S, N , BOTH, HIDDEN, DoubleVar , Spinbox , IntVar , filedialog
import tkinter.scrolledtext as tkst

from fil_chaud_validate import EntryFloat # , EntryFloatSpVal 
#from gerbil import Gerbil

class Guillotine:
    def __init__(self,nb, app , queueCmd):
        self.nb = nb
        self.app = app
        self.queueCmd = queueCmd
        self.frame = ttk.Frame(self.nb)
        self.levelGuillotine = 40
        #self.frame2 = ttk.Frame(self.nb)
        self.nb.add(self.frame, text='   Guillotine & Move   ')
        #self.t_frame= ttk.Frame(self.frame, highlightbackground="black" , highlightthickness=1)
        self.t_frame= ttk.Frame(self.frame, relief="groove",padding=10)
        self.l_frame= ttk.Frame(self.frame, relief="groove",padding=10)
        
        self.r_frame= ttk.Frame(self.frame, relief="groove",padding=10)
        self.m_frame= ttk.Frame(self.frame, relief="groove",padding=10)
        #self.t_frame.pack(side = TOP)
        self.l_frame.pack(side = LEFT , fill= Y)
        self.r_frame.pack(side = RIGHT , fill= Y)
        self.t_frame.pack(side = TOP)
                
        self.m_frame.pack(side = TOP)
        r = 0
        tk.Label(self.l_frame, text="Guillotine",font=("Helvetica", 18)).grid(column=0, row=r, pady=(1,1))
        
        r += 1
        tk.Label(self.l_frame, text="Cutting speed (mm/sec)").grid(column=0, row=r, pady=(20,1), sticky=E)
        EntryFloat(self.l_frame, self.app.gCuttingSpeed , 0.1 , 10, self.levelGuillotine , width='6' ).grid(column=1, row=r , padx=1,pady=(20,1), sticky=W)
        
        r += 1
        tk.Label(self.l_frame, text="Apply calculated heating").grid(column=0, row=r, pady=(20,1), sticky=E)
        tk.Checkbutton(self.l_frame, variable=self.app.gApplyCalculatedHeating , text='' ,
            command=self.updateGuillotineHeating).grid(column=1, row=r , padx=1,pady=(20,1), sticky=W )
        r += 1
        tk.Label(self.l_frame, text="Heating (%)").grid(column=0, row=r, pady=(1,1), sticky=E)
        self.gHeatingBox = EntryFloat(self.l_frame, self.app.gHeating , 0.1 , 100, self.levelGuillotine , width='6' )
        self.gHeatingBox.grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.l_frame, text="Type of guillotine").grid(column=0, row=r, pady=(20,1), sticky=W)
        r += 1
        tk.Radiobutton(self.l_frame, text="Vertical", variable=self.app.gType, value="Vertical",
            command=self.changedGType).grid(column=0, row=r, pady=(1,1), sticky=W)
        self.gVDistBox = EntryFloat(self.l_frame, self.app.gVDist , -500 , 500, self.levelGuillotine , width='6' )
        self.gVDistBox.grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        
        r += 1
        tk.Radiobutton(self.l_frame, text="Horizontal", variable=self.app.gType, value="Horizontal",
            command=self.changedGType).grid(column=0, row=r, pady=(1,1), sticky=W)
        self.gHDistBox = EntryFloat(self.l_frame, self.app.gHDist , -500 , 500, self.levelGuillotine , width='6' , state='disabled' )
        self.gHDistBox.grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)

        r += 1
        tk.Radiobutton(self.l_frame, text="Inclined", variable=self.app.gType, value="Inclined",
            command=self.changedGType).grid(column=0, row=r, pady=(1,1), sticky=W)
        
        r += 1
        tk.Label(self.l_frame, text="Cutting while").grid(column=0, row=r, pady=(20,1), sticky=W)
        r += 1
        tk.Radiobutton(self.l_frame, text="Going forward AND back", variable=self.app.gCuttingWhile, value="Both").grid(column=0, row=r, pady=(1,1), sticky=W)
        r += 1
        tk.Radiobutton(self.l_frame, text="Only going forward", variable=self.app.gCuttingWhile, value="Forward").grid(column=0, row=r, pady=(1,1), sticky=W)
        r += 1
        tk.Radiobutton(self.l_frame, text="Only going back", variable=self.app.gCuttingWhile, value="Back").grid(column=0, row=r, pady=(1,1), sticky=W)
        
        r += 1
        self.goForwardBtn = tk.Button(self.l_frame, text = 'Go forward', command=self.goForward, width = 25 , state='disabled')
        self.goForwardBtn.grid(column=0, columnspan=2 , row=r , padx=(10,10),pady=(10,1), sticky=W)
        r += 1
        self.goBackBtn = tk.Button(self.l_frame, text = 'Go back', command=self.goBackward, width = 25, state='disabled' )
        self.goBackBtn.grid(column=0, columnspan=2, row=r , padx=(10,10),pady=(10,1), sticky=W)
        r += 1
        self.cancelBtn = tk.Button(self.l_frame, text = 'Cancel', command=self.app.tGrbl.resetGrbl, width = 25, state='disabled' )
        self.cancelBtn.grid(column=0, columnspan=2, row=r , padx=(10,10),pady=(10,1), sticky=W)
        
        r=0
        tk.Label(self.t_frame, text="Grbl status").grid(column=3, row=r, pady=(1,1))
        tk.Label(self.t_frame, text="Horiz. left").grid(column=4, row=r, pady=(1,1))
        tk.Label(self.t_frame, text="Vertical left").grid(column=5, row=r, pady=(1,1))
        tk.Label(self.t_frame, text="Horiz. right").grid(column=6, row=r, pady=(1,1))
        tk.Label(self.t_frame, text="Vertical right").grid(column=7, row=r, pady=(1,1))
        tk.Label(self.t_frame, text="Speed").grid(column=8, row=r, pady=(1,1))
        tk.Label(self.t_frame, text="Heating").grid(column=9, row=r, pady=(1,1))
        r += 1
        grblStatusBox = tk.Entry(self.t_frame, textvariable=self.app.grblStatus , width='20',state='disabled' )
        grblStatusBox.grid(column=3, row=r , padx=1,pady=(1,1), sticky=W)
        tk.Entry(self.t_frame, textvariable=self.app.grblXG , width='8',state='disabled' ).grid(column=4, row=r , padx=1,pady=(1,1), sticky=W)
        tk.Entry(self.t_frame, textvariable=self.app.grblYG , width='8',state='disabled' ).grid(column=5, row=r , padx=1,pady=(1,1), sticky=W)
        tk.Entry(self.t_frame, textvariable=self.app.grblXD , width='8',state='disabled' ).grid(column=6, row=r , padx=1,pady=(1,1), sticky=W)
        tk.Entry(self.t_frame, textvariable=self.app.grblYD , width='8',state='disabled' ).grid(column=7, row=r , padx=1,pady=(1,1), sticky=W)
        tk.Entry(self.t_frame, textvariable=self.app.grblF , width='8',state='disabled' ).grid(column=8, row=r , padx=1,pady=(1,1), sticky=W)
        tk.Entry(self.t_frame, textvariable=self.app.grblS , width='8',state='disabled' ).grid(column=9, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        #self.msgText = ""
        self.msgBox = tkst.ScrolledText(self.t_frame,  width=80, height=4, wrap=tk.WORD)
        self.msgBox.grid(column=0, row=r , columnspan=9, padx=(1,1),pady=(10,10), sticky=W)
             
        r += 1
        self.connectBtn = tk.Button(self.t_frame, text = 'Connect to Grbl', command=self.connect, width = 25 )
        self.connectBtn.grid(column=3, row=r , columnspan=3, padx=(1,1),pady=(10,10), sticky=W)
        self.disconnectBtn = tk.Button(self.t_frame, text = 'Disconnect from Grbl', command=self.disconnect, width = 25 , state='disabled' )
        self.disconnectBtn.grid(column=6, row=r , columnspan=3, padx=(1,1),pady=(10,10), sticky=W)
            
        r = 0
        self.resetBtn = tk.Button(self.r_frame, text = 'Reset Grbl', command=self.app.tGrbl.resetGrbl,width = 25 , state='disabled' )
        self.resetBtn.grid(column=2, row=r , padx=(10,10),pady=(20,1), sticky=W)
        r += 1
        self.unlockBtn = tk.Button(self.r_frame, text = 'Unlock Grbl', command=self.app.tGrbl.unlockGrbl, width = 25, state='disabled' )
        self.unlockBtn.grid(column=2, row=r , padx=(10,10),pady=(20,1), sticky=W)
        r += 1
        self.homeBtn = tk.Button(self.r_frame, text = 'Home', command=self.app.tGrbl.homeGrbl, width = 25, state='disabled' )
        self.homeBtn.grid(column=2, row=r , padx=(10,10),pady=(20,1), sticky=W)
        r += 1
        self.setBtn = tk.Button(self.r_frame, text = 'Set position', command=self.app.tGrbl.setPosGrbl, width = 25, state='disabled' )
        self.setBtn.grid(column=2, row=r , padx=(10,10),pady=(40,1), sticky=W)
        r += 1
        self.gotoBtn = tk.Button(self.r_frame, text = 'Go to position', command=self.app.tGrbl.goToPosGrbl, width = 25, state='disabled' ) 
        self.gotoBtn.grid(column=2, row=r , padx=(10,10),pady=(20,1), sticky=W)
        r += 1
        self.startHeatingBtn = tk.Button(self.r_frame, text = 'Start heating', command=self.startHeat, width = 25, state='disabled' )
        self.startHeatingBtn.grid(column=2, row=r , padx=(10,10),pady=(40,1), sticky=W)
        r += 1
        self.stopHeatingBtn = tk.Button(self.r_frame, text = 'Stop heating', command=self.stopHeat, width = 25, state='disabled' )
        self.stopHeatingBtn.grid(column=2, row=r , padx=(10,10),pady=(20,1), sticky=W)

        r=0
        tk.Label(self.m_frame, text="Move",font=("Helvetica", 18)).grid(column=0, row=r, columnspan= 3, pady=(20,1))
        r += 1
        self.moveUpBtn = tk.Button(self.m_frame, text = 'Up', command=self.moveUp, width = 15, state='disabled' )
        self.moveUpBtn.grid(column=1, row=r , padx=(10,10),pady=(20,1))
        r += 1
        self.moveBackBtn = tk.Button(self.m_frame, text = 'Back', command=self.moveBack, width = 15, state='disabled' )
        self.moveBackBtn.grid(column=0, row=r , padx=(10,10),pady=(20,1))
        EntryFloat(self.m_frame, self.app.gMoveDist , 0.1 , 500, self.levelGuillotine , width='6' ).grid(column=1, row=r , padx=1,pady=(20,1))
        self.moveForwardBtn = tk.Button(self.m_frame, text = 'Forward', command=self.moveForward, width = 15, state='disabled' )
        self.moveForwardBtn.grid(column=2, row=r , padx=(10,10),pady=(20,1))
        r += 1
        self.moveDownBtn = tk.Button(self.m_frame, text = 'Down', command=self.moveDown, width = 15, state='disabled' )
        self.moveDownBtn.grid(column=1, row=r , padx=(10,10),pady=(20,1))
        r += 1
        tk.Radiobutton(self.m_frame, text="Left axis", variable=self.app.gMoveAxis, value="Left").grid(column=0, row=r, pady=(20,1))
        tk.Radiobutton(self.m_frame, text="Both axis", variable=self.app.gMoveAxis, value="Both").grid(column=1, row=r, pady=(20,1))
        tk.Radiobutton(self.m_frame, text="Right axis", variable=self.app.gMoveAxis, value="Right").grid(column=2, row=r, pady=(20,1))
        
    
    def changedGType(self):
        if self.app.gType.get() == "Vertical":
            self.gVDistBox['state'] = 'normal'
            self.gHDistBox['state'] = 'disabled'
        elif self.app.gType.get() == "Horizontal":
            self.gVDistBox['state'] = 'disabled'
            self.gHDistBox['state'] = 'normal'
        else:
            self.gVDistBox['state'] = 'normal'
            self.gHDistBox['state'] = 'normal'

    def updateGuillotineHeating(self):
        #if box is checked, calculate heating based on speed and materail and disable the heating box
        # else keep the value but limit it depending on table parameter and set heating box state on normal
        if self.app.gApplyCalculatedHeating.get():
            self.gHeatingBox['validate']='none' #disable focusout while updating
            self.app.gHeating.set(self.calculateHeating(self.app.gCuttingSpeed.get()) )
            self.gHeatingBox['validate']='focusout' #disable focusout while updating
            self.gHeatingBox['state']= 'disabled'
        else:
            self.gHeatingBox['state']= 'normal'    

    def calculateHeating(self, speed):
        x1 = self.app.mSpeedLow.get()
        x2 = self.app.mSpeedHigh.get()
        y1 = self.app.mHeatSpLow.get()
        y2 = self.app.mHeatSpHigh.get()
        heat = 0
        
        if (x2-x1) != 0:
            heat = y1 + (y2-y1)/(x2-x1)*(speed - x1) 
        #print(x1, x2, y1 ,y2 , heat)
        if heat < 1:
            heat =1
        if heat > self.app.tHeatingMax.get():
           heat = self.app.tHeatingMax.get()     
        return heat

    def calculateMove(self , factor):
        axis = self.app.gCodeLetters.get()
        if self.app.gType.get() == "Vertical":
            move = axis[1] + str(factor * self.app.gVDist.get()) + axis[3] + str(factor * self.app.gVDist.get()) 
        elif  self.app.gType.get() == "Horizontal":
            move = axis[0] + str(factor * self.app.gHDist.get()) + axis[2] + str(factor * self.app.gHDist.get()) 
        else:
            move = axis[1] + str(factor * self.app.gVDist.get()) + axis[0] + str(factor * self.app.gHDist.get()) + (
                axis[3] + str(factor * self.app.gVDist.get()) + axis[2] + str(factor * self.app.gHDist.get()) )
        return move
    
    def goForward(self):
        command = ["G21" , "G91"]  # mm incremental
        if self.app.gCuttingWhile.get() == "Forward" or self.app.gCuttingWhile.get() == "Both":
            command.append("M3")
            command.append("S50" )
            command.append( "G04P" + str(self.app.tPreHeat.get() ) ) 
            command.append("F" +str(60 * self.app.gCuttingSpeed.get() ))
            command.append( "G01")
        else:
            command.append( "G00")     
        command.append( self.calculateMove(1))
        if self.app.gCuttingWhile.get() == "Backward" or self.app.gCuttingWhile.get() == "Both":
            command.append( "G04P" + str(self.app.tPostHeat.get() ) ) 
            command.append("M5")
        #print("\n".join(command))
        self.app.tGrbl.stream("\n".join(command))
        
    def goBackward(self):
        command = ["G21" , "G91"]  # mm incremental
        if self.app.gCuttingWhile.get() == "Backward" or self.app.gCuttingWhile.get() == "Both":
            command.append("M3")
            command.append("S50")
            command.append( "G04P" + str(self.app.tPreHeat.get() ) ) 
            command.append("F"+str(60 * self.app.gCuttingSpeed.get() ))
            command.append( "G01")
        else:
            command.append( "G00")     
        command.append( self.calculateMove(-1))
        if self.app.gCuttingWhile.get() == "Backward" or self.app.gCuttingWhile.get() == "Both":
            command.append( "G04P" + str(self.app.tPostHeat.get() ) ) 
            command.append("M5")
        #print("\n".join(command))
        self.app.tGrbl.stream("\n".join(command))

    def startHeat(self):
        command = ["S50" , "M3"] 
        self.app.tGrbl.stream("\n".join(command))

    def stopHeat(self):
        command = ["S0" ,"M5"] 
        self.app.tGrbl.stream("\n".join(command))
        
    def moveUp(self):
        self.move("Up")

    def moveDown(self):
        self.move("Down")

    def moveForward(self):
        self.move("Forward")

    def moveBack(self):
        self.move("Back")

    def move(self, dir):
        command = ["G21" , "G91"]  # mm incremental
        axis = self.app.gCodeLetters.get()
        axisIdx = 0
        dirPos = 1
        if dir == "Up":
            axisIdx = 1
        elif dir == "Down":
            axisIdx = 1
            dirPos = -1
        elif dir == "Back":
            dirPos = -1
        if self.app.gMoveAxis.get() == "Left":
            command.append("G00 "+ axis[axisIdx]+ str(dirPos * self.app.gMoveDist.get() ) )
        elif self.app.gMoveAxis.get() == "Right":
            command.append("G00 "+ axis[axisIdx+2]+ str(dirPos * self.app.gMoveDist.get() ) )
        else:
            command.append("G00 "+ axis[axisIdx]+ str(dirPos * self.app.gMoveDist.get() ) +
                axis[axisIdx+2]+ str(dirPos * self.app.gMoveDist.get() ) )
        print("\n".join(command))
        self.app.tGrbl.stream("\n".join(command))
        

    def connect(self):
        self.queueCmd.put("Connect") 
    
    def disconnect(self):
        self.queueCmd.put("Disconnect")
        
    
    def updateBtnState(self):
        grblStatus= self.app.grblStatus.get()
        if grblStatus == "Not connected" or grblStatus == "Connection lost":
            state = 'disabled'
            oppositeState = 'normal'
        else:
            state = 'normal'
            oppositeState = 'disabled'
        self.goForwardBtn['state'] = state
        self.goBackBtn['state'] = state
        self.cancelBtn['state'] = state
        self.connectBtn['state'] = oppositeState
        self.disconnectBtn['state'] = state
        self.resetBtn['state'] = state
        self.unlockBtn['state'] = state
        self.homeBtn['state'] = state
        self.setBtn['state'] = state
        self.gotoBtn['state'] = state
        self.startHeatingBtn['state'] = state
        self.stopHeatingBtn['state'] = state
        self.moveUpBtn['state'] = state
        self.moveBackBtn['state'] = state
        self.moveForwardBtn['state'] = state
        self.moveDownBtn['state'] = state

        self.app.tCut.cutBtn['state'] = state
        self.app.tCut.cancelBtn['state'] = state

"""
def my_callback(eventstring, *data):
    args = []
    for d in data:
        args.append(str(d))
    print("MY CALLBACK: event={} data={}".format(eventstring.ljust(30), ", ".join(args)))
    # Now, do something interesting with these callbacks

"""
"""
Add a connect button:
    Greate Gerbil instance
    Configure Com and baudrate
Add a disconnect button:
    Disconnect

Add a button reset GRBL
Add a button unlock GRBL
Display a value Disconnected or GRBL status

When Arming:
    generate the string for moving up
    set a heating flag on ON/OFF depending on GUI
    Check that connected and GRBL status
    Send GRBL command : mm, relatif
    If heating: 
        Calculate heating (for the speed)
        Send heating and pause
        Send G01 command with feedrate
        pause
    else
        send G00 command        
When Cutting
    idem with negative value
    set heating flag on OFF

"""