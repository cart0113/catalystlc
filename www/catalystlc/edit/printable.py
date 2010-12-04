import sys
import inspect
import exceptions

from domdom import dom, xhtml, css, settings, routers, events, fx

import images
import gui
import sections

""" 
Printable  
"""        

class pdiv(xhtml.div):
    
    @staticmethod
    def css():
        css.prop.overflow  = 'auto'
        
def inline_css():
    return "button::-moz-focus-inner { border: 0; }"
    
class Printable(xhtml.webpage):

    def __init__(self): 

        xhtml.webpage.__init__(self)       
        #self.includes.css <= 'http://media.tutor.org/forcecss.css'
        self.includes.css <= sys.modules[__name__]        
        self.includes.css <= gui
        self.includes.css <= sections
        
        #self.includes.js  <= 'http://media.tutor.org/jquery-1.3.2.js'
        
        if False:        
            self.includes.js <= 'http://media.tutor.org/mochi/lib/MochiKit/Base.js'
            self.includes.js <= 'http://media.tutor.org/mochi/lib/MochiKit/Iter.js'
            self.includes.js <= 'http://media.tutor.org/mochi/lib/MochiKit/DOM.js'
            self.includes.js <= 'http://media.tutor.org/mochi/lib/MochiKit/Style.js'
            self.includes.js <= 'http://media.tutor.org/mochi/lib/MochiKit/Color.js'
            self.includes.js <= 'http://media.tutor.org/mochi/lib/MochiKit/Position.js'
            self.includes.js <= 'http://media.tutor.org/mochi/lib/MochiKit/Visual.js'
                
                       
        self.debug_window = pdiv(parent = self.main)
        
        self.background     = Background(parent = self.main)
        self.center_frame   = CenterFrame(parent = self.background)    
        self.panel          = Panel(parent = self.center_frame)
        self.pages          = Pages(parent = self.center_frame)
                        
        self.type    = "Handout"
        self.num     = 1
        self.code    = "MM-ADD5"
        self.cutline = "Mental Math with up to 5 Digit Addition"
        
        
        Page(parent = self.pages)

        #self.event_omd = events.MouseDown(parent = self, default = True, bubble = True)        
        self.event_okd = events.KeyDown(parent = self, default = True, bubble = False)    
        
        self.is_in_hide_state = False

    def onkeydown(self, event):
        if event.ctrl and event.key_code == 57:
            if self.is_in_hide_state is False:
                self.is_in_hide_state = True
                for page in self.pages:
                    page.hide()
            elif self.is_in_hide_state is True:
                self.is_in_hide_state = False
                for page in self.pages:
                    page.show()
 
        elif event.key_code == 116:
            self.debug_window.text = "Help menu"
        else:
            #self.debug_window.text = str(event.key_code) + " " + str(event.__dict__)
            pass
                            
class Background(pdiv):

    @staticmethod
    def css():
        css.prop.min_height         = css.inch(12)
        css.prop.background_color   = css.rgb(240,240,240)
        css.prop.padding            = css.inch(0.1)
        #css.prop.border             = 'solid red 2px'
      
class CenterFrame(pdiv):

    @staticmethod
    def css():
        css.prop.width              = css.inch(11)
        css.prop.margin             = '0.1in auto'
        #css.prop.border             = 'solid blue 2px'
        
class Panel(pdiv):

    @staticmethod
    def css():
        css.prop.border            = 'solid rgb(220,220,255) 2px'
        css.prop.overflow          = 'auto'
        css.prop.background_color  = css.rgb(240,240,255)
        css.prop.height            = css.inch(6)
        css.prop.width             = css.inch(2.8)  
        css.prop.margin            = css.inch(0.1)
        css.prop.float             = css.values.floats.left
        css.prop.position          = css.values.positions.fixed
        css.prop.left              = 'auto'
        css.prop.top               = css.inch(0.20)
        
class Pages(gui.Node):

    def gui_menu_insert(self, parent):
        self.button_insert_page = gui.NodeInsertButtonNode(parent = parent, node = Page)
        

    def __init__(self, parent):        
        gui.Node.__init__(self, parent = parent, root = True)
        
    @staticmethod
    def css():
        css.prop.font_family      = css.values.font_families.verdana
    
    def number(self):
        
        for i,page in enumerate(self):
            page.current_number = i + 1
            page.toolbar.page_num.text = "Page " + str(i+1) + " of " + str(len(self))

"""
Page
"""
class Page(gui.Node):
    
    @staticmethod
    def css():
        css.prop.background_color = css.rgb(255,255,255)
        css.prop.width             = css.inch(7.8)
        css.prop.margin            = css.inch(0.1)
        css.prop.margin_left       = css.inch(3.1)
        #css.prop.border            = 'solid green 2px'
    
    def __init__(self, parent = None, older = None, younger = None):
        
        gui.Node.__init__(self, parent = parent, older = older, younger = younger)
        
        self.header   = Header(parent = self.content)
        self.header_L = Header_L(parent = self.header)
        self.header_R = Header_R(parent = self.header)
        
        logo_img = CatalystLogo(parent = self.header_L)
        t0 = TitleTop(parent = self.header_R, text = self.document.type + " #" + str(self.document.num))            
        t1 = TitleBot(parent = self.header_R, text = self.document.code + ": " + str(self.document.cutline))
        
        self.middle    = Middle(parent = self.content)

        self.footer   = Footer(parent = self.content)
        self.footer_L = Footer_L(parent = self.footer, text = 'Printable Create on 11-24-08 | A Catalyst Printable | http://www.catalystlc.org')
        self.footer_R = Footer_R(parent = self.footer, text = 'Page 1 of 4')
         
#        self.parent.number()
        
    def highlight(self):       
        
        for page in (page for page in self.document.pages.children if page is not self):
            page.unhighlight()
        
        self.style.background_color  = css.rgb(240, 240, 255)
        self.style.border            = 'solid rgb(200,200,255) 0.02in'
        self.is_selected             = True
    
    def unhighlight(self):
        self.style.background_color  = css.rgb(250, 250, 255)
        self.style.border            = 'solid white 0.02in'
        self.is_selected             = False
        
    def show(self):
        self.toolbar.show_hide.show()
        
    def hide(self):
        self.toolbar.show_hide.hide()
        
    def get_pages(self):
        return self.parent.children
       
    def add_page_younger(self):
        Page(older = self)
    
    #def delete(self):
        #parent = self.parent
        #pdiv.delete(self)
        #parent.number()

    def add_section(self):
        sections.Section(parent = self.sections, type = 'How To', title_text = '')
             
"""
Header
"""
class Header(pdiv):

    @staticmethod
    def css():
        css.prop.height           = css.inch(0.4)
        css.prop.padding_bottom   = css.inch(0.25)
            
class Header_L(pdiv):

    @staticmethod
    def css():
        css.prop.width            = css.inch(2.0)
        css.prop.background_color = css.rgb(255, 250, 250)
        css.prop.float            = css.values.floats.left

class Header_R(pdiv):

    @staticmethod
    def css():
        css.prop.width            = css.inch(4.5)
        css.prop.background_color = css.rgb(250, 255, 250)
        css.prop.float            = css.values.floats.left
                       
class CatalystLogo(xhtml.img):
    
    @staticmethod
    def css():
        css.prop.width    = css.pixel(150*0.8)
        css.prop.height   = css.pixel(72*0.8)
        css.prop.position = css.values.positions.relative
        #css.prop.top      = css.inch(-0.2)
 
    def __init__(self, parent):
        xhtml.img.__init__(self, parent = parent, src = images.logo_gif)

class TitleTop(pdiv):
    
    @staticmethod
    def css():
        css.prop.font_size        = css.pt(19)
        css.prop.font_weight      = css.values.font_weights.x500
        css.prop.color            = css.rgb(70, 70, 70)
    
class TitleBot(pdiv):    

    @staticmethod
    def css():
        css.prop.font_size        = css.pt(11)
        css.prop.font_weight      = css.values.font_weights.x400
        css.prop.color            = css.rgb(140, 140, 140)
        
class Middle(pdiv):
    
    @staticmethod
    def css():
        css.prop.width            = css.inch(7.0)
        css.prop.min_height           = css.inch(9)
        css.prop.background_color = css.rgb(245, 255, 245)
   
"""
Footer
"""             
class Footer(pdiv):
    
    @staticmethod
    def css():
        css.prop.width            = css.inch(7.0)
        css.prop.margin_top       = css.inch(0.10)
        css.prop.height           = css.inch(0.3)
        css.prop.border_top       = 'solid 0.01in #BBBBBB'
        css.prop.background_color = css.rgb(255, 245, 245)
        css.prop.font_size        = css.pt(6.5)
        css.prop.letter_spacing   = css.pt(0.25)
        css.prop.color            = "#BBBBBB"
        css.prop.font_family      = css.values.font_families.tahoma

class Footer_L(pdiv):

    @staticmethod
    def css():
        css.prop.padding_left     = sections._left_width
        css.prop.height           = css.inch(0.5)
        css.prop.float            = css.values.floats.left
            
class Footer_R(pdiv):
    @staticmethod
    def css():
        css.prop.text_align       = css.values.text_aligns.right
        
        
#"""
#Toolbar
#"""      
#class Toolbar(pdiv):
#    @staticmethod
#    def css():
#        #css.prop.width             = css.inch(7.4)
#        css.prop.height            = css.pixel(35)
#        css.prop.padding           = css.inch(0.03)
#        css.prop.margin_bottom     = css.inch(0.02)
#        css.prop.background_color  = css.rgb(245,245,255)
#        css.prop.opacity           = 0.5   
#        css.prop.border            = 'rgb(210,210,255) solid 0.020in'
#        css.prop.overflow          = 'auto'
#
#    def __init__(self, parent):
#        
#        pdiv.__init__(self, parent = parent)
#                
#        self.show_hide = ToolbarButton_show_hide(parent = self, title = 'hide')
#        
#        self.page_num = ToolbarText(parent = self)
#
#        self.print_page  = ToolbarButton_PagePrint(parent = self,      title = 'Print Page ...')
#        self.check_in    = ToolbarButton_PageCheckIn(parent = self,    title = 'Check In Printable To Database ...')    
#        self.delete_page = ToolbarButton_PageDelete(parent = self,     title = 'Delete Page ...')
#        self.add_page    = ToolbarButton_PageAddPage(parent = self,    title = 'Add Page ...')
#        self.new_section = ToolbarButton_PageNewSection(parent = self, title = 'Add new section to bottom ...')    
#        
#        self.event_omd = events.MouseDown(parent = self)
#        
#    def onmousedown(self, event):
#        self.parent.highlight()
#
#class ToolbarText(pdiv):
#    
#    @staticmethod
#    def css():
#        css.prop.float               = css.values.floats.left
#        css.prop.margin_left         = css.inch(0.1)
#        css.prop.font_family         = css.values.font_families.verdana
#        css.prop.color               = css.rgb(20,20,20)
#        css.prop.font_size           = css.pt(8)
#        css.prop.padding             = css.inch(0.025)
#
#"""
#Toolbar Buttons
#"""         
#class ToolbarButton(xhtml.button):
#    
#    @staticmethod
#    def css():
#        css.prop.width               = css.pixel(32)#css.inch(0.25)
#        css.prop.height              = css.pixel(32)#css.inch(0.25)
#        css.prop.padding             = css.pixel(3)
#        css.prop.background_color    = css.rgb(245,245,255)
#        css.prop.border              = 'rgb(200, 200, 255) solid 2px'
#        css.prop.background_repeat   = 'no-repeat'
#        css.prop.margin              = css.pixel(4)
#        css.prop.background_position = 'center'
#        css.prop.position            = css.values.positions.relative
#        
#        css.prop.pseudo              = css.values.pseudos.hover
#        css.prop.border              = 'rgb(130, 130, 255) solid 3px'
#        
#        css.prop.pseudo              = css.values.pseudos.active
#        css.prop.background_color    = css.rgb(175,175,255)
#        css.prop.border              = 'rgb(255, 255, 255) solid 3px'
#
#"""
#Toolbar Left
#"""                 
#class ToolbarButton_Left(ToolbarButton):    
#    
#    @staticmethod
#    def css():
#        css.prop.float = css.values.floats.left
#    
#class ToolbarButton_show_hide(ToolbarButton_Left):
#    
#    @staticmethod
#    def css():
#        css.prop.background_image = 'url(' + images.buttons.hide_png + ')'        
#        #css.prop.background_position = '4px 4px'
#
#    def __init__(self, **kwargs):
#        xhtml.button.__init__(self, **kwargs)
#        self.page        = self.parent.parent
#        self.event_omd   = events.MouseDown(parent = self, default = True)
#        self.on          = True
#        
#    def onmousedown(self, event):
#        if self.on is True:
#            self.hide()
#        else:
#            self.show()
#            
#    def hide(self):
#        self.style.background_image = 'url(' + images.buttons.show_png + ')'
#        self.page.content.parent = None
#        self.on = False
#        self.att.title = 'show'
#
#    def show(self):
#        self.style.background_image = 'url(' + images.buttons.hide_png + ')'
#        self.page.content.parent = self.page
#        self.on = True
#        self.att.title = 'hide'
#    
#"""
#Toolbar Right
#"""             
#class ToolbarButton_Right(ToolbarButton):    
#
#    @staticmethod
#    def css():
#        css.prop.float                = css.values.floats.right
#        #css.prop.background_position  = '2px 2px'
#        #css.prop.margin_right         = css.pixel(4)
#    
#    def __init__(self, parent, title):
#        xhtml.button.__init__(self, parent = parent, title = title)
#        self.page = self.parent.parent
#        self.event_omd = events.MouseDown(parent = self, default = True, reporter = {self: 'pos'})
#        self.style.background_image = 'url(' + images.buttons.__dict__[self.__class__.__name__.replace('ToolbarButton_', "") + '_png'] + ')'
#    
#    def onmousedown(self, event):            
#        if event.sensor.__class__ is ToolbarButton_PageAddPage:
#            self.page.add_page_younger()           
#            
#        elif event.sensor.__class__ is ToolbarButton_PageDelete:
#            if len(self.page.get_pages()) > 1:
#                gui.Confirm(parent   = self.document.main,
#                            title    = 'Are you sure you want to delete page ' + str(self.page.current_number) + '?', 
#                            sub      = 'All data including all sections on this page will be lost.',
#                            callback = (self.page, 'delete'),
#                            )
#        
#class ToolbarButton_PageAddPage(ToolbarButton_Right):
#    pass
#
#class ToolbarButton_PageNewSection(ToolbarButton_Right):
#    
#    def __init__(self, parent, title):
#        ToolbarButton_Right.__init__(self, parent, title)
#        self.event_omu = events.MouseUp(parent = self, sensor = self.document, handler = self)
#        self.section_type_menu = None
#    
#    def onmousedown(self, event):
#        self.section_type_menu = sections.SectionTypeMenu(parent = self.document.body, pos = event.report[self]['pos'], handler = self, handler_fn = self.add_new_section)
#    
#    def onmouseup(self, event):
#        if self.section_type_menu:
#            self.section_type_menu.delete()
#            self.section_type_menu = None
#            
#    def add_new_section(self, type):
#        sections.Section(parent = self.page.frame, type = type)
#          
#class ToolbarButton_PagePrint(ToolbarButton_Right):
#    pass
#
#class ToolbarButton_PageDelete(ToolbarButton_Right):
#    pass
#
#class ToolbarButton_PageCheckIn(ToolbarButton_Right):
#    pass
#
#"""
#Content
#"""
#class Content(pdiv):
#    
#    @staticmethod
#    def css():
#        css.prop.width             = css.inch(7.0)
#        css.prop.min_height        = css.inch(10.0)        
#        css.prop.padding           = css.inch(0.23)
#        css.prop.background_color  = css.rgb(250,250,255)
#        css.prop.font_family       = css.values.font_families.verdana
#        css.prop.text_align        = css.values.text_aligns.left 
#        css.prop.background_color  = css.rgb(255,255,255)
#        css.prop.border            = 'rgb(210,210,255) solid 0.020in'

