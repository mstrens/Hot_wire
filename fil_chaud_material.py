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

class Material:
    def __init__(self,nb, app):
        self.nb = nb
        self.app = app
        self.frame = ttk.Frame(self.nb)
        self.levelCut = 30
        #self.frame2 = ttk.Frame(self.nb)
        self.nb.add(self.frame, text='   Material   ')
        r = 0
        tk.Button(self.frame, text = 'Upload saved material', command=self.app.uploadMaterial, width = 25).grid(column=0, row=r, pady=10)
        r += 1
        tk.Button(self.frame, text = 'Save current material', command=self.app.saveMaterial, width = 25).grid(column=0, row=r, pady=10)
        r += 1
        tk.Label(self.frame, text="Material (name)").grid(column=0, row=r, pady=(20,2) )
        r += 1
        tk.Entry(self.frame, textvariable=self.app.mName , width='50').grid(column=0, columnspan=2 , row=r , padx=1,pady=(1,10), sticky=W)
        r += 1
        tk.Label(self.frame, text="High speed for this material (mm/sec)").grid(column=0, row=r, pady=(20,2), sticky=W)
        #tk.Entry(self.frame, textvariable=self.app.mSpeedHigh , width='6').grid(column=1, row=r , padx=1,pady=(20,1), sticky=W)
        EntryFloat(self.frame, self.app.mSpeedHigh , 0.1 , 20, self.levelCut , width='6' ).grid(column=1, row=r , padx=1,pady=(20,1), sticky=W)
    
        r += 1
        tk.Label(self.frame, text="      Heating at high speed (%)").grid(column=0, row=r, pady=(10,2), sticky=W)
        #tk.Entry(self.frame, textvariable=self.app.mHeatSpHigh , width='6').grid(column=1, row=r , padx=1,pady=(10,1), sticky=W)
        EntryFloat(self.frame, self.app.mHeatSpHigh , 1 , 100, self.levelCut , width='6' ).grid(column=1, row=r , padx=1,pady=(10,1), sticky=W)
    
        r += 1
        tk.Label(self.frame, text="      Radiance at high speed (mm)").grid(column=0, row=r, pady=(10,2), sticky=W)
        #tk.Entry(self.frame, textvariable=self.app.mRadSpHigh , width='6').grid(column=1, row=r , padx=1,pady=(10,1), sticky=W)
        EntryFloat(self.frame, self.app.mRadSpHigh , 0.1 , 3, self.levelCut , width='6' ).grid(column=1, row=r , padx=1,pady=(10,1), sticky=W)
    
        r += 1
        tk.Label(self.frame, text="Low speed (mm/sec)").grid(column=0, row=r, pady=(20,2), sticky=W)
        #tk.Entry(self.frame, textvariable=self.app.mSpeedLow , width='6').grid(column=1, row=r , padx=1,pady=(20,1), sticky=W)
        EntryFloat(self.frame, self.app.mSpeedLow , 0.1 , 10, self.levelCut , width='6' ).grid(column=1, row=r , padx=1,pady=(20,1), sticky=W)
    
        r += 1
        tk.Label(self.frame, text="      Heating at low speed (%)").grid(column=0, row=r, pady=(10,2), sticky=W)
        #tk.Entry(self.frame, textvariable=self.app.mHeatSpLow , width='6').grid(column=1, row=r , padx=1,pady=(10,1), sticky=W)
        EntryFloat(self.frame, self.app.mHeatSpLow , 1 , 100, self.levelCut , width='6' ).grid(column=1, row=r , padx=1,pady=(10,1), sticky=W)
    
        r += 1
        tk.Label(self.frame, text="Half speed (= high/2) ").grid(column=0, row=r, pady=(20,2), sticky=W)
        tk.Entry(self.frame, textvariable=self.app.mSpeedHalf , width='6', state='disabled').grid(column=1, row=r , padx=1,pady=(20,1), sticky=W)
        
        r += 1
        tk.Label(self.frame, text="      Radiance at high speed / 2 (mm)").grid(column=0, row=r, pady=(20,2), sticky=W)
        #tk.Entry(self.frame, textvariable=self.app.mRadSpHalf , width='6').grid(column=1, row=r , padx=1,pady=(20,1), sticky=W)
        EntryFloat(self.frame, self.app.mRadSpHalf , 0.1 , 3, self.levelCut , width='6' ).grid(column=1, row=r , padx=1,pady=(20,1), sticky=W)
    
        r += 1
        tk.Label(self.frame, text="Usual cutting speed (mm/sec)").grid(column=0, row=r, pady=(20,1), sticky=W)
        EntryFloat(self.frame, self.app.vCut, 0.1, 10, self.levelCut , width='6').grid(column=1, row=r , padx=1,pady=(20,1), sticky=W)
        
"""
       self.mSpeedHigh =  DoubleVar(value='10.0')          #speed max
        self.mSpeedLow =  DoubleVar(value='10.0')          #speed min
        self.mRadSpHigh =  DoubleVar(value='1.0')          #Radiance at high max
        self.mRadSpHalf =  DoubleVar(value='1.0')          #Radiance at half speed
        self.mHeatSpHigh =  DoubleVar(value='90.0')          #Heat at High speed
        self.mHeatSpLow =  DoubleVar(value='90.0')          #Heat at low speed
"""