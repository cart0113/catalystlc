import sys
import os
import inspect
import exceptions

from domdom import dom, xhtml, css, settings, routers, events, fx

import pod
import images

import sys
import inspect
import exceptions

import images

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

class blog_master_div(xhtml.div):
    
    @staticmethod
    def css():
        css.prop.overflow       = 'auto'
        css.prop.font_family    = css.values.font_families.verdana

class BlogPage(xhtml.webpage):

    @staticmethod
    def route(cls, request):
        if len(request.url_args) == 0:
            return request.redirect('/examples/iblog/your_name/on/some_topic/')
        else:
            request.url_args = [arg.lower() for arg in request.url_args]
            return xhtml.webpage.route(cls = BlogPage, request = request)
        
    def __init__(self): 
        
        xhtml.webpage.__init__(self)       
        self.includes.css  <= sys.modules[__name__]        
        
    
        self.header = MyDiv(parent = self.body, text = 'CLICK ON ME')
        
        self.side_bar = xhtml.div(parent = self.body, text = 'HELLO')
        self.side_bar.style.background_color = css.rgb(255, 0, 0)
        
        self.cont = xhtml.div(parent = self.body)
        
    

class MyDiv(xhtml.div):
    
    @staticmethod
    def css():
        css.prop.background_color = css.rgb(100, 100, 100)
        css.prop.height = css.pixel(10)
        css.prop.width  = css.pixel(100)
        

    def __init__(self, **kwargs):
        xhtml.div.__init__(self, **kwargs)
        self.event_omd = events.MouseDown(parent = self)

        
    def onmousedown(self, event):    
        self.style.background_color = css.rgb(0, 255, 0)
        self.text += 'HI'
        
        for i in range(10):
            div = xhtml.div(parent = self.document.cont, text = 'ME')
        




      