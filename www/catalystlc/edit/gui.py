import sys
import exceptions

from domdom import dom, xhtml, css, settings, routers, events, fx
import images


class Gdiv(xhtml.div):
    @staticmethod
    def css():
        css.prop.overflow         = 'auto'
    
class Node(Gdiv):
    
    @staticmethod
    def css():
        css.prop.padding = css.pixel(2)
        
    def __init__(self, parent = None, older = None, younger = None, root = False):
        xhtml.div.__init__(self, parent = parent, older = older, younger = younger)

        insert = getattr(parent, 'gui_menu_insert', None)

        if insert:
            self.insert_above = NodeInsert(parent = self, position = 'above')
            insert(self.insert_above.buttons)
        
        if root is False:
            self.toolbar = NodeToolbar(parent = self)
            self.content = NodeContent(parent = self)

        if insert:
            self.insert_below = NodeInsert(parent = self, position = 'below')
            insert(self.insert_below.buttons)
            
            
    def delete_attempt(self):
        Confirm(parent   = self.document.main,
                title    = 'Are you sure you want to delete ' + self.delete_msg_main() + '?', 
                sub      = self.delete_msg_sub(),
                callback = (self, 'delete'),
                )
                
    def delete_msg_main(self):
        return 'this node'
    
    def delete_msg_sub(self):
        return 'All data contained within this node will also be deleted . . .'
   
class NodeToolbar(Gdiv):
    
    @staticmethod
    def css():
        css.prop.height             = css.pixel(20)
        css.prop.background_color   = css.rgb(230,230,255)
        css.prop.border_left        = 'solid 2px rgb(110,110,255)'
        css.prop.border_top         = 'solid 2px rgb(110,110,255)'

    def __init__(self, parent):
        Gdiv.__init__(self, parent = parent)
        self.button_show_hide = NodeToolbarButtonShowHide(parent = self, node = self.parent)
        self.button_delete    = NodeToolbarButtonDelete(parent = self,   node = self.parent)
        self.button_move_up   = NodeToolbarButtonMoveUp(parent = self,   node = self.parent)
        self.button_move_down = NodeToolbarButtonMoveDown(parent = self, node = self.parent)
       
class NodeToolbarButton(xhtml.button):
        
    @staticmethod
    def css():
        css.prop.width               = css.pixel(16)#css.inch(0.25)
        css.prop.height              = css.pixel(16)#css.inch(0.25)
        css.prop.padding             = css.pixel(2)
        css.prop.margin_left         = css.pixel(3)
        css.prop.margin              = css.pixel(1)
        css.prop.background_color    = css.rgb(230,230,255)
        css.prop.border              = 'rgb(200, 200, 255) solid 0px'
        css.prop.background_repeat   = 'no-repeat'
        css.prop.background_position = 'center'
        css.prop.position            = css.values.positions.relative
        
        #css.prop.pseudo              = css.values.pseudos.hover
        #css.prop.border              = 'rgb(130, 130, 255) solid 1px'
        
        css.prop.pseudo              = css.values.pseudos.active
        css.prop.background_color    = css.rgb(175,175,255)
        #css.prop.border              = 'rgb(255, 255, 255) solid 1px'

    def __init__(self, **kwargs):
        xhtml.button.__init__(self, **kwargs)
        self.event_omc   = events.Click(parent = self, default = True)
          
class NodeToolbarButtonLeft(NodeToolbarButton):    
    
    @staticmethod
    def css():
        css.prop.float = css.values.floats.left

class NodeToolbarButtonRight(NodeToolbarButton):    
    
    @staticmethod
    def css():
        css.prop.float = css.values.floats.right

class NodeToolbarButtonShowHide(NodeToolbarButtonLeft):
    
    @staticmethod
    def css():
        css.prop.background_image = 'url(' + images.buttons.hide_small_png + ')'        

    def __init__(self, **kwargs):
        NodeToolbarButtonLeft.__init__(self, **kwargs)
        self.on          = True        
        self.att.title   = 'hide'
        
    def onclick(self, event):
        if self.on is True:
            self.hide()
        else:
            self.show()
            
    def hide(self):
        self.style.background_image = 'url(' + images.buttons.show_small_png + ')'
        self.node.content.parent    = None
        self.on                     = False
        self.att.title              = 'show'

    def show(self):
        self.style.background_image = 'url(' + images.buttons.hide_small_png + ')'
        self.node.content.parent = self.node
        self.on = True
        self.att.title = 'hide'

class NodeToolbarButtonMoveUp(NodeToolbarButtonRight):
    
    @staticmethod
    def css():
        css.prop.background_image = 'url(' + images.buttons.up_small_png + ')'        

    def __init__(self, **kwargs):
        NodeToolbarButtonRight.__init__(self, **kwargs)
        self.page        = self.parent.parent
        self.att.title   = 'Move Up'

    def onclick(self, event):
        self.node.move_up()
     
class NodeToolbarButtonMoveDown(NodeToolbarButtonRight):
    
    @staticmethod
    def css():
        css.prop.background_image = 'url(' + images.buttons.down_small_png + ')'        

    def __init__(self, **kwargs):
        NodeToolbarButton.__init__(self, **kwargs)
        self.page        = self.parent.parent
        self.att.title   = 'Move Down'

    def onclick(self, event):
        self.node.move_down()
     
class NodeToolbarButtonDelete(NodeToolbarButtonRight):
    
    @staticmethod
    def css():
        css.prop.background_image = 'url(' + images.buttons.delete_small_png + ')'        

    def __init__(self, **kwargs):
        NodeToolbarButton.__init__(self, **kwargs)
        self.page        = self.parent.parent
        self.att.title   = 'delete'

    def onclick(self, event):
        self.node.delete_attempt()
     
class NodeInsert(Gdiv):
    
    @staticmethod
    def css():
        css.prop.padding = css.pixel(2)
        css.prop.height             = css.pixel(14)
        css.prop.background_color   = css.rgb(255,255,255)
        css.prop.color              = css.rgb(150,150,150)
        css.prop.font_weight        = css.values.font_weights.x300
        css.prop.font_size          = css.pixel(8)
        #css.prop.border_left        = 'solid 2px rgb(110,110,255)'
        #css.prop.border_top         = 'solid 2px rgb(110,110,255)'

    def __init__(self, parent, position):
        Gdiv.__init__(self, parent = parent)
        self.buttons = NodeInsertButtons(parent = self)
        self.label   = NodeInsertLabel(parent = self, text = 'insert ' + position + ' ->')
        
class NodeInsertLabel(Gdiv):

    @staticmethod
    def css():
        css.prop.float = css.values.floats.right

class NodeInsertButtons(Gdiv):

    @staticmethod
    def css():
        css.prop.float = css.values.floats.right   

class NodeInsertButtonNode(NodeToolbarButtonRight):
    
    @staticmethod
    def css():
        css.prop.background_color = css.rgb(255, 255, 255)
    
    def __init__(self, parent, node, image = None, tag_line = None):
        NodeToolbarButtonRight.__init__(self, parent = parent)
        
        image = image if image is not None else getattr(images.buttons, 'insert_' + node.__name__.lower() + '_small_png')
        tag_line = tag_line if tag_line is not None else node.__name__
        
        self.style.background_image = 'url(' + image + ')'    
        self.node_id = node.pod.id
        self.att.title   = tag_line

class NodeContent(Gdiv):

    @staticmethod
    def css():
        css.prop.border_left  = 'solid 2px rgb(110,110,255)'
        css.prop.padding_left = css.pixel(2)
        css.prop.padding      = css.pixel(5)

"""
Modal 
"""

class Modal(xhtml.div):

    @staticmethod
    def css():
        css.prop.position           = css.values.positions.absolute
        css.prop.top                = '0'
        css.prop.left               = '0'
        css.prop.opacity            = 1.0
        css.prop.z_index            = 100
        css.prop.font_family        = css.values.font_families.verdana
    
    def __init__(self, parent):
        xhtml.div.__init__(self, parent = parent)
        self.state.full = True

        self.lbox  = LightBox(parent = self)
            
class LightBox(xhtml.div):

    @staticmethod
    def css():
        css.prop.position           = css.values.positions.absolute
        css.prop.top                = '0'
        css.prop.left               = '0'
        css.prop.opacity            = 0.5
        css.prop.background_color   = css.rgb(25, 25, 25)
        css.prop.z_index            = 101

    def __init__(self, parent):
        xhtml.div.__init__(self, parent = parent)
        self.state.full = True

class Frame(xhtml.div):
            
    @staticmethod
    def css():
        css.prop.background_color   = css.rgb(255,255,255)
        css.prop.padding            = css.inch(0.2);
        css.prop.border             = 'solid rgb(200,200,255) 0.15in'
        css.prop.width              = css.pixel(700)
        css.prop.z_index            = 102
        css.prop.opacity            = 1.0
    
    def __init__(self, parent):
        
        xhtml.div.__init__(self, parent = parent)
        self.state.center = True
        
"""
Confirm or Cancel with MsgBox
""" 
class Confirm(Modal):

    def __init__(self, parent, title = None, sub = None, confirm = 'Confirm', cancel = 'Cancel', callback = None):
        
        Modal.__init__(self, parent = parent)
        
        self.msg = MsgBox(parent = self, title = title, sub = sub, confirm = confirm, cancel = cancel)
                
        self.callback = callback
        
        self.event_okd = events.KeyDown(parent = self, default = False, bubble = False, sensor = self.document)
        
    def onkeydown(self, event):
        if event.key_code == 27:
            self.cancel()
        elif event.key_code == 13:
            self.confirm()
        
    def confirm(self):
        args = [] if len(self.callback) == 2 else list(self.callback[2:])
        getattr(self.callback[0], self.callback[1])(*args)
        self.cancel()
        
    def cancel(self):
        self.delete()
                
class MsgBox(Frame):
    
    @staticmethod
    def css():
        css.prop.background_color   = css.rgb(255,255,255)
        css.prop.padding            = css.inch(0.2);
        css.prop.border             = 'solid rgb(200,200,255) 0.15in'
        css.prop.width              = css.pixel(700)
        
    def __init__(self, parent, title = None, sub = None, confirm = 'Confirm', cancel = 'Cancel'):
        
        Frame.__init__(self, parent = parent)
                
        if title:
            self.msg_title  = MsgBox_title(parent = self, text = title)        
        
        self.msg_frame = MsgBox_frame(parent = self)

        if sub:
            self.msg_sub   = MsgBox_sub(parent = self, text = sub)
    
        self.controls = MsgBox_control(parent = self)
        
        self.confirm  = MsgBox_button(parent = self.controls, text = confirm, handler = self.parent, type = 'confirm')
        
        self.span     = xhtml.span(parent = self.controls, text = ' or ')
        self.span.style.padding_left  = css.inch(0.05)
        self.span.style.padding_right = css.inch(0.05)
        
        self.cancel  = MsgBox_button(parent = self.controls, text = cancel,  handler = self.parent, type = 'cancel')
        
    def onkeydown(self, event):
        self.js.alert(self)
        
class MsgBox_frame(xhtml.div):
    @staticmethod
    def css():
        css.prop.padding            = css.inch(0.1)
        css.prop.font_size          = css.pt(10)
        css.prop.font_weight        = css.values.font_weights.normal
        css.prop.color              = css.rgb(30,30,30)
        
class MsgBox_title(xhtml.div):
    
    @staticmethod
    def css():
        css.prop.padding            = css.inch(0.1)
        css.prop.font_size          = css.pt(12)
        css.prop.font_weight        = css.values.font_weights.x700
        css.prop.color              = css.rgb(50,50,50)
        
class MsgBox_sub(xhtml.div):
    
    @staticmethod
    def css():
        css.prop.background_color   = css.rgb(255,255,255)
        css.prop.padding            = css.inch(0.1);
        css.prop.font_weight        = css.values.font_weights.x400
        css.prop.color              = css.rgb(80,80,80)
        css.prop.font_size          = css.pt(11)
        css.prop.font_style         = css.values.font_styles.italic

class MsgBox_control(xhtml.div):
    
    @staticmethod
    def css():
        css.prop.padding            = css.inch(0.1)
        css.prop.float              = css.values.floats.left

class MsgBox_button(xhtml.button):

    @staticmethod
    def css():
        css.prop.padding            = css.pixel(4)
        css.prop.font_size          = css.pt(10)
        css.prop.font_weight        = css.values.font_weights.x800
        css.prop.color              = css.rgb(0,0,0)
        
    def __init__(self, parent, text, handler, type):  
        xhtml.button.__init__(self, parent = parent, text = text)      
        self.event_submit = events.Submit(parent = self, default = True, bubble = False)
        self.handler = handler
        self.type    = type
           
    def onsubmit(self, event):
        if self.type == 'confirm':
            self.handler.confirm()
        elif self.type == 'cancel':
            self.handler.cancel()


class SubMenu(xhtml.div):

    @staticmethod
    def css():
        css.prop.position         = css.values.positions.absolute
        css.prop.background_color = css.values.colors.white
        css.prop.border           = '3px solid rgb(220, 220, 255)'
        css.prop.font_size        = css.pt(8)
        css.prop.font_family      = css.values.font_families.verdana
        css.prop.color            = css.rgb(100,100,100)
        css.prop.font_weight      = css.values.font_weights.x200
        css.prop.font_style       = css.values.font_styles.italic
        css.prop.padding          = css.pixel(4)
        
    def __init__(self, parent, pos, choices, handler, handler_fn = 'onsubmenu'):
        xhtml.div.__init__(self, parent = parent)
        self.style.left = pos[0]
        self.style.top  = pos[1] + pos[3] + css.pixel(1)
        
        for choice in choices:
            SubItem(parent = self, text = choice)
        
        self.handler    = handler    
        self.handler_fn = handler_fn.__name__
                
        self.event_onmouseup = events.MouseUp(parent = self, reporter = {'event': 'target'})
    
    def onmouseup(self, event):
        getattr(self.handler, self.handler_fn)(event.report['event']['target'].text)
            
class SubItem(xhtml.div):
    @staticmethod
    def css():
        css.prop.padding             = css.pixel(4)
        css.prop.pseudo              = css.values.pseudos.hover
        css.prop.background_color    = css.rgb(220, 220, 255)
        


        
