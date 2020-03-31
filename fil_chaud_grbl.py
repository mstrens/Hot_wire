import tkinter as tk
from tkinter import X, Y, BOTTOM, RIGHT, LEFT, HORIZONTAL , END , DISABLED , ttk
from tkinter import StringVar , Tk , W ,E , S , BOTH, HIDDEN, DoubleVar , Spinbox , IntVar , filedialog

from gerbil import Gerbil
import time
import re
import queue


class Grbl:
    def __init__(self,nb, app, queue):
        self.nb = nb
        self.app = app
        self.queue = queue
        self.grbl = Gerbil(self.my_callback)    
        #Next, we tell Gerbil to use its default log handler, which, instead of printing to stdout directly, will also call above my_callback function with eventstring on_log. You could use this, for example, to output the logging strings in a GUI window:
        self.grbl.setup_logging()


    def connectToGrbl(self):
        #We now can connect to the grbl firmware, the actual CNC machine:
        self.grbl.cnect(self.app.tComPort.get() , self.app.tBaudrate.get())
        #We will poll every half tsecond for the state of the CNC machine (working position, etc.):
        time.sleep(1)
        self.grbl.poll_start()
    
    def disconnectToGrbl(self):
        self.grbl.disconnect()
        self.app.grblStatus.set("Not connected")
        
    def resetGrbl(self):
        self.grbl.abort()

    def unlockGrbl(self):
        self.grbl.killalarm()

    def homeGrbl(self):
        self.grbl.homing()

    def setPosGrbl(self):
        self.grbl.send_immediately("G28.1")

    def goToPosGrbl(self):
        self.grbl.send_immediately("G28")

    def stream(self, lines):
        self.grbl.stream(lines)
    
    def my_callback(self , eventstring, *data):
        args = []
        for d in data:
            args.append(str(d))
        print("MY CALLBACK: event={} data={}".format(eventstring.ljust(30), ", ".join(args)))
        # Now, do something interesting with these callbacks
        if eventstring == "on_stateupdate":
            #print("args=", args)
            #print("status=", args[0])
            self.app.grblStatus.set(args[0])
            self.app.tGuillotine.updateBtnState()
            mpos = args[1].replace("(" ,"").replace(")","").split(",")
            self.app.grblXG.set(mpos[0])
            self.app.grblYG.set(mpos[1])
            self.app.grblXD.set(mpos[2])
            self.app.grblYD.set(mpos[3])
            self.app.grblF.set(mpos[4])
            self.app.grblS.set(mpos[5])
        elif eventstring == "on_msg":
            self.queue.put("\n".join(args))
            
        elif eventstring == "on_log":
            if "Error" in ", ".join(args):
                #print("grbl will disconnect because it get an error")
                self.app.grblStatus.set("Connection lost")
                self.grbl.disconnect()
                self.app.tGuillotine.updateBtnState()     
        elif eventstring == "on_iface_error":
            #print("on_iface_error")
            self.queue.put("interface error\n")
            self.disconnectToGrbl()
            self.app.tGuillotine.updateBtnState()
             
        
