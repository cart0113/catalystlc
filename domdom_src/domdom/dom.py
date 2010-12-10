import os
import exceptions
import inspect
import time

import pod
import settings
import css

""" ERRORS """
class DomDomError(exceptions.Exception):
    pass

class JsError(exceptions.Exception):
    pass

class IncludesError(exceptions.Exception):
    pass

""" The basis of Document and Element """         
class DomObject(pod.Object):    
    
    def __init__(self, **kwargs):
        pod.Object.__init__(self, 
                            events = Events(), 
                            events_to_sensor = set(), 
                            events_to_handle = set(), 
                            **kwargs)
    
    def on_load_from_db(self):
        self.dom = self.__class__.Dom(self)

""" Document """
class Document(DomObject):
            
    class DOC_TYPES:
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

    """ The router """
    @staticmethod
    def route(cls, request):
        document = cls.__new__(cls)
        object.__setattr__(document, 'request', request)
        document.__init__()
        return document
             
    def __init__(self):
        DomObject.__init__(self)
        # you need to do this here because you can't pass self in to constructor (object has not been made yet). 
        self.document = self
         
    def on_new_or_load_from_db(self):       
        # These attributes -- which are already of type pod.NoSave -- will be hidden from a commit
        object.__setattr__(self, 'dom',      object.__getattribute__(self, '__class__').Dom(document = self))
        object.__setattr__(self, 'includes', object.__getattribute__(self, '__class__').Includes(document = self))
        object.__setattr__(self, 'js',       object.__getattribute__(self, '__class__').Js(document = self))
                                    
    """
    API
    """
    def set_element_root(self):
        self.element_root = type.__getattribute__(object.__getattribute__(self, '__class__'), 'element_root')(document = self)
        return self.element_root
    
    def set_element_includes(self, parent):
        self.element_includes = type.__getattribute__(object.__getattribute__(self, '__class__'), 'element_includes')(parent = parent)        
        return self.element_includes
    
    def set_element_js_commands(self, parent):
        self.element_js_commands = type.__getattribute__(object.__getattribute__(self, '__class__'), 'element_js_commands')(parent = parent)
        return self.element_js_commands
    
    def redirect(self, url):
        if self.dom.in_update_mode:
            self.dom.redirect_url = url
        else:
            self.request.redirect(url = url)
            
    def onunload(self, event):
 
        if settings.chatty:
            print "\tUnloading document " + str(self.__class__) + " . . ."
        
        self.__class__.handle_unload(document = self)
      
    def pre_publish(self):
        pass
        
    def pre_publish_document(self):
        pass

    def pre_publish_ajax(self):
        pass
    
    def delete(self, clear_cache = False, close = False):
        
        self.element_root.delete()

        for event in self.events:
            event.delete()
        
        DomObject.delete(self)    
        
        settings.db.commit(clear_cache = clear_cache, close = close)
    
    class Dom(pod.NoSave):

        def __init__(self, document):
            self.document            = document
            self.js_commands         = [] 
  
        def __getitem__(self, key):

            if key not in self.updates:
                self.update_list.append(key)
                self.updates[key] = {} 

            return self.updates[key]
                        
        def get_tag_name(self):
            return ""

        def get_xml(self, newline = None, tab = None):
            
            doc_type = getattr(object.__getattribute__(self.document, '__class__'), 'DOC_TYPE', Document.DOC_TYPES.xhtml_1.strict)
            
            return self.document.element_root.dom.get_xml(output  = doc_type + '\n',
                                                          newline = settings.newline if newline is None else newline, 
                                                          tab     = settings.tab if tab is None else tab, 
                                                          ctab    = "")
    
        def get_xml_js_commands(self):
    
            commands = []
            """ millisecond time stamp used for complete id identification """            
            dtime                  = str(int(time.time()*1000))
            self.document.dtime    = dtime

            commands += ['document.id = "' + self.document.get_full_id() + '";']
            commands += ['domdom.elements["' + self.document.get_full_id() + '"] = document;']
            commands += ["domdom.dtime = " + dtime + ';']
            commands += ['domdom.event_url = "' + settings.urls.get_event() + '";']
            commands += ['domdom.main = domdom.get("' + self.document.main.get_full_id() + '");']
            
            for event in self.document.events:
                commands = event.get_xml_js_commands(commands = commands)
                
            commands = self.document.html.dom.get_xml_js_commands(commands = commands)
            
            object.__getattribute__(self.document.js, 'set_xml_js_commands')(commands)
               
        """ AJAX RELATED """
        def handle_event(self, request, event, codes):
            # First, enter update mode and setup the request
            updater.enter_update_mode()
            self.request             = request
            self.redirect_command    = None

            # Then, fire the event -- this will create everything . . . 
            event.onfire(codes = codes)                          
                    
            # Then, publish the event . . . 
            output = self.publish()
            
            # Then, send the request and clean up yourself for pete's sake . . . 
            del self.request
            del self.redirect_command
            updater.exit_update_mode()
            
            # Finally, return the output . . . 
            return output
                              
        def add_to_updates(self, obj):
            if self.in_update_mode:
                self.updates.append(obj)
            return self.in_update_mode
            
        def get_ajax_js_commands(self):
            
            if self.redirect_command:
                output = 'window.location = "' + str(self.redirect_command) + '"'
            else:
                commands = []
                for update in updater.updates_list:
                    commands = update.get_ajax_js_commands(commands = commands)
                output  = settings.newline.join(commands) + settings.newline 

            return output

        """ THEN PUBLISH """
        def publish(self, commit = None, clear_cache = None, close = None):
            
            if updater.in_update_mode is False:  
                self.document.pre_publish()
                self.document.pre_publish_document()    
                self.get_xml_js_commands()              
                output = self.get_xml()
            else: 
                self.document.pre_publish()
                self.document.pre_publish_ajax()
                output = self.get_ajax_js_commands()

            if settings.pod.commit if commit is None else commit:
                settings.pod.db.commit(clear_cache = settings.pod.clear_cache if clear_cache is None else clear_cache, 
                                       close       = settings.pod.close       if close       is None else close, 
                                       )
                
            return output

    class Js(pod.NoSave):
        
        """
        Js namespace -- this is used for calling javascript directly in the form: 
        
        self.document.js.some_function(10, 20, 30)
        
        or even 
        
        self.document.js.domdom.namespace1.hide(self.html, 10, [10, 20, self.div])
        
        or even 
        
        self.document.js <= 'do_some_cool_js_thing = document.getElementById("10:15").bark();'
        
        """
        
        class domdom:
            alert = None
            blur  = None
            focus = None
        
        def __init__(self, document):
            self.document = document
            self.commands = []
    
        def __getattribute__(self, key):
            if key in ['domdom', 'mkit']:
                return self.__class__.JsCall(parent = self, name = key)
            else:
                return pod.NoSave.__getattribute__(self, key)
    
        def __getattr__(self, key):
            return self.__class__.JsCall(parent = self, name = key)
        
        def __le__(self, value):
            value = value.strip().replace(" ", "")
            if value[-1] != ';':
                value += ";"
            self.commands.append(value)
    
        def get_namespace(self, call):
            if updater.in_update_mode is False:
                self.commands.append(call)
            else:
                updater.add_command(command = call)
    
        def set_xml_js_commands(self, commands, newline = "\n"):
            self.document.element_js_commands.dom.set_xml_js_commands(commands = commands + self.commands)
            del self.commands[:]
        
        class JsCall(object):
            
            def __init__(self, parent, name):
                self.parent        = parent
                self.name          = name
        
            def __getattr__(self, key):
                return self.__class__(parent = self, name = key)
            
            def __call__(self, *args):
                call = self.name + '('
                for arg in args:
                    call += self.get_arg(arg) + ','
                call = call[:-1] + ');'
                return object.__getattribute__(self.parent, 'get_namespace')(call = call)
                
            def get_namespace(self, call):
                return self.parent.get_namespace(self.name + '.' + call)
            
            def get_arg(self, arg):
                if isinstance(arg, str):
                    return '"' + arg + '"'
                elif isinstance(arg, pod.Object):
                    return '"' + arg.get_full_id() + '"'
                elif isinstance(arg, bool):
                    return str(arg).lower()
                elif isinstance(arg, (int, float, long)):
                    return str(arg)
                elif isinstance(arg, (list,set)):
                    output = '['
                    for item in arg:
                        output += self.get_arg(item) + ','
                    return output[:-1] + ']'
                elif isinstance(arg, dict):
                    output = '{'
                    for key, item in arg.iteritems():
                        print key,self.get_arg(item)
                        output += '"' + key + '"' + ':' + self.get_arg(item) + ','
                    return output[:-1] + '}'
                elif isinstance(arg, JSON):
                    return self.get_arg(arg = arg.__dict__)
                else:
                    return '"' + str(arg) + '"'

    class Includes(pod.NoSave):
        
        """
        Includes -- 
        
        This allows: self.includes.css <= sys.modules['__main__']
        
        or even 
        
        self.includes.css <= 'http://some.greatcss.com/greatcss.com'
        
        """
        def __init__(self, document):
            object.__setattr__(self, 'document', document)   # Have to call object because you can't call __setattr__ directly
            
        def __setattr__(self, key, value):
            raise DomDomError, "You cannot set an attribute of this special 'include' namespace"
        
        def __getattr__(self, key):
            
            if key == 'css' and key not in self.__dict__:
                object.__setattr__(self, key, self.__class__.CSS(document = self.document))
                return self.__dict__[key]
            elif key == 'js' and key not in self.__dict__:
                object.__setattr__(self, key, self.__class__.JS(document = self.document))
                return self.__dict__[key]
            else:
                return object.__getattribute__(self, key)

        class CSS(object):
            
            def __init__(self, document):
                self.document = document
                
            def __le__(self, module):
                
                if inspect.ismodule(module):
                    css_name = module.__name__ + '.css'
                    css_file = settings.dirs.get_css() + os.sep + css_name
                    if not os.path.isfile(css_file):
                        if settings.chatty:
                            print "Creating css file '" + css_name + "'"
                        self.create_css_file(module = module, css_file = css_file)                
                    elif os.path.getmtime(css_file) < os.path.getmtime(inspect.getabsfile(module)):
                        if settings.chatty:
                            print "Recreating css file '" + css_name + "'"
                        self.create_css_file(module = module, css_file = css_file)                
                    href = settings.urls.get_css() + "/" + css_name
                elif isinstance(module, str):
                    href = module  # This means the module was a string . . .                 
                else:
                    raise IncludesError, "CSS Include '" + str(module) + "' not supported . . ."
        
                type.__getattribute__(object.__getattribute__(self.document, '__class__'), 'element_css_link')(parent = self.document.element_includes, href = href)
        
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
        
        class JS(object):
            
            def __init__(self, document):
                self.document = document
        
            def __le__(self, src):
                type.__getattribute__(object.__getattribute__(self.document, '__class__'), 'element_js_src')(parent = self.document.element_includes, src = src)

class updater:
    
    in_update_mode = False
    updates_list   = []
    updates_set    = set()

    @staticmethod
    def enter_update_mode():
        updater.in_update_mode = True
        
    @staticmethod
    def add_object(obj):
        if obj not in updater.updates_set:
            updater.updates_set.add(obj)
            updater.updates_list.append(obj)

    @staticmethod
    def add_command(command):
        updater.updates_list.append(UpdaterCommand(command = command))
        
    @staticmethod
    def exit_update_mode():
        updater.updates_set.clear()
        del updater.updates_list[:]
        updater.in_update_mode = False
        
class UpdaterCommand(object):
    
    def __init__(self, command):
        self.command = command

    def get_ajax_js_commands(self, commands):
        commands.append(self.command)
        return commands
    
""" Element """
class ElementMetaClass(pod.Meta):
    
    def __init__(cls, name, bases, dict):
        
        pod.Meta.__init__(cls, name, bases, dict)

        if bases[0] is DomObject:
            cls.TAG_NAME = 'DOMDOM_ELEMENT'
        else:
            parent = [base for base in bases if issubclass(base, Element)][0]
                        
            if parent.__dict__.get('DOM_NO_TAG', False):
                cls.TAG_NAME = name
                cls.CSS_CLASS = ""
            else:
                cls.TAG_NAME = parent.TAG_NAME
                if('css' in cls.__dict__ and 'CSS_CLASS' not in cls.__dict__):
                    cls.CSS_CLASS = parent.CSS_CLASS + css.get_css_name(cls) + " "
                                                                  
class Element(DomObject):
    
    __metaclass__ = ElementMetaClass
    
    DOM_NO_TAG    = True
        
    def __init__(self, document = None, parent = None, older = None, younger = None, css_class = None, text = None, **kwargs):
          
        # DO NOT NEED TO CALL BASE CONSTRUCTOR pod.Object.__init__ -- NO NEED.  
        # WE WANT TO PROCESS kwargs IN SPECIFIC WAY (AT BOTTOM) 
        
        # First, create reference to document, which is needed for updating dom on ajax call . . .
        DomObject.__init__(self)
        self.set_many(document   = document, 
                      css_class  = CssClass(element = self, css_class = object.__getattribute__(self, '__class__') if css_class is None else css_class),
                      children   = Children(), 
                      att        = Att(element = self),
                      style      = Style(element = self),
                      state      = State(element = self),
                      text       = Text(element = self, text = text)
                   )
        
        # After, document has been loaded, add to the update stack (this will be ignored if not in an ajax call) . . .  
        if updater.in_update_mode:
            object.__getattribute__(self, 'dom').update_create()
        
        if parent is not None: 
            self.parent = parent
        elif older is not None:
            if older.parent is None:
                raise DomDomError, "You cannot use node '" + str(older) + "' as 'older' . . . it has no parent . . . "
            older.insert_after_me(self)
        elif younger is not None:
            if younger.parent is None:
                raise DomDomError, "You cannot use node '" + str(younger) + "' as 'younger' . . . it has no parent . . . "
            younger.insert_before_me(self)
        
        for key,value in kwargs.iteritems():
            if value is None:
                pass
            elif key in css.prop.__dict__:
                self.style.__setattr__(key, value)
            elif key in Att.allowed.__dict__:
                self.att.__setattr__(key, value)
            else:
                self.__setattr__(self, key, value)
     
    def __setattr__(self, key, value):
        
        #===============================================================================================================================
        # parent
        #===============================================================================================================================
        if key == 'parent' or key == 'younger':
            # valid types: None | Element            
            old_parent = getattr(self, 'parent', None)
            if value is None:
                if old_parent:
                    list.remove(old_parent.children, self)
                    if updater.in_update_mode:
                        object.__getattribute__(self, 'dom').update_detach()
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
                    if updater.in_update_mode:
                        object.__getattribute__(self, 'dom').update_append(parent = value)
                elif key == 'younger':
                    DomObject.__setattr__(self, 'parent', value.parent)
                    list.insert(value.parent.children, value.parent.children.index(value), self)
                    if updater.in_update_mode:
                        object.__getattribute__(self, 'dom').update_insert(younger = value)
                    
        #===============================================================================================================================
        # css_class / text
        #===============================================================================================================================       
        elif key == 'css_class':
            DomObject.__setattr__(self, key, CssClass(element = self, css_class = value)) 
        elif key == 'text':
            DomObject.__setattr__(self, key, Text(element = self, text = value))  
        #===============================================================================================================================
        # else, just set it . . .
        #===============================================================================================================================       
        else:
            DomObject.__setattr__(self, key, value)
                      
    def __iter__(self):
        return self.children.__iter__()

    def __len__(self):
        return self.children.__len__()
          
    def on_new_or_load_from_db(self):
        # Next, create dom namespace 
        object.__setattr__(self, 'dom', type.__getattribute__(object.__getattribute__(self, '__class__'), 'Dom')(element = self))
                  
    """
    API
    """        
    def get_younger(self):
        try:
            return self.parent.children[self.parent.children.index(self)+1]
        except IndexError:
            return None
           
    def get_older(self):
        try:
            return self.parent.children[self.parent.children.index(self)-1]
        except IndexError:
            return None
    
    def get_position(self):
        return self.parent.children.index(self)
    
    def insert_before_me(self, element):
        element.younger = self
        
    def insert_after_me(self, element):
        if self.parent.children[-1] is self:
            element.parent = self.parent
        else:
            self.parent.children[self.parent.children.index(self)+1].insert_before_me(element = element)

    def delete(self, send_update = True, remove_from_parent_list = True):        

        # First, delete my events, so any events are cleared and won't cause error on delete in next step. 
        for event in self.events:
            event.delete(send_update = False, remove_from_parent_list = False)
        
        del self.events[:]
        
        # First, delete all my children -- However, do not send an update to the browser.  Only the first deleted
        # item will send the update.
        for element in self.children:
            element.delete(send_update = False, remove_from_parent_list = False)
        
        del self.children[:]
        
        # Now, check if you are a sensor for anyone else . . .        
        if self.events_to_sensor:
            raise DomDomError, "You cannot delete " + str(self) + " this is a sensor for registered events " + str(self.events_to_sensor)

        if self.events_to_handle:
            raise DomDomError, "You cannot delete " + str(self) + " this is a handler for registered events " + str(self.events_to_handle)
        
                        
        # Then, clear myself from parents list
        if self.parent and remove_from_parent_list:
            list.remove(self.parent.children, self)
        
        if send_update and updater.in_update_mode:
            if self in updater.updates_set:
                # A very rare event -- so it's a bit expense but it should not happen often . . .
                # For this to happen, you would have to create and delete an event in the same ajax call . . . 
                updater.updates_set.remove(self)
                updater.updates_list.remove(self)
            else:
                updater.add_command(command = 'domdom.delete_element("' + self.get_full_id() + '");')
        
        # Last, delete from pod db . . . 
        DomObject.delete(self)
    
    def redirect(self, url):
        self.document.redirect(url)
                    
    def pre_get_xml(self):
        pass
           
    """ The DOM namespace """
    class Dom(pod.NoSave):
        
        def __init__(self, element):            
            self.element = element
            self.updates = {}
            
        def get_tag_name(self):
            return object.__getattribute__(self.element, '__class__').TAG_NAME

        def get_is_one_tag(self):
            return getattr(object.__getattribute__(self.element, '__class__'), 'ONE_TAG', (len(self.element.children) == 0 and self.element.text is None))
             
        def get_xml(self, output = "", newline = "\n", ctab = "", tab = "\t"):
            self.element.pre_get_xml()
            output = self.get_xml_start(output = output, newline = newline, ctab = ctab, tab = tab)
            output = self.get_xml_children(output = output, newline = newline, ctab = ctab, tab = tab)
            return self.get_xml_end(output = output, newline = newline, ctab = ctab, tab = tab)
                  
        def get_xml_start(self, output = "", newline = "\n", ctab = "", tab = "\t"):
            output += ctab + "<" + self.get_tag_name() + ' id="' + self.element.get_full_id() + '"'
            # get_xml class
            if self.element.css_class and len(self.element.css_class) > 0:
                output += ' class="' + self.element.css_class + '"'
            
            # get_xml atts
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
        
        """ get_xml_js_commands -- these are commands used for org document """        
        def get_xml_js_commands(self, commands):
                        
            for state in self.element.state.itervalues():
                commands = state.get_xml_js_commands(commands = commands)
            
            for event in self.element.events:
                commands = event.get_xml_js_commands(commands = commands)

            # children
            for child in self.element.children:
                commands = child.dom.get_xml_js_commands(commands = commands)
    
            return commands
        
        """ get_ajax_js_commands -- these are commands used for ajax update -- all update_ functions set these """                
        def get_ajax_js_commands(self, commands):                        
            commands.append('domdom.update("' + self.element.get_full_id() + '",' + str(self.updates) + ');')
            self.updates.clear()
            return commands
        
        """ All things update """        
        def update_create(self):
            updater.add_object(obj = self)
            self.updates.setdefault('dom', {})['create'] = self.get_tag_name()
            global_atts = getattr(object.__getattribute__(self.element, '__class__'), 'att', None)
            if global_atts:
                for key,value in global_atts.__dict__.iteritems():
                    if key not in ['__module__', '__doc__']:
                        self.update_att(key, value)

        def update_delete(self):
            updater.add_object(obj = self)
            self.updates.setdefault('dom', {})['delete'] = 1

        def update_detach(self):
            updater.add_object(obj = self)
            self.updates.setdefault('dom', {})['detach'] = 1

        def update_append(self, parent):
            updater.add_object(obj = self)
            self.updates.setdefault('dom', {})['append'] = parent.get_full_id()

        def update_insert(self, younger):
            updater.add_object(obj = self)
            self.updates.setdefault('dom', {})['insert'] = younger.get_full_id()

        def update_css_class(self, css_class):
            updater.add_object(obj = self)
            self.updates.setdefault('att', {})['className'] = "" if css_class is None else css_class

        def update_att(self, key, value):
            updater.add_object(obj = self)
            self.updates.setdefault('att', {})[key] = value

        def update_style(self, key, value):
            updater.add_object(obj = self)
            self.updates.setdefault('style', {})[key] = value
        
        def update_state(self, key, value):
            updater.add_object(obj = self)
            self.updates.setdefault('state', {})[key] = value
        
        def update_text(self, key, value):
            updater.add_object(obj = self)
            self.updates.setdefault('text', []).append({key: "" if value is None else value})
            
        def debug(self):
            self.document.js <= 'domdom.debug.element_contents("' + self.element.get_full_id() + '");'
               
""" Element Attributes -- children, css_class, text, att, style """     

""" Collection -- restrict access to list to make things safer (so strong typy though) """
class Collection(list):

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

class Children(Collection):
    pass

class Events(Collection):
    pass

""" CssClass """
class CssClass(str):
        
    def __new__(cls, element, css_class, update = True):
        if css_class is None:
            inst = None
            if update and updater.in_update_mode and getattr(element, 'css_class', None) is not None:  
                object.__getattribute__(element, 'dom').update_css_class(css_class = inst)
        else:
            if isinstance(css_class, ElementMetaClass):
                css_class = getattr(css_class, 'CSS_CLASS', "")
            inst = str.__new__(cls, str(css_class).strip())
            inst.element = element
            if update and updater.in_update_mode:  
                object.__getattribute__(element, 'dom').update_css_class(css_class = inst)
        return inst

""" Text -- so small but so important """
class Text(str):
    
    def __new__(cls, element, text, update = True):
        if len(getattr(element, 'children', [])) > 0:
            raise DomDomError, "You cannot assign text to an element which has children element nodes.  First set children to empty list [] . . . "
        if text is None:
            inst = None
            if update and updater.in_update_mode and getattr(element, 'text', None) is not None:  # THIS IS DUE TO FACT THAT backspace() CREATES NEW STRING (SINCE STRINGS ARE IMMUTABLE) BUT WE DON'T WANT JS UPDATED.
                object.__getattribute__(element, 'dom').update_text(key = 'set', value = inst)
        else:
            inst = str.__new__(cls, str(text))
            inst.element = element        
            if update and updater.in_update_mode:  # THIS IS DUE TO FACT THAT backspace() CREATES NEW STRING (SINCE STRINGS ARE IMMUTABLE) BUT WE DON'T WANT JS UPDATED.
                object.__getattribute__(element, 'dom').update_text(key = 'set', value = inst)            
        return inst
                
    def append(self, new_text):
        if updater.in_update_mode:
            object.__getattribute__(element, 'dom').update_text(key = 'add', value = str(new_text))
        return Text(element = self.element, text = str.__add__(self, str(new_text)), update = False)
        
    def backspace(self, times = 1):        
        if updater.in_update_mode:
            object.__getattribute__(element, 'dom').update_text(key = 'del', value = times)
        return Text(element = self.element, text = self[:-1*times], update = False)
    
    def get_xml(self, output = "", newline = "\n", ctab = "", tab = "\t"):
        str = self.replace("\n", "").replace("\t", "").replace("  ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ")
        return output + str

""" Element name space, these hold all the keys . . . """     
class ElementNameSpace(pod.Object):
            
    def __init__(self, element):
        pod.Object.__init__(self, element = element, kvp = {})

    def __setattr__(self, attr, value):
        self.kvp[attr] = value
        
    def __getattr__(self, attr):
        
        if attr in self.kvp:
            return self.kvp[attr]
        else:
            return pod.Object.__getattribute__(self, attr)
    
    def __delattr__(self, attr):
        if attr in self.kvp:
            del self.kvp[attr]
            self.element.dom.update(type = self.__class__.__name__.lower(), attr = attr, value = "")
        
    def __setitem__(self, key, value):
        return self.__setattr__(key, value)
    
    def __getitem__(self, key):
        return self.kvp[key]
    
    def __contains__(self, key):
        return key in self.kvp
     
    def keys(self):
        return self.kvp.keys()
    
    def values(self):
        return self.kvp.values()
    
    def items(self):
        return self.kvp.items()

    def iterkeys(self):
        return self.kvp.iterkeys()
    
    def itervalues(self):
        return self.kvp.itervalues()
    
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
        ElementNameSpace.__setattr__(self, key, value)
        if update and updater.in_update_mode:
            object.__getattribute__(self.element, 'dom').update_att(key = key, value = value)
    
    def get_xml(self):
        output = ''
        
        class_att = getattr(object.__getattribute__(self.element, '__class__'), 'att', None)
        
        att_dict = {}
        if class_att:
            for key,value in class_att.__dict__.iteritems():
                if key not in ['__module__', '__doc__'] and key not in self.kvp:
                    att_dict[key] = value
                
        att_dict.update(self.kvp)

        for att,value in att_dict.iteritems():
            if value is not None and att != 'css_class':  # We filter out 'css_class' because that's taken care of by Element
                output += ' ' + att.strip() + '="' + str(value).strip().replace("\t", "").replace("\n", "") + '"'

        return output
          
class Style(ElementNameSpace):
    
    @staticmethod
    def get_value(key, value, str_quote = '"'):

        if key == 'display' and value in [None, False]:
            value = str_quote + 'none' + str_quote
        elif key == 'display' and value is True:
            value = str_quote + 'block' + str_quote
        elif value is None:
            value = 'null'
        elif value is False:
            value = 'false'
        elif value is True:
            value = 'true'
        elif isinstance(value, (str, css.CSS_Number)):
            value = str_quote + str(value) + str_quote
        else:
            value = str(value)
            
        return value
        
    def __setattr__(self, key, value, update = True):
        ElementNameSpace.__setattr__(self, key, value)
        if update and updater.in_update_mode:
            object.__getattribute__(self.element, 'dom').update_style(key = css.python_2_js.__dict__[key], value = Style.get_value(key = key, value = value, str_quote = ''))
                 
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

""" State -- full -- focus -- center """         
class State(ElementNameSpace):
                         
    def __setattr__(self, key, value, update = True):
        if key == 'focus':
            ElementNameSpace.__setattr__(self, key, focus(element = self.element, value = value))
        elif key == 'full':
            ElementNameSpace.__setattr__(self, key, full(element = self.element, value = value))
        elif key == 'center':
            ElementNameSpace.__setattr__(self, key, center(element = self.element, value = value))
        if update and updater.in_update_mode:
            object.__getattribute__(self.element, 'dom').update_state(key = key, value = int(value))
     
class StateFn(object):
    
    def __init__(self, element, value):
        self.element = element
        self.value   = value

    def __str__(self):
        return '1' if self.value is True else '0'

    def get_xml_js_commands(self, commands):
        commands.append('domdom.state.' + self.__class__.__name__ + '("' + self.element.get_full_id() + '", ' + str(self) + ');')
        return commands 
        
class focus(StateFn):
    pass

class full(StateFn):
    pass

class center(StateFn):
    pass
        
""" The JSON object -- used to quickly create JSON objects to send to javascript """   
class JSON(object):
    
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class util:
    
    @staticmethod
    def convert_from_xhtml(string, newline = "\n", space = " "):
        string = "" if string is None else string
        string = string.replace("<br/>", "\n").replace("&nbsp;", space)
        add = True
        out = ""
        for char in string:
            add = False if char == "<" else add
            add = True  if char == ">" else add
            if add and char != ">":
                out += char
        return out

    @staticmethod
    def convert_to_xhtml(string, newline = "<br/>", double_space = " &nbsp;"):
        import re
        string = "" if string is None else string
        string = string.replace("\n", "__DOMDOM_SPACE__"  + newline)
        string = string.replace("  ", double_space)
        string = string.replace("__DOMDOM_SPACE__", " ")
        r = re.compile(r"(http://[^ ]+)")
        string = r.sub(r'<a href="\1">\1</a>', string)
        return string 
    
if __name__ == '__main__':
    class m(pod.Object):
        pass
    
    js = Document.Js(None)
    
    mm = JSON(name = 'main', tommy = '10', timmy = 20)
    
    js <= 'domdom.alert()'
    js.domdom.hello.me(1, 2, 'asl', m(), m(), {'a': m(), 'b': [{'c': 10}, 1, 2, 'a', m()]}, [1, 2, 'a', m()], mm)
    js.domdom.blur(mm)
    
    assert js.commands == ['domdom.alert();', 'domdom.hello.me(1,2,"asl","8:1","8:2",{"a":"8:3","b":[{"c":10},1,2,"a","8:4"]},[1,2,"a","8:5"],{"timmy":20,"name":"main","tommy":"10"});', 'domdom.blur({"timmy":20,"name":"main","tommy":"10"});'], js.commands
    
    some_list = UpdateList()
    some_list.append(10)
    some_list.append(20)
    some_list.append(30)
    some_list.append(40)
    some_list.append(30)
    some_list.append(30)
    some_list.append(50)
    some_list.append(30)
    assert some_list == [10, 20, 30, 40, 50]
    some_list.clear()
    assert some_list == []
    

    