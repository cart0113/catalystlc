import os
import sys
import exceptions

from dom import Document,Element,Text,DomDomError
import css
import settings
import events

class XhtmlError(exceptions.Exception):
    pass

"""
Elements
"""

class a(Element):    
    def __init__(self, parent = None, href = None, text = None, **kwargs):
        Element.__init__(self, parent = parent, text = text, href = href, **kwargs)

class body(Element):
    
    @staticmethod
    def css():
        css.prop.vertical_align         = css.values.vertical_aligns.top        
        css.prop.padding                = css.pixel(0)
        css.prop.margin                 = '0 auto'

class br(Element):
    pass

class button(Element):
    ONE_TAG = False
    def __init__(self, parent = None, text = None, title = None, **kwargs):
        Element.__init__(self, parent = parent, text = text, title = title, **kwargs)
         
class div(Element):
    
    ONE_TAG = False

    @staticmethod
    def css():
        #css.prop.overflow  = 'auto'
        pass
        
class form(Element):
    pass

class head(Element):
    pass

class meta(Element):
    pass

class html(Element):
    pass

class iframe(Element):
    pass

class img(Element):
    
    def __init__(self, parent, src = None, alt = None, height = None, width = None, longdesc = None, **kwargs):
        Element.__init__(self, parent = parent, src = src, alt = alt, height = height, width = width, longdesc = longdesc, **kwargs)
                
class input(Element):
    
    def __init__(self, parent, type = None, value = None, text = None, **kwargs):
        Element.__init__(self, parent = parent, text = text, type = type, value = value, **kwargs)
      
class input_text(input):
    
    NO_BREAK_AT_END = True
    ONE_TAG         = False
    ADD_TO_CSS      = False
    
    def __init__(self, parent, value = "", **kwargs):
        input.__init__(self, parent = parent, type = "text", value = value, **kwargs)
        
    def get_value(self):
        return self.att.value        
    
class radio(input):
    pass

class select(Element):
    
    def __init__(self, parent = None, options = None, value = None, **kwargs):
        Element.__init__(self, parent = parent, **kwargs)

        options = [] if options is None else options 
        
        if value:
            if value in options:
                self.value = value
            else:
                raise XhtmlError, "Value is not in list of options"
        else:
            if len(options) > 0:
                self.value = options[0]
            else:
                self.value = None
            
        for an_option in options:
            option(parent = self, text = an_option)
            
        self.event_osc = events.Change(parent = self)
        
    #All select elements have an _onfire method which is called by the event handler. 
    def _onfire(self, value):
        self.value = value
        for an_option in self.children:
            if self.value == an_option.text:
                an_option.att.__setattr__('selected', "yes", update = False)
            elif 'selected' in an_option.att.__dict__:
                an_option.att.__delattr__('selected')

class option(Element):
    
    def __init__(self, parent, text):
        Element.__init__(self, parent = parent, text = text)
        if text == parent.value:
            self.att.selected = "yes"

class link(Element):
    
    def __init__(self, parent, href, rel, type, **kwargs):
        Element.__init__(self, parent = parent, rel = rel, type = type, href = href, **kwargs)
    
class link_css(link):
    
    def __init__(self, parent, href, **kwargs):
        link.__init__(self, parent = parent, href = href, rel = "stylesheet", type = "text/css", **kwargs)

class script(Element):
    
    def __init__(self, parent, type, language, src = None, **kwargs):
        Element.__init__(self, parent = parent, type = type, language = language, src = src, **kwargs)
       
class script_js(script):
    
    NO_BREAK_AT_END = True
    ONE_TAG         = False
    ADD_TO_CSS      = False
 
    def __init__(self, parent, src = None, **kwargs):
        script.__init__(self, parent = parent, type = "text/javascript", language = "javascript", src = src)

class script_js_commands(script_js):
    
    NO_BREAK_AT_END = False
    ONE_TAG         = False 
    ADD_TO_CSS      = False
    
    """ The DOM namespace """
    class Dom(script_js.Dom):
        
        def get_xml_children(self, output = "", newline = "\n", ctab = "", tab = "\t"):
            for command in self.commands:
                output += ctab + tab + command + newline
            return output
            
        def set_xml_js_commands(self, commands):
            self.commands = commands
    
class span(Element):
    pass

class table(Element):
    ONE_TAG = False

class td(Element):
    ONE_TAG = False

class textarea(Element):

    def __init__(self, parent, value = "", **kwargs):
        Element.__init__(self, parent = parent, value = value, **kwargs)
    
class title(Element):
    
    def set_to_default(self):
        self.text = str(self.document.__class__).replace("<", "").replace(">", "")

class tr(Element):
    ONE_TAG = False

"""
webpage -- the document that does it all
"""

class webpage(Document):

    element_root        = html
    element_includes    = head
    element_css_link    = link_css
    element_js_src      = script_js
    element_js_commands = script_js_commands
    element_title       = title
    element_body        = body
    element_main        = div

    def __init__(self):
        
        Document.__init__(self)
        
        self.html  = self.set_element_root() 
        self.head  = self.set_element_includes(parent = self.html) 
        self.title = object.__getattribute__(self, '__class__').element_title(parent = self.head)
        self.body  = object.__getattribute__(self, '__class__').element_body(parent  = self.html)
        self.main  = object.__getattribute__(self, '__class__').element_main(parent  = self.body)
        
        self.includes.js  <= settings.urls.get_domdom_javascript()
        self.includes.css <= sys.modules[__name__] 

        # JAVASCRIPT
        self.set_element_js_commands(parent = self.html)        
                               

    def pre_publish_document(self):
        if self.title.text is None:
            self.title.set_to_default()
