import exceptions
import urllib

import pod, settings, css

from dom import DomObject, updater

class EventError(exceptions.Exception):
    pass

class Event(pod.Object):

    def __init__(self, parent, sensor = None, handler = None):

        # The parent, sensor, and handler can all be different.  Please note, however, 
        # that if any of these objects -- parent, sensor, or handler -- are deleted, that
        # this event will be deleted and removed from all lists.  Also, if the event is deleted, removed from all lists.  
        pod.Object.__init__(self, 
                            parent   = parent,
                            sensor   = parent if sensor  is None else sensor, 
                            handler  = parent if handler is None else handler,  
                            document = parent.document,  
                            )
            
        list.append(self.parent.events, self)

        self.sensor.events_to_sensor.add(self)
        self.handler.events_to_handle.add(self)
        
        if updater.in_update_mode:         
            updater.add_object(obj = self)
                        
    def call_handler(self):
        handler = getattr(self.handler, 'on' + self.__class__.__name__.lower(), None)
        if handler:
            handler(self)

    def delete(self, send_update = True, remove_from_parent_list = True):   
        
        # Note, that a dom.Element cannot be removed if it is either a sensor or a handler.  However, 
        # if the self.parent is delete, this method is called before delete on any other node.  Therefore, 
        # this event will be removed from the list of events to be sensed/handled.  Therefore, conflict should not arise. 
             
        # If send_update is True, this means a delete was called on the event directly. 
        # Otherwise, if the parent is deleted, the javascript takes care of deleting. 
        
        if send_update and updater.in_update_mode:
            if self in updater.updates_set:
                # A very rare event -- so it's a bit expense but it should not happen often . . .
                # For this to happen, you would have to create and delete an event in the same ajax call . . . 
                updater.updates_set.remove(self)
                updater.updates_list.remove(self)
            else:
                updater.add_command(command = 'domdom.delete_event("' + self.get_full_id() + '");')
            
        self.sensor.events_to_sensor.remove(self)
        self.handler.events_to_handle.remove(self)
        
        
        # This event better be in the self.parent.events stack
        if remove_from_parent_list:
            list.remove(self.parent.events, self)
            
        pod.Object.delete(self)
        
    def get_js_create_command(self):
        raise EventError, "You must implement this method . . . this methods creates the javascript call . . ."

    def get_xml_js_commands(self, commands):
        commands.append(self.get_js_create_command())
        return commands
             
    def get_ajax_js_commands(self, commands):
        commands.append(self.get_js_create_command())
        return commands
                      
class EventBasic(Event):
            
    def __init__(self, parent, sensor = None, handler = None, default = True, bubble = True, mods = True, value = False, valid_keycodes = None, reporter = None):
        
        Event.__init__(self, parent = parent, sensor = sensor, handler = handler)

        self.default        = default
        self.bubble         = bubble
        self.mods           = mods
        self.value          = value
        self.valid_keycodes = valid_keycodes
        self.reporter       = reporter 
        
        if self.sensor.dom.get_tag_name() in ['div', 'img', 'a', 'span', 'tr', 'td', 'table'] and isinstance(self, (Key, Blur, Focus)):
            if 'tabindex' not in self.sensor.att:
                self.sensor.att.tabindex = getattr(self, 'tabindex', '1')

    def get_js_create_command(self):
        
        default         = ',1' if self.default   else ',0'
        bubble          = ',1' if self.bubble    else ',0'        
        mods            = ',1' if self.mods      else ',0'
        value           = ',1' if self.value     else ',0'
        valid_keycodes  = ',0' if self.valid_keycodes is None else ',' + str(self.valid_keycodes)
        reporter        = ',0' if self.reporter is None else ',' + self.get_reporter()
          
        front_string = '"' + self.get_full_id() + '","' + self.parent.get_full_id() + '","' + self.sensor.get_full_id()  + '"'
        
        #return 'domdom.events["' + self.get_full_id() + '"] = new domdom.EventBasic(' + front_string + ',' + self.get_event_type() + default + bubble + mods + reporter + valid_keycodes + ');' 
        return 'new domdom.EventBasic(' + front_string + ',' + self.get_event_type() + default + bubble + mods + value + valid_keycodes + reporter + ');' 
        
    def get_event_type(self):
        return '"' + self.__class__.__name__.lower() + '"' 
    
    def get_reporter(self):
        
        reporter = '{'
        
        for key,value in self.reporter.iteritems():
            key = key if not isinstance(key, DomObject) else key.get_full_id()
            reporter += '"' + str(key) + '":"' + str(value) + '",'
            
        return reporter[0:-1] + '}'
        
    def onfire(self, codes):
        
        if "reporter" in codes:
            pos = codes.index("reporter")
            self.report = {}
            for i in range(len(codes[pos:])/2):
                key   = codes[pos + 2*i + 1]
                value = codes[pos + 2*i + 2]
                
                if key not in self.reporter:
                    cls = object.__getattribute__(self, '__class__')
                    key = type.__getattribute__(cls, 'pod').inst_get_inst_by_id(cls = cls, inst_id = key)
                    
                if key not in self.report:
                    self.report[key] = {}
                value = value.split(".")
                if self.reporter[key] == 'pos':
                    self.report[key]['pos'] = [css.pixel(v) for v in value]
                elif self.reporter[key] == 'target':
                    cls = object.__getattribute__(self, '__class__')
                    self.report[key]['target'] = type.__getattribute__(cls, 'pod').inst_get_inst_by_id(cls = cls, inst_id = value[0])    
                else:
                    for i,att in enumerate(self.reporter[key]):
                        self.report[key][att] = value[i]
                    
            codes = codes[:pos]

        if self.value:
            value = urllib.unquote(str(codes[-1]))[1:].replace('__DOMDOM_FSLASH__', '/')
            del codes[-1]
            self.sensor.att.__setattr__('value', value, update = False)
            
        return codes
          
class Mouse(EventBasic):
    
    def __init__(self, parent, sensor = None, handler = None, default = True, bubble = True, mods = True, value = False, reporter = None):        
        EventBasic.__init__(self,parent,sensor,handler, default,bubble,mods,value,None,reporter)
            
    def onfire(self, codes):
        
        codes = EventBasic.onfire(self, codes)
        
        if isinstance(self, (MouseDown, MouseUp, Click, DblClick)):
            self.button         = int(codes.pop(0))
                
        if self.mods:
            if isinstance(self, (MouseOver, MouseOut, MouseLeave)):
               id = codes.pop(0).split(":")
               self.related_target = settings.pod.cache.get_inst(cls_id = int(id[0]), inst_id = int(id[1]))

            if isinstance(self, Mouse):
                self.alt   = int(codes.pop(0)) == 1
                self.ctrl  = int(codes.pop(0)) == 1
                self.meta  = int(codes.pop(0)) == 1
                self.shift = int(codes.pop(0)) == 1 
                
                self.x_client = int(codes.pop(0))
                self.y_client = int(codes.pop(0))
        
        self.call_handler()
    
class MouseDown(Mouse):
    pass

class MouseUp(Mouse):
    pass

class MouseOver(Mouse):
    pass

class MouseOut(Mouse):
    pass

class MouseLeave(Mouse):
    pass

class MouseMove(Mouse):
    pass

class Click(Mouse):
    pass

class DblClick(Mouse):
    pass
    
class Key(EventBasic):
    
    def __init__(self, parent = None, sensor = None, handler = None, default = True, bubble = True, mods = True, value = False, valid_keycodes = None, reporter = None):        
        EventBasic.__init__(self, parent, sensor, handler, default, bubble, mods, value, valid_keycodes, reporter)
        
    def onfire(self, codes):
        codes = EventBasic.onfire(self, codes)
        
        self.key_code = int(codes.pop(0))
        if isinstance(self, KeyPress):
            self.key_char = urllib.unquote(str(codes.pop(0)))

        if self.mods:
            self.alt   = int(codes.pop(0)) == 1
            self.ctrl  = int(codes.pop(0)) == 1
            self.meta  = int(codes.pop(0)) == 1
            self.shift = int(codes.pop(0)) == 1
        
        self.call_handler()
                
class KeyDown(Key):
    pass

class KeyUp(Key):
    pass

class KeyPress(Key):
    pass

class Blur(EventBasic):
    
    def __init__(self, parent = None, sensor = None, handler = None, default = True, bubble = True, value = False):        
        EventBasic.__init__(self, parent = parent, sensor = sensor, handler = handler, default = default, bubble = bubble, value = value)
       
    def onfire(self, codes):
        codes = EventBasic.onfire(self, codes)
        self.sensor.state.__setattr__(key = 'focus', value = False, update = False)
        self.call_handler()

class Focus(EventBasic):
    
    def __init__(self, parent = None, sensor = None, handler = None, default = True, bubble = True, value = False):        
        EventBasic.__init__(self, parent = parent, sensor = sensor, handler = handler, default = default, bubble = bubble, value = value)

    def onfire(self, codes):
        codes = EventBasic.onfire(self, codes)
        self.sensor.state.__setattr__(key = 'focus', value = True, update = False)
        self.call_handler()

class Load(EventBasic):
    
    def __init__(self, parent = None, sensor = None, handler = None, default = True, bubble = True, value = False):        
        EventBasic.__init__(self,parent,sensor,handler,default,bubble)
            
    def onfire(self, codes):
        self.call_handler()

class Unload(EventBasic):
    
    def __init__(self, parent = None, sensor = None, handler = None, default = True, bubble = True):        
        EventBasic.__init__(self,parent,sensor,handler,default,bubble)
            
    def onfire(self, codes):
        self.call_handler()
 
class NativeGUI(EventBasic):

    def __init__(self, parent = None, sensor = None, handler = None, default = True, bubble = True):
        EventBasic.__init__(self, parent, sensor, handler, default, bubble)
 
    def onfire(self, codes):        
        self.call_handler()
                
class Change(NativeGUI):
    pass
       
class Submit(NativeGUI):
    pass



        