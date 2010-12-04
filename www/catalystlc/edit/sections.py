import sys
import inspect

from domdom import dom, xhtml, css, settings, routers, events, fx
import gui
import images

section_names = ['Apply It', 'Challenge', 'Closure', 'Compute It', 'Correct It', 'Cut It', 'Definitions', 'Draw It', 'How To', 'Into', 'Investigate', 'Judge It', 'Plot It', 'Prove It', 'Questions', 'Review', 'Say It', 'Scaffold', 'See It']
  
class Section(xhtml.div):
    
    @staticmethod
    def css():
        pass
        #css.prop.border = 'solid rgb(200,200,255) 0.01in'
        
    def __init__(self, parent, type, title_text = "", edit_mode = True):
        
        xhtml.div.__init__(self, parent = parent)        
        
        self.type       = type
        self.edit_title = title_text
        self.edit_mode  = edit_mode
        
        # setup of DOM
        self.title = Title(parent = self)          
        self.title.left   = Left(parent = self.title)
        self.title.middle = Middle(parent = self.title)
        self.title.img    = TitleIcon(parent = self.title.middle)
        
        self.title.right    = Right(parent = self.title)
        self.title.tag_line = TitleMain(parent = self.title.right)
        self.title.editor   = TitleMain(parent = self.title.right)

        self.content        = Content(parent = self)
        self.content.left   = Left(parent = self.content)
        self.content.middle = Middle(parent = self.content)
        self.content.right  = Right(parent = self.content)
        #self.content.right.style.padding_left = css.inch(0.25) 
        
        if self.edit_mode:
            self.create_editor()
        else:
            self.render()
            
        #self.event_onmousedown = events.MouseDown(parent = self)
        self.event_onfocus     = events.Focus(parent = self)
        self.event_onblur      = events.Blur(parent = self)

    def create_editor(self):
        self.edit_types = EditorTypes(parent = self.title.left, section = self, options = section_names, value = self.type)
        self.edit_title = EditorTitle(parent = self.title.editor, section = self)
        self.set_top()

        self.edit_left  = EditorLeft(parent = self.content.left, section = self)
        self.edit_right = EditorRight(parent = self.content.right, section = self)
        
    def render(self):
        pass

    def set_top(self):
        self.title.img.att.src = images.__dict__[self.type.replace(" ", "").lower() + "_gif"]
        colon = ":" if self.edit_title.has_text() else ""
        self.title.tag_line.text = self.type + colon
        
    def title_colon_add(self):
        self.title.tag_line.text = self.type + ":"

    def title_colon_remove(self):
        self.title.tag_line.text = self.type
         
    def onmousedown(self, event):
        self.js.alert('hi')       
    def onfocus(self, event):
        self.js.alert('hi')
    def onblur(self, event):
        self.js.alert('bye')
                
_left_width = css.inch(2.0)

class Block(xhtml.div):
    @staticmethod
    def css(): 
        css.prop.width = css.inch(6.95)
        css.prop.border         = 'solid red 1px'
        css.prop.overflow       = 'auto'

class Title(Block):
    @staticmethod
    def css(): 

        css.prop.font_size      = css.pt(12)
        css.prop.font_weight    = css.values.font_weights.x300
        
class TitleIcon(xhtml.img):
    
    @staticmethod
    def css():
        css.prop.position = css.values.positions.relative
        css.prop.width    = css.pixel(33)
        css.prop.height   = css.pixel(33)
        css.prop.border   = 'solid 0 white'
        css.prop.float    = css.values.floats.left 

class TitleMain(xhtml.div):
    
    @staticmethod
    def css():
        css.prop.padding_right  = css.inch(0.1)
        css.prop.float          = css.values.floats.left         
        
class Content(Block):

    @staticmethod
    def css():
        pass
    
""" Left Middle Right """
                      
class Left(xhtml.div): 
    
    @staticmethod
    def css():
        css.prop.min_height       = css.inch(0.18)
        css.prop.width            = _left_width
        css.prop.background_color = css.rgb(155, 200, 220)
        css.prop.float            = css.values.floats.left 
        
class Middle(xhtml.div): 
    @staticmethod
    def css():
        css.prop.min_height       = css.inch(0.18)
        css.prop.width            = css.inch(0.35)
        css.prop.background_color = css.rgb(255, 230, 220)
        css.prop.float            = css.values.floats.left 
        
class Right(xhtml.div): 
    @staticmethod
    def css():
        css.prop.min_height       = css.inch(0.18)
        css.prop.width            = css.inch(4.6)
        css.prop.background_color = css.rgb(255, 100, 30)
        css.prop.float            = css.values.floats.left 
        
        
""" Editor """
class EditorTypes(xhtml.select):

    @staticmethod
    def css():
        #css.prop.margin_left = css.inch(-1.9)
        pass
        
    def onchange(self, event):
        self.section.type = self.value
        self.section.set_top()
        
class EditorTitle(xhtml.input_text_onoutput):
    
    @staticmethod
    def css():
        css.prop.width = css.inch(3.0)
        css.prop.float = css.values.floats.left
        
    def onoutput(self, event):
        if self.has_text():
            self.section.title_colon_add()
        else:
            self.section.title_colon_remove()
        
    def has_text(self):
        return len(self.att.value) > 0
        
class EditorTextArea(xhtml.textarea_onoutput):
    
#    def __init__(self, **kwargs):
#        xhtml.textarea_onoutput(default = False, **kwargs)
    
    @staticmethod
    def css():
        css.prop.width = css.percent(99)
        css.prop.min_height = css.inch(4)
        css.prop.height     = css.percent(100)

class EditorLeft(EditorTextArea):
    pass

class EditorRight(EditorTextArea):
    pass


""" Custom Gui """

class SectionTypeMenu(gui.SubMenu):
    
    def __init__(self, parent, pos, handler, handler_fn):
        gui.SubMenu.__init__(self, parent = parent, pos = pos, choices = section_names, handler = handler, handler_fn = handler_fn)

  

"""
Section
"""

#class Dialog_AddSection(gui.Confirm):
#    
#    def __init__(self, handler):
#        
#        gui.Confirm.__init__(self, parent = handler.document.main, title = "Add New Section")        
#        
#        self.handler = handler        
#        
#        self.editor = xhtml.div(parent = self.frame)
#        self.editor.style.width = css.inch(5)
#        self.edit_types  = Dialog_select(parent = self.editor, options = sections.section_names)              
#        self.title  = Dialog_input(parent = self.editor,  under = 'Section Title')
#        self.title.input.style.width = css.inch(4)
#        self.title.style.margin_left = css.pixel(10)
#        
#        self.event_okd = events.KeyDown(parent = self)
#              
#    def onkeydown(self, event):
#        if event.key_code == 13:
#            self.confirm()
#              
#    def confirm(self):
#        self.handler.page.add_section(type = self.edit_types.att.value, title = self.title.input.att.value)        
#        self.cancel()
#        
#class Dialog_select(xhtml.select):
#
#    @staticmethod
#    def css():
#        css.prop.float        = css.values.floats.left
#
#class Dialog_input(xhtml.div):
#
#    @staticmethod
#    def css():
#        css.prop.float        = css.values.floats.left
#        
#    def __init__(self, parent, under = None):
#        xhtml.div.__init__(self, parent = parent)
#        self.input = Dialog_input_input(parent = self)
#        if under:
#            self.desc = Dialog_input_title(parent = self, text = under)
#
#class Dialog_input_input(xhtml.input_text_onoutput):
#
#    @staticmethod
#    def css():
#        css.prop.padding      = css.pixel(1)
#
#class Dialog_input_title(xhtml.div):
#
#    @staticmethod
#    def css():
#        css.prop.padding_bottom  = css.inch(0.05)
#        css.prop.padding_left    = css.inch(0.05)
#        css.prop.font_size       = css.pt(9)
#        css.prop.letter_spacing  = css.pt(0.0)
#        css.prop.color           = css.rgb(50,50,50)
#        css.prop.font_weight     = css.values.font_weights.normal
#        css.prop.margin_left     = css.pixel(-5)


#obj
  #obj_item >> Round numbers in your head. 
  #obj_item >> Round numbers in your brain. 

#ta
  #ta_item >> Probability all around us. >> Did you know that . . . 
  #ta_item >> Probability all around us. >> Did you know that . . . 

#image name="mental_math_5" float="left" scale="100%"

#table_r4_c4 style="gray_header"
  #cell >> #add style="v" >> 1+2
  #cell >> #add style="v" >> 1+2

#table_r4_c4 style="clear"
  #cell >> #add style="v" >> 1+2
  #cell >> #add style="v" >> 1+2