import tkinter as tk
import re

# with this class, the function validateAll is called when the entered value is valid 
class EntryFloat(tk.Entry) :
    def __init__(self, parent, variable, min , max , level, **dargs) :
        self.variable = variable
        self.min = min
        self.max = max
        self.level = level
        super().__init__(parent,
                         dargs,
                         validate='focusout',
                         textvariable=self.variable
                         )
        self._validerCmd = self.register(self.verifier)
        self['validatecommand'] = (self._validerCmd, '%P')
 
    def verifier(self, val ) :
        import fil_chaud_config 
        #print("val=", val)
        try:  
            v = float(val)
            if v >= self.min and v <= self.max:
                #print("v is in range")
                self['bg'] = 'SystemWindow'  #apply normal background
                #print("background is normal")
                return fil_chaud_config.monApp.validateAll(self.level) 
        except :          
            pass
        self['bg'] = 'red'
        #print("value is wrong")
        #print("background is done")
        self.focus_set()
        #print("focus is set")
        return True

"""
# with this class, the function validateAll is NOT called when the entered value is valid
class EntryFloatSpVal(tk.Entry) :
    def __init__(self, parent, variable, min , max , **dargs) :
        self.variable = variable
        self.min = min
        self.max = max
        super().__init__(parent,
                         dargs,
                         validate='focusout',
                         textvariable=variable
                         )
        self._validerCmd = self.register(self.verifier)
        self['validatecommand'] = (self._validerCmd, '%P')
 
    def verifier(self, val ) :
        import fil_chaud_config 
        try:  
            v = float(val)
            if v >= self.min and v <= self.max:
                self['bg'] = 'SystemWindow'  #apply normal background
                return True
                # return fil_chaud_config.monApp.validateAll() 
        except :          
            pass
        self['bg'] = 'red'
        self.focus_set()
        return True

"""