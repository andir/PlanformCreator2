#!/usr/bin/env pythonbutton_color
# -*- coding: utf-8 -*-

"""  

Additional generic (compound) widgets based on original CTK widgets

"""
import os
import customtkinter as ctk
import tkinter as tk
from PIL import Image
from typing import Union, Callable

# some additional color definitions 
cl_edit             = "gray35"                    # background of entry fields
cl_spin             = "gray25"                    # background of spin buttons
cl_text             = "#DCE4EE"
cl_text_disabled    = "gray70"
cl_userHint         = "#E0A721"
cl_button_primary   = ctk.ThemeManager.theme["CTkButton"]["fg_color"] # default Button darker  
cl_button_secondary = ctk.ThemeManager.theme["CTkOptionMenu"]["button_color"] # default Button darker  
fs_header           = 18                          # font size header 
def_height          = 25                          # base height in px
def_width           = 105                         # base width in px for entry fields
def_lab_width       = 95                          # ... for labels of enty fields

class AccessPath():
    """
    Work in Progress! - Base class of an access path

    Returns:
            _description_
     """
    def __init__ (self, get=None, set=None, dataType = None):

        if not callable (get):
            self._fixedVal = get
            self._getter = None
        else: 
            self._fixedVal = None
            self.getter = get
        self._setter = set

        # get data type of access path 
        if not dataType is None: 
            self._dataType = dataType
        else: 
            if not self._fixedVal is None:  checkVal = self._fixedVal                  # a input val overwrites the setter altwernative
            else:                           checkVal = self._eval () 
            if checkVal is None: checkVal = ""

            if isinstance (checkVal, bool):                       # supported data types
                self._dataType = bool
            elif isinstance  (checkVal, float):    
                self._dataType = float
            elif isinstance (checkVal, int):
                self._dataType = int
            elif isinstance (checkVal, str):
                self._dataType = str
            else:
                raise ValueError ("This type is not supported in Widgets: ", checkVal)


    def eval (self):
        return self._eval()


    def eval_set (self, aVal):
        self._eval_set(aVal)

    def isMethod(self): 
        return (self._valFixed is None) and (not self.getter is None)

    def _eval (self):
        
        if self._fixedVal is None:  
            if callable (self._getter): 
                return self._getter()
            else: 
                raise ValueError ("getter is not a bound method: %s" %self._getter)
        else: 
            return self._fixedVal 

    def _eval_set (self, aVal):
        
        if callable (self._setter): 
            self._setter(aVal)
        else: 
            raise ValueError ("getter is not a bound method: %s" %self._getter)






class Base_Widget2():
    #
    # Work in Progress - new Implementation
    #
    """Base class of all compound widget 

    Arguments:
        parent --   parent frame self should belong to (CTkFrame) 
        row --      row in grid of parent :)
        col --      column in grid of parent :)

    Keyword Arguments:
        val --      value to show - overwrites a setter path :)
        lab --      label of an entry field, or text on button, header :)
        obj --      object getter and setter belong to :) 
        get --      either string path or callable method to get the value to show :)
        set --      either string path or callable method to invoke after a value is entered by user  :)
        disable --  either string path or callable method to disbale/enable widget  :)
        event --    tkinter virtual event like '<<MY_ALARM>>' :)
        lim  --     upper and lower numerical limit values for entry fields  :)
        dec --      decimals in numeric entry fields :)
        unit --     unit of entry fields like 'mm' :)
        step --     step size for spin button  :)
        options --  Option_Widget: list of string values or access path being options to select 

    """
  
    ctk_root : ctk.CTk = None             # holds eventhandler - has to be set in the very beginnging"

    def __init__(self, parent: ctk.CTkFrame, row:int, column:int, 
                 val = None, lab:str=None, obj=None, 
                 get =None, set =None, disable = False, 
                 event: str= None,
                 lim:tuple=None, dec: int = 1, unit : str = None, 
                 spin: bool = False, step: float = 0.1,
                 options: list = None,
                 width:int=None, height:int=None):

        self.parent = parent
        self.row    = row
        self.column = column

        self._decimals = dec
        if not self._decimals is None: 
            dataType = float
        else:
            dataType = None

        if val is None: 
            self._ap_value = AccessPath (get=val, set=set, dataType=dataType)
        else:
            self._ap_value = AccessPath (get=get, set=set, dataType=dataType)

        self._ap_disable = AccessPath (get=disable, dataType=bool)
        self._ap_label   = AccessPath (get=lab)
        self._ap_options = AccessPath (get=options, dataType=list)
        self._ap_limits  = AccessPath (get=lim, dataType=tuple)
        self.unit     = unit

        if not spin is None: self.spinner  = spin
        self.step     = step

        self.event    = event

        self.width    = width
        self.height   = height
        if not self.width:  self.width  = def_width
        if not self.height: self.height = def_height

        self.whileSetting = False                       # avoid circular actions with refresh()

        self.mainCTk  = None                        # in a compound widget this is the important one
        self.subCTk   = None                        # the small add/sub buttons
        self.addCTk   = None   
        self.labelCtk = None 

    def refresh (self):
        """refesh self by re-reading the 'getter' path 
        """
        if not self.whileSetting:               # avoid circular actions with refresh()
            # only access path with method makes sense to refesh 
            if self._ap_value.isMethod:   self.set_CTkControl ()
            if self._ap_label.isMethod:   self.set_CTkControl_label ()
            if self._ap_disable.isMethod: self.set_CTkControl_state ()

    def set_value(self):
        """write the current value of the widget to object via getter path
        """
        self.whileSetting = True                # ??? avoid circular actions with refresh()
        self._ap_value.eval_set (self.val)
        self.whileSetting = False


    #---  from / to CTkControl - inside the widget 

    def set_CTkControl (self):
        """sets val into the final CTk control 
        """
        newVal  = self._ap_value.eval() 
        dataType = self._ap_value.dataType
        limits = self._ap_limits.eval()
        decimals = self._decimals 

        self.val_asString = self.str_basedOnVal (newVal, dataType, limits, decimals)
        # to overwrite by sub class for CTk specific setting
        self._set_CTkControl       (self.mainCTk, self.val_asString)


    def _set_CTkControl (self, widgetCTk, newValStr: str):
        """sets val into the final CTk control 
        """
        # to overwrite by sub class 
        pass

    def set_CTkControl_label (self):
        """sets the label text into the final CTk control 
        """
        # to overwrite by sub class for CTk specific setting
        self._set_CTkControl_label       (self.mainCTk, self._ap_label.eval())

    def _set_CTkControl_label (self, widgetCTk, newLabelStr: str):
        """sets val into the final CTk control 
        """
        # to overwrite by sub class which supports labels
        pass

    def set_CTkControl_state (self):
        """sets disable bool into the final CTk control 
        """
        self._set_CTkControl_state (self.mainCTk, self._ap_disable.eval())


    def _set_CTkControl_state (self, widgetCTk, disable: bool):
        """sets the disabled / normal state in CTk control 
        """
        curCTk_state = widgetCTk.cget("state")
        if disable: 
            if curCTk_state == "normal":
                widgetCTk.configure (state ="disabled" )         # "normal" (standard) or "disabled" (not clickable, darker color)
        else: 
            if curCTk_state == "disabled":
                widgetCTk.configure (state ="normal" )           # "normal" (standard) or "disabled" (not clickable, darker color)

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


    def CTk_callback (self, dummy=None):
        """will be called by CTk control when user hit a button or pressed enter 
        """
        # now get it from CTK 
        newStr = self._getFrom_CTkControl()

        if newStr is None:                                      # this was a button
            setAndFire = True
            self.val = None
        else: 
            newVal = self.val_basedOnStr (self.val, self.valType, newStr, self.limits)
            if (newVal != self.val):                            # defensive to set in model ...
                self.val  = newVal                              # store new value
                setAndFire = True
            else:
                setAndFire = False

        if setAndFire:
            if not self.setter is None: self.set_value()        # write val back to object
            if not self.event  is None: self.fireEvent()
        
        # update entry field if there was a re-formatting e.g. digits
        self.set_CTkControl()



    def str_basedOnVal (self, val, valType, limits, decimals):
        """converts val to a string for ctk entry based on type of val 
        """
        if   val is None:
            s = "" 
        elif valType == bool:
            if val: s = "1" 
            else:   s = "0"
        elif valType == str:  
            s = val
        elif valType == int:
            if limits: 
                minVal, maxVal = limits
                val2 = max (int(minVal), int(val))
                val  = min (int(maxVal), val2)
            s = str(val)
        elif valType == float:
            if limits: 
                minVal, maxVal = limits
                val2 = max (float(minVal), float(val))
                val  = min (float(maxVal), val2)
            s = "%0.*f" %(decimals,val)
        else:
            s = '???'
        return s



class Messagebox(ctk.CTkToplevel):
    """ Message in different styles - inspired vom CTKMessagebox"""

    
    def __init__(self, master, 
                 width: int = 400,
                 height: int = 200,
                 title: str = "Messagebox",
                 message: str = "This is a Messagebox!",
                 option_1: str = "Ok",
                 option_2: str = None,
                 option_3: str = None,
                 border_width: int = 1,
                 button_color: str = "default",
                 button_width: int = None,
                 icon: str = "info",             #  "check", "cancel", "info", "question", "warning"
                 font: tuple = None):
        
        import sys
    
        super().__init__(master)

        self.master_window = master

        self.width   = 250 if width<250 else width
        self.height  = 150 if height<150 else  height
        self.spawn_x = int(self.master_window.winfo_width() * .5 + self.master_window.winfo_x() - .5 * self.width + 7)
        self.spawn_y = int(self.master_window.winfo_height() * .5 + self.master_window.winfo_y() - .5 * self.height + 20)
        self.geometry(f"{self.width}x{self.height}+{self.spawn_x}+{self.spawn_y}")

        self.title(title)
        self.protocol("WM_DELETE_WINDOW", self.button_event)
        self.resizable(width=False, height=False)
        self.transient(master)

        self.focus_force()
        self.grab_set()
        self.after(10)


        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)   
        self.x = self.winfo_x()
        self.y = self.winfo_y()
        self._title = title
        self.message = message
        self.font = font
        self.button_width = button_width if button_width else 80 
        self.border_width = border_width if border_width<6 else 5
        

        if button_color=="default":
            self.button_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"])
            # jxjo second and third button in a darker color 
            self.button2_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkOptionMenu"]["button_color"])
        else:
            self.button_color = button_color
            self.button2_color = self.button_color
                    
        if icon in ["check", "cancel", "info", "question", "warning"]:
            self.icon = ctk.CTkImage(Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icons', icon+'.png')),
                                               size=(25, 25))
        else:
            self.icon = ctk.CTkImage(Image.open(icon), size=(25, 25)) if icon else None

        # ---------------

        self.bg_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        self.fg_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"])

        self.frame_middle = ctk.CTkFrame(self, bg_color=self.bg_color, fg_color=self.fg_color)
        self.frame_middle.grid(row=0, column=0, columnspan=3, sticky="nwes", padx=(0,0), pady=(0,0))
        self.frame_middle.grid_rowconfigure   (0, weight=1)
        self.frame_middle.grid_columnconfigure(0, weight=1)
        self.frame_middle.grid_columnconfigure(1, weight=6)
        self.frame_middle.grid_columnconfigure(2, weight=1)

        self.message_icon = ctk.CTkButton(self.frame_middle,  width=1, height=100, corner_radius=0, text=None, font=self.font,
                                            fg_color="transparent", hover=False,  image=self.icon)
        self.message_text = ctk.CTkButton(self.frame_middle,  width=1, height=100, corner_radius=0, text=self.message, font=self.font,
                                            fg_color="transparent", hover=False,  image=None)
        self.message_text._text_label.configure(wraplength=self.width *0.8, justify="center")
        self.message_icon.grid(row=0, column=0, columnspan=1, sticky="nes")
        self.message_text.grid(row=0, column=1, columnspan=2, sticky="nwes")
        

        # ---------------
        self.frame_bottom = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_bottom.grid(row=1, column=0, columnspan=3, sticky="nwes", padx=(0,0))
        self.frame_bottom.grid_columnconfigure((0,4), weight=1)

        self.option_text_1 = option_1
        self.button_1 = ctk.CTkButton(self.frame_bottom, text=self.option_text_1, fg_color=self.button_color,
                                                width=self.button_width, height=25, font=self.font, 
                                                command=lambda: self.button_event(self.option_text_1))
        self.button_1.grid(row=0, column=1, sticky="e", padx=(30,10), pady=10)

        if option_2:
            self.option_text_2 = option_2      
            self.button_2 = ctk.CTkButton(self.frame_bottom, text=self.option_text_2, fg_color=self.button2_color,
                                                    width=self.button_width, height=25, font=self.font, 
                                                    command=lambda: self.button_event(self.option_text_2))
            self.button_2.grid(row=0, column=2, sticky="e", padx=10, pady=10)
            
        if option_3:
            self.option_text_3 = option_3
            self.button_3 = ctk.CTkButton(self.frame_bottom, text=self.option_text_3, fg_color=self.button2_color,
                                                    width=self.button_width, height=25, font=self.font, 
                                                    command=lambda: self.button_event(self.option_text_3))
            self.button_3.grid(row=0, column=3, sticky="e", padx=(10,0), pady=10)
        

            
    def get(self):
        self.master.wait_window(self)
        return self.event
                    
    def button_event(self, event=None):
        self.grab_release()
        self.destroy()
        self.event = event




class Base_Widget():
    """Base class of all compound widget 

    Arguments:
        parent --   parent frame self should belong to (CTkFrame) 
        row --      row in grid of parent :)
        col --      column in grid of parent :)

    Keyword Arguments:
        val --      value to show - overwrites a setter path :)
        lab --      label of an entry field, or text on button, header :)
        obj --      object getter and setter belong to :) 
        get --      either string path or callable method to get the value to show :)
        set --      either string path or callable method to invoke after a value is entered by user  :)
        disable --  either string path or callable method to disbale/enable widget  :)
        event --    tkinter virtual event like '<<MY_ALARM>>' :)
        lim  --     upper and lower numerical limit values for entry fields  :)
        dec --      decimals in numeric entry fields :)
        unit --     unit of entry fields like 'mm' :)
        step --     step size for spin button  :)
        options --  Option_Widget: list of string values or access path being options to select 

    """
  
    ctk_root : ctk.CTk = None             # holds eventhandler - has to be set in the very beginnging"

    def __init__(self, parent: ctk.CTkFrame, row:int, column:int, 
                 val = None, lab:str=None, obj=None, 
                 get =None, set =None, disable = False, 
                 event: str= None,
                 lim:tuple=None, dec = None, unit : str = None, 
                 spin: bool = False, step: float = 0.1,
                 options: list = None,
                 width:int=None, height:int=None):

        self.parent = parent
        self.row    = row
        self.column = column

        self.getter = get
        self.setter = set
        self.obj    = obj                 
        if not val is None:  self.val = val                  # a input val overwrites the setter altwernative
        else:                self.val = self.get_value (get, obj, parent) 
        if self.val is None: self.val = ""

        if isinstance (self.val, bool):                       # supported data types
           self.valType = bool
        elif isinstance  (self.val, float) or (spin and (not dec is None) and (dec > 0)):    
           self.valType = float
        elif isinstance (self.val, int) or (spin and (not dec is None) and (dec == 0)):
           self.valType = int
        elif isinstance (self.val, str):
           self.valType = str
        else:
           raise ValueError ("This type is not supported in Widgets", self.val)
 

        if (isinstance(disable, bool)):
            self.disGetter = None
            self.disabled = disable
        else: 
            self.disGetter = disable
            self.disabled = self.get_value (disable, obj, parent)

        if (isinstance(lab, str)) or lab is None:
            self.label    = lab
            self.labGetter = None
        else:
            self.labGetter = lab
            self.label    = self.get_value (lab, obj, parent)

        if (isinstance(options, list)) or options is None:
            self.options  = options
            self.optionsGetter = None
        else: 
            self.optionsGetter = options
            self.options  = self.get_value (options, obj, parent)

        if (isinstance(lim, tuple)) or lim is None:
            self.limits    = lim
            self.limGetter = None
        else:
            self.limGetter = lim
            self.limits    = self.get_value (lim, obj, parent)

        self.decimals = dec
        self.unit     = unit
        if not spin is None: self.spinner  = spin
        self.step     = step
        self.event    = event

        self.width    = width
        self.height   = height
        if not self.width:  self.width  = def_width
        if not self.height: self.height = def_height

        self.whileSetting = False                       # avoid circular actions with refresh()

        self.mainCTk  = None                        # in a compound widget this is the important one
        self.subCTk   = None                        # the small add/sub buttons
        self.addCTk   = None    

    #---  public methods 

    def refresh (self):
        """refesh self by re-reading the 'getter' path 
        """
        if self.whileSetting:                           # avoid circular actions with refresh()
            pass # print(" - refresh while setting in ", self)
 
        if self.limGetter:
            self.limits     = self.get_value(self.limGetter, self.obj, self.parent)
        if self.getter:
            self.val        = self.get_value(self.getter, self.obj, self.parent)
            self.set_CTkControl ()
        if self.labGetter:
            self.label      = self.get_value (self.labGetter, self.obj, self.parent)  
            self.set_CTkControl_label ()                     
        if self.disGetter:
            self.disabled   = self.get_value (self.disGetter, self.obj, self.parent)  
            self.set_CTkControl_state ()                    # disable / enable

              
    #---  from / to outside - owner or object of the widget 
 
    def get_value(self, getter, obj, parent):
        """read the initial value from object via getter path
        """
        if not obj and not parent: raise ValueError ("Object for getter path is missing")
        if not getter: 
            return None                 # could be a button
        if callable(getter):                       # getter is a method ?
            return getter()                
        else:                                           # ... no - getter is a String
            if obj:
                if callable(obj):                       # obj getter is a method ?
                    dataObject = obj()
                else:
                    dataObject = obj
                propOrMethod =  getattr (dataObject, getter)
            else:                                       # if no obj-argument, try it with parent (self...)
                propOrMethod =  getattr (parent, getter)
            if (not callable(propOrMethod)):
                return propOrMethod                    # access path showed to a property
            else: 
                return propOrMethod()                  # access path showed to a method


    def set_value(self):
        """write the current value of the widget to object via getter path
        """
        if not self.obj and not self.parent: raise ValueError ("Object for setter path is missing")
        if not self.setter: raise ValueError ("Getter path is missing")

        myVal = self.val 

        self.whileSetting = True                # avoid circular actions with refresh()
        if callable(self.setter):               # getter is a method ?
            if self.val is None: 
                self.setter()                   # typically a button method which has bo arg
            else:
                self.setter(myVal)              # a method like: def myMth(self, newVal) 
        else:                                   # ... no - getter is a String of a function for 'obj'
            if self.obj:
                if callable(self.obj):                       # obj getter is a method ?
                    dataObject = self.obj()
                else:
                    dataObject = self.obj
                propOrMethod =  getattr (dataObject, self.setter)
            else:                               # if no obj-argument, try it with parent (self...)
                propOrMethod =  getattr (self.parent, self.setter)
            if (not callable(propOrMethod)):
                propOrMethod = myVal            # access path showed to a property
            else: 
                 propOrMethod(myVal)            # access path showed to a method
        self.whileSetting = False               # avoid circular actions with refresh()



    #---  from / to CTkControl - inside the widget 

    def set_CTkControl (self):
        """sets val into the final CTk control 
        """
        self.val_asString = self.str_basedOnVal (self.val, self.valType, self.limits, self.decimals)
        # to overwrite by sub class for CTk specific setting
        self._set_CTkControl       (self.mainCTk, self.val_asString)

    def _set_CTkControl (self, widgetCTk, newValStr: str):
        """sets val into the final CTk control 
        """
        # to overwrite by sub class 
        pass


    def set_CTkControl_label (self):
        """sets the label text into the final CTk control 
        """
        # to overwrite by sub class for CTk specific setting
        self._set_CTkControl_label       (self.mainCTk, self.label)

    def _set_CTkControl_label (self, widgetCTk, newLabelStr: str):
        """sets val into the final CTk control 
        """
        # to overwrite by sub class which supports labels
        pass


    def set_CTkControl_state (self):
        """sets disable bool into the final CTk control 
        """
        self._set_CTkControl_state (self.mainCTk, self.disabled)

    def _set_CTkControl_state (self, widgetCTk, disable: bool):
        """sets the disabled / normal state in CTk control 
        """
        curCTk_state = widgetCTk.cget("state")
        if disable: 
            if curCTk_state == "normal":
                widgetCTk.configure (state ="disabled" )         # "normal" (standard) or "disabled" (not clickable, darker color)
        else: 
            if curCTk_state == "disabled":
                widgetCTk.configure (state ="normal" )           # "normal" (standard) or "disabled" (not clickable, darker color)

    def CTk_callback (self, dummy=None):
        """will be called by CTk control when user hit a button or pressed enter 
        """
        # now get it from CTK 
        newStr = self._getFrom_CTkControl()

        if newStr is None:                                      # this was a button
            setAndFire = True
            self.val = None
        else: 
            newVal = self.val_basedOnStr (self.val, self.valType, newStr, self.limits)
            if (newVal != self.val):                            # defensive to set in model ...
                self.val  = newVal                              # store new value
                setAndFire = True
            else:
                setAndFire = False

        if setAndFire:
            if not self.setter is None: self.set_value()        # write val back to object
            if not self.event  is None: self.fireEvent()
        
        # update entry field if there was a re-formatting e.g. digits
        self.set_CTkControl()


    def _getFrom_CTkControl (self):
        """returns the current value in CTk control as String  
        """
        # must be over written by specific widget 
        # raise RuntimeError ("getFrom_CTkControl not implemented by", self)
        return None
    
                    
    def str_basedOnVal (self, val, valType, limits, decimals):
        """converts val to a string for ctk entry based on type of val 
        """
        if   val is None or val =="" :
            s = "" 
        elif valType == bool:
            if val: s = "1" 
            else:   s = "0"
        elif valType == str:  
            s = val
        elif valType == int:
            if limits: 
                minVal, maxVal = limits
                val2 = max (int(minVal), int(val))
                val  = min (int(maxVal), val2)
            s = str(val)
        elif valType == float:
            if limits: 
                minVal, maxVal = limits
                val2 = max (float(minVal), float(val))
                val  = min (float(maxVal), val2)
            s = "%0.*f" %(decimals,val)
        else:
            s = '???'
        return s

    def val_basedOnStr (self, val, valType, newStr, limits=None):
        """converts string (from entry field) in the type val normally has 
        """

        if valType == int:
            try:
                newVal = int(float(newStr))
            except:                             # user enetered a non int
                newVal = int(val) 
            if limits: 
                minVal, maxVal = limits
                newVal2 = max (int(minVal), newVal)
                newVal  = min (int(maxVal), newVal2)
        elif valType == float:
            try:
                newVal = float(newStr)
            except:                             # user enetered a non float
                newVal = float(val) 
            if limits: 
                minVal, maxVal = limits
                newVal2 = max (float(minVal), newVal)
                newVal  = min (float(maxVal), newVal2)
        elif valType == bool: 
                newVal = (newStr == "1" or newStr == 1)        # Ctk returns int (?) 
        else: 
                newVal = newStr
        return newVal

    def fireEvent(self):
        if self.ctk_root and self.event:
            # print ("fire ", self.event, ' from ', self.__class__.__name__)
            self.ctk_root.event_generate (self.event) 



#-----------  real widget subclasses ----------------------------



class Blank_Widget(Base_Widget):
    """Creates a non visible blank frame as a placeholder in grid
                                                        
        Blank_Widget (self, 0,0) :)
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
            
        # self.mainCTk = ctk.CTkFrame (self.parent, width=self.width, height=self.height, fg_color="blue")     # dummy frame
        self.mainCTk = ctk.CTkFrame (self.parent, width=self.width, height=self.height, fg_color="transparent")     # dummy frame
        self.mainCTk.grid(row=self.row, column=self.column,  pady=1, padx=1, sticky="w")



class Header_Widget(Base_Widget):
    """Header label  - uses one columns in the grid
                                                        
        Header_Widget (self, 0,0, lab='Header from val') :)
        Header_Widget (self, 0,2, lab=self.localString) :)
    """
    def __init__(self, *args, columnspan = 1, pady=None, **kwargs):
        super().__init__(*args, **kwargs)
            
        if pady is None: pady = (10,15)
        self.mainCTk = ctk.CTkLabel (self.parent, width=def_lab_width+5, text=self.label, anchor= "w", font= ("", fs_header))
        self.mainCTk.grid(row=self.row, column=self.column,  columnspan= columnspan, pady=pady, padx=10, sticky="w")

    def _set_CTkControl_label (self, widgetCTk, newLabelStr: str):
        widgetCTk.configure (text=newLabelStr)



class Label_Widget(Base_Widget):
    """a subtle label text with word wrap - spans 5 columns
                                                        
        Label_Widget  (self, 3,0, lab='Loremm ipsumm') :)
        Label_Widget  (self, 3,0, width=200, lab=self.myLabeText) :)
    """
    def __init__(self, *args, padx=10, sticky = None, columnspan=None, text_color=None, **kwargs):
        super().__init__(*args, **kwargs)

        if sticky       is None: sticky = "sw"
        if columnspan   is None: columnspan = 6
        if text_color   is None: 
            text_color = cl_text_disabled
        elif text_color == 'hint':
            text_color = cl_userHint

        self.mainCTk = ctk.CTkLabel(self.parent, width=self.width, justify ='left', 
                                    text=self.label, anchor= "w", text_color=text_color)           
        self.mainCTk.grid(row=self.row, column=self.column,  columnspan=columnspan, padx=padx, sticky=sticky)

    def _set_CTkControl_label (self, widgetCTk, newLabelStr: str):
        widgetCTk.configure (text=newLabelStr)



class Button_Widget(Base_Widget):
    """CTKButton - uses one column in the grid

    Keyword Arguments:
        val or obj+getter -- val string to show or access path with obj and getter          :)
        set -- access path setter when button is pressed             :)
    """
    def __init__(self, *args, sticky= None, pady= None, columnspan = 1, primary=False, **kwargs):
        super().__init__(*args, **kwargs)

        if sticky is None: sticky = 'w'
        if pady   is None: pady = 0
        if primary: 
            self.fg_color = cl_button_primary
        else:
            self.fg_color = cl_button_secondary

        self.mainCTk = ctk.CTkButton(self.parent, text=self.label, height=self.height, width=self.width, 
                                     command=self.CTk_callback)
        self.mainCTk.grid(row=self.row, column=self.column, columnspan=columnspan, padx=(10,10), pady=pady, sticky=sticky)
     
        self.set_CTkControl_state ()        # state explicit as no value is set_value in button

    def _getFrom_CTkControl (self):
        return None                     # button has nothing to give ...

    def _set_CTkControl_label (self, widgetCTk, newLabelStr: str):
        widgetCTk.configure (text=newLabelStr)

    def CTk_callback(self, dummy=None):
        # overwritten because of flicker of CTkButton
        # no call back when disabled 
        if not self.disabled: return super().CTk_callback(dummy)

    def _set_CTkControl_state (self, widgetCTk, disable: bool):
        """sets the disabled / normal state in CTk control 
        """
        # overwritten because of flicker of CTkButton
        if disable: 
            widgetCTk.configure (text_color =cl_text_disabled )
            widgetCTk.configure (fg_color =cl_spin )
        else: 
            widgetCTk.configure (text_color = cl_text)
            widgetCTk.configure (fg_color =self.fg_color )



    def refresh(self):
        return super().refresh()

class Switch_Widget(Base_Widget):
    """CTKSwitch - uses one column in the grid

    Keyword Arguments:
        val or obj+getter -- val string to show or access path with obj and getter          :)
        set -- access path setter when switched              :)
    """
    def __init__(self, *args, padx=None, pady=None, columnspan=None, **kwargs):
        super().__init__(*args, **kwargs)

        if padx is None: padx = 20
        if pady is None: pady = 0
        if columnspan is None: columnspan = 1

        self.mainCTk = ctk.CTkSwitch(self.parent, text=self.label, onvalue=1, command=self.CTk_callback)
        self.mainCTk.grid(row=self.row, column=self.column, columnspan=columnspan, padx=padx, pady=pady, sticky="w")

        self.set_CTkControl()
        self.set_CTkControl_state()

    def _getFrom_CTkControl (self):
        return self.mainCTk.get()

    def _set_CTkControl (self,  widgetCTk, newValStr: str):
        if newValStr == "1":  widgetCTk.select()
        else:                 widgetCTk.deselect()

    def _set_CTkControl_label (self, widgetCTk, newLabelStr: str):
        widgetCTk.configure (text=newLabelStr)


class CheckBox_Widget(Base_Widget):
    """CTKCheckBox - uses one column in the grid

    Keyword Arguments:
        val or obj+getter -- val string to show or access path with obj and getter          :)
        set -- access path setter when switched              :)
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        height = def_height - 10

        self.mainCTk = ctk.CTkCheckBox (self.parent, text=self.label, onvalue=1, command=self.CTk_callback)
        self.mainCTk.grid(row=self.row, column=self.column, padx=10, pady = 3, sticky="w")

        self.set_CTkControl()
        self.set_CTkControl_state()

    def _getFrom_CTkControl (self):
        return self.mainCTk.get()

    def _set_CTkControl (self,  widgetCTk, newValStr: str):
        if newValStr == "1":  widgetCTk.select()
        else:                 widgetCTk.deselect()

    def _set_CTkControl_label (self, widgetCTk, newLabelStr: str):
        widgetCTk.configure (text=newLabelStr)




class Field_Widget(Base_Widget):
    """ Compund widget existing out of 
        column i    : Field label - optional (CTkLabel)
        column i+1  : Entry Field (CTkEntry) or compound spin entry 
        column i+2  : Unit label - optional (CTkLabel)

    Additional:
        spin -- Boolean if entry field should have a spinner       :)
        step -- integer step size              :)
    """
    def __init__(self, *args, lab_width= None, columnspan=None, **kwargs):
        super().__init__(*args, **kwargs)

        column = self.column
        if columnspan is None:  columnspan = 1
        if (self.label):  
            if lab_width:
                width = lab_width
            else:
                width= def_lab_width
            label_ctk = ctk.CTkLabel (self.parent, width= width, text=self.label,  
                                      justify='left', anchor='w')
            label_ctk.grid (row=self.row, column=column, padx=(5, 5), pady=1, sticky='w')
            column += 1

        if self.spinner:
            # this new frame with 3 widget replaces the normal entry field in grid  
            entry_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
            button_width  = self.height  - 2
            button_height = self.height
            entry_width = self.width - 2 * button_width - 2
        else: 
            entry_frame = self.parent
            entry_width  = self.width

        self.mainCTk = ctk.CTkEntry (entry_frame, width=entry_width, height=self.height, border_width=1,
                                   justify='right', fg_color=cl_edit)

        if self.spinner:
            self.subCTk = ctk.CTkButton(entry_frame, text="-", command=self.sub_button_callback,
                                        width=button_width, height=button_height, fg_color=cl_spin)
            self.addCTk = ctk.CTkButton(entry_frame, text="+", command=self.add_button_callback,
                                        width=button_width, height=button_height, fg_color=cl_spin)
            entry_frame.grid_columnconfigure((0, 2), weight=0)   # buttons don't expand
            entry_frame.grid_columnconfigure(1, weight=0)        # entry expands

            self.subCTk.grid (row=0, column=0, padx=(1, 1), pady=1, sticky='w')
            self.mainCTk.grid(row=0, column=1, padx=(1, 1), pady=1, sticky='we')
            self.addCTk.grid (row=0, column=2, padx=(1, 1), pady=1, sticky='w')

            entry_frame.grid (row=self.row, column=column, columnspan= columnspan, padx=(1, 1), pady=0, sticky='w')
        else:
            self.mainCTk.grid(row=self.row, column=column, columnspan= columnspan, padx=(1, 1), pady=1, sticky='w')

        column += 1
        if (self.unit):
            unit_ctk  = ctk.CTkLabel (self.parent, text=self.unit, anchor='w')
            unit_ctk.grid (row=self.row, column=column, padx=(2,15), pady=1, sticky='w')
        else: 
            unit_ctk  = ctk.CTkFrame (self.parent, width=1, height=1, fg_color="transparent")
            unit_ctk.grid (row=self.row, column=column, padx=(2,5),  pady=1, sticky='w')

        self.mainCTk.bind('<Return>', self.CTk_callback)
        self.set_CTkControl()
        self.set_CTkControl_state()


    def _getFrom_CTkControl (self):
        return self.mainCTk.get()

    def _set_CTkControl (self,  widgetCTk, newValStr: str):

        # ctk special - if field is disabed, not update is made
        #  --> enable, set, disable 
        if self.disabled: self._set_CTkControl_state (widgetCTk, False)
        widgetCTk.delete(0, "end")
        widgetCTk.insert(0, newValStr)
        if self.disabled: self._set_CTkControl_state (widgetCTk, True)

    def add_button_callback(self):
        curStr = self._getFrom_CTkControl ()
        try:    newVal = float(curStr) + self.step
        except: newVal = 0
        val_asString = self.str_basedOnVal (newVal, self.valType, self.limits, self.decimals)
        self._set_CTkControl (self.mainCTk, val_asString)
        self.CTk_callback ('dummyEvent')

    def sub_button_callback(self):
        curStr = self._getFrom_CTkControl ()
        try:    newVal = float(curStr) - self.step
        except: newVal = 0
        val_asString = self.str_basedOnVal (newVal, self.valType, self.limits, self.decimals)
        self._set_CTkControl (self.mainCTk, val_asString)
        self.CTk_callback ('dummyEvent')

    def set_CTkControl_state (self):
        """sets disable bool into the final CTk control 
        """
        # over written to disable also the add/ sub buttons
        self._set_CTkControl_state (self.mainCTk, self.disabled)
        if self.spinner:
            self._set_CTkControl_state (self.subCTk,  self.disabled)
            self._set_CTkControl_state (self.addCTk,  self.disabled)
    
    def _set_CTkControl_state (self, widgetCTk, disable: bool):
        """sets the disabled / normal state in CTk control 
        """
        # ! overwrite because of CTk bug text_color_disabled
        curCTk_state = widgetCTk.cget("state")
        if disable: 
            if curCTk_state == "normal":
                pass
                widgetCTk.configure (state ="disabled" )         # "normal" (standard) or "disabled" (not clickable, darker color)
                widgetCTk.configure (text_color =cl_text_disabled )
        else: 
            if curCTk_state == "disabled":
                widgetCTk.configure (state ="normal" )           # "normal" (standard) or "disabled" (not clickable, darker color)
                widgetCTk.configure (text_color =cl_text )



class Option_Widget(Base_Widget):
    """ Compund widget existing out of 
        column i    : Field label - optional (CTkLabel)
        column i+1  : Option combox box  (CTkOption)

    Keyword Arguments:
        val or obj+getter -- val string to show or access path with obj and getter          :)
        options -- list of string values or access path being options to select 
        set -- access path setter when switched              :)
        spin -- Boolean if entry field should have a spinner       :)
    """
    def __init__(self, *args, padx=None, pady=None, **kwargs):
        super().__init__(*args, **kwargs)

        option_width = self.width 
        if padx is None: padx = (1,1)
        if pady is None: pady = 0


        # label support not active
        #if (self.label):  label_ctk = ctk.CTkLabel (self.parent, text=self.label)
        #else:             label_ctk = ctk.CTkFrame (self.parent, width=10, height=5, fg_color="transparent")     # dummy frame
        #label_ctk.grid (row=self.row, column=self.column, padx=(15, 15), pady=1, sticky='e')

        if self.spinner:
            # this new frame with 3 widget replaces the normal entry field in grid  
            option_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
            button_width  = self.height * 2 #* 1.2
            button_height = self.height
            option_width = self.width 
        else: 
            option_frame = self.parent
            option_width  = self.width

        self.mainCTk = ctk.CTkOptionMenu (option_frame, values= self.options, 
                                          width=option_width, height=self.height, 
                                          dynamic_resizing=False,
                                          command=self.CTk_callback)        

        if self.spinner:
            self.prevCTk = ctk.CTkButton(option_frame, text="prev", command=self.prev_button_callback,
                                         width=button_width, height=button_height, fg_color=cl_spin)
            self.nextCTk = ctk.CTkButton(option_frame, text="next", command=self.next_button_callback,
                                         width=button_width, height=button_height, fg_color=cl_spin)
            option_frame.grid_columnconfigure((0, 2), weight=0)   # buttons don't expand
            option_frame.grid_columnconfigure(1, weight=0)        # entry expands

            self.prevCTk.grid (row=self.row, column=self.column,   padx=(0, 0), pady=0, sticky='w')
            self.mainCTk.grid (row=self.row, column=self.column+1, padx=(2, 2), pady=0, sticky='w')
            self.nextCTk.grid (row=self.row, column=self.column+2, padx=(0, 0), pady=0, sticky='w')

            option_frame.grid (row=self.row, column=self.column, padx=padx, pady=pady, sticky='w')
        else:
            self.mainCTk.grid (row=self.row, column=self.column, padx=padx, pady=pady, sticky='w')

        self.set_CTkControl()
        self.set_CTkControl_state()


    def _getFrom_CTkControl (self):
        return self.mainCTk.get()

    def _set_CTkControl (self, widgetCTk, newValStr: str):
        if newValStr == '':
            widgetCTk.set(self.options[0])
        else:    
            widgetCTk.set(newValStr)

    def refresh (self):
        # first refresh options list 
        if not self.whileSetting:                           # avoid circular actions with refresh()
            if self.optionsGetter:
                self.options = self.get_value(self.optionsGetter, self.obj, self.parent)
                self.mainCTk.configure (values=self.options)
        # then refresh the selected item
        super().refresh()

    def next_button_callback(self):
        curVal = self._getFrom_CTkControl ()
        values = self.options
        try:    
            newIndex = values.index (curVal) 
            if newIndex < (len(self.options) -1) :
                newIndex += 1
        except: newIndex = 0
        self._set_CTkControl (self.mainCTk, str(self.options[newIndex]))
        self.set_CTkControl_state ()
        self.CTk_callback ('dummyEvent')

    def prev_button_callback(self):
        curVal = self._getFrom_CTkControl ()
        values = self.options
        try:    
            newIndex = values.index (curVal) 
            if newIndex > 0:
                newIndex -= 1
        except: newIndex = 0
        self._set_CTkControl (self.mainCTk, str(self.options[newIndex]))
        self.set_CTkControl_state ()
        self.CTk_callback ('dummyEvent')

    def set_CTkControl_state (self):
        """sets disable bool into the final CTk control 
        """
        # over written to disable also the add/ sub buttons
        self._set_CTkControl_state (self.mainCTk, self.disabled)
        if self.spinner:
            prevDisabled = self.disabled
            nextDisabled = self.disabled
            try:    
                curIndex = self.options.index (self._getFrom_CTkControl ()) 
                nextDisabled = nextDisabled or (curIndex >= (len(self.options) -1))
                prevDisabled = prevDisabled or (curIndex == 0)
            except: pass

            self._set_CTkControl_state (self.prevCTk, prevDisabled)
            self._set_CTkControl_state (self.nextCTk, nextDisabled)
    

class Combo_Widget(Base_Widget):
    """ Compund widget existing out of 
        column i    : Field label - optional (CTkLabel)
        column i+1  : Option combox box  (CTkOption)

    Keyword Arguments:
        val or obj+getter -- val string to show or access path with obj and getter          :)
        options -- list of string values or access path being options to select 
        set -- access path setter when switched              :)
        spin -- Boolean if entry field should have a spinner       :)
    """
    def __init__(self, *args, padx=None, pady=None, **kwargs):
        super().__init__(*args, **kwargs)

        if padx is None: padx = (1,1)
        if pady is None: pady = 0

        r = self.row
        c = self.column

        if (self.label):  label_ctk = ctk.CTkLabel (self.parent, text=self.label)
        else:             label_ctk = ctk.CTkFrame (self.parent, width=10, height=5, fg_color="transparent")     # dummy frame
        label_ctk.grid (row=r, column=c, padx=(15, 15), pady=1, sticky='e')

        self.mainCTk = ctk.CTkComboBox (self.parent, values= self.options, 
                                        width=self.width, height=self.height, 
                                        command=self.CTk_callback)        

        self.mainCTk.grid (row=r, column=c+1, padx=padx, pady=pady, sticky='w')
        self.set_CTkControl()
        self.set_CTkControl_state()

    def _getFrom_CTkControl (self):
        return self.mainCTk.get()

    def _set_CTkControl (self, widgetCTk, newValStr: str):
        if newValStr == '':
            widgetCTk.set(self.options[0])
        else:    
            widgetCTk.set(newValStr)

    def refresh (self):
        # first refresh options list 
        if not self.whileSetting:                           # avoid circular actions with refresh()
            if self.optionsGetter:
                self.options = self.get_value(self.optionsGetter, self.obj, self.parent)
                self.mainCTk.configure (values=self.options)
        # then refresh the selected item
        super().refresh()



#=========================================================
#========     Test App    ================================

class TestModelObject (): 
    def __init__(self):
        self._aString = 'Hello jo'
        self._aInt    = 654321
        self._aFloat  = 1234.5678

    @property
    def aString(self):      return self._aString
    @aString.setter
    def aString (self, val):
        self._aString = val
    @property
    def aInt(self):         return self._aInt
    @property
    def aFloat(self):       return self._aInt

    def aString_no_property(self):  return self._aString

    # @x.setter
    
    def set_aString(self, val):
        print ("mo set aString: ", val)
        self._aString = val 
    def set_aFloat(self, val):
        print ("mo set aFloat: ", val)
        self._aFloat = val 


class TestApp(ctk.CTk):
    def currentMo (self):
        if self.localBool:
            cur = self.mos[0]
        else:
            cur = self.mos[1]
        return cur
    

    def localString (self):
        return 'I am a local string'
    def localString2 (self):
        return 'This is the second'
    def localBoolOn (self):
        return True
    def localBoolOff (self):
        return False

    def setlocalBool (self, aBool):
        self.localBool = aBool 
        print("Current is currently ",self.currentMo().aString)
        self.moCurrentWidget.refresh()

    def setlocalFloat(self, val):
        print ("local set aFloat: ", val)
        self.localFloat = val 
        self.setlocalBool(val % 2)
        self.slaveWidget.refresh()
        self.switchWidget.refresh()

    def hitMe(self):
        print ("I was hit by button")

    def __init__(self):
        super().__init__()



        ctk.set_appearance_mode("Dark")    
        # ctk.set_default_color_theme("blue") 

        self.title("Test App for widgets")
        self.geometry("900x500")

        Base_Widget.ctk_root = self
        self.event_add('<<TEST_EVENT>>','None')

        #self.grid_rowconfigure   (1, weight=1)
        #self.grid_rowconfigure   (1, weight=1)

        mo = TestModelObject()
        self.localBool = True
        self.localFloat = 0
        self.mymo = mo

        mo1 = TestModelObject()
        mo1.set_aString ("des erschte")
        mo2 = TestModelObject()
        mo2.set_aString ("des zwoite")

        self.mos = [mo1,mo2]

        print("Initial mo ", self.mos[0].aString)

        a = self.localBoolOn
        print (a)
        a = self.localBoolOn()

        ap = AccessPath (self, get=lambda: mo1.aString)
        print ("1:   ", ap.eval())

        ap = AccessPath (self, get=mo1.aString_no_property)
        print ("2:   ", ap.eval())

        ap = AccessPath (self, get=mo1.aString_no_property, val="hoho")
        print ("3:   ", ap.eval())

        ap = AccessPath (self, get=lambda: mo.aString, set=mo.set_aString)
        print ("4:   ", ap.eval())
        ap.eval_set ('hihi')
        print ("5:   ", ap.eval(), "mo: ", mo.aString)


        return
        a = mo.aString
        a = lambda: self.localBoolOn()
        a = a()
        a = lambda: self.mymo.aString
        print (callable(a))
        a = a()
        b = lambda: self.mymo.aString
        print (callable(b), b.__name__, b.__self__)
        prop = getattr (b.__self__, b.__name__) 
        print (prop)
        prop = 'yeppe'
        # b = b('huhu')
        print (b,a, mo.aString)
        raise ValueError ("ohhh!") from None
        a = mo.aString_no_property
        a = mo.aString_no_property ()


        print (a) 



        Header_Widget (self, 0,0, lab='Header from val')
        Header_Widget (self, 0,1, get='localString')
        Header_Widget (self, 0,2, get=self.localString2)
        Header_Widget (self, 0,3, obj=mo, get='aString')
        Header_Widget (self, 0,4, get=mo.aString_no_property)
        Header_Widget (self, 0,5, get=lambda:mo.aFloat)  

        Button_Widget (self, 1,0, lab='Header from val')
        Button_Widget (self, 1,1, get=self.localString2, width=50, height=20)
        Button_Widget (self, 1,2, lab='Hit me', set=self.hitMe)

        Switch_Widget (self, 2,0, lab='Should be on', val=True)
        Switch_Widget (self, 2,1, lab='and off',      get=self.localBoolOff)
        Switch_Widget (self, 2,2, lab='and on again', get=self.localBoolOn)

        Field_Widget  (self, 3,0, lab='Field with lab', val='oho') 
        Field_Widget  (self, 3,3, val = '') 
        Field_Widget  (self, 4,0, lab='Field lab & units', val='123455', unit='mkg') 

        Field_Widget   (self, 6,0, lab='My super Spinner', val=123455, spin=True, step=1000, unit='mkg') 

        Header_Widget (self, 7,0, lab='Now writing back')
        Field_Widget  (self, 8,0, lab='Field set + get by string', obj=mo, get='aString', set='set_aString' ) 
        Field_Widget  (self, 9,0, lab='Field set + get by method', get=lambda: mo.aString, set=mo.set_aString ) 

        Switch_Widget (self, 10,0, lab='Activator Switch', get=lambda: self.localBool, set=self.setlocalBool)
        Field_Widget   (self, 11,0, lab='mo afloat #1', get=lambda:mo.aFloat, set=self.setlocalFloat, spin = True, step=1, ) 
        self.slaveWidget = \
            Field_Widget  (self, 11,3, lab='Slave of Spin', get=lambda: self.localFloat ) 
        self.switchWidget = \
            Switch_Widget (self, 11,5, lab='Number is even', get=lambda: self.localBool, disable=lambda: self.localBool)
        Field_Widget   (self, 12,0, lab='mo afloat inaktiv', get=lambda:mo.aFloat, set=self.setlocalFloat, disable= self.localBoolOn,  spin = True, step=1, ) 

        self.moCurrentWidget = Field_Widget   (self, 12,0, lab='Current mo aString', obj= self.currentMo,  get='aString') 





# Main program for testing -----------------------------------

if __name__ == "__main__":

    TestApp().mainloop()