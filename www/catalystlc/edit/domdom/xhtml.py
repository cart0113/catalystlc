import os
import sys
import exceptions
import inspect

from dom import Document,Element,Text,DomDomError
import css
import settings
import events

class XhtmlError(exceptions.Exception):
    pass

"""
Includes -- 

This allows: self.includes.css <= sys.modules['__main__']     
"""
class Includes(object):
    
    def __init__(self, document):
        object.__setattr__(self, 'document', document)
        
    def __setattr__(self, key, value):
        raise DomDomError, "You cannot set an attribute of this special 'include' namespace"
    
    def __getattr__(self, key):
        
        if(key == 'css' and key not in self.__dict__):
            object.__setattr__(self, key, IncludesCSS(document = self.document))
            return self.__dict__[key]
        elif(key == 'js' and key not in self.__dict__):
            object.__setattr__(self, key, IncludesJS(document = self.document))
            return self.__dict__[key]
        else:
            return object.__getattr__(self, key)
        
class IncludesCSS(object):
    
    def __init__(self, document):
        self.document = document
        self.links   = []
        
    def __le__(self, module):
        
        if(inspect.ismodule(module)):
            css_name = module.__name__
            css_dir  = settings.get_dir_css()
            css_file = css_dir + os.sep + css_name + '.domdom.css'
            # FIXME: Take out 'dsaf'  this is just to force reload . . .
            if(os.path.isfile(css_file + 'dsaf')):
                pass
            else:
                self.create_css_file(module = module, css_file = css_file)                
            self.links.append(settings.get_url_css() + "/" + css_name + '.domdom.css')
        else:
            self.links.append(module)

        if(isinstance(self.document, Document)):
            self.document.add_css_link(self.links[-1])                

    def create_css_file(self, module, css_file):
        
        inline_css = getattr(module, 'inline_css', None)
        
        if inline_css and inspect.isfunction(inline_css):
            css_text = inline_css() + "\n\n"
        else:
            css_text = ""
            
        for object in dir(module):
            css_text = self.create_css_for_object(css_text = css_text, object = module.__dict__[object])   
        open(css_file, 'w').write(css_text)
    
    def create_css_for_object(self, css_text, object):
        
        if inspect.isclass(object) and issubclass(object, Element) and inspect.isroutine(object.__dict__.get('css', None)):
            
            css.prop.start_css(tag = object.TAG_NAME, css_class = css.get_css_name(cls = object))
            object.css()
            css_text += css.prop.get_css() + "\n\n"
    
            for item in object.__dict__:
                css_text = self.create_css_for_object(css_text = css_text, object = item)

        return css_text

class IncludesJS(object):
    
    def __init__(self, document):
        self.document = document
        self.links    = []

    def __le__(self, url):
        self.links.append(url)
        if(isinstance(self.document, Document)):
            self.document.add_js_src(self.links[-1])    

"""
Js namespace -- this is used for calling javascript directly in the form: 

self.js.some_function(10, 20, 30)
"""
class JsDocument(object):
    
    def __init__(self, document):
        self._document = document

    def __getattr__(self, key):
        return JsCall(document = self._document, name = key)

class JsElement(object):
    
    def __init__(self, element):
        self._element = element
    
    def __getattr__(self, key):
        return JsCall(document = self._element.document, name = key, element = self._element)

class JsCall(object):
    
    def __init__(self, document, name, element = None):
        self.document = document
        self.name     = name
        # element is like a default arg -- the id of the element . . . 
        self.element  = element
    
    def __call__(self, *args):
        # element is like a default arg -- the id of the element . . . 
        self.document.dom.js_execute(fn = self.name, element = self.element, args = args)

"""
webpage -- the document that does it all
"""
class webpage(Document):

    def __init__(self):
                
        Document.__init__(self)
                        
        self.html     = getattr(self.__class__, 'html',  html)(document     = self)    #, xmlns="http://www.w3.org/1999/xhtml", dir="ltr", xml_lang="en")
        self.head     = getattr(self.__class__, 'head',  head)(parent       = self.html)
        self.title    = getattr(self.__class__, 'title', title)(parent      = self.head)
        self.body     = getattr(self.__class__, 'body',  body)(parent       = self.html)
        self.main     = getattr(self.__class__, 'main',  div)(parent        = self.body)
        
        self.includes      = Includes(document = self)
        self.includes.js  <= settings.get_url_domdom_javascript()
        self.includes.css <= sys.modules[__name__] 

        # JAVASCRIPT
        self.commands = script_js_commands(parent = self.html)        
        
        self.root     = self.html
              
    def __getattr__(self, key):
        if key == 'js':
            return JsDocument(document = self)
        else:
            return Document.__getattribute__(self, key)
                       
    def add_css_link(self, link):
        link_css(parent = self.head, href = link)
        
    def add_js_src(self, src):
        script_js(parent = self.head, src = src)  

    def pre_publish_document(self):
        if self.title.text is None:
            self.title.set_to_default()

"""
Elements
"""
class Tag(Element):
    
    POD_NO_TAG    = True

    def __getattr__(self, key):
        if key == 'js':
            return JsElement(document = self)
        else:
            return Element.__getattribute__(self, key)

class a(Tag):    
    def __init__(self, parent = None, href = None, text = None, **kwargs):
        Tag.__init__(self, parent = parent, text = text, href = href, **kwargs)

class body(Tag):
    
    @staticmethod
    def css():
        css.prop.vertical_align         = css.values.vertical_aligns.top        
        css.prop.padding                = css.pixel(0)
        css.prop.margin                 = '0 auto'

class br(Tag):
    pass

class button(Tag):
    ONE_TAG = False
    def __init__(self, parent = None, text = None, title = None, **kwargs):
        Tag.__init__(self, parent = parent, text = text, title = title, **kwargs)
         
class div(Tag):
    
    ONE_TAG = False

    @staticmethod
    def css():
        #css.prop.overflow  = 'auto'
        pass
        
class form(Tag):
    pass

class head(Tag):
    pass

class meta(Tag):
    pass

class html(Tag):
    pass

class iframe(Tag):
    pass

class img(Tag):
    
    def __init__(self, parent, src = None, alt = None, height = None, width = None, longdesc = None, **kwargs):
        Tag.__init__(self, parent = parent, src = src, alt = alt, height = height, width = width, longdesc = longdesc, **kwargs)
                
class input(Tag):
    
    def __init__(self, parent, type = None, value = None, text = None, **kwargs):
        Tag.__init__(self, parent = parent, text = text, type = type, value = value, **kwargs)
      
class input_text(input):
    
    NO_BREAK_AT_END = True
    ONE_TAG         = False
    ADD_TO_CSS      = False
    
    def __init__(self, parent, value = None, **kwargs):
        input.__init__(self, parent = parent, type = "text", value = value, **kwargs)
        
        
    def get_value(self):
        return self.att.value

class input_text_oninput(input_text):

    def __init__(self, parent, value = None, **kwargs):
        input.__init__(self, parent = parent, type = "text", value = value, **kwargs)
        self.event_oin = events.Input(parent = self)
        
class input_text_onoutput(input_text):
    
    def __init__(self, parent, value = None, title = None, **kwargs):
        input.__init__(self, parent = parent, type = "text", **kwargs)
        self.att.value = "" if value is None else value
        self.event_oou = events.Output(parent = self, default = True, bubble = False)
    
class radio(input):
    pass

class select(Tag):
    
    def __init__(self, parent = None, options = None, value = None, **kwargs):
        Tag.__init__(self, parent = parent, **kwargs)

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

class option(Tag):
    
    def __init__(self, parent, text):
        Tag.__init__(self, parent = parent, text = text)
        if text == parent.value:
            self.att.selected = "yes"

class link(Tag):
    
    def __init__(self, parent, href, rel, type, **kwargs):
        Tag.__init__(self, parent = parent, rel = rel, type = type, href = href, **kwargs)
    
class link_css(link):
    
    def __init__(self, parent, href, **kwargs):
        link.__init__(self, parent = parent, href = href, rel = "stylesheet", type = "text/css", **kwargs)

class script(Tag):
    
    def __init__(self, parent, type, language, src = None, **kwargs):
        Tag.__init__(self, parent = parent, type = type, language = language, src = src, **kwargs)
       
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

    def __init__(self, parent):
        script_js.__init__(self, parent = parent)
        self.commands = []
        
    def append(self, command, persist = False):
        command = command.strip()
        #command = util.escape(string = command)
        if(command[-1] != ";"):
            command += ";"        
        
        if(self.document.pod.update.in_update_mode is True):
            self.document.pod.update.commands.append(command)
        
        if(self.document.pod.update.in_update_mode is False or (self.document.pod.update.in_update_mode is True and persist)):
            self.commands.append( [command, persist] )
        
    def _get_xml_children(self, output = "", newline = "\n", ctab = "", tab = "\t"):
        for command in self.document._get_dom_commands() + [command[0] for command in self.commands]:
            if(len(command) > 0):
                output += ctab + tab + command  + newline
        self.commands = [[command[0], True] for command in self.commands if command[1] is True]
        return output
    
    def pop(self):
        return self.commands.pop()
    
    def first(self):
        return self.commands[0]

    def last(self):
        return self.commands[-1]
    
class span(Tag):
    pass

class table(Tag):
    ONE_TAG = False

class td(Tag):
    ONE_TAG = False

class textarea(Tag):
    pass

class textarea_oninput(textarea):

    def __init__(self, parent, value = None, **kwargs):
        textarea.__init__(self, parent = parent, **kwargs)
        self.att.value = "" if value is None else value
        self.event_oin = events.Input(parent = self, default = True)
        
class textarea_onoutput(textarea):
    
    def __init__(self, parent, value = None, **kwargs):
        textarea.__init__(self, parent = parent, **kwargs)
        self.att.value = "" if value is None else value
        self.event_oou = events.Output(parent = self, default = True)
    
class title(Tag):
    
    def set_to_default(self):
        self.text = str(self.document.__class__).replace("<", "").replace(">", "")

class tr(Tag):
    ONE_TAG = False


    
