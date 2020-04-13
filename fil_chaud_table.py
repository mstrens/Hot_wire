import tkinter as tk
from tkinter import X, Y, BOTTOM, RIGHT, LEFT, HORIZONTAL , END , DISABLED , ttk
from tkinter import StringVar , Tk , W ,E , S , BOTH, HIDDEN, DoubleVar , Spinbox , IntVar , filedialog 

import time
import threading

import serial.tools.list_ports

from fil_chaud_validate import EntryFloat


class Table:
    def __init__(self,nb , app):
        self.nb = nb
        self.app = app
        self.frame = ttk.Frame(self.nb)
        self.levelBloc = 20
        self.levelCut = 30
        self.nb.add(self.frame, text='   Table   ')
        #reg_tableYY =  self.frame.register(self.validate_tableYY)            #enregistre la fonction de validation
        
        r = 0
        tk.Button(self.frame, text = 'Upload saved table', command=self.app.uploadTable, width = 25).grid(column=0, row=r, pady=10)
        r += 1
        tk.Button(self.frame, text = 'Save current table', command=self.app.saveTable, width = 25).grid(column=0, row=r, pady=10)
        r += 1
        tk.Label(self.frame, text="Table (name)").grid(column=0, row=r, pady=(20,2) )
        r += 1
        tk.Entry(self.frame, textvariable=self.app.tName , width='50').grid(column=0, columnspan=2 , row=r , padx=1,pady=(1,10), sticky=W)
               
        r += 1
        tk.Label(self.frame, text="Distance between axes (mm)").grid(column=0, row=r, pady=(1,1) , sticky=W)
        #tk.Entry(self.frame, textvariable=self.app.tableYY , width='5' , validate='focusout',
        #    validatecommand=(reg_tableYY) ).grid(column=1, row=r , padx=1,pady=(1,1))
        EntryFloat(self.frame, self.app.tableYY , 10 , 1600, self.levelBloc , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="Distance between table and").grid(column=0, row=r, pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="     left axis (mm)").grid(column=0, row=r, pady=(1,1), sticky=W)
        #tk.Entry(self.frame, textvariable=self.app.tableYG , width='5').grid(column=1, row=r , padx=1,pady=(1,1))
        EntryFloat(self.frame, self.app.tableYG , 1 , 500, self.levelBloc , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="     right axis (mm)").grid(column=0, row=r, pady=(1,1), sticky=W)
        #tk.Entry(self.frame, textvariable=self.app.tableYD , width='5').grid(column=1, row=r , padx=1,pady=(1,1))
        EntryFloat(self.frame, self.app.tableYD , 1 , 500, self.levelBloc , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="Max course (mm)").grid(column=0, row=r, pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="       Horizontal").grid(column=0, row=r, pady=(1,1), sticky=W)
        #tk.Entry(self.frame, textvariable=self.app.cMaxY , width='5').grid(column=1, row=r , padx=1,pady=(1,1))
        EntryFloat(self.frame, self.app.cMaxY , 1 , 1300, self.levelBloc , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="       Vertical").grid(column=0, row=r, pady=(1,1), sticky=W)
        #tk.Entry(self.frame, textvariable=self.app.cMaxZ , width='5').grid(column=1, row=r , padx=1,pady=(1,1))
        EntryFloat(self.frame, self.app.cMaxZ , 1 , 1200, self.levelBloc , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="Max speed (mm/sec)").grid(column=0, row=r, pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="            Horizontal").grid(column=0, row=r, pady=(1,1), sticky=W)
        #tk.Entry(self.frame, textvariable=self.app.vMaxY , width='5').grid(column=1, row=r , padx=1,pady=(1,1))
        EntryFloat(self.frame, self.app.vMaxY , 1 , 50, self.levelCut , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="            Vertical").grid(column=0, row=r, pady=(1,1), sticky=W)
        #reg_vMaxZ =  self.frame.register(self.validate_vMaxZ)         
        #tk.Entry(self.frame, textvariable=self.app.vMaxZ , width='5' ).grid(column=1, row=r , padx=1,pady=(1,1))
        EntryFloat(self.frame, self.app.vMaxZ , 1 , 500, self.levelCut , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="Max heating").grid(column=0, row=r, pady=(1,1), sticky=W)
        #reg_vMaxZ =  self.frame.register(self.validate_vMaxZ)         
        #tk.Entry(self.frame, textvariable=self.app.vMaxZ , width='5' ).grid(column=1, row=r , padx=1,pady=(1,1))
        EntryFloat(self.frame, self.app.tHeatingMax , 1 , 100, self.levelCut , width='6' ).grid(column=1, row=r , padx=1,pady=(1,1), sticky=W)
        
        r += 2
        tk.Label(self.frame, text=" Com Port").grid(column=0, row=r, pady=(20,1), sticky=W)
        self.comListBox = ttk.Combobox(self.frame,textvariable=self.app.tComPort , values=self.comGet(), state="readonly")
        self.comListBox.grid(column=1, row=r , padx=1,pady=(20,1), sticky=E)
        tk.Button(self.frame, text = 'Refresh Com list', command=self.refreshComList).grid(column=2, row=r, pady=(20,1), padx=20)
        r += 1
        tk.Label(self.frame, text=" Baudrate").grid(column=0, row=r, pady=(10,1), sticky=W)
        ttk.Combobox(self.frame,textvariable=self.app.tBaudrate , values=["9600" , "19200","38400" , "57600","115200"],
            state="readonly").grid(column=1, row=r , padx=1,pady=(10,1), sticky=E)
        r += 1
        tk.Label(self.frame, text="Selected Com is").grid(column=0, row=r, pady=(10,1), sticky=E)
        tk.Entry(self.frame, textvariable=self.app.connected , width='5' ).grid(column=1, row=r , padx=1,pady=(10,1), sticky=W)
        
        r = 3
        tk.Label(self.frame, text="Apply heating before move (sec)").grid(column=3, row=r, pady=(1,1), sticky=E)
        EntryFloat(self.frame, self.app.tPreHeat , 0 , 10, self.levelCut , width='6' ).grid(column=4, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Label(self.frame, text="Keep heating after move (sec)").grid(column=3, row=r, pady=(1,1), sticky=E)
        EntryFloat(self.frame, self.app.tPostHeat , 0 , 10, self.levelCut , width='6' ).grid(column=4, row=r , padx=1,pady=(1,1), sticky=W)
        
        r += 2
        tk.Label(self.frame, text="Gcode").grid(column=3, row=r, pady=(1,1))
        r += 1
        tk.Label(self.frame, text="   start with").grid(column=3, row=r, pady=(1,1), sticky=E)
        tk.Entry(self.frame, textvariable=self.app.gCodeStart1 , width='20').grid(column=4, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Entry(self.frame, textvariable=self.app.gCodeStart2 , width='20').grid(column=4, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Entry(self.frame, textvariable=self.app.gCodeStart3 , width='20').grid(column=4, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Entry(self.frame, textvariable=self.app.gCodeStart4 , width='20').grid(column=4, row=r , padx=1,pady=(1,1), sticky=W)
        
        r += 1
        tk.Label(self.frame, text="   end with").grid(column=3, row=r, pady=(1,1), sticky=E)
        tk.Entry(self.frame, textvariable=self.app.gCodeEnd1 , width='20').grid(column=4, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Entry(self.frame, textvariable=self.app.gCodeEnd2 , width='20').grid(column=4, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Entry(self.frame, textvariable=self.app.gCodeEnd3 , width='20').grid(column=4, row=r , padx=1,pady=(1,1), sticky=W)
        r += 1
        tk.Entry(self.frame, textvariable=self.app.gCodeEnd4 , width='20').grid(column=4, row=r , padx=1,pady=(1,1), sticky=W)
        r += 2
        tk.Label(self.frame, text="Axis letters").grid(column=3, row=r, pady=(1,1), sticky = E)
        tk.Entry(self.frame, textvariable=self.app.gCodeLetters , width='5').grid(column=4, row=r , padx=1,pady=(1,1), sticky=W)
        


    def comGet(self):
        comlist = serial.tools.list_ports.comports()
        connectedCom = []
        for element in comlist:
            connectedCom.append(element.device)
        #print("Connected COM ports: " + str(connectedCom))
        return connectedCom
    
    def refreshComList(self):
        newComList =  self.comGet()
        self.comListBox['values'] = newComList
        if self.app.tComPort.get() in newComList:
            pass
        else:
            self.app.tComPort.set("Select a Com Port")
    


    def connectedCom(self):
        if self.app.tComPort.get() in self.comGet():
            return True
        else:
            return False        
    
