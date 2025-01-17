#!/usr/bin/env pythonbutton_color
# -*- coding: utf-8 -*-

"""  

Additional generic (compound) widgets based on original CTK widgets

"""
import os
import customtkinter as ctk
import tkinter as tk
from PIL import Image


cl_entry            = ("gray95","gray35")         # background of entry fields
cl_entry_disable    = ("gray88","gray35")         # background of diabeld entry fields
cl_spin             = ("gray75","gray25")         # background of spin buttons
cl_spin_text        = ("gray5" ,"gray95")         # text color of spin buttons
cl_spin_text_disable= ("gray55","gray70")         # text color of spin buttons
cl_button_primary   = ctk.ThemeManager.theme["CTkButton"]["fg_color"] # default Button darker  
cl_button_secondary = ctk.ThemeManager.theme["CTkOptionMenu"]["button_color"] # brighter 
fs_header           = 18                          # font size header 

PRIMARY             = 1                           # buttonstyle for highlighted button 
SECONDARY           = 2                           # buttonstyle for normal action
SUPTLE              = 3                           # buttonstyle for subtle appearance 
ICON                = 4                           # buttonstyle for icon only button 


STYLE_NORMAL        = 'Normal'
STYLE_COMMENT       = 'Comment'
STYLE_DISABLED      = 'Disabled'
STYLE_ERROR         = 'Error'
STYLE_HINT          = 'Hint'
STYLE_WARNING       = 'Warning'

# some additional color definitions 
cl_styles ={
        STYLE_NORMAL    : ("gray10","gray95"),
        STYLE_DISABLED  : ("gray30","gray70"),
        STYLE_COMMENT   : ("gray40","gray60"),
        STYLE_ERROR     : ("red2","red2") ,
        STYLE_HINT      : ("RoyalBlue3", "cornflower blue"),
        STYLE_WARNING   : ("DarkOrange3", "orange")
        }



#-------------------------------------------------------------------------------
# Widgets  
#-------------------------------------------------------------------------------

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
        objId --    an 'id' for object. If set, will be passed in callback
        get --      either string path or callable method to get the value to show :)
        set --      either string path or callable method to invoke after a value is entered by user  :)
        disable --  either string path or callable method to disbale/enable widget  :)
        event --    tkinter virtual event like '<<MY_ALARM>>' :)
                       ... or  bound method, which will be called 
        lim  --     upper and lower numerical limit values for entry fields  :)
        dec --      decimals in numeric entry fields :)
        unit --     unit of entry fields like 'mm' :)
        step --     step size for spin button  :)
    """
  
    def __init__(self, parent: ctk.CTkFrame, 
                 row:int, column:int, 
                 val = None, 
                 lab:str=None, 
                 obj=None, objId=None,
                 get =None, set =None, 
                 disable = False, 
                 event: str= None,
                 lim:tuple=None, dec = None, unit : str = None, 
                 spin: bool = False, step: float = 0.1,
                 options: list = None,
                 width:int=None, height:int=None,
                 text_style=None):

        self.parent   = parent
        self.ctk_root = parent.winfo_toplevel()

        self.row    = row
        self.column = column

        self.getter = get
        self.setter = set
        self.obj    = obj                 
        self.objId  = objId                 
        if not val is None:  self.val = val                  # a input val overwrites the setter altwernative
        else:                self.val = self.get_value (get, obj, parent) 
        if self.val is None: self.val = ""

        if isinstance (self.val, bool):                       # supported data types
           self.valType = bool
        elif isinstance (self.val, int) or ((not dec is None) and (dec == 0)):
           self.valType = int
        elif isinstance  (self.val, float) or ((not dec is None) and (dec > 0)):    
           self.valType = float
        elif isinstance (self.val, str):
           self.valType = str
        else:
           raise ValueError ("This type is not supported in Widgets", self.val)
 
        if self.setter is None:                 # no setter? disable field 
            self.disGetter = None
            self.disabled = True
        elif (isinstance(disable, bool)):       # disable is either bool or access path
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
        if not self.width:  self.width  = 110
        if not self.height: self.height = 25

        self._styleGetter = None
        if text_style is None:
            self._text_style = STYLE_NORMAL
        else: 
            if not (isinstance(text_style, str)):
                self._styleGetter = text_style
                text_style = self.get_value (self._styleGetter, obj, parent)
            if text_style in cl_styles:
                self._text_style = text_style
            else:
                self._text_style = STYLE_NORMAL

        self.whileSetting = False                   # avoid circular actions with refresh()

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
            oldVal = self.val 
            self.val        = self.get_value(self.getter, self.obj, self.parent)
            if oldVal != self.val: 
                # print (" refresh !=  ", oldVal, self.val)
                self.set_CTkControl ()
        if self.labGetter:
            self.label      = self.get_value (self.labGetter, self.obj, self.parent)  
            self.set_CTkControl_label ()                     
        if self.disGetter:
            self.disabled   = self.get_value (self.disGetter, self.obj, self.parent)  
            self.set_CTkControl_state ()                    # disable / enable
        if self.spinner: 
            self.set_CTkControl_state ()                    # spin buttons active / inactive?  

    def force_set (self):
        """ write back the current value of the widgets via setter.
        Can be used to ensure the current value is handled without "Return" being pressed  
        """

        self.CTk_callback ()
        self.set_value()


    #---  from / to outside - owner or object of the widget 
 
    def get_value(self, getter, obj, parent):
        """read the initial value from object via getter path
        """
        if not obj and not parent: raise ValueError ("%s: Object for getter path is missing" % self._name)
        if not getter: 
            return None                                 # could be a button
        if callable(getter):                            # getter is a method ?
            if not self.objId is None:                  # an object Id was set to identify object
                return getter(objId=self.objId) 
            else:            
                return getter()                         # normal callback
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
        """write the current value of the widget to object via setter path
        """

        if not self.setter: return              # self has no setter - do nothing

        if not self.obj and not self.parent: raise ValueError ("Object for setter path is missing")

        myVal = self.val 

        self.whileSetting = True                # avoid circular actions with refresh()
        if callable(self.setter):               # getter is a method ?
            if self.val is None:                # typically a button method which has bo arg
                if not self.objId is None:      # an object Id was set to identify object
                    self.setter(objId=self.objId) 
                else:            
                    self.setter()               # normal callback
            else:                               # a method like: def myMth(self, newVal)
                if not self.objId is None:      # an object Id was set to identify object
                    self.setter(myVal, objId=self.objId) 
                else:            
                    self.setter(myVal)          # normal callback
        else:                                   # ... no - getter is a String of a function for 'obj'
            if self.obj:
                if callable(self.obj):                       # obj getter is a method ?
                    dataObject = self.obj()
                else:
                    dataObject = self.obj
                propOrMethod =  getattr (dataObject, self.setter)
            else:                               # if no obj-argument, try it with parent (self...)
                propOrMethod =  getattr (self.parent, self.setter)
            if (not callable(propOrMethod)):    # access path showed to a property
                propOrMethod = myVal            
            else:                               # access path showed to a method
                if not self.objId is None:      # an object Id was set to identify object
                     propOrMethod(myVal, objId=self.objId) 
                else:            
                    propOrMethod(myVal)         # normal callback
        self.whileSetting = False               # avoid circular actions with refresh()



    #---  from / to CTkControl - inside the widget 

    def set_CTkControl (self):
        """sets val into the final CTk control 
        """
        self.val_asString = self.str_basedOnVal (self.val, self.valType, self.limits, self.decimals)

        # re-convert to val so rounding will not lead to an update (write back)   
        self.val = self.val_basedOnStr (self.val, self.valType, self.val_asString, self.limits)

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
            s = str(int(val))
        elif valType == float:
            if limits: 
                minVal, maxVal = limits
                val2 = max (float(minVal), float(val))
                val  = min (float(maxVal), val2)
            if decimals:
                s = "%0.*f" %(decimals,val)
            else: 
                s = "%f" % val
        else:
            s = '???'
        return s

    def val_basedOnStr (self, val, valType, newStr, limits=None):
        """converts string (from entry field) in the type val normally has 
        """

        newVal = None 

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
                if val: newVal = float(val)     #   could also be None
            if limits and newVal: 
                minVal, maxVal = limits
                newVal2 = max (float(minVal), newVal)
                newVal  = min (float(maxVal), newVal2)
        elif valType == bool: 
                newVal = (newStr == "1" or newStr == 1)        # Ctk returns int (?) 
        else: 
                newVal = newStr
        return newVal

    def fireEvent(self):

        if self.event:                            # the event property has a bound method 
            if callable(self.event):
               self.event()         
            elif self.ctk_root:                       # the event property is a string with an event name
                # print ("fire ", self.event, ' from ', self.__class__.__name__)
                self.ctk_root.event_generate (self.event) 

    def _text_color (self, aStyle=None):
        """ returns the text_color depending on style"""

        if aStyle is None  : 
            if self._styleGetter: 
                aStyle = self.get_value (self._styleGetter, self.obj, self.parent)
            else: 
                aStyle = self._text_style
        elif aStyle == STYLE_DISABLED and self._styleGetter:        # external style overwrites disabled style
                extStyle = self.get_value (self._styleGetter, self.obj, self.parent)
                if extStyle: 
                    aStyle = extStyle

        if aStyle in cl_styles:
            return cl_styles [aStyle]
        else:
            return cl_styles [STYLE_NORMAL]

    @property     
    def _name (self): 
        """ name for error messages etc. """

        return self.__class__

#-----------  real widget subclasses ----------------------------



class Blank_Widget(Base_Widget):
    """Creates a non visible blank frame as a placeholder in grid - default 10x10 pixels
                                                        
        Blank_Widget (self, 0,0) :)
    """
    def __init__(self, *args, width= 10, height=10, padx=None, **kwargs):
        super().__init__(*args, width= width, height=height, **kwargs)
            
        if padx   is None: padx = 0

        # self.mainCTk = ctk.CTkFrame (self.parent, width=self.width, height=self.height, fg_color="blue")     # dummy frame
        self.mainCTk = ctk.CTkFrame (self.parent, width=self.width, height=self.height, fg_color="transparent")     # dummy frame
        self.mainCTk.grid(row=self.row, column=self.column,  pady=0, padx=padx, sticky="w")



class Header_Widget(Base_Widget):
    """Header label  - uses one columns in the grid
                                                        
        Header_Widget (self, 0,0, lab='Header from val') :)
        Header_Widget (self, 0,2, lab=self.localString) :)
    """
    def __init__(self, *args, 
                 columnspan = 1, 
                 padx=None, pady=None, 
                 sticky = None, anchor=None, 
                 **kwargs):
        super().__init__(*args, **kwargs)

        if anchor is None: anchor = 'w'
        if sticky is None: sticky = "w"
        if padx   is None: padx = (10,0)
        if pady   is None: pady = (10,15)

        self.mainCTk = ctk.CTkLabel (self.parent, width=self.width, text=self.label, 
                                     anchor= anchor, font= ("", fs_header))
        self.mainCTk.grid(row=self.row, column=self.column,  columnspan= columnspan, pady=pady, padx=padx, sticky="w")

    def _set_CTkControl_label (self, widgetCTk, newLabelStr: str):
        widgetCTk.configure (text=newLabelStr)



class Label_Widget(Base_Widget):
    """a subtle label text with word wrap - spans 5 columns
                                                        
        Label_Widget  (self, 3,0, lab='Loremm ipsumm') :)
        Label_Widget  (self, 3,0, width=200, lab=self.myLabeText) :)
    """
    def __init__(self, *args, 
                 textvariable=None,         # optional- use tkinter textvariable for auto update 
                 padx=None, pady=None, 
                 justify=None,              # left or right - default left 
                 sticky=None,               # default sw
                 text_style='Disabled', 
                 columnspan=None,
                 wraplength=0,              # enable wrap at length
                 **kwargs):
        
        super().__init__(*args, text_style=text_style, **kwargs)

        if justify is None: justify = "left"

        if sticky is None: 
            if justify == "right": sticky = "se"
            else:                  sticky = "sw" 
        if "e" in sticky:
            anchor = "e"
        else:
            anchor = "w"

        if columnspan   is None: columnspan = 6

        if padx         is None: padx = 10
        if pady         is None: pady = 0

        if textvariable: self.label = None                  # a textvariable overwrites an additional label 

        self.mainCTk = ctk.CTkLabel(self.parent, text=self.label, textvariable=textvariable,
                                    width=self.width, justify =justify, 
                                    anchor= anchor, text_color=self._text_color(),
                                    wraplength=wraplength) 
                  
        self.mainCTk.grid(row=self.row, column=self.column,  columnspan=columnspan, 
                          padx=padx, pady=pady, sticky=sticky)

    def _set_CTkControl_label (self, widgetCTk, newLabelStr: str):
        widgetCTk.configure (text_color=self._text_color())
        widgetCTk.configure (text=newLabelStr)



class Button_Widget(Base_Widget):
    """CTKButton - uses one column in the grid

    Keyword Arguments:
        val or obj+getter -- val string to show or access path with obj and getter          :)
        set -- access path setter when button is pressed             :)
        style -- button appearance - either PRIMARY, SECONDARY or SUPTLE
    """

    # <a target="_blank" href="https://icons8.com/icon/15813/pfeil%3A-einklappen">Pfeil: Einklappen</a> Icon von <a target="_blank" href="https://icons8.com">Icons8</a>
    ICONS = {
        "settings": None,
        "collapse": None
        }
    

    def __init__(self, *args, 
                 style=SECONDARY, 
                 sticky= None, anchor=None, 
                 icon_name: str = None,             #  "settings"
                 pady= None, padx=None, columnspan = 1, **kwargs):
        super().__init__(*args, **kwargs)

        icon_size = None 
        if anchor is None: anchor = 'center'
        if padx   is None: padx = 10
        if pady   is None: pady = 0

        if style == PRIMARY: 
            self.fg_color = cl_button_primary
        elif style == SUPTLE:
            self.fg_color = cl_spin
        elif style == ICON:
            self.fg_color = "transparent"
            self.width = 25
            icon_size= (17,17)
            icon_name = icon_name if icon_name is not None else "settings"
        else:
            self.fg_color = cl_button_secondary
            style = SECONDARY
        self.style = style

        sticky = 'w' if sticky is None else sticky
        text = self.val if self.getter else self.label      # either 'get' or 'lab' can be used

        icon = self.load_icon (icon_name, icon_size=icon_size) if icon_name else None 


        self.mainCTk = ctk.CTkButton(self.parent, text=text, height=self.height, width=self.width, 
                                     anchor=anchor, image=icon, 
                                     border_spacing=0, border_width=0,
                                     command=self.CTk_callback)
        self.mainCTk.grid(row=self.row, column=self.column, columnspan=columnspan, padx=padx, pady=pady, sticky=sticky)
     
        self.set_CTkControl_state ()        # state explicit as no value is set_value in button

    def _getFrom_CTkControl (self):
        # button has nothing to give ...
        return None                     

    def _set_CTkControl  (self, widgetCTk, newLabelStr):
        # if self is destroyed , newLaberlStr good be ''
        if newLabelStr: 
            widgetCTk.configure (text=newLabelStr)

    def _set_CTkControl_label (self, widgetCTk, newLabelStr: str):
        widgetCTk.configure (text=newLabelStr)

    def CTk_callback(self, dummy=None):
        # overwritten because of flicker of CTkButton
        # no call back when disabled 
        if not self.disabled: return super().CTk_callback(dummy)

    def _set_CTkControl_state (self, widgetCTk, disable: bool):
        # overwritten because of flicker of CTkButton
        if disable: 
            widgetCTk.configure (text_color = cl_spin_text_disable) 
            widgetCTk.configure (fg_color =cl_spin )
        else: 
            if self.style == SUPTLE: 
                " for suptle buttons same as Spin Button (black)"
                widgetCTk.configure (text_color = cl_spin_text)
            else:
                # for buttons always color of Dark mode
                widgetCTk.configure (text_color = self._text_color()[1])
            widgetCTk.configure (fg_color =self.fg_color )


    def load_icon(self, icon_name, icon_size= (20,20)):
            if icon_name not in self.ICONS or self.ICONS[icon_name] is None:
                dirname = os.path.dirname(os.path.realpath(__file__))
                image_path_light = os.path.join(dirname, 'icons', icon_name + '_light'+ '.png')
                image_path_dark  = os.path.join(dirname, 'icons', icon_name + '_dark'+ '.png')
                self.ICONS[icon_name] = ctk.CTkImage(light_image=Image.open(image_path_light), 
                                                     dark_image =Image.open(image_path_dark), 
                                                     size=icon_size)
            return self.ICONS[icon_name]       


    def refresh(self):
        """ overloaded """
        if self._styleGetter :                  #  new text style for button? 
            self.set_CTkControl_state ()

        return super().refresh()
    


class Switch_Widget(Base_Widget):
    """CTKSwitch - uses one column in the grid

    Keyword Arguments:
        val or obj+getter -- val string to show or access path with obj and getter          :)
        set -- access path setter when switched              :)
    """
    def __init__(self, *args, padx=None, pady=None, columnspan=None, **kwargs):
        super().__init__(*args, **kwargs)

        if padx is None: padx = (15,5)
        if pady is None: pady = 0
        if columnspan is None: columnspan = 1

        self.mainCTk = ctk.CTkSwitch(self.parent, switch_height=14, switch_width=32, text=self.label, width=self.width, onvalue=1, command=self.CTk_callback)
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

        height = 15
        pady= 2

        self.mainCTk = ctk.CTkCheckBox (self.parent, text=self.label, onvalue=1, command=self.CTk_callback)
        self.mainCTk.grid(row=self.row, column=self.column, padx=10, pady = pady, sticky="w")

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
    def __init__(self, *args, 
                 padx=None, pady=None, 
                 lab_width= None, 
                 columnspan=None, 
                 justify=None,                  # justify data within entry field - 'right' or 'left'
                 sticky=None,                   # alignment of widget within grid - 'w 'oder 'e'
                 **kwargs):
        
        super().__init__(*args, **kwargs)

        column = self.column
        if columnspan is None: columnspan = 1

        if justify is None: justify = 'right'

        if sticky is None: sticky = 'w'
        
        if padx is None: padx= (5, 5)
        if pady is None: pady= 0

        if (self.label):  
            if lab_width:
                width = lab_width
            else:
                width= 95

            label_ctk = ctk.CTkLabel (self.parent, width= width, text=self.label,  
                                      justify='left', anchor='w')
            label_ctk.grid (row=self.row, column=column, padx=padx, pady=pady, sticky='w')
            column += 1

        if self.spinner:
            # this new frame with 3 widget replaces the normal entry field in grid  
            entry_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
            button_width  = self.height  - 2
            button_height = self.height
            entry_width = self.width - 2 * button_width - 2
        else: 
            entry_frame = self.parent
            entry_width = self.width

        self.mainCTk = ctk.CTkEntry (entry_frame, width=entry_width, height=self.height, border_width=1,
                                     justify=justify, fg_color=cl_entry)

        if self.spinner:
            self.subCTk = ctk.CTkButton(entry_frame, text="-", command=self.sub_button_callback,
                                        width=button_width, height=button_height, 
                                        fg_color=cl_spin, text_color=cl_spin_text, text_color_disabled=cl_spin_text_disable)
            self.addCTk = ctk.CTkButton(entry_frame, text="+", command=self.add_button_callback,
                                        width=button_width, height=button_height, 
                                        fg_color=cl_spin, text_color=cl_spin_text, text_color_disabled=cl_spin_text_disable)
            entry_frame.grid_columnconfigure((0, 2), weight=0)   # buttons don't expand
            entry_frame.grid_columnconfigure(1, weight=0)        # entry expands

            self.subCTk.grid (row=0, column=0, padx=(1, 1), pady=1, sticky='w')
            self.mainCTk.grid(row=0, column=1, padx=(1, 1), pady=1, sticky='we')
            self.addCTk.grid (row=0, column=2, padx=(1, 1), pady=1, sticky='w')

            entry_frame.grid (row=self.row, column=column, columnspan= columnspan, padx=(1, 1), pady=pady, sticky=sticky)
        else:
            self.mainCTk.grid(row=self.row, column=column, columnspan= columnspan, padx=(1, 1), pady=pady, sticky=sticky)

        column += 1
        if (self.unit):
            unit_ctk  = ctk.CTkLabel (self.parent, text=self.unit, anchor='w')
            unit_ctk.grid (row=self.row, column=column, padx=(2,15), pady=pady, sticky=sticky)
        else: 
            unit_ctk  = ctk.CTkFrame (self.parent, width=1, height=1, fg_color="transparent")
            unit_ctk.grid (row=self.row, column=column, padx=(2,5),  pady=pady, sticky=sticky)

        self.mainCTk.bind('<Return>', self.CTk_callback)
        self.mainCTk.bind('<FocusOut>', self.CTk_callback)

        self.set_CTkControl()
        self.set_CTkControl_state()


    def _getFrom_CTkControl (self):
        return self.mainCTk.get()

    def _set_CTkControl (self,  widgetCTk, newValStr: str):

        # ctk special - if field is disabed, no update is made
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
                widgetCTk.configure (state ="disabled" )         # "normal" (standard) or "disabled" (not clickable, darker color)
                widgetCTk.configure (text_color = self._text_color('Disabled'))
                # also set background of entry field
                if widgetCTk == self.mainCTk: 
                    widgetCTk.configure (fg_color = cl_entry_disable)
        else: 
            if curCTk_state == "disabled":
                widgetCTk.configure (state ="normal" )           # "normal" (standard) or "disabled" (not clickable, darker color)
                widgetCTk.configure (text_color = self._text_color())
                # also set background of entry field
                if widgetCTk == self.mainCTk: 
                    widgetCTk.configure (fg_color = cl_entry)



class Slider_Widget(Base_Widget):
    """ Slider to select a Value within 'limits'
        ... takes 1 column 

        Special arguments :
            limits:     upper and lower limit of slider 
            step:       integer step size              
    """
    def __init__(self, *args, padx=None, pady=None, columnspan=None, **kwargs):
        super().__init__(*args, **kwargs)
        """ New slider 
        """

        column = self.column
        if columnspan is None:  columnspan = 1
        if padx is None: padx = 1 
        if pady is None: pady = 0 

        self.mainCTk = ctk.CTkSlider (self.parent, width=self.width, height=self.height, border_width=1,
                                      command=self.CTk_callback, fg_color=cl_entry)

        self._set_slider_range()                            # min, max, steps ...

        self.mainCTk.grid(row=self.row, column=column, columnspan= columnspan, 
                          padx=padx, pady=pady, sticky='we')

        self.set_CTkControl()
        self.set_CTkControl_state()

    def set_CTkControl (self):
        """sets val into the final CTk control 
        """
        # overwritten to allow '-1' for the last element of slider 
        if self.val == -1:
            self.val = self.limits[1]
        super().set_CTkControl()


    def _getFrom_CTkControl (self):
        return self.mainCTk.get()


    def _set_CTkControl (self, widgetCTk, newValStr: str):
        """sets val into the final CTk control 
        """
        # to overwrite by sub class 
        if newValStr: 
            self._set_slider_range()                   # limits could have been changed
            minVal, maxVal = self.limits
            if (maxVal-minVal) > 0:                    # ctk doesn't like 0 
                widgetCTk.set (eval(newValStr))


    def _set_slider_range (self):
        # set limits and steps of Ctk slider 

        minVal, maxVal = self.limits
        nsteps = max (1, (maxVal-minVal) / self.step)   # step must be > 0 

        self.mainCTk.configure(from_=minVal) 
        self.mainCTk.configure(to=maxVal) 
        self.mainCTk.configure(number_of_steps=nsteps) 


class Option_Widget(Base_Widget):
    """ Compund widget existing out of 
        column i    : Field label - optional (CTkLabel)
        column i+1  : Option combox box  (CTkOption)

    Keyword Arguments:
        spin -- Boolean if entry field should have a spinner      
        spinPos -- 'below' of 'beside' - default 'beside'
    """
    def __init__(self, *args, 
                 sticky=None, 
                 padx=None, pady=None, 
                 spinPos=None,
                 columnspan=None,
                 **kwargs):
        super().__init__(*args, **kwargs)

        option_width = self.width 
        if padx is None: padx = (1,1)
        if pady is None: pady = 0
        if sticky is None: sticky = 'w'

        if columnspan   is None: columnspan = 1

        # label support not active
        #if (self.label):  label_ctk = ctk.CTkLabel (self.parent, text=self.label)
        #else:             label_ctk = ctk.CTkFrame (self.parent, width=10, height=5, fg_color="transparent")     # dummy frame
        #label_ctk.grid (row=self.row, column=self.column, padx=(15, 15), pady=1, sticky='e')

        if self.spinner:
            if spinPos == 'below':
                # this new frame with 2 button will be below OptionMenu  
                button_frame = ctk.CTkFrame(self.parent, fg_color="transparent") 
                option_frame = self.parent
            else: 
                # this new frame with 3 widget replaces the normal entry field in grid  
                option_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
                button_frame  = option_frame

            button_width  = self.height * 2 
            button_height = self.height
            option_width  = self.width 
        else: 
            option_frame = self.parent
            option_width  = self.width

        self.mainCTk = ctk.CTkOptionMenu (option_frame, values= self.options, 
                                          width=option_width, height=self.height, 
                                          dynamic_resizing=False,
                                          command=self.CTk_callback)        

        if self.spinner:
            self.prevCTk = ctk.CTkButton(button_frame, text="prev", command=self.prev_button_callback,
                                         width=button_width, height=button_height, 
                                         fg_color=cl_spin, text_color=cl_spin_text, text_color_disabled=cl_spin_text_disable)
            self.nextCTk = ctk.CTkButton(button_frame, text="next", command=self.next_button_callback,
                                         width=button_width, height=button_height, 
                                         fg_color=cl_spin, text_color=cl_spin_text, text_color_disabled=cl_spin_text_disable)
            if spinPos == 'below':
                self.mainCTk.grid (row=self.row, column=self.column, columnspan=columnspan, 
                                   padx=padx, pady=pady, sticky=sticky)
                button_frame.grid_columnconfigure((0,1), weight=1)       
                button_frame.grid (row=self.row+1, column=self.column, columnspan=columnspan,
                                   padx=padx, pady=pady, sticky='we')
                self.prevCTk.grid (row=0, column=0, padx=(0, 2), pady=0, sticky='w')
                self.nextCTk.grid (row=0, column=1, padx=(2, 0), pady=0, sticky='e')
            else:
                option_frame.grid_columnconfigure((0, 2), weight=0)   # buttons don't expand
                option_frame.grid_columnconfigure(1, weight=0)        # entry expands

                self.prevCTk.grid (row=self.row, column=self.column,   padx=(0, 0), pady=0, sticky=sticky)
                self.mainCTk.grid (row=self.row, column=self.column+1, padx=(2, 2), pady=0, sticky=sticky)
                self.nextCTk.grid (row=self.row, column=self.column+2, padx=(0, 0), pady=0, sticky=sticky)

                option_frame.grid (row=self.row, column=self.column, columnspan=columnspan,
                                   padx=padx, pady=pady, sticky=sticky)
        else:
            self.mainCTk.grid (row=self.row, column=self.column, columnspan=columnspan,
                               padx=padx, pady=pady, sticky=sticky)

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
        # if not self.whileSetting:                           # avoid circular actions with refresh()
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
            self._set_CTkControl (self.mainCTk, str(self.options[newIndex]))
        except: 
            pass

        self.set_CTkControl_state ()
        self.CTk_callback ('dummyEvent')

    def prev_button_callback(self):
        curVal = self._getFrom_CTkControl ()
        values = self.options
        try:    
            newIndex = values.index (curVal) 
            if newIndex > 0: newIndex -= 1
            self._set_CTkControl (self.mainCTk, str(self.options[newIndex]))
        except: 
            pass

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
            except: 
                prevDisabled = True
                nextDisabled = True

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
    def __init__(self, *args, padx=None, pady=None, lab_width=None, **kwargs):
        super().__init__(*args, **kwargs)

        if padx is None: padx = (1,1)
        if pady is None: pady = 0

        r = self.row
        c = self.column

        if (self.label):
            if lab_width:   width = lab_width
            else:           width= 95
            label_ctk = ctk.CTkLabel (self.parent, width=width, text=self.label,
                                      justify='left', anchor='w')
        else:
            label_ctk = ctk.CTkFrame (self.parent, width=10, height=5, fg_color="transparent")     # dummy frame

        label_ctk.grid (row=r, column=c, padx=padx, pady=pady, sticky='w')

        self.mainCTk = ctk.CTkComboBox (self.parent, values= self.options, 
                                        width=self.width, height=self.height, 
                                        button_color=cl_spin, border_width=1,
                                        command=self.CTk_callback)        

        self.mainCTk.grid (row=r, column=c+1, padx=None, pady=pady, sticky='w')
        self.set_CTkControl()
        self.set_CTkControl_state()

        self.mainCTk.bind('<Return>', self.CTk_callback)
        self.mainCTk.bind('<FocusOut>', self.CTk_callback)



    def _getFrom_CTkControl (self):
        return self.mainCTk.get()

    def _set_CTkControl (self, widgetCTk, newValStr: str):
        if newValStr == '':
            widgetCTk.set(newValStr)
            # widgetCTk.set(self.options[0])
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