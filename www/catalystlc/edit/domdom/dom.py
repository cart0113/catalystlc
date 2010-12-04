import exceptions
import time

import pod
import settings
import css

"""
The basis of Document and Element
"""         
class DomObject(pod.Object):    
    
    def __new__(cls, **kwargs):
        inst = pod.Object.__new__(cls)
        inst.events = Events()
        inst.events_to_sensor = set()
        inst.events_to_handle = set()
        return inst
    
    #def get_printable_html(self, br = True):
    #     html = "<br/>" if br is True else ""
    #     return html + str(self).replace("<", "").replace(">", "")

    def on_load_from_db(self):
        self.dom = self.__class__.Dom(self)

"""
Document
"""
class DomDomError(exceptions.Exception):
    pass
    
class Document(DomObject):
            
    class DOC_TYPE:
        class html_4:
            strict          = r'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">'
            transitional    = r'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">'
            frameset        = r'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN" "http://www.w3.org/TR/html4/frameset.dtd">'
        class xhtml_1:
            strict          = r'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
            transitional    = r'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
            frameset        = r'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">'
        class xhtml_11:
            dtd             = r'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">'

    """ Class Methods """
    @classmethod
    def route(cls, request, url_args, doc_type = None):
        request.url_args = url_args
        inst = cls.__new__(cls)
        inst.request      = request
        inst.doc_type     = doc_type
        inst.__init__()
        return inst.dom.publish()
     
    @classmethod
    def handle_event_error(cls):
        if settings.chatty:
             "\tDomDom could not find a DomObject to handle the event (maybe it's deleted), so we will reload the page . . . "
        return "window.location.reload();"
                
    @classmethod
    def init_user(cls, request):
        user = request.get_cookie(settings.user_cookie)
        if user is None:
            user = request.get_client_ip() + ":" + str(int(time.time()))
            request.set_cookie(settings.user_cookie, user)
        request.user = user
       
    def __new__(cls):

        inst = DomObject.__new__(cls)
        
        inst.document     = inst
        inst.request      = None
        inst.root         = None
        inst.doc_type     = None
                
        # By default, the update is updated server.Router in response to a returned event
        inst.dom          = inst.__class__.Dom(document = inst)
                
        return inst
       

            
    """
    API
    """        
    def redirect(self, url):
        if self.dom.in_update_mode:
            self.dom.redirect_url = url
        else:
            self.request.redirect(url = url)
            
    def onunload(self, event):
 
        if settings.chatty:
            print "\tUnloading document " + str(self.__class__) + " . . ."
        
        self.__class__.handle_unload(document = self)
        
    def get_user(self, user):
        return self.request.get_user()
    
    def set_user(self, user):
        return self.request.set_user(user = user)

    def pre_publish_document(self):
        pass

    def pre_publish_ajax(self):
        pass
    
    def delete(self):
        self.html.delete()

        for event in self.events:
            event.delete()
        
        self.pod.delete()    
        
        settings.db.commit(clear_cache = False, close = False)
    
    class Dom(pod.NoSave):

        def __init__(self, document):
            self.document            = document
            self.in_update_mode      = False     
            self.js_commands         = [] 
  
        def __getitem__(self, key):

            if key not in self.updates:
                self.update_list.append(key)
                self.updates[key] = {} 

            return self.updates[key]
                        
        def get_tag_name(self):
            return ""

        def get_xml(self, output = "", newline = settings.newline, tab = settings.tab):
            return self.document.root.dom.get_xml(output = Document.DOC_TYPE.xhtml_1.strict + '\n' if self.document.doc_type is None else self.document.doc_type,
                                                  newline = newline, 
                                                  tab = tab, 
                                                  ctab = "")
    
        def get_dom_commands(self):
    
            commands = []
            """ millisecond time stamp used for complete id identification """            
            self.dtime    = str(int(time.time()*1000))
            commands     += ['document.id = "' + self.get_full_id() + '";']
            commands     += ['domdom.elements["' + self.get_full_id() + '"] = document;']
            commands     += ["domdom.dtime = " + self.dtime + ';']
            commands     += ['domdom.event_url = "' + settings.get_url_event() + '";']
            commands     += ['domdom.main = domdom.get("' + self.main.get_full_id() + '");']
            
            for event in self.events:
                commands = event.get_dom_commands(commands = commands)
      
            commands = self.html.get_dom_commands(commands = commands)
            
            commands += self.js_commands
            
            self.js_commands = []
            
            return commands
               
        def get_dtime(self):
            return int(self.dtime)  

        def js_execute(self, fn, element, args = None):
            
            if element is not None:
                farg = '"' + element.get_full_id() + '"'
            else:
                farg = ''
            
            if args is None: 
                nargs = '(' + farg + ')'
            elif isinstance(args, tuple):
                if len(args) == 0:
                    nargs = '(' + farg + ')'
                else:
                    nargs = '(' if element is None else '(' + farg + ','
                    for elem in args:
                        if isinstance(elem, pod.Object):
                            nargs += '"' + elem.get_full_id() + '",'
                        elif isinstance(elem, str):
                            nargs += '"' + elem + '",'
                        else:
                            nargs +=  str(elem) + ','                
                    nargs = nargs[0:-1] + ')'
                    
            elif isinstance(args, str):
                nargs = '("' if element is None else '(' + farg + ',"'
                nargs += args + '")'
                args = str(args)
            else:
                nargs = '(' if element is None else '(' + farg + ','
                nargs += '(' + str(args) + ')'
    
            # You cannot have <> directly into js
            fn = 'domdom.' + fn + nargs + ';'
            
            if self.update is None:
                self.js_commands.append(fn)
            else:
                self.post_fn(fn)

        def enter_update_mode(self, request):
            self.request          = request
            self.update_mode      = True
            self.redirect_command = None

            self.update_list      = []
            self.updates          = {}

        def exit_update_mode(self):
            self.request          = None
            self.update_mode      = False
            self.redirect_command = None

            del self.update_list
            del self.updates          
              
        def get_element_update(self, update):
            
            if isinstance(update, list):
                for i in range(len(update)):
                    update[i] = self.get_element_update(update[i])
            elif isinstance(update, dict):
                for key,value in update.iteritems():
                    update[key] = self.get_element_update(value)
            elif isinstance(update, (str, int, float, list, set, tuple)):
                    update = str(update)
            else: 
                update = update.get_ajax()

            return update
                
        def update(self, element = None, type = True, key = None, value = None):
                  
            if self.in_update_mode is False:
                return      
            
            element = self.document if element is None else element
                               
            if type == 'create':
                css_class = getattr(element.__class__, 'CSS_CLASS', "").strip()
                if len(css_class) > 0:
                    self.post_update(element, type = 'att', key = 'css_class', value = css_class)                            
                att = getattr(element.__class__, 'att', None) 
                if att:
                    for k,v in att.__dict__.iteritems():
                        if k in Att.allowed.__dict__ and k not in ['__module__', '__doc__']:
                            self.post_update(element, type = "att", key = k, value = v)
            
            element_id = element.get_full_id()
            
            # mod updates            
            if type in ['create', 'del', 'parent', 'insert', 'str', 'event']:
                if 'mod' not in self[element_id]: self[element_id]['mod'] = {}
                if type in ['str', 'event']:
                    if type not in self[element_id]['mod']: self[element_id]['mod'][type] = []                       
                    self[element_id]['mod'][type].append({key: value})
                elif type in ['create', 'insert']:
                    self[element_id]['mod'][type] = key                                
                    if type == 'insert' and 'parent' in self[element_id]['mod']:
                        del self[element_id]['mod']['parent'] 
                elif type in ['del']:
                    self[element_id]['mod']['del'] = 'true'                    
                elif type in ['parent']:
                    if type not in self[element_id]['mod']: self[element_id]['mod'][type] = {} 
                    if type == 'state': value = State.get_value(value = value)      
                    self[element_id]['mod'][type][key] = value

            # att, style update
            elif type in ['att', 'style']:                
                if type not in self[element_id]: self[element_id][type] = {}
                if type == 'att':
                    key = Att.allowed.__dict__[key]
                elif type == 'style':
                    key = css.python_2_js.__dict__[key]
                self[element_id][type][key] = value                
            elif type == 'state':
                State.make_js(element = element, key = key, value = value)
            else:
                raise DomDomError, "Type '" + type + "' not supported . . . "
            
        def get_ajax(self):
            
            if self.redirect_command:
                output = 'window.location = "' + str(self.redirect_command) + '"'
            else:
                output = ""                
                for update in self.update_list:
                    if isinstance(update, tuple):
                        output += update[1] + '\n'
                    else:
                        output += 'domdom.update("' + update + '",' + str(self.get_element_update(self.updates[update])) + ');\n'    

            self.exit_update_mode()

            return output

        def post_fn(self, fn):
            self.update_list.append(('fn', fn))

        def publish(self, pod_commit = True, clear_cache = None, close = None):
            
            if self.in_update_mode is False:  
                self.document.pre_publish_document()                  
                output = self.get_xml()
            else: 
                self.document.pre_publish_ajax()
                output = self.get_ajax()
    
            if pod_commit:
                self.document.pod.db.commit(clear_cache = clear_cache if clear_cache is not None else settings.pod.clear_cache, 
                                            close       = close       if close       is not None else settings.pod.close, 
                                            )
                
            return output

 
"""
Element
"""
class ElementMetaClass(pod.Meta):
    
    def __init__(cls, name, bases, dict):
        
        pod.Meta.__init__(cls, name, bases, dict)

        if(bases[0] is DomObject):
            cls.TAG_NAME = 'DOMDOM_ELEMENT'
        else:
            parent = [base for base in bases if issubclass(base, Element)][0]
                        
            if parent.__dict__.get('POD_NO_TAG', False):
                cls.TAG_NAME = name
                cls.CSS_CLASS = ""
            else:
                cls.TAG_NAME = parent.TAG_NAME
                if('css' in cls.__dict__ and 'CSS_CLASS' not in cls.__dict__):
                    cls.CSS_CLASS = parent.CSS_CLASS + css.get_css_name(cls) + " "
                                                                  
class Element(DomObject):
    
    __metaclass__ = ElementMetaClass
    
    POD_NO_TAG    = True
        
    def __init__(self, document = None, parent = None, older = None, younger = None, text = None, **kwargs):
                    
        # DO NOT CALL BASE CONSTRUCTOR -- NO NEED.  WE WANT TO PROCESS kwargs IN SPECIFIC WAY (AT BOTTOM) 
        
        # First, create reference to document, which is needed for updating dom on ajax call . . .
        self.document  = document        

        # Next, create dom namespace 
        self.dom = self.__class__.Dom(element = self)
                
        if older:
            if older.parent is None:
                raise DomDomError, "You cannot use node '" + str(older) + "' as 'older' . . . it has no parent . . . "
            older.insert_after_me(self)
        elif younger:
            if younger.parent is None:
                raise DomDomError, "You cannot use node '" + str(younger) + "' as 'younger' . . . it has no parent . . . "
            younger.insert_before_me(self)
        else:
            self.parent = parent
        
        self.children  = Children()
        # Note self.Events is set in in DomObject.__init__ -- since both documents and elements can have events. 
        
        self.text      = text 
        
        self.att       = Att(  element = self)
        self.style     = Style(element = self)
        self.state     = State(element = self)
  
        for key,value in kwargs.iteritems():
            if value is None:
                pass
            elif key in css.prop.__dict__:
                self.style.__setattr__(key, value)
            elif key in Att.allowed.__dict__:
                self.att.__setattr__(key, value)
            elif isinstance(value, Element):
                self.__dict__[key] = value
            else:
                raise DomDomError, "Attribute " + key + " is not supported at this time . . . "
     
    def __setattr__(self, key, value):
        
        #===============================================================================================================================
        # parent
        #===============================================================================================================================
        if key == 'parent' or key == '_younger':
            # valid types: None | Element            
            old_parent = getattr(self, 'parent', None)
            if value is None:
                if old_parent:
                    list.remove(old_parent.children, self)
                    self.dom.update(type = "parent", key = "remove", value = old_parent.get_full_id())
                DomObject.__setattr__(self, key, None)
            else:
                self.document = value.document

                if old_parent: 
                    list.remove(old_parent.children, self)

                if key == 'parent':
                    if(value.text): 
                        raise DomDomError, "This element " + str(value) + " already has text!  It cannot have children . . ."
                    DomObject.__setattr__(self, key, value)
                    list.append(value.children, self)
                    self.dom.update(type = "parent", key = "add", value = value.get_full_id())
                elif key == '_younger':
                    DomObject.__setattr__(self, 'parent', value.parent)
                    list.insert(value.parent.children, value.parent.children.index(value), self)
                    self.dom.update(type = "insert", key = value.get_full_id())
                        
        #===============================================================================================================================
        # document
        #===============================================================================================================================
        elif(key == 'document'):
            # This is for enter_update_mode -- it can only be set to None once . . .
            add_document = False
            if(key not in self.__dict__):
                if(value is None):
                    DomObject.__setattr__(self, key, None)
                elif(isinstance(value, Document)):
                    DomObject.__setattr__(self, key, value)  
                else:
                    raise DomDomError, "You cannot enter_update_mode the element document attribute to value " + str(value) + " . . ."  
            # valid types: Document
            elif(self.document is None and isinstance(value, Document)):
                DomObject.__setattr__(self, key, value)  
            elif(self.document is not value):
                raise DomDomError, "Element's document already set.  You cannot set it to another document.  You tried to set it to " + str(value) + " . . ."
        #===============================================================================================================================
        # children, att, style
        #===============================================================================================================================
        elif key in ['children', 'events', 'att', 'style', 'state', 'js']:
            if key not in self.__dict__ :
                DomObject.__setattr__(self, key, value)
            else:
                raise DomDomError, "You cannot set " + key + " directly . . ."     
        #===============================================================================================================================
        # text
        #===============================================================================================================================       
        elif key == 'text' :
            if value is None :
                DomObject.__setattr__(self, key, None)
            elif isinstance(value, str):
                Text(element = self, text = str(value))  # The element's local element.text field is set in Text constructor . . . 
            else:
                raise DomDomError, "You cannot assign to element.text value " + str(value) + " which is of object type " + str(type(value)) + " . . . "
        #===============================================================================================================================
        # forbidden keys!
        #===============================================================================================================================       
        elif key in ['__class__', 'pod']:
            raise DomDomError, key + " is a read-only attribute on domdom elements . . . "
        #===============================================================================================================================
        # else, just set it . . .
        #===============================================================================================================================       
        else:
            DomObject.__setattr__(self, key, value)
              
    def __iter__(self):
        return self.children.__iter__()

    def __len__(self):
        return self.children.__len__()
                  
    """
    API
    """        
    def get_younger(self):
        try:
            return self.parent.children[self.parent.children.index(self)+1]
        except IndexError:
            return None
           
    def get_older(self):
        pos = self.parent.children.index(self)
        if pos > 0:
            return self.parent.children[pos-1]
        else:
            return None
    
    def insert_before_me(self, element):
        element._younger = self
        
    def insert_after_me(self, element):
        if(self.parent.children[-1] is self):
            element.parent = self.parent
        else:
            self.parent.children[self.parent.children.index(self)+1].insert_before_me(element = element)

    def delete(self, send_update = True):        

        # First, delete my events, so any events are cleared and won't cause error on delete in next step. 
        for event in self.events:
            event.delete(send_update = False)
        
        if self.events_to_sensor:
            raise DomDomError, "You cannot delete " + str(self) + " this is a sensor for registered events " + str(self.events_to_sensor)

        if self.events_to_handle:
            raise DomDomError, "You cannot delete " + str(self) + " this is a handler for registered events " + str(self.events_to_handle)
        
        # First, delete all my children -- However, do not send an update to the browser.  Only the first deleted
        # item will send the update.
        for element in self.children:
            element.delete(send_update = False)
                        
        # Then, clear myself from parents list
        if self.parent:
            list.remove(self.parent.children, self)
        
        if send_update:
            # Then, update the client DOM
            self.dom.update(type = "del", key = True) # True not really needed . . . 
        
        # Last, delete from pod db . . . 
        self.pod.delete()
    
    def redirect(self, url):
        self.document.redirect(url)
                    
    def pre_get_xml(self):
        pass
           
    """
    The DOM namespace
    """
    class Dom(pod.NoSave):
        
        def __init__(self, element):            
            self.element = element
            self.update(type = "create", key = self.get_tag_name())
            
        def get_tag_name(self):
            return self.element.__class__.TAG_NAME

        def get_xml(self, output = "", newline = "\n", ctab = "", tab = "\t"):
            self.element.pre_get_xml()
            output = self.get_xml_start(output = output, newline = newline, ctab = ctab, tab = tab)
            output = self.get_xml_children(output = output, newline = newline, ctab = ctab, tab = tab)
            return self.get_xml_end(output = output, newline = newline, ctab = ctab, tab = tab)
                  
        def get_xml_start(self, output = "", newline = "\n", ctab = "", tab = "\t"):
            output += ctab + "<" + self.get_tag_name() + ' id="' + self.element.get_full_id() + '"'
            # get_xml class
            css_class = getattr(self.element.att, 'css_class', getattr(self.element.__class__, 'CSS_CLASS', "")).strip()
            if len(css_class) > 0:
                output += ' class="' + css_class + '"'
            # get_xml atts
            if len(self.element.att.kvp) > 0:
                output += self.element.att.get_xml() 
            # get_xml style
            if len(self.element.style.kvp) > 0:
                output += ' ' + self.element.style.get_xml() 
            if self.get_is_one_tag():
                output += "/>" + newline
            else:
                newline = "" if (getattr(self.element, 'NO_BREAK_AT_END', False) or self.element.text) else newline
                output += ">" + newline
            return output
            
        def get_xml_children(self, output = "", newline = "\n", ctab = "", tab = "\t"):
            if self.element.text:
                output = self.element.text.get_xml(output = output, newline = newline, ctab = ctab + tab, tab = tab)
            else:
                for child in self.element.children:
                    output = child.dom.get_xml(output = output, newline = newline, ctab = ctab + tab, tab = tab)
            return output
        
        def get_xml_end(self, output = "", newline = "\n", ctab = "", tab = "\t"):
            if self.get_is_one_tag() is False :
                ctab = "" if (getattr(self.element.__class__, 'NO_BREAK_AT_END', False) or self.element.text) else ctab
                output += ctab + "</" + self.get_tag_name() + ">" + newline
            return output
                
        def get_dom_commands(self, commands):
            
            for event in self.element.events:
                commands = event.get_dom_commands(commands = commands);
                
            self.element.state.make_js_on_load()
    
            # children
            for child in self.element.children:
                commands = child.dom.get_dom_commands(commands = commands)
    
            return commands
        
        def get_is_one_tag(self):
            return getattr(self.element.__class__, 'ONE_TAG', (len(self.element.children) == 0 and self.element.text is None))
             
        def get_dtime(self):
            return int(self.document.dtime)
        
        def update(self, type, key = None, value = None):
            if self.element.document:
                self.element.document.dom.update(element = self.element, type = type, key = key, value = value)
        
        def debug_alert_dict(self):
            self.document.commands.append('domdom.debug_alert_dict("' + self.element.get_full_id() + '")')
               
"""
Element Attributes -- children, text, att, style
"""     
class Objects(list):

    def __setitem__(self, key, value):
        raise DomDomError, "You cannot set a domdom " + self.__class__.__name__ + " list directly . . . "

    def append(self, child):
        raise DomDomError, "You cannot append to a domdom " + self.__class__.__name__ + " list.  Try 'some_element.parent = some_parent' instead of some_parent.children.append(some_element) . . . "
    
    def clear(self):
        try:
            self[0].delete()
            return self.clear()
        except IndexError:
            return None
        
    def remove(self, child):
        raise DomDomError, "You cannot remove an element of a domdom " + self.__class__.__name__ + " list . . . try setting element's parent to None . . . "
    
    def pop(self):
        raise DomDomError, "You cannot pop an element of a domdom " + self.__class__.__name__ + " list . . . try parent.children[-1].parent = None . . . "
    
    def insert(self, pos, child):
        raise DomDomError, "You cannot insert into a domdom " + self.__class__.__name__ + " list . . ."

class Children(Objects):
    pass

class Events(Objects):
    pass

class Text(str):
    
    def __new__(cls, element, text, update = True):
        if(len(getattr(element, 'children', [])) > 0):
            raise DomDomError, "You cannot assign text to an element which has children element nodes.  First set children to empty list [] . . . "
        self = str.__new__(cls, text)
        DomObject.__setattr__(element, 'text', self)
        if update:  # THIS IS DUE TO FACT THAT backspace() CREATES NEW STRING (SINCE STRINGS ARE IMMUTABLE) BUT WE DON'T WANT JS UPDATED.
            element.dom.update(type = "str", key = 'set', value = self)
        self.element   = element
        return self
                
    def append(self, new_text):
        self.element.dom.update(type = "str", key = 'add', value = str(new_text))
        return Text(element = self.element, text = str.__add__(self, str(new_text)), update = False)
        
    def backspace(self, times = 1):        
        self.element.dom.update(type = "str", key = 'del', value = times)
        return Text(element = self.element, text = self[:-1*times], update = False)
    
    def get_xml(self, output = "", newline = "\n", ctab = "", tab = "\t"):
        str = self.replace("\n", "").replace("\t", "").replace("  ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ")
        return output + str
     
class ElementNameSpace(pod.Object):
            
    def __init__(self, element):
        pod.Object.__setattr__(self, 'element',  element)
        pod.Object.__setattr__(self, 'kvp',     {})

    def __setattr__(self, key, value, update = True):
        is_new = True if key not in self.kvp else False
        self.kvp[key] = value
        if update:
            if value is not None:
                self.element.dom.update(type = self.__class__.__name__.lower(), key = key, value = str(value))
            elif is_new: 
                self.element.dom.update(type = self.__class__.__name__.lower(), key = key, value = "")
        
    def __getattr__(self, key):
        
        if key in self.kvp:
            return self.kvp[key]
        else:
            raise AttributeError, key
    
    def __delattr__(self, key):
        if key in self.kvp:
            del self.kvp[key]
            self.element.dom.update(type = self.__class__.__name__.lower(), key = key, value = "")
        
    def __setitem__(self, key, value):
        return self.__setattr__(key, value)
    
    def __getitem__(self, key):
        return self.kvp[key]
    
    def __contains__(self, key):
        return key in object.__getattribute__(self, 'kvp')
     
    def keys(self):
        return self.kvp.keys()
    
    def values(self):
        return self.kvp.values()

    def iterkeys(self):
        return self.kvp.iterkeys()
    
    def iteritems(self):
        return self.kvp.iteritems()
    
    def has_key(self, key):
        raise DomDomError, "Do not use 'has_key' -- use 'in' which calls '__contains__' instead . . . "
             
    def get(self, key, default = None):
        return self.kvp.get(key, default)
                
class Att(ElementNameSpace):
    
    class allowed:
        alt        =      'alt'
        css_class  =      'className'
        dir        =      'dir'
        href       =      'href'
        language   =      'language'
        link       =      'link'
        longdesc   =      'longdesc'
        name       =      'name'
        rel        =      'rel'
        selected   =      'selected'
        src        =      'src'
        tabindex   =      'tabindex'
        title      =      'title'
        type       =      'type'
        value      =      'value'
        xmlns      =      'xmlns'
        xml_lang   =      'xml:lang'
    
    def __setattr__(self, key, value, update = True):
        if key == 'css_class' and isinstance(value, ElementMetaClass): value = value.CSS_CLASS.strip()
        ElementNameSpace.__setattr__(self, key = key, value = value, update = update)
    
    def get_xml(self):
        output = ''
        
        class_att = getattr(self.element.__class__, 'att', None)
        
        att_dict = {}
        if(class_att):
            for key,value in class_att.__dict__:
                if key not in self.kvp:
                    att_dict[key] = value
                
        att_dict.update(self.kvp)

        for att,value in att_dict.iteritems():
            if value is not None and att != 'css_class':
                output += ' ' + att.strip() + '="' + str(value).strip().replace("\t", "").replace("\n", "") + '"'

        return output
          
class Style(ElementNameSpace):
    
    @staticmethod
    def get_value(key, value, str_quote = '"'):

        if(key == 'display' and value in [None, False]):
            value = str_quote + 'none' + str_quote
        elif(key == 'display' and value is True):
            value = str_quote + 'block' + str_quote
        elif(value is None):
            value = 'null'
        elif(value is False):
            value = 'false'
        elif(value is True):
            value = 'true'
        elif(isinstance(value, (str, css.CSS_Number))):
            value = str_quote + str(value) + str_quote
        else:
            value = str(value)
            
        return value
                 
    def __le__(self, css_directive):
        
        css_name = str(css_directive[0])

        if css_directive[0] == 'center':
            raise exceptions.KeyError

        if css_directive[1] is None:
            if css_name in self.kvp:
                ElementNameSpace.__delattr__(self, css_name)
        else:
            ElementNameSpace.__setattr__(self, css_name, css_directive[1])
 
    def get_xml(self):
        
        output = 'style="'
        
        for prop,value in self.kvp.iteritems():
            if(value):
                output += css.python_2_css.__dict__[prop] + ':' + Style.get_value(prop, value, str_quote = "") + ';'

        output = output[:-1] # To take of extra ';'
        output += '"'
        
        if(output == 'style="'):
            output = ""
        
        return output
         
class State(ElementNameSpace):
    
    @staticmethod
    def get_value(value):
        return 1 if value == "True" else 0
            
    @staticmethod
    def make_js(element, key, value):
        
        if key == 'focus':
            element.js.focus()
        
        if key == 'full':
            element.js.full()
        
        if key == 'center':
            element.js.center()
            
    def __init__(self, element):
        ElementNameSpace.__init__(self, element = element)
        ElementNameSpace.__setattr__(self, key = 'focus',   value = False, update = False)
        ElementNameSpace.__setattr__(self, key = 'full',    value = False, update = False)
        ElementNameSpace.__setattr__(self, key = 'center',  value = False, update = False)
        
    def __setattr__(self, key, value, update = True):
        if key in ['focus', 'full', 'center'] and value in [True, False]:
            ElementNameSpace.__setattr__(self, key, value, update)
        else:
            raise DomDomError, "State does not support key,value " + str(key) + "," + str(key)
     
    def make_js_on_load(self):
        for key in ['focus', 'full', 'center']:
            value = getattr(self, key, False)
            if value:
                State.make_js(element = self.element, key = key, value = value)

class util:
    @staticmethod
    def espace_javascript(string):
        return string.replace("'", "\\'").replace('"', '\\"')



