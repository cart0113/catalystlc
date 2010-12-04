import exceptions

from events import Event
from css    import pixel, percent

class FxError(exceptions.Exception):
    pass

class Fx(Event):
    pass
      
class ChangeOnMouseMove(Fx):

    def __init__(self, parent, move_opacity = None, min = None, max = None, bbox = None):
        
        Fx.__init__(self, parent = parent)
        
        if self.type not in parent.style:
            raise FxError, "Style attribute '" + str(type) + "' must be in instance '" + str(parent) + "' style namespace . . ."
        
        self.move_style   = {}
        if move_opacity:
            self.set_move_style(move_style = {'opacity': move_opacity})
        
        self.min, self.max, self.bbox = min,max,bbox
        
        if isinstance(self.parent.style[self.type], pixel):
            self.units = '"px"'
        elif isinstance(self.parent.style[self.type], percent):
            self.units = '"%"'
        else: 
            raise FxError, "Units must be of type css.pixel or css.percent . . . "

    def _get_js_create(self):
        
        ## function(id, parent_element, type, units, bbox, e0,e1,e2,e3, listener, move_style, min, max)
        id = '"' + self.pod.get_full_id() + '"'        
        bbox        = 'null' if self.bbox        is None else '"' + self.bbox.pod.get_full_id() + '"'
        
        min = 'null' if self.min is None else self.min
        max = 'null' if self.max is None else self.max
        
        move_start = (self.parent,            'mousedown') if getattr(self, 'move_start', None) is None else self.move_start
        move_stop  = (self.parent.document,   'mouseup')   if getattr(self, 'move_stop',  None) is None else self.move_stop
        
        e0, e1, e2, e3 = '"' + move_start[0].pod.get_full_id() + '"', '"' + move_start[1] + '"', '"' + move_stop[0].pod.get_full_id() + '"', '"' + move_stop[1] + '"' 
        
        command =  'domdom.events[' + id + '] = new domdom.Fx_OMM(' + id + ',"' + self.parent.pod.get_full_id() + '",'
        command += '"' + self.type + '",' + self.units + ',' + bbox + ',' + e0 + "," + e1 + "," + e2 + "," + e3 + ',' + str(self.move_style) 
        command += ',' + str(min) + ',' + str(max) + ');'
        
        return command  
    
    def set_move_start(self, element, event):
        self.move_start = (element, event)
        
    def set_move_stop(self, element, event):
        self.move_stop = (element, event)
        
    def set_move_style(self, move_style):
        for key,value in move_style.iteritems():
            if key not in self.parent.style:
                raise FxError, "You must already have '" + key + "' in element's style attributes if you want to change it on move . . ."
            else:
                self.move_style[key] = value
    
    def onfire(self, codes = None):
        value = pixel(int(codes[0])) if self.units == '"px"' else percent(int(codes[0]))
        self.parent.style.__setattr__(key = self.type, value = value, update = False)
        self.call_handler()
        
class MoveLeft(ChangeOnMouseMove):
    type = 'left'
    
class MoveRight(ChangeOnMouseMove):
    type = 'right'
    
class MoveTop(ChangeOnMouseMove):
    type = 'top'

class MoveBottom(ChangeOnMouseMove):
    type = 'bottom'

class Animate(Fx):
    pass