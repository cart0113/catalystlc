import exceptions

import pod, settings, css

from dom import DomObject

class EventError(exceptions.Exception):
    pass

class Event(pod.Object):

    def __init__(self, parent, sensor = None, handler = None):

        # The parent, sensor, and handler can all be different.  Please note, however, 
        # that if any of these objects -- parent, sensor, or handler -- are deleted, that
        # this event will be deleted and removed from all lists.  Also, if the event is deleted, removed from all lists.  
        
        self.parent  = parent    
        self.sensor  = parent if sensor  is None else sensor
        self.handler = parent if handler is None else handler
        
        self.document = self.parent.document

        list.append(self.parent.events, self)

        self.sensor.events_to_sensor.add(self)
        self.handler.events_to_handle.add(self)

        self.parent.dom.update(type = "event", key = "set", value = self)
        
    def handle_request(self, request):
        self.document.request = request
        self.document.dom.enter_update_mode(request = request)                       
        event.onfire(request.path_list[3:])  
        return document.dom.publish()
   
    def get_dtime(self):
        return self.sensor.get_dtime()
    
    def _get_dom_commands(self, commands):        
        return commands + [self.get_js_create()] 
    
    def _get_update(self):
        return self.get_js_create()
    
    def get_js_create(self):
        raise EventError, "You must implement this method . . . this methods creates the javascript call . . ."
    
    def onfire(self, codes = None):
        self.call_handler()
    
    def call_handler(self):
        handler = getattr(self.handler, 'on' + self.__class__.__name__.lower(), None)
        if(handler):
            handler(self)

    def delete(self, send_update = True):   
        # Note, that a dom.Element cannot be removed if it is either a sensor or a handler.  However, 
        # if the self.parent is delete, this method is called before delete on any other node.  Therefore, 
        # this event will be removed from the list of events to be sensed/handled.  Therefore, conflict should not arise. 
             
        # If send_update is True, this means a delete was called on the event directly. 
        # Otherwise, if the parent is deleted, the javascript takes care of deleting. 
        if self.sensor.in_update_mode() and send_update:
            self.sensor.send_update(type = "event", key = "del", value = self.pod.get_full_id())
        
        self.sensor.events_to_sensor.remove(self)
        self.handler.events_to_handle.remove(self)
        
        # This event better be in the self.parent.events stack
        list.remove(self.parent.events, self)
            
        self.pod.delete()
                
class EventBasic(Event):
            
    def __init__(self, parent, sensor = None, handler = None, default = True, bubble = True, mods = True, reporter = None):
        
        Event.__init__(self, parent = parent, sensor = sensor, handler = handler)

        self.default  = default
        self.bubble   = bubble
        self.mods     = mods
        self.reporter = reporter 
        
        if self.sensor.dom.get_tag_name() in ['div', 'img', 'a', 'span', 'tr', 'td', 'table'] and isinstance(self, (Key, Blur, Focus)):
            if('tabindex' not in self.sensor.att):
                self.sensor.att.tabindex = getattr(self, 'tabindex', '1')

    def get_js_create(self):
        
        default   = ',1' if self.default   else ',0'
        bubble    = ',1' if self.bubble    else ',0'        
        mods      = ',1' if self.mods      else ',0'
        reporter  = ',0' if self.reporter is None else ',' + self._get_reporter()
        
        front_string = '"' + self.pod.get_full_id() + '","' + self.parent.pod.get_full_id() + '","' + self.sensor.pod.get_full_id()  + '"'
        
        command = 'domdom.events["' + self.pod.get_full_id() + '"] = new domdom.EventBasic(' + front_string + ',' + self._get_type() + default + bubble + mods + reporter + ');' 
        
        return command
        
    def _get_type(self):
        return '"' + self.__class__.__name__.lower() + '"' 
    
    def _get_reporter(self):
        
        reporter = '{'
        
        for key,value in self.reporter.iteritems():
            key = key if not isinstance(key, DomObject) else key.pod.get_full_id()
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
                    key = self.pod.get_inst_by_full_id(id = key)
                    
                if key not in self.report:
                    self.report[key] = {}
                value = value.split(".")
                if self.reporter[key] == 'pos':
                    self.report[key]['pos'] = [css.pixel(v) for v in value]
                elif self.reporter[key] == 'target':
                    self.report[key]['target'] = self.pod.get_inst_by_full_id(id = value[0])    
                else:
                    for i,att in enumerate(self.reporter[key]):
                        self.report[key][att] = value[i]
                    
            codes = codes[:pos]

        return codes
          
class Mouse(EventBasic):
    
    def __init__(self, parent, sensor = None, handler = None, default = True, bubble = True, mods = True, reporter = None):        
        EventBasic.__init__(self,parent,sensor,handler, default,bubble,mods,reporter)
            
    def onfire(self, codes):
        
        codes = EventBasic.onfire(self, codes)
        
        if isinstance(self, (MouseDown, MouseUp, Click, DblClick)):
            self.button         = int(codes.pop(0))
                
        if self.mods:
            if isinstance(self, (MouseOver, MouseOut)):
               id = codes.pop(0).split(":")
               self.related_target = settings.cache.get_inst_by_cls_id_and_inst_id(cls_id = int(id[0]), inst_id = int(id[1]))

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

class MouseMove(Mouse):
    pass

class Click(Mouse):
    pass

class DblClick(Mouse):
    pass
    
class Key(EventBasic):
    
    def __init__(self, parent = None, sensor = None, handler = None, default = True, bubble = True, mods = True):        
        EventBasic.__init__(self, parent = parent, sensor = sensor, handler = handler, default = default, bubble = bubble, mods = mods)

    def onfire(self, codes):
        
        codes = EventBasic.onfire(self, codes)

        self.key_code = int(codes.pop(0))
        if isinstance(self, KeyPress):
            self.key_char = str(codes.pop(0))

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


    


#class KeyEvent(Event):
#    
#    def __init__(self, event_code, type, codes):        
#        Event.__init__(self, event_code = event_code)
#    
#    def onfire(self, codes):
#        self.alt   = int(codes[0]) == 1
#        self.ctrl  = int(codes[1]) == 1
#        self.mods  = int(codes[2]) == 1
#        self.shift = int(codes[3]) == 1 
#
#        self.key_code = int(codes[4])
#        try:
#            self.key_char = str(codes[5])
#        except:
#            if(self.key_code == 32):
#                self.key_char = " "
#            else:
#                self.key_char = None
#  
#class OutputEvent(Event):
#    
#    def __init__(self, event_code, value):
#        Event.__init__(self, event_code = event_code)
#        self.value = str(value)
#  
#class LoadEvent(Event):
#    pass
#
#class UnloadEvent(Event):
#    pass
#
#class PollEvent(Event):
#
#    def __init__(self, event_code, codes):
#        
#        Event.__init__(self, event_code = event_code)
#        
#        self.message    = str(codes[0])
#        self.javascript = str(codes[1]) 
#        
#class OnStopMoveEvent(Event):
#    
#    def __init__(self, event_code, codes):
#        
#        Event.__init__(self, event_code = event_code)
#        
#        self.attr    = str(codes[0]).strip()
#        self.value   = str(codes[1]).strip()
#      
#class OnStopAnimateEvent(Event):
#    pass
   
class Blur(EventBasic):
    
    def __init__(self, parent = None, sensor = None, handler = None, default = True, bubble = True):        
        EventBasic.__init__(self,parent,sensor,handler,default,bubble)
            
    def onfire(self, codes):
        self.sensor.state._silent_update(key = 'focus', value = False)
        self.call_handler()

class Focus(EventBasic):
    
    def __init__(self, parent = None, sensor = None, handler = None, default = True, bubble = True):        
        EventBasic.__init__(self,parent,sensor,handler,default,bubble)

    def onfire(self, codes):
        self.sensor.state.__setattr__(key = 'focus', value = True, update = False)
        self.call_handler()

class Load(EventBasic):
    
    def __init__(self, parent = None, sensor = None, handler = None, default = True, bubble = True):        
        EventBasic.__init__(self,parent,sensor,handler,default,bubble)
            
    def onfire(self, codes):
        self.call_handler()

class Unload(EventBasic):
    
    def __init__(self, parent = None, sensor = None, handler = None, default = True, bubble = True):        
        EventBasic.__init__(self,parent,sensor,handler,default,bubble)
            
    def onfire(self, codes):
        self.call_handler()
 
class _NativeGUI(EventBasic):

    def __init__(self, parent = None, sensor = None, handler = None, default = True, bubble = True):
        EventBasic.__init__(self, parent, sensor, handler, default, bubble)
 
    def onfire(self, codes):        
        self.call_handler()
        
class Input(_NativeGUI):
    pass

class Output(_NativeGUI):

    def onfire(self, codes):
        codes = EventBasic.onfire(self, codes)
        value = str(codes.pop()) if len(codes) > 0 else ""
        self.sensor.att.__setattr__('value', value, update = False)
        self.call_handler()
        
class Change(_NativeGUI):

    def onfire(self, codes):
        codes = EventBasic.onfire(self, codes)
        value = str(codes.pop()) if len(codes) > 0 else ""
        self.sensor._onfire(value = value)
        self.call_handler()
       
class Submit(_NativeGUI):
    pass


        