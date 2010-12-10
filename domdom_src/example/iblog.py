import sys
import os
import inspect
import exceptions

import pod
import images

import sys
import inspect
import exceptions

import images

from domdom import dom, settings, css
import dos

""" model """

class AnEntry(pod.Object):
    blog   = pod.typed.String(index = True)
    number = pod.typed.Int(index = True) 
    title  = pod.typed.String(index = True)
    
    def __init__(self, blog, number = None, title = "", text = ""):
        pod.Object.__init__(self, blog = blog, number = number, title = title, text = text)

entry_db = pod.Db(settings.dirs.get_media() + os.sep + 'entries.pod.sqlite3', attach = AnEntry)


""" view """

def inline_css():
    return "button::-moz-focus-inner { border: 0; }"

class blog_master_div(dos.div):
    
    @staticmethod
    def css():
        css.prop.overflow       = 'auto'
        css.prop.font_family    = css.values.font_families.verdana

class BlogPage(dos.webpage):

    @staticmethod
    def route(cls, request):
        if len(request.url_args) == 0:
            return request.redirect('/examples/iblog/your_name/on/some_topic/')
        else:
            request.url_args = [arg.lower() for arg in request.url_args]
            return dos.webpage.route(cls = BlogPage, request = request)
        
    def __init__(self): 
        
        dos.webpage.__init__(self)       
        self.includes.css  <= sys.modules[__name__]        

        self.set_blog_name()
        
        self.background     = Background(parent = self.main)
        self.center_frame   = CenterFrame(parent = self.background)    
        self.panel          = Panel(parent = self.center_frame)
        self.header         = Header(parent = self.center_frame)
        self.entries        = Entries(parent = self.center_frame)
            
        self.event_oku = dos.KeyUp(parent = self, default = False, valid_keycodes = [57, 48])

        AddEntry(parent = self.entries, entry = False)
                   
        self.load_entries()

    def pre_publish(self):
        entry_db.commit()

    def set_blog_name(self):
        username = " ".join(self.request.url_args[0].split("_")).strip()
        if username[-1].lower() == 's':
            username += "' "
        else:
            username += "'s "

        args = self.request.url_args[1:]
        if len(args) > 0 and args[0].lower() == 'on':
            args = args[1:]
        
        topic = 'domdom' if len(args) == 0 else " ".join(args[0].split("_")).strip()
        self.blog_name = username + " thoughts on " + topic + " . . ."
        
    def load_entries(self):
        
        entries = [entry for entry in pod.Query(where = AnEntry.blog == self.blog_name, order_by = AnEntry.number.asc())]
                                
        if len(entries) == 0:
            AddEntry(parent = self.entries, entry = True)
        else:
            for entry in entries:
                AddEntry(parent = self.entries, entry = entry)
    
    def number(self):
        i = 1
        for child in self.entries:
            if isinstance(child, EntryView):
                child.number(number = i)
                i += 1

    def onkeyup(self, event):
        if event.ctrl:
            for child in self.entries:
                if isinstance(child, EntryView):
                    if event.key_code == 57:
                        child.toolbar.button_show_hide.hide()
                    if event.key_code == 48:
                        child.toolbar.button_show_hide.show()
          
class Background(blog_master_div):

    @staticmethod
    def css():
        css.prop.min_height         = css.inch(12)
        css.prop.background_color   = css.rgb(240,240,240)
        css.prop.padding            = css.inch(0.1)
      
class CenterFrame(blog_master_div):

    @staticmethod
    def css():
        css.prop.width              = css.inch(11)
        css.prop.min_height         = css.inch(12)
        css.prop.margin             = '0.1in auto'
        
class Panel(blog_master_div):

    @staticmethod
    def css():
        css.prop.border            = 'solid rgb(220,220,255) 2px'
        css.prop.overflow          = 'auto'
        css.prop.background_color  = css.rgb(240,240,255)
        css.prop.height            = css.inch(6)
        css.prop.width             = css.inch(2.4)  
        css.prop.margin            = css.inch(0.1)
        css.prop.float             = css.values.floats.left
        css.prop.position          = css.values.positions.fixed
        css.prop.left              = 'auto'
        css.prop.top               = css.inch(0.20)
        css.prop.padding           = css.pixel(8)
        css.prop.padding_top       = css.pixel(24)
        css.prop.color             = css.rgb(100,100,100)
        css.prop.font_size         = css.pt(9)
        css.prop.font_style        = css.values.font_styles.italic 
        
    def __init__(self, parent):
        blog_master_div.__init__(self, parent = parent)
        
        self.always = blog_master_div(parent = self, text = """
        Welcome to the iBlog -- just roll over an object for instructions on how to use. 
        """)

        self.split                  = blog_master_div(parent = self, text = '<br/><br/>--------------<br/><br/>')
        self.split.style.text_align = css.values.text_aligns.center
        
        self.special  = blog_master_div(parent = self)
        
        self.set_default_msg()
        
    def set_default_msg(self):
        self.special.text = """
        To collapse all blog entries, press Ctrl+Shift+9<br/><br/>
        To example, press Ctrl+Shift+0<br/><br/>
        """
        
class Entries(blog_master_div):

    @staticmethod
    def css():
        css.prop.font_family      = css.values.font_families.verdana

""" Page """
class Header(blog_master_div):

    @staticmethod
    def css():
        css.prop.background_color = css.rgb(255,255,255)
        css.prop.width             = css.inch(7.8)
        css.prop.height            = css.pixel(200)
        css.prop.margin            = css.inch(0.1)
        css.prop.margin_left       = css.inch(3.1)
        css.prop.background_image  = "url('" + images.anewday_png + "')"
        css.prop.font_family       = css.values.font_families.verdana
        css.prop.color             = css.rgb(255,255,255)
        css.prop.font_weight       = css.values.font_weights.bold
        css.prop.font_size         = css.pt(11)
        css.prop.font_style        = css.values.font_styles.italic
        css.prop.vertical_align    = css.values.vertical_aligns.bottom

    def __init__(self, parent):
        blog_master_div.__init__(self, parent = parent)
            
        self.title = blog_master_div(parent = self)        
        self.title.style.padding      = css.pixel(10)
        self.title.style.padding_top  = css.pixel(160)
        self.title.style.padding_left = css.pixel(20)
        self.title.text = self.document.blog_name        
        self.event_omover = dos.MouseOver(parent = self)
        self.event_omout  = dos.MouseOut(parent = self)
                
    def onmouseover(self, event):
        self.document.panel.special.text = """
        You can automatically make up any blog you want, just use the url: <br/><br/>
        &nbsp;&nbsp;&nbsp; iblog / your_full_name / on / any_topic_you_want <br/><br/>
        underscores are turned into spaces for you . . . 
        """
        
    def onmouseout(self, event):
        self.document.panel.set_default_msg()
        
class AddEntry(blog_master_div):
    
    @staticmethod
    def css():
        css.prop.background_color  = css.rgb(245,255,245)
        css.prop.width             = css.inch(7.8)
        css.prop.height            = css.pixel(18)
        css.prop.margin            = css.inch(0.1)
        css.prop.margin_left       = css.inch(3.1)
        css.prop.color             = css.rgb(115,115,115)
        css.prop.text_align        = css.values.text_aligns.center
        css.prop.padding_top       = css.pixel(3)
        css.prop.padding_bottom    = css.pixel(3)
        css.prop.font_size         = css.pt(7)
        css.prop.font_style        = css.values.font_styles.italic
    
    def __init__(self, parent = None, older = None, entry = None):
        blog_master_div.__init__(self, parent = parent, older = older, text = '-- double click here to add blog entry here --')
        self.event_odc    = dos.DblClick(parent = self)
        self.event_omover = dos.MouseOver(parent = self)
        self.event_omout  = dos.MouseOut(parent = self)

        if entry:
            EntryView(younger = self, entry = entry)

    def ondblclick(self, event):
        AddEntry(older = self, entry = True)
        
    def onmouseover(self, event):
        self.document.panel.special.text = """
        Just double click this green box and an new entry will be made <i>right</i> here . . . 
        """
        
    def onmouseout(self, event):
        self.document.panel.set_default_msg()
            
class EntryView(blog_master_div):
    
    @staticmethod
    def css():
        css.prop.background_color  = css.rgb(255,255,255)
        css.prop.width             = css.inch(7.8)
        css.prop.margin            = css.inch(0.1)
        css.prop.margin_left       = css.inch(3.1)
    
    def __init__(self, parent = None, younger = None, older = None, entry = True):
        blog_master_div.__init__(self, parent = parent, younger = younger, older = older)
        self.toolbar = EntryToolbar(parent = self)
        self.content = EntryContent(parent = self, entry = self)
        self.toolbar.title.setup()
        
        if entry is True:
            self.an_entry = AnEntry(blog = self.document.blog_name)
        else:
            self.an_entry = entry
            self.toolbar.title.back.display.text = entry.title
            self.content.display.text    = entry.text

        self.document.number()
            
        self.event_omover   = dos.MouseOver(parent = self, default = False)
        self.event_omleave  = dos.MouseLeave(parent = self,  default = False)
       
    def onmouseover(self, event):
        self.document.panel.special.text = """
        To edit the title or the entry body, just double click over the element.  
        
        <br/><br/>When you're done, just double click again or hit 'Esc' to 
        save . . .<br/><br/> 
        """
        
    def onmouseleave(self, event):
        self.document.panel.set_default_msg()
            
    def number(self, number):
        self.toolbar.title.number(number = number)
        self.an_entry.number = number

    def move_up(self):
        pos = self.get_position()
        if pos > 2:
            self.parent.children[pos-3].insert_after_me(self.parent.children[pos])
            self.parent.children[pos-2].insert_after_me(self.parent.children[pos+1])
            self.document.number()
    
    def move_down(self):
        pos = self.get_position()
        if pos+2 < len(self.parent.children):
            self.parent.children[pos+3].insert_after_me(self.parent.children[pos])
            self.parent.children[pos+3].insert_after_me(self.parent.children[pos])
            self.document.number()

    def delete(self):
        self.an_entry.delete()
        blog_master_div.delete(self)
        
""" Toolbar """
class EntryToolbar(blog_master_div):
    
    @staticmethod
    def css():
        css.prop.background_color  = css.rgb(240,240,255)
        css.prop.width             = css.inch(7.65)
        css.prop.height            = css.pixel(34)
        css.prop.margin            = css.pixel(4)
        css.prop.padding           = css.pixel(2)
        
    def __init__(self, parent):
        blog_master_div.__init__(self, parent = parent)
        self.table                   = dos.table(parent = self)
        self.table.style.width       = css.percent(100)
        self.row                     = dos.tr(parent = self.table)
        self.col_0                   = dos.td(parent = self.row)
        self.col_1                   = dos.td(parent = self.row)
        self.col_1.style.width       = css.percent(100)
        self.col_2                   = dos.td(parent = self.row)
        self.col_3                   = dos.td(parent = self.row)
        self.col_4                   = dos.td(parent = self.row)

        self.button_show_hide        = ButtonShowHide(parent = self.col_0, entry = self.parent)
        self.title                   = ToolbarTitle(parent = self.col_1,   entry = self.parent)
        self.button_move_down        = ButtonMoveDown(parent = self.col_2, entry = self.parent)
        self.button_move_up          = ButtonMoveUp(parent = self.col_3,   entry = self.parent)
        self.button_delete           = ButtonDelete(parent = self.col_4,   entry = self.parent)
              
class Button(dos.button):
        
    @staticmethod
    def css():
        css.prop.width               = css.pixel(24) 
        css.prop.height              = css.pixel(24) 
        css.prop.padding             = css.pixel(5)
        css.prop.margin_left         = css.pixel(3)
        css.prop.margin              = css.pixel(1)
        css.prop.background_color    = css.rgb(230,230,255)
        css.prop.border              = 'rgb(200, 200, 255) solid 1px'
        css.prop.background_repeat   = 'no-repeat'
        css.prop.background_position = 'center'
        css.prop.position            = css.values.positions.relative
        
        css.prop.pseudo              = css.values.pseudos.active
        css.prop.background_color    = css.rgb(175,175,255)

    def __init__(self, entry, **kwargs):
        dos.button.__init__(self, **kwargs)
        self.entry       = entry
        self.event_omc   = dos.Click(parent = self, default = True)

class ButtonLeft(Button):    
    
    @staticmethod
    def css():
        css.prop.float = css.values.floats.left
        css.prop.margin_right = css.pixel(4)

class ButtonRight(Button):    
    
    @staticmethod
    def css():
        css.prop.float = css.values.floats.right
        css.prop.margin_left = css.pixel(4)

class ButtonShowHide(ButtonLeft):
    
    @staticmethod
    def css():
        css.prop.background_image = 'url(' + images.hide_png + ')'        

    def __init__(self, **kwargs):
        
        ButtonLeft.__init__(self, **kwargs)
        self.on          = True        
        self.att.title   = 'hide'
        
    def onclick(self, event):
        if self.on is True:
            self.hide()
        else:
            self.show()
            
    def hide(self):
        self.style.background_image  = 'url(' + images.show_png + ')'
        self.entry.content.parent    = None
        self.on                      = False
        self.att.title               = 'show'

    def show(self):
        self.style.background_image = 'url(' + images.hide_png + ')'
        self.entry.content.parent   = self.entry
        self.on = True
        self.att.title = 'hide'

class ButtonMoveUp(ButtonRight):
    
    @staticmethod
    def css():
        css.prop.background_image = 'url(' + images.up_png + ')'        

    class att:
        title = 'Move Up'

    def onclick(self, event):
        self.entry.move_up()
     
class ButtonMoveDown(ButtonRight):
    
    @staticmethod
    def css():
        css.prop.background_image = 'url(' + images.down_png + ')'        

    class att:
        title = 'Move Down'

    def onclick(self, event):
        self.entry.move_down()
     
class ButtonDelete(ButtonRight):
    
    @staticmethod
    def css():
        css.prop.background_image = 'url(' + images.delete_png + ')'        

    class att:
        title = 'Delete'

    def onclick(self, event):
        document = self.document
        self.entry.get_older().delete()
        self.entry.delete()
        document.number()
      
""" The title """  
class ToolbarTitle(blog_master_div):

    @staticmethod
    def css():
        css.prop.color             = css.rgb(80,80,80)
        css.prop.font_size         = css.pt(10)
        css.prop.width             = css.inch(5.4)
        css.prop.padding           = css.pixel(2)
        css.prop.padding_left      = css.pixel(10)
    
    def __init__(self, parent, entry):
        blog_master_div.__init__(self, parent = parent)
        self.entry = entry
        
    def setup(self):
        self.table = dos.table(parent = self)
        self.row   = dos.tr(parent = self.table)
        self.col_0 = dos.td(parent = self.row)
        self.col_1 = dos.td(parent = self.row)
        self.front = FrontTitle(parent = self.col_0)
        self.back  = BackTitle(parent = self.col_1, entry = self.entry)

    def number(self, number):
        self.front.text = "Post #" + str(number) + ": "

class FrontTitle(blog_master_div):
    
    @staticmethod
    def css():
        css.prop.float          = css.values.floats.left
        css.prop.padding_right  = css.pixel(4)

class BackTitle(blog_master_div):
    
    @staticmethod
    def css():
        css.prop.font_style        = css.values.font_styles.italic
        css.prop.width             = css.percent(100)
        css.prop.background_color  = css.rgb(245,245,255)

    def __init__(self, parent, entry):        
        blog_master_div.__init__(self, parent = parent)
        self.display        = dos.div(parent = self)
        self.display.text   = '-- add title --'
        self.entry          = entry
        self.mode_display   = True
        self.event_on_click = dos.DblClick(parent = self, sensor = self.entry.toolbar, default = False)
        self.event_oku      = dos.KeyUp(parent = self,    sensor = self.entry.toolbar, default = False, valid_keycodes = [13, 27])
           
    def event_omd(self, event):
        self.state.focus    = True
        
    def ondblclick(self, event):
        self.switch_modes()
    
    def onkeyup(self, event):
        self.switch_modes()

    def switch_modes(self):
        if self.mode_display:
            self.mode_display     = False
            self.display.parent   = None
            text = self.display.text
            text = text if text  != '-- add title --' else " "
            self.edit             = TitleEdit(parent = self, value = text)
            self.edit.state.focus = True
        elif self.mode_display is False:
            self.mode_display    = True
            title = self.edit.att.value.strip().replace("<", "").replace(">", "")
            title = '-- add title --' if len(title) < 2 else title
            self.entry.an_entry.title = title 
            self.display.text         = title
            self.display.parent       = self
            self.edit.delete()

class TitleEdit(dos.input_text):
    
    @staticmethod
    def css():
        css.prop.background_color  = css.rgb(245,245,255)
        css.prop.color             = css.rgb(20,20,20)
        css.prop.height            = css.pixel(13)
        css.prop.font_size         = css.pt(6)
        css.prop.width             = css.inch(4.0)
        css.prop.border            = 'solid 1px rgb(210, 210, 255)'

    def __init__(self, parent, value):
        dos.input_text.__init__(self, parent = parent, value = value)
        self.event_onblur   = dos.Blur(parent = self, value = True)
        self.event_omd      = dos.MouseDown(parent = self, value = True)
        self.event_okd      = dos.KeyDown(parent = self, value = True, default = False, valid_keycodes = [13, 27])

    def onblur(self, event):
        self.parent.switch_modes()
        
""" Content """        
class EntryContent(blog_master_div):
    
    @staticmethod
    def css():
        css.prop.background_color  = css.rgb(255,245,245)
        css.prop.width             = css.inch(7.4)
        css.prop.min_height        = css.inch(4.0)
        css.prop.margin            = css.pixel(10)
        css.prop.padding           = css.pixel(10)
    
    def __init__(self, parent, entry):        
        blog_master_div.__init__(self, parent = parent)
        self.display        = dos.div(parent = self)
        self.mode_display   = True
        self.event_on_click = dos.DblClick(parent = self)
        self.event_oku      = dos.KeyUp(parent = self, default = False, valid_keycodes = [27])
        self.entry          = entry
        
       
    def ondblclick(self, event):
        self.switch_modes()
    
    def onkeyup(self, event):
        self.switch_modes()

    def switch_modes(self):
        if self.mode_display:
            self.mode_display     = False
            self.display.parent   = None
            self.edit             = EntryEdit(parent = self, value = dom.util.convert_from_xhtml(self.display.text))
            self.edit.state.focus = True
        elif self.mode_display is False:
            self.mode_display        = True
            text                     = dom.util.convert_to_xhtml(self.edit.att.value)
            self.display.text        = text
            self.entry.an_entry.text = text
            self.display.parent      = self
            self.edit.delete()

class EntryEdit(dos.textarea):
    
    @staticmethod
    def css():
        css.prop.background_color  = css.rgb(255,255,255)
        css.prop.width             = css.inch(7.3)
        css.prop.height            = css.inch(4.0)

    def __init__(self, parent, value):
        dos.textarea.__init__(self, parent = parent, value = value)
        self.event_onblur   = dos.Blur(parent = self, value = True)
        self.event_omd      = dos.MouseDown(parent = self, value = True)
        self.event_okd      = dos.KeyDown(parent = self, value = True, default = False, valid_keycodes = [27])


      